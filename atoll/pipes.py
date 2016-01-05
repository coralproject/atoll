from functools import partial
import atoll.pipeline
from atoll.friendly import name, signature


class Pipe(object):
    def __init__(self, func, *args, **kwargs):
        # register expected keyword arguments' keys
        if 'kwargs' in kwargs:
            self.expected_kwargs = kwargs['kwargs']
            del kwargs['kwargs']
        else:
            self.expected_kwargs = []

        if func is None:
            func = identity

        self.name = name(func, *args, **kwargs)
        self.sig = signature(func)

        # prep the pipe's function
        if args or kwargs:
            self._func = partial(func, *args, **kwargs)
        else:
            self._func = func

    def __repr__(self):
        return self.name


class Branches(object):
    def __init__(self, branches, default='to'):
        """
        Branches must either be pipelines, functions,
        or None, which represents an identity pipeline.

        The `default` kwarg defines which operator to use
        for connecting functions.
        """
        assert (default in atoll.pipeline.Pipeline.operators()), \
            '"{}" is not a valid pipeline operator'.format(default)

        self.branches = []
        for b in branches:
            if b is None:
                branch = Pipe(b)
            elif isinstance(b, atoll.pipeline.Pipeline):
                branch = b
            else:
                branch = getattr(atoll.pipeline.Pipeline(), default)(b)
            self.branches.append(branch)

        self.name = '|'.join([str(b) for b in self.branches])
        self.sig = [str(b.sig) for b in self.branches]
        self.expected_kwargs = sum([b.expected_kwargs for b in self.branches], [])

    def __iter__(self):
        for pipe in self.branches:
            yield pipe

    def __repr__(self):
        return self.name


def identity(input):
    return input
