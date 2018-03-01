# data-feed
[![Build Status](https://ci.lanlytics.com/nisac/data-feed.svg?token=RmFwLDimUxzrPXXq8Kti&branch=master)](https://ci.lanlytics.com/arnold/data-feed) 
[![codecov](https://cov.lanlytics.com/ghe/nisac/data-feed/branch/master/graph/badge.svg)](https://cov.lanlytics.com/ghe/arnold/data-feed)

Generic structure for retrieving and processing regularly updated data from the web 

## Scraper Usage
To create a new scraper simply create a class that inherits from the `Scraper` class 
and override the `check()` method.

Here is a quick pseudo example:

```python
import requests
from scraper import NewFile, Scraper

class MyScraper(Scraper):
  def check(self):
    response = requests.get(self.channel)
    # Parse content from page 
    # If the file has changed return a NewFile object
    return [NewFile(file_url, self.s3_folder)]
    
def run_scraper():
  s3_folder = 's3://bucket/path/to/store/data'
  channel = 'http://somedata.com'
  scraper = MyScraper(s3_folder, channel)
  scraper.run()
  
if __name__ == '__main__':
  run_scraper()
```

See [noaa_wind_scraper.py](noaa_wind_scraper.py) for a real example. The example
also requires that `BeautifulSoup4` and `lxml` are installed. To install, simply
run `pip install BeautifulSoup4 lxml`.

## Subscriber Usage
To create a new subscriber simply create a class that inherits from the `Subscriber` 
class and override the `process()` method.

Here is a quick pseduo example:

```python
from subscriber import Subscriber

class MySubscriber(Subscriber):
  def process(self, s3_uri):
    # Process file(s) in s3_uri
    
def subscribe():
  channel = 'http://somedata.com'
  sub = MySubscriber(channel)
  sub.subscribe()
  
if __name__ == '__main__':
  subscribe()
```
  
See [noaa_wind_subscriber.py](noaa_wind_subscriber.py) for a real example using the 
lanlytics API.
