import unittest
from functools import partial
from atoll import Pipeline
from atoll.friendly import _get_name

def add(x, y):
    return x + y

class Adder():
    def __call__(self, x, y):
        return add(x, y)


class FriendlyTests(unittest.TestCase):
    def test_get_name(self):
        self.assertEqual(_get_name(add), 'add')
        self.assertEqual(_get_name(partial(add, 4)), 'add')
        self.assertEqual(_get_name(Adder), 'Adder')

        f = lambda x,y: x+y
        self.assertEqual(_get_name(f), 'f = lambda x,y: x+y')

    def test_pipeline_signature(self):
        p = Pipeline().to(add).to(Adder())
        self.assertEqual(p.sig, '1f3c5e11d0facd1e488cf225227f5d26')

    def test_pipeline_repr(self):
        p = Pipeline().to(add).to(Adder())
        self.assertEqual(str(p), 'to:add -> to:Adder')

    def test_pipeline_branching_repr(self):
        p = Pipeline().to(add).fork(Pipeline().to(add),
                                    Pipeline().to(add))
        self.assertEqual(str(p), 'to:add -> fork:to:add|to:add')
