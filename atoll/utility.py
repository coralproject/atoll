from functools import partial
from atoll.pipes import Branches


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
