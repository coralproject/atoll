import json
import requests
from celery import Celery
from atoll.service.conf import SERVICE_CONF

celery = Celery('tasks', 
                backend='amqp',
                broker='amqp://guest:guest@{}/'.format(SERVICE_CONF['worker_host']))


@celery.task
def pipeline_task(pipeline, input, callback_url):
    results = pipeline(input)
    payload = {
        'results': results
    }
    requests.post(callback_url, data=json.dumps(payload))
