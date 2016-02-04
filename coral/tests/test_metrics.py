from coral.metrics.common import has_key
import unittest


class MetricsTest(unittest.TestCase):
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
