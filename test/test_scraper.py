import os, pytest, sys

sys.path.append('')

import mock
from datetime import datetime
from scraper import Scraper

def test_override():
    return True

class TestScraper:
    def setup_method(self, _):
        url = 'http://foo.com'
        s3_folder = 's3://bucket/path/to/folder'
        channel = 'test-data-feed'
        self.scraper = Scraper(url, s3_folder, channel)
        self.scraper.db = mock.MagicMock()

    def test_check_not_implemented(self):
        with pytest.raises(NotImplementedError):
            self.scraper.check()

    def test_check(self):
        self.scraper.check = test_override
        assert(self.scraper.check())

    def test_scrape_not_implemented(self):
        with pytest.raises(NotImplementedError):
            self.scraper.scrape()

    def test_scrape(self):
        self.scraper.scrape = test_override
        assert(self.scraper.scrape())
    
    def test_last_modified(self):
        d = datetime.now()
        self.scraper.db.hget.return_value = b'2000-01-01 00:00:00'
        last_modified = self.scraper.last_modified()
        assert(last_modified == datetime(2000,1,1))

