import json
import os
import requests
from lanlytics_api_lib.job import run_task
from data_feed.subscriber import Subscriber

class WindForecastSubscriber(Subscriber):
    def process(self, s3_uri):
        """Launch an API task to process the published wind forecast and publish the
            result on a separate channel when the task completes.
        """
        api_url = 'https://api.lanlytics.com'
        service = 'process-wind-forecast'
        data = {'service': service,
                'command': {
                    'arguments': [
                        {'type': 'input', 'value': s3_uri}    
                    ]
                }
               }
        try:
            result = run_task(api_url, data)

            # Publish the processed wind forecast result 
            # for processing by additional subscribers
            self.db.publish(os.path.dirname(s3_uri), s3_uri)
        except ValueError as e:
            print(e)


def subscribe():
    channel = 'http://tgftp.nws.noaa.gov/SL.us008001/ST.opnl/DF.gr2/DC.ndfd'
    wind_sub = WindForecastSubscriber(channel)
    wind_sub.subscribe()

if __name__ == '__main__':
    subscribe()
