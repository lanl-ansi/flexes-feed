import os, pytest, sys

sys.path.append('')

import mock
from datetime import datetime
from subscriber import Subscriber

class DummySubscriber(Subscriber):
    def process(self):
        return True

class TestSubscriber:
    def setup_method(self, _):
        self.channel = 'test-data-feed'
        self.bad_sub = Subscriber(self.channel)
        self.good_sub = DummySubscriber(self.channel)
        self.good_sub.db = mock.MagicMock()

    def test_process_not_implemented(self):
        with pytest.raises(NotImplementedError):
            self.bad_sub.process()

    def test_process(self):
        assert(self.good_sub.process())

    def test_subscribe(self):
        self.good_sub.db.pubsub.return_value.listen.return_value = [{'data': b's3://bucket/path/to/file'}]
        self.good_sub.subscribe()
        self.good_sub.db.pubsub.return_value.subscribe.assert_called_with(self.channel)
        self.good_sub.db.pubsub.return_value.close.assert_called()
