import inspect
from functools import partial
from joblib import Parallel, delayed


class _pipe(object):
    name_format = '{}'

    def __init__(self, n_jobs, func, *args, **kwargs):
        # not ideal, should import Pipeline and check against that
        if func.__class__.__name__ == 'Pipeline':
            self.name = str(func)
        else:
            self.name = self.name_format.format(_name(func, *args, **kwargs))

        self.sig = _signature(func)
        self.n_jobs = n_jobs
        if args or kwargs:
            self.func = partial(func, *args, **kwargs)
        else:
            self.func = func

    def __call__(self, input):
        if isinstance(input, tuple):
            return self.func(*input)
        return self.func(input)

    def __repr__(self):
        return self.name


class _branch(_pipe):
    def __init__(self, func, *args, **kwargs):
        super(_branch, self).__init__(0, func, *args, **kwargs)


class _map(_pipe):
    name_format = 'map[{}]'
    def __call__(self, input):
        if not isinstance(input[0], tuple):
            input = [(i,) for i in input]
        if self.n_jobs:
            return Parallel(n_jobs=self.n_jobs)(delayed(self.func)(*i) for i in input)
        return list(map(self.func, *zip(*input)))


class _map_dict(_pipe):
    name_format = 'map_dict[{}]'
    def __call__(self, input):
        if self.n_jobs:
            return Parallel(n_jobs=self.n_jobs)(delayed(self.func)(*i) for i in input.items())
        return list(map(self.func, *zip(*input.items())))


class _branches(object):
    def __init__(self, n_jobs, funcs):
        funcs = [f if f is not None else identity for f in funcs]
        self.branches = [_branch(f) for f in funcs]
        self.n_jobs = n_jobs

        self.name = self.name_format.format('|'.join([str(b) for b in self.branches]))
        self.sig = [str(b.sig) for b in self.branches]

    def __repr__(self):
        return self.name


class _fork(_branches):
    name_format = 'fork[{}]'
    def __call__(self, input):
        if self.n_jobs:
            return tuple(Parallel(n_jobs=self.n_jobs)(delayed(b)(input) for b in self.branches))
        # NOTE: potential problem here: if you modify the input,
        # it will be modified for the other functions.
        # may be best to copy the input.
        return tuple(b(input) for b in self.branches)


class _split(_branches):
    name_format = 'split[{}]'
    def __call__(self, input):
        if self.n_jobs:
            return tuple(Parallel(n_jobs=self.n_jobs)(delayed(p)(i) for p, i in zip(self.branches, input)))
        return tuple(p(i) for p, i in zip(self.branches, input))


def _get_name(func):
    if hasattr(func, '__name__'):
        if func.__name__ == '<lambda>':
            # this is pretty sketchy
            return inspect.getsource(func).strip()
        return func.__name__
    elif isinstance(func, partial):
        return _get_name(func.func)
    else:
        return func.__class__.__name__


def _name(func, *args, **kwargs):
    name = _get_name(func)
    args = ', '.join([ags for ags in [
                        ', '.join(map(str, args)),
                        ', '.join(['{}={}'.format(k, v) for k, v in kwargs.items()])
                    ] if ags])
    if args:
        return '{}({})'.format(name, args)
    return name


def _signature(func):
    if inspect.isclass(func):
        return inspect.signature(func.__call__)
    elif isinstance(func, partial):
        return _signature(func.func)
    else:
        return inspect.signature(func)


def identity(input):
    return input
