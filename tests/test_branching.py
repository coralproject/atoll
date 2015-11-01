import unittest
from atoll import Pipeline


def a(input):
    return [i+1 for i in input]

def b(input):
    return [i+2 for i in input]

def c(input):
    return [i+3 for i in input]

def d(input1, input2):
    return [sum([i1,i2]) for i1,i2 in zip(input1,input2)]


class BranchingPipelineTests(unittest.TestCase):
    def test_fork_branching_pipeline(self):
        p = Pipeline([a]).fork(b, c).to(d)
        out = p([1,2,3,4])
        self.assertEqual(out, [9,11,13,15])

    def test_split_branching_pipeline(self):
        p = Pipeline([a]).fork(b, c).split(b, c).to(d)
        out = p([1,2,3,4])
        self.assertEqual(out, [14,16,18,20])

    def test_parallel_fork_branching(self):
        p = Pipeline([a], n_jobs=2).fork(b, c).to(d)
        out = p([1,2,3,4])
        self.assertEqual(out, [9,11,13,15])

    def test_parallel_branching(self):
        p = Pipeline([a], n_jobs=2).fork(b, c).split(b, c).to(d)
        out = p([1,2,3,4])
        self.assertEqual(out, [14,16,18,20])

    def test_identity_pipes(self):
        p = Pipeline([a]).fork(b, c, None)
        out = p([1,2,3,4])
        self.assertEqual(out, (
            [4,5,6,7],
            [5,6,7,8],
            [2,3,4,5],
        ))
