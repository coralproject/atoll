import os
import unittest
from socket import socket
from unittest import skipIf
from atoll import Pipeline
from atoll.distrib import pyspark, DISTRIB_CONF


def check_cluster():
    try:
        s = socket()
        ip, port = DISTRIB_CONF['zookeeper_host'].split(':')
        s.connect(ip, int(port))
        s.close()
        return True
    except OSError:
        return False


@skipIf(not os.environ.get('ATOLL_TEST_DISTRIB', False), 'skipping distributed tests, set env var ATOLL_TEST_DISTRIB=True to run them')
@skipIf(pyspark is None, 'no pyspark installation found')
@skipIf(not check_cluster, 'could not reach zookeeper')
class DistributedTest(unittest.TestCase):

    def test_map(self):
        pipeline = Pipeline().map(lambda x: x+2).map(lambda x: x*2)
        result = pipeline([0,1,2,3,4], n_jobs=1, distributed=True)
        self.assertEqual(result, [4,6,8,10,12])

    def test_mapValues(self):
        pipeline = Pipeline().mapValues(lambda x: sum(x))
        result = pipeline([('a', [0,1,2]), ('b', [3,4,5])], n_jobs=1, distributed=True)
        self.assertEqual(result, [('a', 3), ('b', 12)])

    def test_MapValues_dict(self):
        pipeline = Pipeline().mapValues(lambda x: x['foo'])
        result = pipeline([('a', {'foo':'yo'}), ('b', {'foo':'bar'})], n_jobs=1, distributed=True)
        self.assertEqual(result, [('a', 'yo'), ('b', 'bar')])

    def test_mapValues_multiple(self):
        pipeline = Pipeline().mapValues(lambda x: x['foo']).mapValues(lambda x: len(x))
        result = pipeline([('a', {'foo':'yo'}), ('b', {'foo':'bar'})], n_jobs=1, distributed=True)
        self.assertEqual(result, [('a', 2), ('b', 3)])

    def test_flatMap(self):
        pipeline = Pipeline().flatMap(lambda x: ['foo', x])
        result = pipeline([0,1,2,3,4], n_jobs=1, distributed=True)
        self.assertEqual(result, ['foo', 0, 'foo', 1, 'foo', 2, 'foo', 3, 'foo', 4])

    def test_flatMapValues(self):
        pipeline = Pipeline().flatMapValues(lambda x: [i+2 for i in x])
        result = pipeline([('a', [0,1,2]), ('b', [3,4,5])], n_jobs=1, distributed=True)
        self.assertEqual(result, [('a', 2), ('a', 3), ('a', 4), ('b', 5), ('b', 6), ('b', 7)])

    def test_reduce(self):
        pipeline = Pipeline().reduce(lambda x, y: x+ y)
        result = pipeline([0,1,2,3,4], n_jobs=1, distributed=True)
        self.assertEqual(result, 10)

    def test_reduceByKey(self):
        pipeline = Pipeline().reduceByKey(lambda x, y: x + y)
        result = pipeline([('a', 1), ('a', 2), ('b', 3), ('b', 4)], n_jobs=1, distributed=True)
        self.assertEqual(result, [('a', 3), ('b', 7)])

    def test_fork(self):
        p1 = Pipeline().map(lambda x: 2*x)
        p2 = Pipeline().map(lambda x: x/2)
        pipeline = Pipeline().map(lambda x: x + 2).fork(p1, p2)
        result = pipeline([0,1,2,3,4], n_jobs=1, distributed=True)
        self.assertEqual(result, [[4, 6, 8, 10, 12], [1.0, 1.5, 2.0, 2.5, 3.0]])

    def test_to(self):
        pipeline = Pipeline().map(lambda x: x + 2).to(lambda x: sum(x))
        result = pipeline([0,1,2,3,4], n_jobs=1, distributed=True)
        self.assertEqual(result, 20)

        pipeline = Pipeline().to(lambda x: sum(x))
        result = pipeline([0,1,2,3,4], n_jobs=1, distributed=True)
        self.assertEqual(result, 10)

    def test_fork_to(self):
        p1 = Pipeline().map(lambda x: 2*x)
        p2 = Pipeline().map(lambda x: x/2)
        pipeline = Pipeline().map(lambda x: x + 2).fork(p1, p2).to(lambda l: [x*y for x,y in zip(*l)])
        result = pipeline([0,1,2,3,4], n_jobs=1, distributed=True)
        self.assertEqual(result, [4.0, 9.0, 16.0, 25.0, 36.0])
