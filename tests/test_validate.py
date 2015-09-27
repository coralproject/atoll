import unittest
from atoll.validate import build_tree, _dict_to_struct


class TestTypeTrees(unittest.TestCase):
    def unroll_tree(self, node):
        if not node.children:
            return node.type
        else:
            return [node.type, [self.unroll_tree(ch) for ch in node.children]]

    def test_simple_type(self):
        input = str
        root = build_tree(input)
        self.assertEquals(str, self.unroll_tree(root))

    def test_invalid_type(self):
        input = 'sup'
        self.assertRaises(TypeError, lambda _: build_tree(input))

    def test_homogenous_list(self):
        input = [str]
        root = build_tree(input)
        self.assertEquals([list, [str]], self.unroll_tree(root))

    def test_heterogenous_list(self):
        input = [str, int]
        self.assertRaises(TypeError, lambda _: build_tree(input))

    def test_homogenous_set(self):
        input = {str}
        root = build_tree(input)
        self.assertEquals([set, [str]], self.unroll_tree(root))

    def test_heterogenous_set(self):
        input = {str, int}
        self.assertRaises(TypeError, lambda _: build_tree(input))

    def test_empty_list(self):
        input = []
        self.assertRaises(TypeError, lambda _: build_tree(input))

    def test_empty_set(self):
        input = set()
        self.assertRaises(TypeError, lambda _: build_tree(input))

    def test_empty_tuple(self):
        input = tuple()
        self.assertRaises(TypeError, lambda _: build_tree(input))

    def test_nested_lists(self):
        input = [[int]]
        root = build_tree(input)
        self.assertEquals([list, [[list, [int]]]], self.unroll_tree(root))

    def test_tuple(self):
        input = (int, str)
        root = build_tree(input)
        self.assertEquals([tuple, [int, str]], self.unroll_tree(root))

    def test_tuple_list(self):
        input = [(int, str)]
        root = build_tree(input)
        self.assertEquals([list, [[tuple, [int, str]]]], self.unroll_tree(root))

    def test_arbitrary_class(self):
        class MyClass():
            pass

        input = MyClass
        root = build_tree(input)
        self.assertEquals(MyClass, self.unroll_tree(root))

    def test_simple_dict(self):
        input = {'sup': str, 'hey': int}
        root = build_tree(input)

        s1 = _dict_to_struct(input)
        self.assertEquals(s1, self.unroll_tree(root))

    def test_simple_dict_inequality(self):
        input = {'sup': str, 'hey': int}
        root = build_tree(input)

        input = {'sup': int, 'hey': str}
        s1 = _dict_to_struct(input)
        self.assertNotEquals(s1, self.unroll_tree(root))


class TestDictStruct(unittest.TestCase):
    def test_simple_dict_to_struct(self):
        input = {'sup': str, 'hey': int}
        s1 = _dict_to_struct(input)
        s2 = _dict_to_struct(input)
        self.assertEquals(s1, s2)

    def test_simple_dict_to_struct_inequality(self):
        input = {'sup': int, 'hey': str}
        s1 = _dict_to_struct(input)
        input = {'sup': str, 'hey': int}
        s2 = _dict_to_struct(input)
        self.assertNotEquals(s1, s2)

    def test_nested_dict_to_struct(self):
        input = {'sup': {'yo': str}, 'hey': int}
        s1 = _dict_to_struct(input)
        s2 = _dict_to_struct(input)
        self.assertEquals(s1, s2)

    def test_nested_dict_to_struct_inequality(self):
        input = {'sup': {'yo': str}, 'hey': int}
        s1 = _dict_to_struct(input)
        input = {'sup': {'yo': int}, 'hey': str}
        s2 = _dict_to_struct(input)
        self.assertNotEquals(s1, s2)

    def test_complex_dict_to_struct(self):
        input = {'sup': {'yo': [int]}, 'hey': int}
        s1 = _dict_to_struct(input)
        s2 = _dict_to_struct(input)
        self.assertEquals(s1, s2)

    def test_recursive_dict_to_struct(self):
        input = {
            'sup': int,
            'hey': ['self']
        }
        s1 = _dict_to_struct(input)
        s2 = _dict_to_struct(input)
        self.assertEquals(s1, s2)


class TestValidation(unittest.TestCase):
    def test_simple_validation(self):
        input = [(int, str)]
        root_a = build_tree(input)
        root_b = build_tree(input)
        self.assertTrue(root_a.accepts(root_b))
        self.assertTrue(root_b.accepts(root_a))

    def test_complex_validation(self):
        input = {
            'sup': int,
            'hey': [(int, str)],
            'bar': {
                'ay': str,
                'yo': {bool}
            }
        }
        root_a = build_tree(input)
        root_b = build_tree(input)
        self.assertTrue(root_a.accepts(root_b))
        self.assertTrue(root_b.accepts(root_a))

    def test_dict_validation(self):
        output = {
            'sup': int,
            'hey': [(int, str)]
        }
        input = {
            'sup': int
        }
        root_input = build_tree(input)
        root_output = build_tree(output)
        self.assertTrue(root_input.accepts(root_output))
        self.assertFalse(root_output.accepts(root_input))

    def test_dict_recursion_validation(self):
        output = {
            'sup': 'self',
            'hey': [(int, str)]
        }
        input = {
            'sup': 'self'
        }
        root_input = build_tree(input)
        root_output = build_tree(output)
        self.assertTrue(root_input.accepts(root_output))
        self.assertFalse(root_output.accepts(root_input))
