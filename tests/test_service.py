import json
import unittest
import httpretty
from atoll.service import create_app
from atoll import Pipeline, register_pipeline, pipeline_blueprint
from atoll.service.tasks import celery

# force celery to be synchronous for testing
celery.conf.update(CELERY_ALWAYS_EAGER=True)

test_config = {
    'TESTING': True
}


def lowercase(input):
    return input.lower()

# pipelines must be registered _before_ creating the app!
pipeline = Pipeline(name="example_pipeline").map(lowercase)
pipeline_bp = pipeline_blueprint()
register_pipeline('/example', pipeline, pipeline_bp)


class ServiceTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(**test_config)
        self.app.register_blueprint(pipeline_bp)
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

    def test_invalid_input_exception(self):
        # create a client with TESTING=False so we get error responses
        self.app = create_app(**{'TESTING': False})
        self.app.register_blueprint(pipeline_bp)
        self.client = self.app.test_client()

        headers = [('Content-Type', 'application/json')]
        resp = self.client.post('/pipelines/example', data=json.dumps({
            # munge the data to incorrect form (dict instead of a list)
            'data': {'foobar': ['AA', 'BB']}
        }), headers=headers)
        self.assertEquals(resp.status_code, 500)

        expected = {
            'type': str,
            'message': str,
            'data': dict
        }
        resp_json = json.loads(resp.data.decode('utf-8'))
        for k, t in expected.items():
            self.assertTrue(isinstance(resp_json[k], t))
