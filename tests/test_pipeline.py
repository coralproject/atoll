import unittest
from atoll import Pipe, Pipeline


class LowercasePipe(Pipe):
    """
    A simple test pipe
    """
    input = [str]
    output = [str]

    def __call__(self, input):
        return [s.lower() for s in input]

class TokenizePipe(Pipe):
    input = [str]
    output = [[str]]

    def __call__(self, input):
        return [s.split(' ') for s in input]

class WordCounterPipe(Pipe):
    input = [[str]]
    output = [int]

    def __call__(self, input):
        return [len(s) for s in input]

class FirstCharPipe(Pipe):
    input = [[str]]
    output = [[str]]

    def __call__(self, input):
        return [[s_[0] for s_ in s] for s in input]



class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.docs = [
            'Coral reefs are diverse underwater ecosystems',
            'Coral reefs are built by colonies of tiny animals'
        ]
        self.expected_counts = [6,9]
        self.expected_chars = [['c', 'r', 'a', 'd', 'u', 'e'], ['c', 'r', 'a', 'b', 'b', 'c', 'o', 't', 'a']]

    def test_docstring(self):
        docstring = LowercasePipe.__doc__
        self.assertEqual(docstring, 'A simple test pipe\n\nInput:\n[str]\n\nOutput:\n[str]')

    def test_pipeline(self):
        expected = [
            ['coral', 'reefs', 'are', 'diverse', 'underwater', 'ecosystems'],
            ['coral', 'reefs', 'are', 'built', 'by', 'colonies', 'of', 'tiny', 'animals']
        ]
        pipeline = Pipeline([LowercasePipe(), TokenizePipe()])
        output = pipeline(self.docs)
        for o, e in zip(output, expected):
            self.assertEqual(set(o), set(e))

    def test_incompatible_pipeline(self):
        self.assertRaises(Exception, Pipeline, [WordCounterPipe(), LowercasePipe()])

    def test_nested_pipeline(self):
        nested_pipeline = Pipeline([LowercasePipe(), TokenizePipe()])
        pipeline = Pipeline([nested_pipeline, WordCounterPipe()])
        counts = pipeline(self.docs)
        self.assertEqual(counts, [6,9])




# pre-define types to use for the tests
Ain = [str]
Aout = bool
Bin = [str]
Cin = [int]
Din = [bool]
Bout = int
Cout = [[str]]
Dout = [(int,str)]
Eout = [int]

# should be diff from the rest
X = [(bool,str)]

class BranchingPipelineTests(unittest.TestCase):
    def test_valid_branching_pipeline_multiout_to_branches(self):
        class A(Pipe):
            input = Ain
            # A outputs tuples
            output = (Bin, Cin, Din)

        class B(Pipe):
            input = Bin
            output = Bout

        class C(Pipe):
            input = Cin
            output = Cout

        class D(Pipe):
            input = Din
            output = Dout

        class E(Pipe):
            input = (B.output, C.output, D.output)
            output = Eout

        try:
            Pipeline([
                A(),
                (B(), C(), D()),
                E()
            ])
        except Exception:
            self.fail('Valid pipeline raised exception')

    def test_invalid_branching_pipeline_multiout_to_branches(self):
        class A(Pipe):
            input = Ain
            # A outputs tuples
            output = (Bin, Cin, Din)

        class B(Pipe):
            input = Bin
            output = Bout

        class C(Pipe):
            input = Cin
            output = Cout

        class D(Pipe):
            input = Din
            output = Dout

        class E(Pipe):
            input = (B.output, C.output, D.output)
            output = Eout

        # Wrong branch size
        self.assertRaises(Exception, Pipeline, [A(), (B(), C()), E()])

        # Wrong branch order
        self.assertRaises(Exception, Pipeline, [A(), (C(), B(), D()), E()])

        # Wrong input type
        class D_(Pipe):
            input = X
            output = Dout

        self.assertRaises(Exception, Pipeline, [A(), (B(), C(), D_()), E()])

        # Wrong output size
        class A_(Pipe):
            input = Ain
            output = (Bin, Cin)

        self.assertRaises(Exception, Pipeline, [A_(), (B(), C(), D()), E()])

        # Wrong output types
        class A_(Pipe):
            input = Ain
            output = (Bin, Cin, X)

        self.assertRaises(Exception, Pipeline, [A_(), (B(), C(), D()), E()])

    def test_valid_branching_pipeline_branches_to_branches(self):
        class A(Pipe):
            input = Ain
            # A outputs tuples
            output = (Bin, Cin, Din)

        class B(Pipe):
            input = Bin
            output = Bin

        class C(Pipe):
            input = Cin
            output = Cin

        class D(Pipe):
            input = Din
            output = Din

        class E(Pipe):
            input = (B.output, C.output, D.output)
            output = Eout

        try:
            Pipeline([
                A(),
                (B(), C(), D()),
                (B(), C(), D()),
                E()
            ])
        except Exception:
            self.fail('Valid pipeline raised exception')

    def test_invalid_branching_pipeline_branches_to_branches(self):
        class A(Pipe):
            input = Ain
            # A outputs tuples
            output = (Bin, Cin, Din)

        class B(Pipe):
            input = Bin
            output = Bout

        class C(Pipe):
            input = Cin
            output = Cout

        class D(Pipe):
            input = Din
            output = X

        class E(Pipe):
            input = (B.output, C.output, D.output)
            output = Eout

        self.assertRaises(Exception, Pipeline, [A(),
                                                (B(), C(), D()),
                                                (B(), C(), D()),
                                                E()])

    def test_valid_branching_pipeline_one_output_to_branches(self):
        class A(Pipe):
            input = Ain
            # A does not output tuples
            output = Aout

        class B(Pipe):
            input = A.output
            output = Bout

        class C(Pipe):
            input = A.output
            output = Cout

        class D(Pipe):
            input = A.output
            output = Dout

        class E(Pipe):
            input = (B.output, C.output, D.output)
            output = Eout

        try:
            Pipeline([
                A(),
                (B(), C(), D()),
                E()
            ])
        except Exception:
            self.fail('Valid pipeline raised exception')

    def test_invalid_branching_pipeline_one_output_to_branches(self):
        class A(Pipe):
            input = Ain
            # A does not output tuples
            output = Aout

        class B(Pipe):
            input = A.output
            output = Bout

        class C(Pipe):
            input = A.output
            output = Cout

        class D(Pipe):
            input = X
            output = Dout

        class E(Pipe):
            input = (B.output, C.output, D.output)
            output = Eout

        self.assertRaises(Exception, Pipeline, [A(),
                                                (B(), C(), D()),
                                                E()])

    def test_invalid_branching_pipeline_reduce_pipe(self):
        class A(Pipe):
            input = Ain
            # A does not output tuples
            output = Aout

        class B(Pipe):
            input = A.output
            output = Bout

        class C(Pipe):
            input = A.output
            output = Cout

        class D(Pipe):
            input = A.output
            output = Dout

        class E(Pipe):
            input = (B.output, C.output, X)
            output = Eout

        self.assertRaises(Exception, Pipeline, [A(),
                                                (B(), C(), D()),
                                                E()])

    def test_valid_branching_pipeline_start_with_branches(self):
        class B(Pipe):
            input = Bin
            output = Bout

        class C(Pipe):
            input = Cin
            output = Cout

        class D(Pipe):
            input = Din
            output = Dout

        class E(Pipe):
            input = (B.output, C.output, D.output)
            output = Eout

        try:
            Pipeline([
                (B(), C(), D()),
                E()
            ])
        except Exception:
            self.fail('Valid pipeline raised exception')

    def test_valid_branching_pipeline_end_with_branches(self):
        class A(Pipe):
            input = Ain
            # A does not output tuples
            output = Aout

        class B(Pipe):
            input = A.output
            output = Bout

        class C(Pipe):
            input = A.output
            output = Cout

        class D(Pipe):
            input = A.output
            output = Dout

        try:
            Pipeline([
                A(),
                (B(), C(), D()),
            ])
        except Exception:
            self.fail('Valid pipeline raised exception')

    def test_branching_pipeline(self):
        class A(Pipe):
            input = [int]
            output = [int]
            def __call__(self, vals):
                return [v+1 for v in vals]

        class B(Pipe):
            input = [int]
            output = [int]
            def __call__(self, vals):
                return [v+2 for v in vals]

        class C(Pipe):
            input = [int]
            output = [int]
            def __call__(self, vals):
                return [v+3 for v in vals]

        class D(Pipe):
            input = [int]
            output = [int]
            def __call__(self, vals):
                return [v+4 for v in vals]

        class E(Pipe):
            input = ([int], [int], [int])
            output = [int]
            def __call__(self, vals1, vals2, vals3):
                return [sum([v1,v2,v3]) for v1,v2,v3 in zip(vals1,vals2,vals3)]

        p = Pipeline([
            A(),
            (B(), C(), D()),
            (B(), C(), D()),
            E()
        ])

        out = p([1,2,3,4])
        self.assertEqual(out, [24,27,30,33])
