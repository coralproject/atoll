from functools import partial
from joblib import Parallel, delayed
from atoll.friendly import name, signature


class _pipe(object):
    name_format = '{}'

    def __init__(self, n_jobs, func, *args, **kwargs):
        # register expected keyword arguments' keys
        if 'kwargs' in kwargs:
            self.expected_kwargs = kwargs['kwargs']
            del kwargs['kwargs']
        else:
            self.expected_kwargs = []

        self.name = self.name_format.format(name(func, *args, **kwargs))
        self.sig = signature(func)
        self.n_jobs = n_jobs
        if args or kwargs:
            self.func = partial(func, *args, **kwargs)
        else:
            self.func = func

    def __call__(self, input, **kwargs):
        kwargs_ = {}
        for key in self.expected_kwargs:
            if key not in kwargs:
                raise KeyError('Missing expected keyword argument: {}'.format(key))
            kwargs_[key] = kwargs[key]
        return self.run(input, **kwargs_)

    def run(self, input, **kwargs):
        if isinstance(input, tuple):
            return self.func(*input, **kwargs)
        return self.func(input, **kwargs)

    def __repr__(self):
        return self.name


class _branch(_pipe):
    def __init__(self, func, *args, **kwargs):
        super(_branch, self).__init__(0, func, *args, **kwargs)


class _map(_pipe):
    name_format = 'map[{}]'
    def run(self, input, **kwargs):
        if not isinstance(input[0], tuple):
            input = [(i,) for i in input]
        if self.n_jobs:
            return Parallel(n_jobs=self.n_jobs)(delayed(self.func)(*i, **kwargs) for i in input)
        return list(map(partial(self.func, **kwargs), *zip(*input)))


class _map_dict(_pipe):
    name_format = 'map_dict[{}]'
    def run(self, input, **kwargs):
        if self.n_jobs:
            return Parallel(n_jobs=self.n_jobs)(delayed(self.func)(*i, **kwargs) for i in input.items())
        return list(map(partial(self.func, **kwargs), *zip(*input.items())))


class _branches(object):
    def __init__(self, n_jobs, funcs):
        funcs = [f if f is not None else identity for f in funcs]
        self.branches = [_branch(f) for f in funcs]
        self.n_jobs = n_jobs

        self.name = self.name_format.format('|'.join([str(b) for b in self.branches]))
        self.sig = [str(b.sig) for b in self.branches]

        # TODO add kwarg support for branches
        self.expected_kwargs = []

    def __call__(self, input, **kwargs):
        kwargs_ = {}
        for key in self.expected_kwargs:
            if key not in kwargs:
                raise KeyError('Missing expected keyword argument: {}'.format(key))
            kwargs_[key] = kwargs[key]
        return self.run(input, **kwargs_)

    def __repr__(self):
        return self.name


class _fork(_branches):
    name_format = 'fork[{}]'
    def run(self, input, **kwargs):
        if self.n_jobs:
            return tuple(Parallel(n_jobs=self.n_jobs)(delayed(b)(input, **kwargs) for b in self.branches))
        # NOTE: potential problem here: if you modify the input,
        # it will be modified for the other functions.
        # may be best to copy the input.
        return tuple(b(input, **kwargs) for b in self.branches)


class _split(_branches):
    name_format = 'split[{}]'
    def run(self, input, **kwargs):
        if self.n_jobs:
            return tuple(Parallel(n_jobs=self.n_jobs)(delayed(b)(i, **kwargs) for b, i in zip(self.branches, input)))
        return tuple(b(i, **kwargs) for b, i in zip(self.branches, input))


def identity(input):
    return input
