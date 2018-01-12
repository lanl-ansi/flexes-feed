import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from scraper import Scraper

class WindForecastScraper(Scraper):
    def check(self):
        new_files = []
        forecasts = [os.path.join(self.channel, location, day)
                        for location in ['AR.conus', 'AR.hawaii', 'AR.puertori']
                        for day in ['VP.001-003', 'VP.004-007']]
        for forecast in forecasts:
            filename = os.path.join(forecast, 'ds.wspd.bin')
            response = requests.get(forecast)
            date_modified = self.scrape(response)
            if date_modified > self.last_modified(filename):
                new_files.append(filename)
        return new_files

    def scrape(self, response):
        soup = BeautifulSoup(response.content, 'lxml')
        date_modified = soup.find(href='ds.wspd.bin').parent.nextSibling.text
        return datetime.strptime(date_modified, '%d-%b-%Y %H:%M ')


def check_forecasts():
    s3_folder = 's3://lanlytics/noaa/ndfd'
    channel = 'http://tgftp.nws.noaa.gov/SL.us008001/ST.opnl/DF.gr2/DC.ndfd'
    wind_scraper = WindForecastScraper(s3_folder=s3_folder, channel=channel, frequency=300)
    wind_scraper.run()

if __name__ == '__main__':
    check_forecasts()
