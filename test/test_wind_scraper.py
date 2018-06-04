import os, pytest, sys

sys.path.append('')

import mock
from datetime import datetime
from noaa_wind_scraper import WindForecastScraper

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

class TestWindForecastScraper:
    def setup_method(self, _):
        with open(os.path.join(ROOT_DIR, 'data/test_page.html')) as f:
            self.response_content = f.read()
        s3_folder = 's3://lanlytics/test/folder'
        channel = 'http://path/to/data'
        self.scraper = WindForecastScraper(s3_folder, channel)
        self.scraper.db = mock.MagicMock()
        self.scraper.db.hget.return_value = None

    @mock.patch('requests.get')
    def test_check(self, mock_get):
        mock_get.return_value.content = self.response_content
        new_files = self.scraper.check()
        assert(len(new_files) == 6)

    def test_scrape(self):
        expected_date = datetime(2018,1,11,23,49)
        mock_response = mock.MagicMock()
        mock_response.content = self.response_content
        date_modified = self.scraper.scrape(mock_response)
        assert(date_modified == expected_date)

