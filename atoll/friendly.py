import inspect
from itertools import islice
from functools import partial
from types import BuiltinFunctionType


def _get_name(func):
    """get a function's name"""
    if hasattr(func, '__name__'):
        if func.__name__ == '<lambda>':
            # this is pretty sketchy
            return inspect.getsource(func).strip()
        return func.__name__
    elif isinstance(func, partial):
        return _get_name(func.func)
    else:
        return func.__class__.__name__


def name(func, *args, **kwargs):
    """get a function's name, with called args if any"""
    name = _get_name(func)
    args = ', '.join([ags for ags in [
                        ', '.join(map(str, args)),
                        ', '.join(['{}={}'.format(k, v) for k, v in kwargs.items()])
                    ] if ags])
    if args:
        return '{}({})'.format(name, args)
    return name


def signature(func):
    """get a function's signature"""
    if inspect.isclass(func):
        return str(inspect.signature(func.__call__))
    elif isinstance(func, partial):
        return str(signature(func.func))
    else:
        try:
            return str(inspect.signature(func))
        except ValueError:
            if isinstance(func, BuiltinFunctionType):
                return '(builtin)'
            else:
                raise


def get_example(input, depth=0):
    # stop-gap to avoid too deep recursion
    if depth > 10: return '...'

    """produce an "example" out of some input"""
    if isinstance(input, tuple):
        return '({})'.format(','.join('{}'.format(get_example(i)) for i in input))
    if isinstance(input, dict):
        # only get the first 5 items
        return '{{{}}}'.format(','.join('{}:{}'.format(k, get_example(v)) for k, v in islice(input.items(), 5)))
    if hasattr(input, '__iter__') and not isinstance(input, str):
        example = next(iter(input))
        return '[{},...]'.format(get_example(example, depth + 1))
    else:
        example = input
    return str(example)
