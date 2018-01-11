import os, pytest, sys

sys.path.append('')

import mock
from datetime import datetime
from scraper import Scraper

class DummyScraper(Scraper):
    def check(self):
        return True

    def scrape(self):
        return True

class TestScraper:
    def setup_method(self, _):
        s3_folder = 's3://bucket/path/to/folder'
        channel = 'test-data-feed'
        self.bad_scraper = Scraper(s3_folder, channel)
        self.good_scraper = DummyScraper(s3_folder, channel)
        self.good_scraper.db = mock.MagicMock()

    def test_check_not_implemented(self):
        with pytest.raises(NotImplementedError):
            self.bad_scraper.check()

    def test_check(self):
        assert(self.good_scraper.check())

    def test_scrape_not_implemented(self):
        with pytest.raises(NotImplementedError):
            self.bad_scraper.scrape()

    def test_scrape(self):
        assert(self.good_scraper.scrape())
    
    def test_last_modified(self):
        self.good_scraper.db.hexists.return_value = True
        self.good_scraper.db.hget.return_value = b'2003-04-01 00:00:00'
        last_modified = self.scraper.last_modified('http://foo.com/file.txt')
        assert(last_modified == datetime(2003,4,1))

    def test_last_modified(self):
        self.good_scraper.db.hexists.return_value = False
        last_modified = self.good_scraper.last_modified('http://foo.com/file.txt')
        assert(last_modified == datetime(2000,1,1))

