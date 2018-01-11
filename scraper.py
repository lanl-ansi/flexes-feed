import requests
import sys
import time
from aws_utils.aws_utils import s3_utils
from datetime import datetime, timedelta
from redis import StrictRedis

REDIS_HOST = 'localhost'
LAST_MODIFIED_CHANNEL = 'data-feeds:last-modified'

class Scraper(object):
    def __init__(self, url, s3_folder, channel, frequency=600):
        self.url = url
        self.dest = s3_folder
        self.channel = channel
        self.frequency = frequency
        self.db = StrictRedis(REDIS_HOST)

    def check(self):
        # Track last file update
        # Return list of new files
        raise NotImplementedError('check method must be overridden')

    def publish(self, new_file, last_modified=datetime.utcnow()):
        filename = os.path.basename(new_file)
        s3_file = os.path.join(self.dest, filename)
        with requests.get(new_file, stream=True) as response_stream:
            s3_utils.stream_to_s3(response_stream, s3_file)
        self.db.publish(self.channel, s3_file)
        self.db.hset(LAST_MODIFIED_CHANNEL, self.channel, str(last_modified))

    def scrape(self):
        # Scrape page and return file update information
        raise NotImplementedError('scrape method must be overridden')

    def last_modified(self):
        t = self.db.hget(LAST_MODIFIED_CHANNEL, self.channel).decode()
        return datetime.strptime(t, '%Y-%m-%d %H:%M:%S')

    def run(self):
        try:
            # Create key in last-modified store 
            # if it doesn't already exist set it 
            # to 2000-01-01 00:00:00
            self.db.hsetnx(LAST_MODIFIED_CHANNEL, 
                           self.channel, 
                           str(datetime(2000, 1, 1)))
            while True:
                new_files = self.check()
                for f in new_files:
                    publish(f)
                time.sleep(self.frequency)
        except KeyboardInterrupt:
            print('Stopping scraper')
            sys.exit()
        except Exception as e:
            # Send notification that scraper encountered an exception
            print(e)
