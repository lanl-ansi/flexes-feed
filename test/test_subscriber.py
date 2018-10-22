import os, pytest, sys

import mock
import time
from datetime import datetime
from redis import StrictRedis
from data_feed.subscriber import Subscriber
from signal import SIGTERM
from threading import Thread

class DummySubscriber(Subscriber):
    def process(self):
        return True

class TestSubscriber:
    @mock.patch('data_feed.subscriber.StrictRedis')
    def setup_method(self, _, mock_db):
        self.channel = 'test-data-feed'
        self.bad_sub = Subscriber(channel=self.channel)
        self.good_sub = DummySubscriber(channel=self.channel)

    def test_process_not_implemented(self):
        with pytest.raises(NotImplementedError):
            self.bad_sub.process()

    def test_process(self):
        assert(self.good_sub.process())

    @mock.patch('time.sleep', side_effect=KeyboardInterrupt)
    def test_subscribe(self, mock_sleep):
        with pytest.raises(SystemExit):
            self.good_sub.subscribe()
            self.good_sub.db.pubsub.return_value.close.assert_called()

    @mock.patch('time.sleep')
    def test_subscribe_SIGTERM(self, mock_sleep):
        pid = os.getpid()
        def trigger_signal():
            while len(mock_sleep.mock_calls) < 1:
                time.sleep(0.2)
            os.kill(pid, SIGTERM)

        with pytest.raises(SystemExit):
            thread = Thread(target=trigger_signal)
            thread.daemon = True
            thread.start()

            self.good_sub.subscribe()
            self.good_sub.db.pubsub.return_value.close.assert_called()
            self.good_sub.gracefully_exit.assert_called()
