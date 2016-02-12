# from atoll.config import EXECUTOR_HOST
from functools import partial
from itertools import chain
from distributed import Executor
from atoll.pipes import Branches

EXECUTOR_HOST = '127.0.0.1:8786'


def prep_func(pipe, **kwargs):
    """
    Prepares a pipe's function or branches
    by returning a partial function with its kwargs.
    """
    if isinstance(pipe, Branches):
        return [prep_func(b) for b in pipe.branches]
    else:
        kwargs_ = {}
        for key in pipe.expected_kwargs:
            try:
                kwargs_[key] = kwargs[key]
            except KeyError:
                raise KeyError('Missing expected keyword argument: {}'.format(key))
        return partial(pipe._func, **kwargs_)


def _kv(f):
    def kv_func(p):
        """helper to apply function `f` to value `v`"""
        k, v = p
        return k, f(v)
    return kv_func

def _unpack(f):
    def decorated(input):
        if not isinstance(input, tuple):
            input = (input,)
        return f(*input)
    return decorated

def map(executor, f, input):
    f = _unpack(f)
    return executor.map(f, input)

def mapValues(executor, f, input):
    f = _kv(f)
    return executor.map(f, input)

def flatMap(executor, f, input):
    fmap = lambda input: [result for result in chain(*input)]
    f = _unpack(f)
    return executor.submit(fmap, executor.map(f, input))

def flatMapValues(executor, f, input):
    fmap = lambda input: [result for result in chain(*[[(k, v) for v in vs] for k, vs in input])]
    return executor.submit(fmap, mapValues(executor, f, input))

def _reduce(f):
    def reduce_func(input):
        output = input[0]
        for i in input[1:]:
            output = f(output, i)
        return output
    return reduce_func

def reduce(executor, f, input):
    f = _reduce(f)
    return executor.submit(f, input)

def _reduceByKey(f):
    def reduce_func(input):
        results = {}
        for k, v in input:
            try:
                results[k] = f(results[k], v)
            except KeyError:
                results[k] = v
        return list(results.items())
    return reduce_func

def reduceByKey(executor, f, input):
    f = _reduceByKey(f)
    return executor.submit(f, input)

def compute_pipeline(pipes, input, **kwargs):
    exc = Executor(EXECUTOR_HOST)
    for op, pipe in pipes:
        f = prep_func(pipe, **kwargs)
        input = globals()[op](exc, f, input)
    return _get_results(exc, input)

def _get_results(executor, input):
    if isinstance(input, list):
        return executor.gather(input)
    elif isinstance(input, tuple):
        return [_get_results(executor, i) for i in input]
    else:
        return input.result()

def split(executor, fs, input):
    return [executor.submit(f, i) for f, i in zip(fs, input)]

def splitMap(executor, fs, input):
    return [executor.submit(f, i) for f, i in zip(fs, input)]

def _to(f):
    def func(input):
        print('CALLED WITH INPUT', input)
        if not isinstance(input, tuple):
            input = (input,)
        else:
            # flatten nested tuples
            args = []
            for arg in input:
                if isinstance(arg, tuple):
                    args.extend(arg)
                else:
                    args.append(arg)
            input = args
        print('CALLING', f)
        print('WITH INPUTS', input)
        return f(*input)
    return func

def to(executor, f, input):
    f = _to(f)
    return executor.submit(f, input)

def fork(executor, fs, input):
    return [executor.submit(f, input) for f in fs]


def _identity(f):
    # a hack to fix issues with forkMap, see forkMap
    def func(input):
        return f(input)
    return func

def forkMap(executor, fs, input):
    # TODO for some reason the executor thinks each function is identical
    # wrapping the function in this way solves the problem
    return [executor.submit(_identity(f), input) for f in fs]


if __name__ == '__main__':
    executor = Executor(EXECUTOR_HOST)

    # basics
    def square(x):
        x,y=x
        return x**2, y

    def neg(x):
        x,y=x
        return -x

    # inp = [1,2,3,4]
    inp = [(1,1),(2,1),(3,1),(4,1)]

    A = executor.map(square, inp)
    B = executor.map(neg, A)
    C = executor.submit(sum, B)
    print(C.result())

    print(executor.gather(B))
