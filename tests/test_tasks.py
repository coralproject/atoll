import json
import unittest
import httpretty
from atoll import Pipe, Pipeline
from atoll.service.tasks import pipeline_task


class LowercasePipe(Pipe):
    input = [str]
    output = [str]
    def __call__(self, input):
        return [s.lower() for s in input]

class ExceptionPipe(Pipe):
    input = [str]
    output = [str]
    def __call__(self, input):
        raise Exception('exc message')


class TasksTest(unittest.TestCase):

    @httpretty.activate
    def test_pipeline_success(self):
        httpretty.register_uri(httpretty.POST, "http://sup.com/callback")
        pipeline = Pipeline([LowercasePipe()])
        pipeline_task.apply(args=(pipeline, ['AA', 'BB'], 'http://sup.com/callback')).get()

        resp_json = json.loads(httpretty.last_request().body.decode('utf-8'))
        self.assertEquals({
            'results': ['aa', 'bb'],
            'error': None
        }, resp_json)

    @httpretty.activate
    def test_pipeline_failure(self):
        httpretty.register_uri(httpretty.POST, "http://sup.com/callback")
        pipeline = Pipeline([ExceptionPipe()])
        pipeline_task.apply(args=(pipeline, ['AA', 'BB'], 'http://sup.com/callback')).get()

        resp_json = json.loads(httpretty.last_request().body.decode('utf-8'))

        # for easier comparison
        self.assertTrue(resp_json['error']['traceback'])
        resp_json['error']['traceback'] = []

        self.assertEquals({
            'results': None,
            'error': {
                'name': 'Exception',
                'message': 'exc message',
                'traceback': []
            }
        }, resp_json)
