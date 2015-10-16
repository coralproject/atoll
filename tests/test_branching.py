import unittest
from atoll import Pipe, Pipeline
from atoll.pipeline import InvalidPipelineError


# for parallielization pickling, must define pipes here
class Ap(Pipe):
    input = [int]
    output = [int]
    def __call__(self, vals):
        return [v+1 for v in vals]

class Bp(Pipe):
    input = [int]
    output = [int]
    def __call__(self, vals):
        return [v+2 for v in vals]

class Cp(Pipe):
    input = [int]
    output = [int]
    def __call__(self, vals):
        return [v+3 for v in vals]

class Ep(Pipe):
    input = ([int], [int])
    output = [int]
    def __call__(self, vals1, vals2):
        return [sum([v1,v2]) for v1,v2 in zip(vals1,vals2)]


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
    def test_valid_branching_pipeline_split_to_branches(self):
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
            Pipeline([A()]).split(B(), C(), D()).to(E)
        except InvalidPipelineError:
            self.fail('Valid pipeline raised exception')

    def test_invalid_branching_pipeline_split_to_branches(self):
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

        p = Pipeline([A()])
        self.assertRaises(InvalidPipelineError, p.split, B(), C())

        # Wrong branch order
        self.assertRaises(InvalidPipelineError, p.split, C(), B(), D())

        # Wrong input type
        class D_(Pipe):
            input = X
            output = Dout

        self.assertRaises(InvalidPipelineError, p.split, B(), C(), D_())

        # Wrong output size
        class A_(Pipe):
            input = Ain
            output = (Bin, Cin)

        p = Pipeline([A_()])
        self.assertRaises(InvalidPipelineError, p.split, B(), C(), D())

        # Wrong output types
        class A_(Pipe):
            input = Ain
            output = (Bin, Cin, X)

        p = Pipeline([A_()])
        self.assertRaises(InvalidPipelineError, p.split, B(), C(), D())

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
            Pipeline([A()]).split(B(), C(), D()).split(B(), C(), D()).to(E())
        except InvalidPipelineError:
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

        p = Pipeline([A()]).split(B(), C(), D())
        self.assertRaises(InvalidPipelineError, p.split, B(), C(), D())

    def test_valid_branching_pipeline_fork_to_branches(self):
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
            Pipeline([A()]).fork(B(), C(), D()).to(E())
        except InvalidPipelineError:
            self.fail('Valid pipeline raised exception')

    def test_invalid_branching_pipeline_fork_to_branches(self):
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

        p = Pipeline([A()])
        self.assertRaises(InvalidPipelineError, p.fork, B(), C(), D())

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

        p = Pipeline([A()]).fork(B(), C(), D())
        self.assertRaises(InvalidPipelineError, p.to, E())

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
            Pipeline().fork(B(), C(), D()).to(E())
        except InvalidPipelineError:
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
            Pipeline([A()]).fork(B(), C(), D())
        except InvalidPipelineError:
            self.fail('Valid pipeline raised exception')

    def test_branching_pipeline(self):
        p = Pipeline([Ap()]).fork(Bp(), Cp()).split(Bp(), Cp()).to(Ep())
        out = p([1,2,3,4])
        self.assertEqual(out, [14,16,18,20])

    def test_parallel_branching(self):
        p = Pipeline([Ap()], n_jobs=2).fork(Bp(), Cp()).split(Bp(), Cp()).to(Ep())
        out = p([1,2,3,4])
        self.assertEqual(out, [14,16,18,20])

    def test_identity_pipes(self):
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

        class E(Pipe):
            input = (B.output, C.output, A.output)
            output = Eout

        try:
            Pipeline([A()]).fork(B(), C(), None).to(E())
        except InvalidPipelineError:
            self.fail('Valid pipeline raised exception')

    def test_invalid_identity_pipes(self):
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

        class E(Pipe):
            input = (B.output, C.output, X)
            output = Eout

        p = Pipeline([A()]).fork(B(), C(), None)
        self.assertRaises(InvalidPipelineError, p.to, E())

