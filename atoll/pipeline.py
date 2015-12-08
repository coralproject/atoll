import random
import logging
from hashlib import md5
from itertools import chain
from functools import partial
from joblib import Parallel, delayed
from atoll.pipes import Pipe, Branches
from atoll.friendly import get_example
from atoll.distrib import spark_context, is_rdd


logger = logging.getLogger(__name__)


def composition(f):
    """decorates a function which builds the pipeline,
    i.e. a function that adds a new pipe"""
    def decorated(self, func, *args, **kwargs):
        assert ((not isinstance(func, type)) and callable(func)) or func is None, 'Pipes must be callable'

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
            assert func is None or isinstance(func, Pipeline), 'Fork branches must be pipelines'
        branches = f(self, funcs)
        self.expected_kwargs += branches.expected_kwargs
        self.pipes.append((f.__name__, branches))
        return self
    return decorated


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
        return partial(pipe.func, **kwargs_)

def kv_func(f, k, v):
    """helper to apply function `f` to value `v`"""
    return k, f(v)

def execution(f):
    """decorates the function which executes a corresponding pipe"""
    def decorated(self, pipe, input, **kwargs):
        func = prep_func(pipe, **kwargs)
        return f(self, func, input)
    return decorated


class Pipeline(Pipe):
    def __init__(self, **kwargs):
        self._name = kwargs.get('name', None)
        self.expected_kwargs = []
        self.pipes = []

    def func(self, input, distributed=False, **kwargs):
        """
        Used if the pipeline is nested in another.
        This prevents nested pipelines from running their own parallel processes.
        """
        return self(input, distributed=distributed, nested=True, **kwargs)

    def __call__(self, input, n_jobs=1, serial=False, distributed=False, validate=False, nested=False, **kwargs):
        """
        Specify `validate=True` to first
        check the pipeline with a random sample from the input
        before running on the entire input.
        """
        if validate and not nested:
            self.validate(input, n_jobs=n_jobs)

        if distributed:
            rdd = input
            # create RDD from input if necessary
            if not is_rdd(input):
                sc = spark_context(self.name)
                n_jobs = None if n_jobs <= 0 else n_jobs
                rdd = sc.parallelize(input, n_jobs)

            # run the pipes
            for op, pipe in self.pipes:
                func = prep_func(pipe, **kwargs)
                if op == 'fork':
                    # cache the current RDD
                    rdd.cache()

                    # bleh, build out each branch as an RDD,
                    # then we have to (afaik) collect their results
                    # then build a new rdd out of that
                    rdds = [branch(rdd, distributed=True) for branch in func]
                    rdd = sc.parallelize([r.collect() if is_rdd(r) else r for r in rdds], n_jobs)
                elif op == 'to':
                    # the `to` operation requires the resulting dataset
                    # so we have to collect the results (if necessary)
                    # we don't create the new RDD, we'll let the next
                    # iteration do so if necessary
                    rdd = self._to(pipe, rdd.collect() if is_rdd(rdd) else rdd, **kwargs)
                else:
                    rdd = getattr(rdd, op)(func)
            return rdd.collect() if is_rdd(rdd) else rdd

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
                except:
                    logger.exception('Failed to execute pipe "{}{}"\nInput:\n{}'.format(
                        pipe,
                        pipe.sig,
                        get_example(input)))
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

    def validate(self, data, n_jobs=1, n=1):
        """
        Approximately validate the pipeline
        using a "canary" method, i.e. compute on
        a random sample and see if it doesn't break.

        Does not guarantee that the pipeline will run
        without error, but a good approximation.
        """
        sample = random.sample(data, n)
        self(sample, n_jobs=n_jobs, validate=False)

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
        return Branches(funcs)

    # execution methods just take care of execution of the pipes
    # produced by the above composition/branching methods

    @execution
    def _to(self, func, input):
        if not isinstance(input, tuple):
            input = (input,)
        return func(*input)

    @execution
    def _map(self, func, input):
        if not isinstance(input[0], tuple):
            input = [(i,) for i in input]
        return self.executor(self.funcproc(func)(*i) for i in input)

    @execution
    def _flatMap(self, func, input):
        if not isinstance(input[0], tuple):
            input = [(i,) for i in input]
        return [result for result in chain(*self.executor(self.funcproc(func)(*i) for i in input))]

    @execution
    def _mapValues(self, func, input):
        if isinstance(input, dict):
            input = input.items()
        # TODO should we handle dicts like this?
        # or throw an error w/ a helpful message?
        func = partial(kv_func, func)
        return self.executor(self.funcproc(func)(k, v) for k, v in input)

    @execution
    def _flatMapValues(self, func, input):
        if isinstance(input, dict):
            input = input.items()
        func = partial(kv_func, func)

        # perhaps this can be improved
        return [result for result in
                chain(*[[(k, v) for v in vs] for k, vs in
                        self.executor(self.funcproc(func)(*i) for i in input)])]

    @execution
    def _reduce(self, func, input):
        output = input[0]
        for i in input[1:]:
            output = func(output, i)
        return output

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

    def _serial(self, stream):
        return list(stream)

    def __p(self, func):
        return delayed(func)

    def __s(self, func):
        return func
