import unittest
from atoll import Pipeline


def lowercase(input):
    return input.lower()

def tokenize(input, delimiter=' '):
    return input.split(delimiter)

def word_counter(input):
    return len(input)

def count_per_key(key, value):
    return key, len(value)

def add(x, y):
    return x + y


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
        pipeline = Pipeline().map(lowercase).map(tokenize)
        output = pipeline(self.docs)
        for o, e in zip(output, expected):
            self.assertEqual(set(o), set(e))

    def test_nested_pipeline(self):
        nested_pipeline = Pipeline().map(lowercase).map(tokenize)
        pipeline = Pipeline().to(nested_pipeline).map(word_counter)
        counts = pipeline(self.docs)
        self.assertEqual(counts, [6,9])

    def test_mapped_pipeline_parallel(self):
        expected = [
            ['coral', 'reefs', 'are', 'diverse', 'underwater', 'ecosystems'],
            ['coral', 'reefs', 'are', 'built', 'by', 'colonies', 'of', 'tiny', 'animals']
        ]
        pipeline = Pipeline().map(lowercase).map(tokenize)
        output = pipeline(self.docs, n_jobs=2)
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
        expected = [5, 6]
        pipeline = Pipeline().map(add, 4)
        output = pipeline([1,2])
        self.assertEqual(output, expected)

    def test_validation(self):
        pipeline = Pipeline().map(tokenize)
        self.assertRaises(AttributeError, pipeline.validate, [[1,2,3],[4,5,6]])

    def test_kwargs_missing(self):
        pipeline = Pipeline().map(tokenize, kwargs=['delimiter'])
        input = [doc.replace(' ', ',') for doc in self.docs]
        self.assertRaises(KeyError, pipeline, input)

    def test_kwargs(self):
        expected = [
            ['Coral', 'reefs', 'are', 'diverse', 'underwater', 'ecosystems'],
            ['Coral', 'reefs', 'are', 'built', 'by', 'colonies', 'of', 'tiny', 'animals']
        ]
        pipeline = Pipeline().map(tokenize, kwargs=['delimiter'])
        input = [doc.replace(' ', ',') for doc in self.docs]
        output = pipeline(input, delimiter=',')
        for o, e in zip(output, expected):
            self.assertEqual(set(o), set(e))

    def test_kwargs_nested(self):
        expected = [
            ['coral', 'reefs', 'are', 'diverse', 'underwater', 'ecosystems'],
            ['coral', 'reefs', 'are', 'built', 'by', 'colonies', 'of', 'tiny', 'animals']
        ]
        token_pipeline = Pipeline().map(tokenize, kwargs=['delimiter'])
        lowercase_pipeline = Pipeline().map(lowercase) # kinda hacky
        pipeline = Pipeline().to(token_pipeline).map(lowercase_pipeline)

        input = [doc.replace(' ', ',') for doc in self.docs]
        output = pipeline(input, delimiter=',')
        for o, e in zip(output, expected):
            self.assertEqual(set(o), set(e))
