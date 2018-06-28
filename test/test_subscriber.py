import os, pytest, sys

sys.path.append('')

import mock
from datetime import datetime
from redis import StrictRedis
from subscriber import Subscriber

class DummySubscriber(Subscriber):
    def process(self):
        return True

class TestSubscriber:
    def setup_method(self, _):
        self.channel = 'test-data-feed'
        self.bad_sub = Subscriber(channel=self.channel)
        self.good_sub = DummySubscriber(channel=self.channel)
        self.good_sub.db = mock.MagicMock()

    def test_process_not_implemented(self):
        with pytest.raises(NotImplementedError):
            self.bad_sub.process()

    def test_process(self):
        assert(self.good_sub.process())

    @mock.patch('time.sleep', side_effect=KeyboardInterrupt)
    def test_subscribe(self, mock_sleep):
        with pytest.raises(SystemExit) as e:
            self.good_sub.subscribe()
            self.good_sub.db.pubsub.return_value.close.assert_called()
