import inspect
from itertools import islice
from functools import partial


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


def name(func, *args, **kwargs):
    name = _get_name(func)
    args = ', '.join([ags for ags in [
                        ', '.join(map(str, args)),
                        ', '.join(['{}={}'.format(k, v) for k, v in kwargs.items()])
                    ] if ags])
    if args:
        return '{}({})'.format(name, args)
    return name


def signature(func):
    if inspect.isclass(func):
        return str(inspect.signature(func.__call__))
    elif isinstance(func, partial):
        return str(signature(func.func))
    else:
        return str(inspect.signature(func))


def get_example(input):
    """
    Produce an "example" out of some input.
    """
    if isinstance(input, tuple):
        return '({})'.format(','.join('{}'.format(get_example(i)) for i in input))
    if isinstance(input, dict):
        # only get the first 5 items
        return '{{{}}}'.format(','.join('{}:{}'.format(k, get_example(v)) for k, v in islice(input.items(), 5)))
    if hasattr(input, '__iter__') and not isinstance(input, str):
        example = next(iter(input))
        return '[{},...]'.format(get_example(example))
    else:
        example = input
    return str(example)
