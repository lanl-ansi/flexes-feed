import sys
import time
from redis import StrictRedis

REDIS_HOST = 'localhost'

class Subscriber:
    def __init__(self, channel):
        self.channel = channel
        self.db = StrictRedis(REDIS_HOST)

    def process(self):
        raise NotImplementedError('process method must be overridden')

    def message_handler(self, message):
                s3_uri = message['data'].decode()
                print('{} published a new file {}'.format(self.channel, s3_uri))
                self.process(s3_uri)

    def subscribe(self):
            p = self.db.pubsub(ignore_subscribe_messages=True)
            p.subscribe(**{self.channel: self.message_handler})
            while True:
                try:
                    message = p.get_message()
                    time.sleep(1)
                except KeyboardInterrupt:
                    print('\rStopping subscriber')
                    sys.exit()
                except Exception as e:
                    print(e)
                    # Send notification that subscriber encountered an exception
                finally:
                    p.close()

        
