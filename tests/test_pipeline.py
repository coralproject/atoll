import unittest
from atoll import Pipe, Pipeline
from atoll.pipeline import InvalidPipelineError


class LowercasePipe(Pipe):
    """
    A simple test pipe
    """
    input = [str]
    output = [str]

    def __call__(self, input):
        return [s.lower() for s in input]

class TokenizePipe(Pipe):
    input = [str]
    output = [[str]]

    def __call__(self, input):
        return [s.split(' ') for s in input]

class WordCounterPipe(Pipe):
    input = [[str]]
    output = [int]

    def __call__(self, input):
        return [len(s) for s in input]

class FirstCharPipe(Pipe):
    input = [[str]]
    output = [[str]]

    def __call__(self, input):
        return [[s_[0] for s_ in s] for s in input]


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.docs = [
            'Coral reefs are diverse underwater ecosystems',
            'Coral reefs are built by colonies of tiny animals'
        ]
        self.expected_counts = [6,9]
        self.expected_chars = [['c', 'r', 'a', 'd', 'u', 'e'], ['c', 'r', 'a', 'b', 'b', 'c', 'o', 't', 'a']]

    def test_docstring(self):
        docstring = LowercasePipe.__doc__
        self.assertEqual(docstring, 'A simple test pipe\n\nInput:\n[str]\n\nOutput:\n[str]')

    def test_pipeline(self):
        expected = [
            ['coral', 'reefs', 'are', 'diverse', 'underwater', 'ecosystems'],
            ['coral', 'reefs', 'are', 'built', 'by', 'colonies', 'of', 'tiny', 'animals']
        ]
        pipeline = Pipeline([LowercasePipe(), TokenizePipe()])
        output = pipeline(self.docs)
        for o, e in zip(output, expected):
            self.assertEqual(set(o), set(e))

    def test_incompatible_pipeline(self):
        self.assertRaises(InvalidPipelineError, Pipeline, [WordCounterPipe(), LowercasePipe()])

    def test_nested_pipeline(self):
        nested_pipeline = Pipeline([LowercasePipe(), TokenizePipe()])
        pipeline = Pipeline([nested_pipeline, WordCounterPipe()])
        counts = pipeline(self.docs)
        self.assertEqual(counts, [6,9])

    def test_valid_struct_pipeline(self):
        class CommentPipe(Pipe):
            input = [str]
            output = [{'body':str,'user':str}]
            def __call__(self, input):
                return [{'body':s,'user':'foo'} for s in input]

        class BodyLenPipe(Pipe):
            input = [{'body':str}]
            output = [int]
            def __call__(self, input):
                return [len(s['body']) for s in input]

        pipeline = Pipeline([CommentPipe(), BodyLenPipe()])
        output = pipeline(self.docs)
        print(output)
