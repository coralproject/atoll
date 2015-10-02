import json
import unittest
import httpretty
from atoll.service import create_app
from atoll import Pipe, Pipeline, register_pipeline
from atoll.service.tasks import celery

# force celery to be synchronous for testing
celery.conf.update(CELERY_ALWAYS_EAGER=True)

test_config = {
    'TESTING': True
}


class LowercasePipe(Pipe):
    """
    A simple test pipe
    """
    input = [str]
    output = [str]

    def __call__(self, input):
        return [s.lower() for s in input]

# pipelines must be registered _before_ creating the app!
pipeline = Pipeline([LowercasePipe()], name="example_pipeline")
register_pipeline('/example', pipeline)


class ServiceTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(**test_config)
        self.client = self.app.test_client()

    def tearDown(self):
        self.app = None

    def test_pipeline_synchronous(self):
        headers = [('Content-Type', 'application/json')]
        resp = self.client.post('/pipelines/example', data=json.dumps({
            'data': ['AA', 'BB']
        }), headers=headers)
        resp_json = json.loads(resp.data.decode('utf-8'))
        self.assertEquals({
            'results': ['aa', 'bb']
        }, resp_json)
        self.assertEquals(resp.status_code, 200)

    @httpretty.activate
    def test_pipeline_asynchronous(self):
        httpretty.register_uri(httpretty.POST, "http://sup.com/callback")
        headers = [('Content-Type', 'application/json')]
        resp = self.client.post('/pipelines/example', data=json.dumps({
            'data': ['AA', 'BB'],
            'callback': 'http://sup.com/callback'
        }), headers=headers)
        self.assertEquals(resp.status_code, 202)

        resp_json = json.loads(httpretty.last_request().body.decode('utf-8'))
        self.assertEquals({
            'results': ['aa', 'bb'],
            'error': None
        }, resp_json)
