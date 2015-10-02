import sys
import json
import requests
import traceback
from celery import Celery
from atoll.service.conf import SERVICE_CONF

celery = Celery('tasks', 
                backend='amqp',
                broker='amqp://guest:guest@{}/'.format(SERVICE_CONF['worker_host']))


@celery.task
def pipeline_task(pipeline, input, callback_url):
    res = None
    err = None

    try:
        res = pipeline(input)
    except Exception as e:
        if hasattr(e, '__traceback__'): # py3
            tb = e.__traceback__
        else:
            ex_type, ex, tb = sys.exc_info() # py2
        err = {
            'name': type(e).__name__,
            'traceback': traceback.format_tb(tb),
            'message': str(e)
        }
    payload = {
        'results': res,
        'error': err
    }
    requests.post(callback_url, data=json.dumps(payload))
