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
            latest_forecast = self.scrape(response)
            last_modified = self.last_modified(file_url)
            if last_modified is None:
                last_modified = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            if latest_forecast > last_modified:
                d = datetime.strftime(latest_forecast, '%Y%d%m%H%M')
                filename = '_'.join([forecast.location, forecast.period, d, 'ds.wspd.bin'])
                new_file = NewFile(file_url, self.s3_folder, filename=filename, last_modified=latest_forecast)
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
