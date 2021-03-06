import unittest
from coral.composer.parser import parse, parse_func


def my_func(input):
    return input + 10

class ParserTests(unittest.TestCase):
    def setUp(self):
        self.funcs = {
            'my_func': my_func
        }
        self.colors = {
            'my_func': '#ffffff'
        }
        self.inputs = [0,1,2,3,4]

    def test_parse(self):
        expr = '2*4 + my_func'
        results, texes, expr_tex = parse(expr, self.inputs, self.funcs, self.colors)
        self.assertEqual(results, [18, 19, 20, 21, 22])
        self.assertEqual(expr_tex, '2*4+\color{#ffffff}{\\text{my_func}}')
        self.assertEqual(texes, [
            '2*4+\color{#ffffff}{10}',
            '2*4+\color{#ffffff}{11}',
            '2*4+\color{#ffffff}{12}',
            '2*4+\color{#ffffff}{13}',
            '2*4+\color{#ffffff}{14}',
        ])

    def test_parse_unknown_func(self):
        expr = '2*4+unknown'
        self.assertRaises(Exception, parse, expr, self.inputs, self.funcs, self.colors)

    def test_parse_simple_func(self):
        expr = '2*4 + my_func'
        whitelist = [my_func.__name__]
        f = parse_func(expr, whitelist, globals())
        result = f(10)
        self.assertEqual(result, 28)

    def test_parse_illegal_func(self):
        expr = '2*4+unknown'
        whitelist = []
        self.assertRaises(ValueError, parse_func, expr, whitelist, locals())
