from itertools import product
from atoll.validate import build_tree, TypeNode


class MetaPipe(type):
    """
    A metaclass which automatically building of a
    pipe's input and output type trees.

    Also automatically adds these input and output type trees
    as part of the class's docstring.
    """
    def __init__(cls, name, parents, dct):
        cls._input = build_tree(cls.input)
        cls._output = build_tree(cls.output)

    @property
    def __doc__(self):
        doc = super().__doc__ or ''
        return '\n'.join([doc.strip(),
                          '\nInput:', str(self._input),
                          '\nOutput:', str(self._output)])

class BranchedPipe():
    """
    A special type of pipe for representing branched pipes
    """
    def __init__(self, pipes):
        self.pipes = pipes
        self._input = TypeNode(tuple, ch=[p._input for p in pipes])
        self._output = TypeNode(tuple, ch=[p._output for p in pipes])

    def __call__(self, *input):
        # Multi-to-branch/branch-to-branch
        if len(input) > 1:
            return tuple(p(i) for p, i in zip(self.pipes, input))

        # One-to-branch
        else:
            return tuple(p(*input) for p in self.pipes)

    @property
    def name(self):
        return '({})'.format(', '.join([p.name for p in self.pipes]))


class Pipe(metaclass=MetaPipe):
    input = [str]
    output = [str]

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        obj._args = args
        obj._kwargs = kwargs

        # Build Pipe's signature
        args = ', '.join([ags for ags in [
                            ', '.join(map(str, args)),
                            ', '.join(['{}={}'.format(k, v) for k, v in kwargs.items()])
                        ] if ags])
        obj._sig = '{}({})'.format(
            cls.__name__,
            args
        )

        return obj

    def __init__(self, *args, **kwargs):
        self.args = args
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return self._sig

    def __call__(self):
        raise NotImplementedError

    def __doc__(self):
        return super().__doc__()

    @property
    def name(self):
        return type(self).__name__


class Pipeline():
    def __init__(self, pipes, **kwargs):
        self.pipes = []
        # Process branches if necessary
        for p in pipes:
            if isinstance(p, tuple):
                self.pipes.append(BranchedPipe(p))
            else:
                self.pipes.append(p)

        # Validate the pipeline
        for p_out, p_in in zip(self.pipes, self.pipes[1:]):
            output = p_out._output
            input = p_in._input

            if isinstance(p_in, BranchedPipe):
                # If the output is not a tuple,
                # we are replicating it across each branch (one-to-branch)
                if output.type != tuple:
                    output = TypeNode(tuple, ch=[output for i in input.children])

            if output != input:
                raise Exception('Incompatible pipes:\npipe {} outputs {},\npipe {} requires input of {}.'.format(p_out.name, output, p_in.name, input))

        # Pipelines can be nested
        self._input = self.pipes[0]._input
        self._output = self.pipes[-1]._output

    def __call__(self, input):
        for pipe in self.pipes:
            if isinstance(input, tuple):
                output = pipe(*input)
            else:
                output = pipe(input)
            input = output
        return output

    def __repr__(self):
        return ' -> '.join([str(p) for p in self.pipes])
