import json
import requests
from celery import Celery

celery = Celery('tasks', backend='amqp', broker='amqp://guest:guest@<DOCKERIP>/')


@celery.task
def async_pipeline(pipeline, input, callback_url):
    results = pipeline(input)
    payload = {
        'results': results
    }
    requests.post(callback_url, data=json.dumps(payload))
