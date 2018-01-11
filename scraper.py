import requests
import sys
import time

class Scraper(object):
    def __init__(self, url, s3_folder, channel, frequency=600):
        self.url = url
        self.dest = s3_folder
        self.channel = channel
        self.frequency = frequency

    def check(self):
        # Track last file update
        # Return list of new files
        raise NotImplementedError('check method must be overridden')

    def publish(self, new_file):
        # Upload new file to s3
        # Publish new file on publish channel
        pass

    def scrape(self):
        # Scrape page and return file update information
        raise NotImplementedError('scrape method must be overridden')

    def run(self):
        try:
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
            pass
