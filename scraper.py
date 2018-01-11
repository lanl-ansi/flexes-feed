import requests
import sys
import time
from aws_utils import s3_utils
from datetime import datetime, timedelta
from redis import StrictRedis

REDIS_HOST = 'localhost'
LAST_MODIFIED_CHANNEL = 'data-feeds:last-modified'

class Scraper:
    def __init__(self, s3_folder, channel, frequency=600):
        print('class init')
        self.dest = s3_folder
        self.channel = channel
        self.frequency = frequency
        self.db = StrictRedis(REDIS_HOST)

    def check(self):
        # Track last file update
        # Return list of new files
        raise NotImplementedError('check method must be overridden')

    def scrape(self):
        # Scrape page and return file update information
        raise NotImplementedError('scrape method must be overridden')

    def publish(self, file_url, filename=None, subfolder='', last_modified=datetime.utcnow()):
        filename = os.path.basename(file_url) if filename is None else filename
        s3_file = os.path.join(self.dest, subfolder, filename)
        with requests.get(new_file, stream=True) as response_stream:
            s3_utils.stream_to_s3(response_stream, s3_file)
        self.db.publish(self.channel, s3_file)
        self.db.hset(LAST_MODIFIED_CHANNEL, new_file, str(last_modified))

    def last_modified(self, filename):
        # Create key in last-modified store 
        # if it doesn't already exist set it 
        # to 2000-01-01 00:00:00
        if self.db.hexists(LAST_MODIFIED_CHANNEL, filename):
            t = self.db.hget(LAST_MODIFIED_CHANNEL, filename).decode()
            date_modified = datetime.strptime(t, '%Y-%m-%d %H:%M:%S')
        else:
            date_modified = datetime(2000, 1, 1)
            self.db.hset(LAST_MODIFIED_CHANNEL, filename, str(date_modified))
        return date_modified

    def run(self):
        try:
            while True:
                new_files = self.check()
                for f in new_files:
                    self.publish(f)
                time.sleep(self.frequency)
        except KeyboardInterrupt:
            print('Stopping scraper')
            sys.exit()
        except Exception as e:
            # Send notification that scraper encountered an exception
            print(e)
