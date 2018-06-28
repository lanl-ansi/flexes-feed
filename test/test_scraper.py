import os, pytest, sys

sys.path.append('')

import mock
from datetime import datetime
from scraper import Scraper

class DummyScraper(Scraper):
    def check(self):
        return True

class TestScraper:
    def setup_method(self, _):
        s3_folder = 's3://bucket/path/to/folder'
        channel = 'test-data-feed'
        self.bad_scraper = Scraper(s3_folder=s3_folder, channel=channel)
        self.good_scraper = DummyScraper(s3_folder=s3_folder, channel=channel)
        self.good_scraper.db = mock.MagicMock()

    def test_check_not_implemented(self):
        with pytest.raises(NotImplementedError):
            self.bad_scraper.check()

    def test_check(self):
        assert(self.good_scraper.check())

    def test_last_modified(self):
        self.good_scraper.db.hget.return_value = '2003-04-01 00:00:00'
        last_modified = self.good_scraper.last_modified('http://foo.com/file.txt')
        assert(last_modified == datetime(2003,4,1))

    def test_last_modified_not_exist(self):
        self.good_scraper.db.hget.return_value = None
        last_modified = self.good_scraper.last_modified('http://foo.com/file.txt')
        assert(last_modified is None)

    @mock.patch('time.sleep', side_effect=KeyboardInterrupt)
    def test_run(self, mock_sleep):
        self.good_scraper.check = mock.MagicMock(return_value=['new_file'])
        self.good_scraper.publish = mock.MagicMock()
        with pytest.raises(SystemExit) as e:
            self.good_scraper.run()
            self.good_scraper.publish.assert_called()
