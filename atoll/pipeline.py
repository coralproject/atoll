import six
import logging
from hashlib import md5
from joblib import Parallel, delayed
from atoll.validate import build_tree, TypeNode

logger = logging.getLogger(__name__)


class InvalidPipelineError(Exception):
    pass


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
        doc = super(MetaPipe, self).__doc__ or ''
        return '\n'.join([doc.strip(),
                          '\nInput:', str(self._input),
                          '\nOutput:', str(self._output)])


class MappedPipe():
    """
    A special type of pipe representing mapped pipes
    """
    def __init__(self, pipe, n_jobs):
        self.pipe = pipe
        self.n_jobs = n_jobs
        self._input = TypeNode(list, ch=[pipe._input])
        self._output = TypeNode(list, ch=[pipe._output])

        self.name = '[{}]'.format(pipe.name)
        self.sig = '[{}]'.format(pipe.sig)

    def __call__(self, inputs):
        # TODO clean this up
        if isinstance(inputs, dict):
            inputs = inputs.items()
            if self.n_jobs != 0:
                return Parallel(n_jobs=self.n_jobs)(delayed(self.pipe)(*i) for i in inputs)
            else:
                return [self.pipe(*i) for i in inputs]

        else:
            if self.n_jobs != 0:
                return Parallel(n_jobs=self.n_jobs)(delayed(self.pipe)(i) for i in inputs)
            else:
                return [self.pipe(i) for i in inputs]

    def __repr__(self):
        return self.sig


class BranchedPipe():
    """
    A special type of pipe representing branched pipes
    """
    def __init__(self, pipes, n_jobs):
        # Check for any identity pipes
        pipes = [p if p != None else IdentityPipe() for p in pipes]

        self._input = TypeNode(tuple, ch=[p._input for p in pipes])
        self._output = TypeNode(tuple, ch=[p._output for p in pipes])
        self.n_jobs = n_jobs

        self.name = '({})'.format(', '.join([p.name for p in pipes]))
        self.sig = '({})'.format(', '.join([p.sig for p in pipes]))
        self.pipes = pipes

    def __call__(self, *input):
        # One-to-branch, duplicate input for each pipe
        if len(input) == 1:
            input = tuple(input for p in self.pipes)

        # otherwise, multi-to-branch/branch-to-branch
        else:
            input = tuple((i,) for i in input)

        stream = zip(self.pipes, input)
        if self.n_jobs != 0:
            return tuple(Parallel(n_jobs=self.n_jobs)(delayed(p)(*i) for p, i in stream))
        else:
            return tuple(p(*i) for p, i in stream)

    def __repr__(self):
        return self.sig


class IdentityPipe():
    """
    The identity pipe is a special pipe which passes along its input unmodified.
    It is used only in branching.
    """
    name = 'IdentityPipe'
    sig = 'IdentityPipe'

    def __init__(self):
        # These are established during validation
        self._input = None
        self._output = None

    def __call__(self, input):
        return input


@six.add_metaclass(MetaPipe)
class Pipe():
    input = [str]
    output = [str]

    def __new__(cls, *args, **kwargs):
        obj = super(Pipe, cls).__new__(cls)
        obj._args = args
        obj._kwargs = kwargs

        # Build Pipe's signature
        args = ', '.join([ags for ags in [
                            ', '.join(map(str, args)),
                            ', '.join(['{}={}'.format(k, v) for k, v in kwargs.items()])
                        ] if ags])
        obj.sig = '{}({})'.format(
            cls.__name__,
            args
        )

        obj.name = type(obj).__name__

        return obj

    def __init__(self, *args, **kwargs):
        self.args = args
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return self.sig

    def __call__(self):
        raise NotImplementedError

    def __doc__(self):
        return super(Pipe, self).__doc__()


class Pipeline():
    def __init__(self, pipes=[], **kwargs):
        self.pipes = []
        for pipe in pipes:
            self.to(pipe)

        self.n_jobs = kwargs.get('n_jobs', 0)
        self._name = kwargs.get('name', None)

    def _validate(self, p_out, p_in):
        output = p_out._output
        input = p_in._input

        if not input.accepts(output):
            msg = 'Incompatible pipes:\npipe {} outputs {},\npipe {} requires input of {}.'.format(p_out.name, output, p_in.name, input)
            logger.error(msg)
            raise InvalidPipelineError(msg)

        return True

    def __call__(self, input):
        for pipe in self.pipes:
            try:
                if isinstance(input, tuple):
                    output = pipe(*input)
                else:
                    output = pipe(input)
            except:
                logger.exception('Failed to execute pipe {}'.format(pipe))
                raise
            input = output
        return output

    def __repr__(self):
        return ' -> '.join([str(p) for p in self.pipes])

    @property
    def name(self):
        # Ideally users should name their own pipelines
        # so they know what a pipeline does, but a fallback is offered
        return self._name if self._name is not None else self.sig

    @property
    def sig(self):
        """
        Produce a sig of the pipeline.
        This is for establishing data analysis provenance,
        but note that it does not (yet) account for stochastic pipes!
        """
        return md5('->'.join([p.sig for p in self.pipes]).encode('utf-8')).hexdigest()


    # Pipeline composition methods
    def to(self, pipe):
        if self.pipes and self._validate(self.pipes[-1], pipe):
            self.pipes.append(pipe)
            self._output = pipe._output
        else:
            self.pipes.append(pipe)
            self._input = pipe._input
            self._output = pipe._output

        return self

    def map(self, pipe):
        mapped = MappedPipe(pipe, self.n_jobs)

        if self.pipes and self._validate(self.pipes[-1], mapped):
            self._input
            self.pipes.append(mapped)
            self._output = mapped._output
        else:
            self.pipes.append(mapped)
            self._input = mapped._input
            self._output = mapped._output

        return self

    def fork(self, *branches):
        branches = BranchedPipe(branches, self.n_jobs)
        next_type = branches._input

        # TODO clean this up
        # Check for identity pipes
        if self.pipes:
            prev_type = self.pipes[-1]._output
            next_type = branches._input
            for i, ch in enumerate(next_type.children):
                if ch is None:
                    # The identity pipe's input and output
                    # depend on the pipe that feeds into it,
                    # so update its input and output here
                    next_type.children[i] = prev_type
                    branches._output.children[i] = prev_type
                    branches.pipes[i]._input = prev_type
                    branches.pipes[i]._output = prev_type

        # TODO clean this up, validating manually here
        if self.pipes:
            for branch in branches.pipes:
                self._validate(self.pipes[-1], branch)
        else:
            self._input = branches._input
        self.pipes.append(branches)
        self._output = branches._output
        return self

    def split(self, *branches):
        branches = BranchedPipe(branches, self.n_jobs)

        # Check for identity pipes
        if self.pipes:
            prev_type = self.pipes[-1]._output
            next_type = branches._input
            for i, ch in enumerate(next_type.children):
                if ch is None:
                    # The identity pipe's input and output
                    # depend on the pipe that feeds into it,
                    # so update its input and output here
                    next_type.children[i] = prev_type.children[i]
                    branches._output.children[i] = prev_type.children[i]
                    branches.pipes[i]._input = prev_type
                    branches.pipes[i]._output = prev_type

        self.to(branches)
        return self
