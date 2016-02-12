import unittest
from unittest import skipIf
from socket import socket
from atoll import Pipeline
from atoll.config import EXECUTOR_HOST


def check_cluster():
    try:
        s = socket()
        ip, port = EXECUTOR_HOST.split(':')
        s.connect((ip, int(port)))
        s.close()
        return True
    except OSError:
        return False


def prod(x, y):
    return x*y


@skipIf(not check_cluster(), 'could not connect to cluster executor')
class DistributedTest(unittest.TestCase):
    def test_to(self):
        pipeline = Pipeline().map(lambda x: x + 2).to(lambda x: sum(x))
        result = pipeline([0,1,2,3,4], n_jobs=1, distributed=True)
        self.assertEqual(result, 20)

        pipeline = Pipeline().to(lambda x: sum(x))
        result = pipeline([0,1,2,3,4], n_jobs=1, distributed=True)
        self.assertEqual(result, 10)

    def test_map(self):
        pipeline = Pipeline().map(lambda x: x+2).map(lambda x: x*2)
        result = pipeline([0,1,2,3,4], n_jobs=1, distributed=True)
        self.assertEqual(result, [4,6,8,10,12])

    def test_map_tuples(self):
        pipeline = Pipeline().map(prod).map(lambda x: x+2)
        result = pipeline([(0,1),(1,2),(2,3),(3,4),(4,5)], n_jobs=1, distributed=True)
        self.assertEqual(result, [2, 4, 8, 14, 22])

    def test_mapValues(self):
        pipeline = Pipeline().mapValues(lambda x: sum(x)).mapValues(lambda x: x*2)
        result = pipeline([('a', [0,1,2]), ('b', [3,4,5])], n_jobs=1, distributed=True)
        self.assertEqual(result, [('a', 6), ('b', 24)])

    def test_mapValues_dict(self):
        pipeline = Pipeline().mapValues(lambda x: x['foo']).mapValues(lambda x: x*2)
        result = pipeline([('a', {'foo':'yo'}), ('b', {'foo':'bar'})], n_jobs=1, distributed=True)
        self.assertEqual(result, [('a', 'yoyo'), ('b', 'barbar')])

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
        self.assertEqual(set(result), set([('a', 3), ('b', 7)]))

    def test_fork(self):
        p1 = Pipeline().map(lambda x: 2*x)
        p2 = Pipeline().map(lambda x: x/2)
        pipeline = Pipeline().map(lambda x: x + 2).fork(p1, p2)
        result = pipeline([0,1,2,3,4], n_jobs=1, distributed=True)
        self.assertEqual(result, [[4, 6, 8, 10, 12], [1.0, 1.5, 2.0, 2.5, 3.0]])

    def test_forkMap(self):
        pipeline = Pipeline().forkMap(lambda x: 2*x, lambda x: x/2)
        result = pipeline([0,1,2,3,4], n_jobs=1, distributed=True)
        self.assertEqual(result, [[0, 2, 4, 6, 8], [0, 0.5, 1., 1.5, 2.]])

    def test_fork_to(self):
        p1 = Pipeline().map(lambda x: 2*x)
        p2 = Pipeline().map(lambda x: x/2)
        pipeline = Pipeline().map(lambda x: x + 2).fork(p1, p2).to(lambda l: [x*y for x,y in zip(*l)])
        result = pipeline([0,1,2,3,4], n_jobs=1, distributed=True)
        self.assertEqual(result, [4.0, 9.0, 16.0, 25.0, 36.0])

    def test_split(self):
        pipeline = Pipeline().forkMap(lambda x: 2*x, lambda x: x/2).split(lambda x: len(x), lambda x: len(x)*2)
        result = pipeline([0,1,2,3,4], n_jobs=1, distributed=True)
        self.assertEqual(result, [5, 10])

    def test_splitMap(self):
        pipeline = Pipeline().forkMap(lambda x: 2*x, lambda x: x/2).splitMap(lambda x: x+1, lambda x: x+2)
        result = pipeline([0,1,2,3,4], n_jobs=1, distributed=True)
        self.assertEqual(result, [[1, 3, 5, 7, 9], [2, 2.5, 3., 3.5, 4.]])
