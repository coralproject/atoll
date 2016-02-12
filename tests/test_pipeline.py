import unittest
from atoll import Pipeline


def lowercase(x):
    return x.lower()

def tokenize(x, delimiter=' '):
    return x.split(delimiter)

def word_counter(x):
    return len(x)

def count_per_key(value):
    return len(value)

def add(x, y):
    return x + y

def make_list(x):
    return ['a', x]


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.docs = [
            'Coral reefs are diverse underwater ecosystems',
            'Coral reefs are built by colonies of tiny animals'
        ]
        self.expected_counts = [6,9]
        self.expected_chars = [['c', 'r', 'a', 'd', 'u', 'e'], ['c', 'r', 'a', 'b', 'b', 'c', 'o', 't', 'a']]

    def test_map_pipeline(self):
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

    def test_map_parallel(self):
        expected = [
            ['coral', 'reefs', 'are', 'diverse', 'underwater', 'ecosystems'],
            ['coral', 'reefs', 'are', 'built', 'by', 'colonies', 'of', 'tiny', 'animals']
        ]
        pipeline = Pipeline().map(lowercase).map(tokenize)
        output = pipeline(self.docs, n_jobs=2)
        for o, e in zip(output, expected):
            self.assertEqual(set(o), set(e))

    def test_map_values(self):
        expected = [
            ('a', 2),
            ('b', 3)
        ]
        pipeline = Pipeline().mapValues(count_per_key)
        output = pipeline({
            'a': [0,0],
            'b': [0,0,0]
        })
        self.assertEqual(set(output), set(expected))

    def test_flat_map(self):
        expected = ['a', 2, 'a', 3]
        pipeline = Pipeline().flatMap(make_list)
        output = pipeline([2,3])
        self.assertEqual(output, expected)

    def test_flat_map_values(self):
        expected = [('a', 1), ('a', 2), ('b', 3), ('b', 4)]
        pipeline = Pipeline().flatMapValues(None) # None = identity func
        output = pipeline({
            'a': [1,2],
            'b': [3,4]
        })
        self.assertEqual(set(output), set(expected))

    def test_reduce(self):
        expected = 10
        pipeline = Pipeline().reduce(add)
        output = pipeline([1,2,3,4])
        self.assertEqual(output, expected)

    def test_reduce_by_key(self):
        expected = [('a', 3), ('b', 7)]
        pipeline = Pipeline().reduceByKey(add)
        output = pipeline([('a', 1), ('a', 2), ('b', 3), ('b', 4)])
        self.assertEqual(set(output), set(expected))

    def test_partial_handling(self):
        expected = [5, 6]
        pipeline = Pipeline().map(add, 4)
        output = pipeline([1,2])
        self.assertEqual(output, expected)

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
