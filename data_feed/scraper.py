import os
import requests
import signal
import sys
import time
#from aws_utils import s3_utils
from .config import load_config
from datetime import datetime, timedelta
from redis import StrictRedis
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class NewFile:
    def __init__(self, url, s3_folder, filename=None, subfolder='', last_modified=None):
        """Constructor for NewFile data class
        
        Args:
            url (str): URL for new file. Used to download the file to S3
            s3_folder (str): Location on S3 to save the new file
            filename (str): (optional) Filename for S3 file, default is the basename in the file URL
            subfolder (str): (optional) Subfolder in s3_folder to save the file, default is s3_folder
            last_modified (datetime): Timestamp representing the last time the file was modified (default None)
        """
        self.url = url
        self.filename = os.path.basename(url) if filename is None else filename
        self.s3_file = os.path.join(s3_folder, subfolder, self.filename)
        self.last_modified = last_modified


class Scraper:
    def __init__(self, *args, **kwargs):
        """Constructor for the Scraper
        
        Args:
            channel (str): The Redis pub/sub channel for the subscriber to publish to
            s3_folder (str): Default location for new files (e.g., s3://bucket/path/to/folder)
            frequency (float): Time (in seconds) between checking for new files (default 600)
        """
        self.config = load_config()
        self.channel = kwargs['channel']
        self.s3_folder = kwargs['s3_folder']
        self.frequency = kwargs.get('frequency', 600)
        self.db = StrictRedis(self.config['REDIS_HOST'], decode_responses=True)

    def check(self):
        """Method used to check for new files
        
        Returns:
            new_files (list): Should return a list of NewFile objects which will be 
                uploaded to the specified location on S3
        """
        # Track last file update
        # Return list of new files
        raise NotImplementedError('check method must be overridden')

    def download_file(self, new_file):
        """Download NewFile object to S3"""
        session = requests.Session()
        retry = Retry(total=3, read=3, connect=3, 
                      backoff_factor=0.3, status_forcelist=(500,502,504))
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        response = session.get(new_file.url, stream=True)
        print('Publishing {}'.format(new_file.url))
#        s3_utils.stream_to_s3(response.raw, new_file.s3_file)

    def publish(self, new_file):
        """Publish the S3 URI of the new file on the Scraper's channel"""
        self.download_file(new_file)
        self.db.publish(self.channel, new_file.s3_file)
        if new_file.last_modified is not None:
            self.db.hset(self.config['LAST_MODIFIED_CHANNEL'], new_file.url, str(new_file.last_modified))

    def last_modified(self, filename):
        """Retrieve the timestamp of when the file was last modified"""
        t = self.db.hget(self.config['LAST_MODIFIED_CHANNEL'], filename)
        date_modified = datetime.strptime(t, '%Y-%m-%d %H:%M:%S') if t is not None else None
        return date_modified

    def report_error(self, error):
        """Publish error to SNS topic"""
        sns = boto3.resource('sns')
        topic = sns.Topic(self.config['SNS_TOPIC'])
        subject = 'Scraper error: {}'.format(self.url)
        topic.publish(Subject=subject, Message=error)

    def gracefully_exit(self, signo, stack_frame):
        """Gracefully exit when SIGTERM signal is received"""
        print('SIGTERM received')
        if self.config['SNS_TOPIC']: 
            self.report_error('Scraper terminated')
        sys.exit(signo)

    def run(self):
        """Start the scraper"""
        signal.signal(signal.SIGTERM, self.gracefully_exit) 
        errors = 0
        while True:
            try:
                new_files = self.check()
                for f in new_files:
                    self.publish(f)
                time.sleep(self.frequency)
            except KeyboardInterrupt:
                print('\rStopping scraper')
                sys.exit()
            except Exception as e:
                print(e)
                errors += 1
                time.sleep(self.frequency)
                if errors == 5:
                    print('Error limit exceeded')
                    if self.config['SNS_TOPIC']: 
                        self.report_error(e)
                    break
