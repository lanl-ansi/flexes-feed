import boto3
import signal
import sys
import time
from .config import load_config
from redis import StrictRedis

class Subscriber:
    """Base class for the data feed subscriber. Users are required to override the 
    `process` method which is passed the S3 URI when a file is published on the 
    subscribed channel.
    
    Args:
        channel (str): The Redis pub/sub channel for the subscriber to listen to
        frequency (float): Time (in seconds) between checking for new messages (default 1.0)
    """
    def __init__(self, *args, **kwargs):
        self.config = load_config()
        self.channel = kwargs['channel']
        self.frequency = kwargs.get('frequency', 1)
        self.db = StrictRedis(self.config['REDIS_HOST'], decode_responses=True)
        self.sub = self.db.pubsub(ignore_subscribe_messages=True)
        self.sub.subscribe(**{self.channel: self.message_handler})

    def process(self, s3_uri):
        """Method to process a message published on the subscribed channel.
        
        Args:
            s3_uri (str): File URI published on the channel (e.g., s3://bucket/path/to/new/file.txt)
        """
        raise NotImplementedError('process method must be overridden')

    def message_handler(self, message):
        """Handler called when a new message is published on the subscribed channel"""
        s3_uri = message['data']
        print('{} published a new file {}'.format(self.channel, s3_uri))
        self.process(s3_uri)

    def check_for_message(self):
        """Optional method which can be used to aggregate message information rather 
        than operating on messages individually as through the `message_handler`. 
        This can be useful when multiple files are pulled at the same time and the 
        subscriber wants to wait for all of the files to be published before taking 
        action."""
        self.sub.get_message()

    def report_error(self, error):
        """Publish error to SNS topic"""
        sns = boto3.resource('sns')
        topic = sns.Topic(self.config['SNS_TOPIC'])
        subject = 'Subscriber error: {}'.format(self.channel)
        topic.publish(Subject=subject, Message=error)

    def gracefully_exit(self, signo, stack_frame):
        """Gracefully exit when SIGTERM signal is received"""
        print('SIGTERM received')
        if self.config['SNS_TOPIC']:
            self.report_error('Subscriber terminated')
        self.sub.close()
        sys.exit(signo)

    def subscribe(self):
        """Start the subscriber"""
        signal.signal(signal.SIGTERM, self.gracefully_exit) 
        p = self.db.pubsub(ignore_subscribe_messages=True)
        p.subscribe(**{self.channel: self.message_handler})
        while True:
            try:
                self.check_for_message()
                time.sleep(self.frequency)
            except KeyboardInterrupt:
                print('\rStopping subscriber')
                self.sub.close()
                sys.exit()
            except Exception as e:
                if self.config['SNS_TOPIC']:
                    self.report_error(e)
                self.sub.close()
                sys.exit()
