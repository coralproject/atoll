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
