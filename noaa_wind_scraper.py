import os
import requests
from bs4 import BeautifulSoup
from collections import namedtuple
from datetime import datetime
from scraper import NewFile, Scraper

Forecast = namedtuple('Forecast', ['url', 'location', 'period'])

class WindForecastScraper(Scraper):
    def check(self):
        new_files = []
        forecasts = [Forecast(*[os.path.join(self.channel, location, period), location, period])
                        for location in ['AR.conus', 'AR.hawaii', 'AR.puertori']
                        for period in ['VP.001-003', 'VP.004-007']]
        for forecast in forecasts:
            file_url = os.path.join(forecast.url, 'ds.wspd.bin')
            response = requests.get(forecast.url)
            date_modified = self.scrape(response)
            if date_modified > self.last_modified(file_url):
                d = datetime.strftime(date_modified, '%Y%d%m%H%M')
                filename = '_'.join([forecast.location, forecast.period, d, 'ds.wspd.bin'])
                new_file = NewFile(file_url, self.s3_folder, filename=filename, last_modified=date_modified)
                new_files.append(new_file)
        return new_files

    def scrape(self, response):
        soup = BeautifulSoup(response.content, 'lxml')
        date_modified = soup.find(href='ds.wspd.bin').parent.nextSibling.text
        return datetime.strptime(date_modified, '%d-%b-%Y %H:%M ')


def check_forecasts():
    s3_folder = 's3://lanlytics/test1'
    channel = 'http://tgftp.nws.noaa.gov/SL.us008001/ST.opnl/DF.gr2/DC.ndfd'
    wind_scraper = WindForecastScraper(s3_folder=s3_folder, channel=channel, frequency=300)
    wind_scraper.run()

if __name__ == '__main__':
    check_forecasts()
