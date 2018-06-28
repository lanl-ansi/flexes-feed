import os
import requests
import signal
import sys
import time
from aws_utils import s3_utils
from config import load_config
from datetime import datetime, timedelta
from redis import StrictRedis
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class NewFile:
    def __init__(self, url, s3_folder, filename=None, subfolder='', last_modified=None):
        self.url = url
        self.filename = os.path.basename(url) if filename is None else filename
        self.s3_file = os.path.join(s3_folder, subfolder, self.filename)
        self.last_modified = last_modified


class Scraper:
    def __init__(self, s3_folder, channel, frequency=600):
        self.config = load_config()
        self.s3_folder = s3_folder
        self.channel = channel
        self.frequency = frequency
        self.db = StrictRedis(self.config['REDIS_HOST'], decode_responses=True)

    def check(self):
        # Track last file update
        # Return list of new files
        raise NotImplementedError('check method must be overridden')

    def download_file(self, new_file):
        session = requests.Session()
        retry = Retry(total=3, read=3, connect=3, 
                      backoff_factor=0.3, status_forcelist=(500,502,504))
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        response = session.get(new_file.url, stream=True)
        print('Publishing {}'.format(new_file.url))
        s3_utils.stream_to_s3(response.raw, new_file.s3_file)

    def publish(self, new_file):
        self.download_file(new_file)
        self.db.publish(self.channel, new_file.s3_file)
        if new_file.last_modified is not None:
            self.db.hset(self.config['LAST_MODIFIED_CHANNEL'], new_file.url, str(new_file.last_modified))

    def last_modified(self, filename):
        t = self.db.hget(self.config['LAST_MODIFIED_CHANNEL'], filename)
        date_modified = datetime.strptime(t, '%Y-%m-%d %H:%M:%S') if t is not None else None
        return date_modified

    def report_error(self, error):
        sns = boto3.resource('sns')
        topic = sns.Topic(self.config['SNS_TOPIC'])
        subject = 'Scraper error: {}'.format(self.url)
        topic.publish(Subject=subject, Message=error)

    def gracefully_exit(self, signo, stack_frame):
        print('SIGTERM received')
        if self.config['SNS_TOPIC']: 
            self.report_error('Scraper terminated')

    def run(self):
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
