import yaml
import unittest
from atoll import Pipe, Pipeline
from atoll.conf import parse_pipe, parse_conf


class TestPipe(Pipe):
    input = [str]
    output = int

    def __init__(self, arg=0):
        self.arg = arg

class TestPipe2(Pipe):
    input = int
    output = int

class NotPipe():
    pass


test_conf = '''
super_pipeline:
    endpoint: /super_pipeline
    pipeline:
        - tests.test_config.TestPipe
        - tests.test_config.TestPipe2
        - tests.test_config.TestPipe2:
            arg: 10
'''


class TestConfigParsing(unittest.TestCase):
    def setUp(self):
        self.importstr = 'tests.test_config.TestPipe'

    def test_string_pipe(self):
        pipe_ = self.importstr
        pipe = parse_pipe(pipe_)
        self.assertIsInstance(pipe, TestPipe)

    def test_dict_pipe(self):
        pipe_ = {self.importstr: {'arg': 1}}
        pipe = parse_pipe(pipe_)
        self.assertIsInstance(pipe, TestPipe)
        self.assertEqual(pipe.arg, 1)

    def test_branch(self):
        pipe_ = [self.importstr, self.importstr]
        pipe = parse_pipe(pipe_)
        self.assertEqual(len(pipe), 2)
        for p in pipe:
            self.assertIsInstance(p, TestPipe)

    def test_branch_dict(self):
        pipe_ = [
            {self.importstr: {'arg': 1}},
            {self.importstr: {'arg': 2}}
        ]
        pipe = parse_pipe(pipe_)
        self.assertEqual(len(pipe), 2)
        for i, p in enumerate(pipe):
            self.assertIsInstance(p, TestPipe)
            self.assertEqual(p.arg, i+1)

    def test_not_pipe(self):
        pipe_ = 'tests.test_config.NotPipe'
        self.assertRaises(TypeError, lambda _: parse_pipe(pipe_))

    def test_parse_conf(self):
        conf = yaml.load(test_conf)
        pipelines = parse_conf(conf)
        self.assertEqual(len(pipelines), 1)

        endpoint, pipeline = pipelines[0]
        self.assertEqual(endpoint, '/super_pipeline')
        self.assertIsInstance(pipeline, Pipeline)
        self.assertEqual(pipeline.pipes[-1].arg, 10)

    def test_nonexistant_module(self):
        pipe_ = 'foo.bar.TestPipe'
        self.assertRaises(ImportError, lambda: parse_pipe(pipe_))
