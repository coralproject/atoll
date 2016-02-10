import unittest
from atoll import Pipeline
from coral.metrics import group_by_taxonomy
from coral.metrics.common import has_key

def faux_metrics(vals):
    return {
        'count': len(vals),
        'foo': sum(v['id'] for v in vals)
    }

class MetricsTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_group_by_taxonomy(self):
        data = [{
            'id': 0,
            'taxonomy': 'section:world;author:Foo Bar;section:politics'
        },
        {
            'id': 1,
            'taxonomy': 'section:world;author:Foo Bar;section:politics'
        },
        {
            'id': 2,
            'taxonomy': 'section:sports;author:Sup Yo'
        },
        {
            'id': 3,
            'taxonomy': 'section:sports;author:Foo Bar;section:entertainment'
        }]
        expected = [('section', [('politics', {'foo': 1, 'count': 2}), ('world', {'foo': 1, 'count': 2}), ('entertainment', {'foo': 3, 'count': 1}), ('sports', {'foo': 5, 'count': 2})]), ('author', [('Foo Bar', {'foo': 4, 'count': 3}), ('Sup Yo', {'foo': 2, 'count': 1})])]

        taxonomy_pipeline = Pipeline().mapValues(faux_metrics)
        pipeline = Pipeline().to(group_by_taxonomy).mapValues(taxonomy_pipeline)
        metrics = pipeline(data)

        # make them comparable
        metrics = dict(metrics)
        expected = dict(expected)
        for v in metrics.values():
            v.sort()
        for v in expected.values():
            v.sort()
        self.assertEqual(metrics, expected)

    def test_has_key(self):
        data = {
            'foo': {
                'bar': {
                    'sup': 10
                }
            }
        }
        path = 'foo.bar.sup'
        self.assertTrue(has_key(data, path))

    def test_has_key_false(self):
        data = {
            'foo': {
                'bar': {}
            }
        }
        path = 'foo.bar.sup'
        self.assertFalse(has_key(data, path))

    def test_has_key_list(self):
        data = {
            'comments': [{'likes': 0}]
        }
        path = 'comments[].likes'
        self.assertTrue(has_key(data, path))

    def test_has_key_empty_list(self):
        data = {
            'comments': []
        }
        path = 'comments[].likes'
        self.assertTrue(has_key(data, path))
