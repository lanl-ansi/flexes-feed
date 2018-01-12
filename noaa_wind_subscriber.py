import json
import os
import requests
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
        response = requests.post(api_url, json=data)
        resp_json = response.json()
        job_id = resp_json['job_id']

        status_url = os.path.join(api_url, service, 'jobs', job_id)
        response = requests.get(status_url)
        resp_json = response.json()
        job_status = resp_json['status']

        while job_status not in ['completed', 'failed']:
            response = requests.get(status_url)
            resp_json = resp.json()
            job_status = resp_json['status']
            time.sleep(5)

        if job_status == 'completed':
            return
        else:
            raise RuntimeError(resp_json['result'])
