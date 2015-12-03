from functools import partial
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
            self.func = partial(func, *args, **kwargs)
        else:
            self.func = func

    def __repr__(self):
        return self.name


class Branches(object):
    def __init__(self, branches):
        """
        Branches must either be pipelines or None,
        which represents an identity pipeline.
        """
        self.branches = [b if b is not None else Pipe(b) for b in branches]
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
