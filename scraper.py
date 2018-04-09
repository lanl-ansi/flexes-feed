import os
import requests
import sys
import time
from aws_utils import s3_utils
from datetime import datetime, timedelta
from io import BytesIO
from redis import StrictRedis

REDIS_HOST = 'localhost'
LAST_MODIFIED_CHANNEL = 'data-feeds:last-modified'

class NewFile:
    def __init__(self, url, s3_folder, filename=None, subfolder='', last_modified=datetime.utcnow()):
        self.url = url
        self.filename = os.path.basename(url) if filename is None else filename
        self.s3_file = os.path.join(s3_folder, subfolder, self.filename)
        self.last_modified = last_modified


class Scraper:
    def __init__(self, s3_folder, channel, frequency=600):
        self.s3_folder = s3_folder
        self.channel = channel
        self.frequency = frequency
        self.db = StrictRedis(REDIS_HOST)

    def check(self):
        # Track last file update
        # Return list of new files
        raise NotImplementedError('check method must be overridden')

    def download_file(new_file):
        response = requests.get(new_file.url)
        print('Publishing {}'.format(new_file.url))
        data = BytesIO(response.content)
        s3_utils.stream_to_s3(data, new_file.s3_file)

    def publish(self, new_file):
        download_file(new_file)
        self.db.publish(self.channel, new_file.s3_file)
        self.db.hset(LAST_MODIFIED_CHANNEL, new_file.url, str(new_file.last_modified))

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
            print('\rStopping scraper')
            sys.exit()
        except Exception as e:
            # Send notification that scraper encountered an exception
            print(e)
