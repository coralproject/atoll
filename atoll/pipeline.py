import logging
from hashlib import md5
from itertools import chain
from functools import partial
from joblib import Parallel, delayed
from atoll import distrib
from atoll.utility import prep_func
from atoll.pipes import Pipe, Branches
from atoll.exceptions import InvalidInputError


logger = logging.getLogger(__name__)


def composition(f):
    """decorates a function which builds the pipeline,
    i.e. a function that adds a new pipe"""
    def decorated(self, func=None, *args, **kwargs):
        assert callable(func) or func is None, \
            'Pipes must be callable'

        if isinstance(func, Pipeline):
            pipe = func
        else:
            pipe = f(self, func, *args, **kwargs)

        self.expected_kwargs += pipe.expected_kwargs
        self.pipes.append((f.__name__, pipe))
        return self
    return decorated


def branching(f):
    """decorates a branching composition function"""
    def decorated(self, *funcs):
        for func in funcs:
            assert ((not isinstance(func, type)) and callable(func)) or func is None, \
                'Branches must be callable'
        branches = f(self, funcs)
        self.expected_kwargs += branches.expected_kwargs
        self.pipes.append((f.__name__, branches))
        return self
    return decorated


def execution(f):
    """decorates the function which executes a corresponding pipe"""
    def decorated(self, pipe, input, **kwargs):
        func = prep_func(pipe, **kwargs)
        return f(self, func, input)
    return decorated


def validate_input(*types):
    def decorated(f):
        def wrapped(self, func, input, *args, **kwargs):
            if not isinstance(input, types):
                raise InvalidInputError('Error running pipe "{}", input is not one of: {}'.format(
                    func, [t.__name__ for t in types]))
            return f(self, func, input, *args, **kwargs)
        return wrapped
    return decorated


def kv_func(f, k, v):
    """helper to apply function `f` to value `v`"""
    return k, f(v)


class Pipeline(Pipe):
    def __init__(self, **kwargs):
        self._name = kwargs.get('name', None)
        self.expected_kwargs = []
        self.pipes = []

    def _func(self, input, distributed=False, **kwargs):
        """
        Used if the pipeline is nested in another.
        This prevents nested pipelines from running their own parallel processes.
        """
        return self(input, distributed=distributed, nested=True, **kwargs)

    def __call__(self, input, n_jobs=1, serial=False, distributed=False, nested=False, **kwargs):
        if distributed:
            return distrib.compute_pipeline(self.pipes, input, **kwargs)

        else:
            if nested or serial:
                # execute serially if nested
                self.executor = self._serial
                self.funcproc = self.__s
            else:
                self.executor = Parallel(n_jobs=n_jobs)
                self.funcproc = self.__p

            for op, pipe in self.pipes:
                try:
                    input = getattr(self, '_' + op)(pipe, input, **kwargs)
                except Exception as e:
                    # attach the data the pipeline failed on
                    e.data = input
                    logger.exception('Failed to execute pipe "{}{}"'.format(
                        pipe, pipe.sig))
                    raise

            del self.executor
            del self.funcproc
        return input

    def __repr__(self):
        return ' -> '.join(['{}:{}'.format(op, pipe) for op, pipe in self.pipes])

    @property
    def name(self):
        # Ideally users should name their own pipelines
        # so they know what a pipeline does, but a fallback is offered
        return self._name if self._name is not None else self.sig

    @property
    def sig(self):
        """
        Produce a sig of the pipeline.
        This is for establishing data analysis provenance,
        but note that it does not (yet) account for stochastic pipes!
        """
        return md5('->'.join(['{}:{}'.format(op, pipe) for op, pipe in self.pipes]).encode('utf-8')).hexdigest()

    @composition
    def to(self, func, *args, **kwargs):
        """call `func` with all input"""
        return Pipe(func, *args, **kwargs)

    @composition
    def map(self, func, *args, **kwargs):
        """call `func` for each input"""
        return Pipe(func, *args, **kwargs)

    @composition
    def flatMap(self, func, *args, **kwargs):
        """map but flatten result"""
        return Pipe(func, *args, **kwargs)

    @composition
    def mapValues(self, func, *args, **kwargs):
        """call `func` for each value of a list of key-value pairs"""
        return Pipe(func, *args, **kwargs)

    @composition
    def flatMapValues(self, func, *args, **kwargs):
        """mapValues but flatten the result"""
        return Pipe(func, *args, **kwargs)

    @composition
    def reduce(self, func, *args, **kwargs):
        """combine/collapse inputs by applying `func`"""
        return Pipe(func, *args, **kwargs)

    @composition
    def reduceByKey(self, func, *args, **kwargs):
        """combine/collapse inputs with matching keys by applying `func`"""
        return Pipe(func, *args, **kwargs)

    @branching
    def fork(self, funcs):
        """copy input for each func in `funcs`"""
        return Branches(funcs, default='to')

    @branching
    def forkMap(self, funcs):
        """like fork, but assumes bare functions are to be mapped"""
        return Branches(funcs, default='map')

    @branching
    def split(self, funcs):
        """assumes input is tuples, each element is sent to a different branch"""
        return Branches(funcs, default='to')

    @branching
    def splitMap(self, funcs):
        """like split, but assumes bare functions are to be mapped"""
        return Branches(funcs, default='map')

    # execution methods just take care of execution of the pipes
    # produced by the above composition/branching methods

    @execution
    def _to(self, func, input):
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
        return func(*input)

    @validate_input(list, tuple)
    @execution
    def _map(self, func, input):
        if not isinstance(input[0], tuple):
            input = [(i,) for i in input]
        return self.executor(self.funcproc(func)(*i) for i in input)

    @validate_input(list, tuple)
    @execution
    def _flatMap(self, func, input):
        if not isinstance(input[0], tuple):
            input = [(i,) for i in input]
        return [result for result in chain(*self.executor(self.funcproc(func)(*i) for i in input))]

    @validate_input(list, dict, tuple)
    @execution
    def _mapValues(self, func, input):
        if isinstance(input, dict):
            input = input.items()
        # TODO should we handle dicts like this?
        # or throw an error w/ a helpful message?
        func = partial(kv_func, func)
        return self.executor(self.funcproc(func)(k, v) for k, v in input)

    @validate_input(list, dict, tuple)
    @execution
    def _flatMapValues(self, func, input):
        if isinstance(input, dict):
            input = input.items()
        func = partial(kv_func, func)

        # perhaps this can be improved
        return [result for result in
                chain(*[[(k, v) for v in vs] for k, vs in
                        self.executor(self.funcproc(func)(*i) for i in input)])]

    @validate_input(list, tuple)
    @execution
    def _reduce(self, func, input):
        output = input[0]
        for i in input[1:]:
            output = func(output, i)
        return output

    @validate_input(list, dict, tuple)
    @execution
    def _reduceByKey(self, func, input):
        if isinstance(input, dict):
            input = input.items()

        results = {}
        for k, v in input:
            try:
                results[k] = func(results[k], v)
            except KeyError:
                results[k] = v
        return list(results.items())

    @execution
    def _fork(self, funcs, input):
        return tuple(self.executor(self.funcproc(func)(input) for func in funcs))

    @execution
    def _forkMap(self, funcs, input):
        return tuple(self.executor(self.funcproc(func)(input) for func in funcs))

    @validate_input(list, tuple)
    @execution
    def _split(self, funcs, input):
        return tuple(self.executor(self.funcproc(f)(i) for f, i in zip(funcs, input)))

    @validate_input(list, tuple)
    @execution
    def _splitMap(self, funcs, input):
        return tuple(self.executor(self.funcproc(f)(i) for f, i in zip(funcs, input)))

    def _serial(self, stream):
        return list(stream)

    def __p(self, func):
        return delayed(func)

    def __s(self, func):
        return func

    @classmethod
    def operators(cls):
        """returns a list of valid operators"""
        return [k for k, v in cls.__dict__.items()
                if not k.startswith('_')
                and not isinstance(v, property)
                and ('composition.<locals>.decorated' in str(v)
                    or 'branching.<locals>.decorated' in str(v))]
