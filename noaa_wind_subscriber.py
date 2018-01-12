import json
import os
import requests
from lanlytics_api import run_task
from subscriber import Subscriber

class WindForecastSubscriber(Subscriber):
    def process(self, s3_uri):
        api_url = 'https://api.lanlytics.com'
        service = 'ep-damage'
        data = {'service': service,
                'command':
                    'arguments': [
                        {'type': 'input', 'value': s3_uri}    
                    ]
               }
        try:
            result = run_task(api_url, data)
        except ValueError as e:
            print(e)
