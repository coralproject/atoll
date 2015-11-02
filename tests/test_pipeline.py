import unittest
from atoll import Pipeline


def lowercase(input):
    """
    A simple test pipe
    """
    return [s.lower() for s in input]

def tokenize(input, delimiter=' '):
    return [s.split(delimiter) for s in input]

def tokenize_single(input, delimiter=' '):
    return input.split(delimiter)

def word_counter(input):
    return [len(s) for s in input]

def first_char(input):
    return [[s_[0] for s_ in s] for s in input]

def count_per_key(key, value):
    return key, len(value)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.docs = [
            'Coral reefs are diverse underwater ecosystems',
            'Coral reefs are built by colonies of tiny animals'
        ]
        self.expected_counts = [6,9]
        self.expected_chars = [['c', 'r', 'a', 'd', 'u', 'e'], ['c', 'r', 'a', 'b', 'b', 'c', 'o', 't', 'a']]

    def test_pipeline(self):
        expected = [
            ['coral', 'reefs', 'are', 'diverse', 'underwater', 'ecosystems'],
            ['coral', 'reefs', 'are', 'built', 'by', 'colonies', 'of', 'tiny', 'animals']
        ]
        pipeline = Pipeline([lowercase, tokenize])
        output = pipeline(self.docs)
        for o, e in zip(output, expected):
            self.assertEqual(set(o), set(e))

    def test_nested_pipeline(self):
        nested_pipeline = Pipeline([lowercase, tokenize])
        pipeline = Pipeline([nested_pipeline, word_counter])
        counts = pipeline(self.docs)
        self.assertEqual(counts, [6,9])

    def test_mapped_pipeline(self):
        expected = [
            ['coral', 'reefs', 'are', 'diverse', 'underwater', 'ecosystems'],
            ['coral', 'reefs', 'are', 'built', 'by', 'colonies', 'of', 'tiny', 'animals']
        ]
        pipeline = Pipeline([lowercase]).map(tokenize_single)
        output = pipeline(self.docs)
        for o, e in zip(output, expected):
            self.assertEqual(set(o), set(e))

    def test_mapped_pipeline_parallel(self):
        expected = [
            ['coral', 'reefs', 'are', 'diverse', 'underwater', 'ecosystems'],
            ['coral', 'reefs', 'are', 'built', 'by', 'colonies', 'of', 'tiny', 'animals']
        ]
        pipeline = Pipeline([lowercase], n_jobs=2).map(tokenize_single)
        output = pipeline(self.docs)
        for o, e in zip(output, expected):
            self.assertEqual(set(o), set(e))

    def test_pipeline_start_with_mapped(self):
        expected = [
            ['Coral', 'reefs', 'are', 'diverse', 'underwater', 'ecosystems'],
            ['Coral', 'reefs', 'are', 'built', 'by', 'colonies', 'of', 'tiny', 'animals']
        ]
        pipeline = Pipeline().map(tokenize_single)
        output = pipeline(self.docs)
        for o, e in zip(output, expected):
            self.assertEqual(set(o), set(e))

    def test_valid_mapped_pipeline_dict(self):
        expected = [
            ('a', 2),
            ('b', 3)
        ]
        pipeline = Pipeline().map_dict(count_per_key)
        output = pipeline({
            'a': [0,0],
            'b': [0,0,0]
        })
        self.assertEqual(set(output), set(expected))

    def test_partial_handling(self):
        def add(x, y):
            return x + y
        expected = [5, 6]
        pipeline = Pipeline().map(add, 4)
        output = pipeline([1,2])
        self.assertEqual(output, expected)

    def test_validation(self):
        pipeline = Pipeline().map(tokenize_single)
        self.assertRaises(AttributeError, pipeline.validate, [[1,2,3],[4,5,6]])

    def test_kwargs_missing(self):
        pipeline = Pipeline().map(tokenize_single, kwargs=['delimiter'])
        input = [doc.replace(' ', ',') for doc in self.docs]
        self.assertRaises(KeyError, pipeline, input)

    def test_kwargs(self):
        expected = [
            ['Coral', 'reefs', 'are', 'diverse', 'underwater', 'ecosystems'],
            ['Coral', 'reefs', 'are', 'built', 'by', 'colonies', 'of', 'tiny', 'animals']
        ]
        pipeline = Pipeline().map(tokenize_single, kwargs=['delimiter'])
        input = [doc.replace(' ', ',') for doc in self.docs]
        output = pipeline(input, delimiter=',')
        for o, e in zip(output, expected):
            self.assertEqual(set(o), set(e))

    def test_kwargs_nested(self):
        expected = [
            ['coral', 'reefs', 'are', 'diverse', 'underwater', 'ecosystems'],
            ['coral', 'reefs', 'are', 'built', 'by', 'colonies', 'of', 'tiny', 'animals']
        ]
        token_pipeline = Pipeline().map(tokenize_single, kwargs=['delimiter'])
        pipeline = Pipeline([token_pipeline]).map(lowercase)

        input = [doc.replace(' ', ',') for doc in self.docs]
        output = pipeline(input, delimiter=',')
        for o, e in zip(output, expected):
            self.assertEqual(set(o), set(e))
