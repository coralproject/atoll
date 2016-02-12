from itertools import chain
from distributed import Executor
from atoll.utility import prep_func
from atoll.config import EXECUTOR_HOST


def compute_pipeline(pipes, input, **kwargs):
    """computes a pipeline in a distributed fashion"""
    exc = Executor(EXECUTOR_HOST)
    for op, pipe in pipes:
        f = prep_func(pipe, **kwargs)
        input = globals()[op](exc, f, input)
    return _get_results(exc, input)


def to(executor, f, input):
    f = _to(f)
    return executor.submit(f, input)


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


def fork(executor, fs, input):
    return [executor.submit(f, input) for f in fs]


def forkMap(executor, fs, input):
    # TODO for some reason the executor thinks each function is identical
    # wrapping the function in this way solves the problem
    return [executor.submit(_identity(f), input) for f in fs]


def reduce(executor, f, input):
    f = _reduce(f)
    return executor.submit(f, input)


def reduceByKey(executor, f, input):
    f = _reduceByKey(f)
    return executor.submit(f, input)


def split(executor, fs, input):
    return [executor.submit(f, i) for f, i in zip(fs, input)]


def splitMap(executor, fs, input):
    return [executor.submit(f, i) for f, i in zip(fs, input)]


def _get_results(executor, input):
    """retrieves distributed results, causing the pipeline to execute"""
    if isinstance(input, list):
        return executor.gather(input)
    elif isinstance(input, tuple):
        return [_get_results(executor, i) for i in input]
    else:
        return input.result()


def _kv(f):
    """helper to apply function `f` to value `v`"""
    def kv_func(p):
        k, v = p
        return k, f(v)
    return kv_func


def _unpack(f):
    """to unpack arguments"""
    def decorated(input):
        if not isinstance(input, tuple):
            input = (input,)
        return f(*input)
    return decorated


def _reduce(f):
    def reduce_func(input):
        output = input[0]
        for i in input[1:]:
            output = f(output, i)
        return output
    return reduce_func


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


def _to(f):
    def func(input):
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
        return f(*input)
    return func


def _identity(f):
    # a hack to fix issues with forkMap, see forkMap
    def func(input):
        return f(input)
    return func

