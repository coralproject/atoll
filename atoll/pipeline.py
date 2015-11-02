import random
import logging
from hashlib import md5
from joblib import Parallel, delayed
from atoll.pipes import Pipe, Branches
from atoll.friendly import get_example

logger = logging.getLogger(__name__)


def composition(f):
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


def execution(f):
    def decorated(self, pipe, input, **kwargs):
        kwargs_ = {}
        for key in pipe.expected_kwargs:
            try:
                kwargs_[key] = kwargs[key]
            except KeyError:
                raise KeyError('Missing expected keyword argument: {}'.format(key))
        return f(self, pipe, input, **kwargs_)
    return decorated


class Pipeline(Pipe):
    def __init__(self, **kwargs):
        self._name = kwargs.get('name', None)
        self.expected_kwargs = []
        self.pipes = []

    def func(self, input, **kwargs):
        return self(input, nested=True, **kwargs)

    def __call__(self, input, n_jobs=1, distributed=False, validate=False, nested=False, **kwargs):
        """
        Specify `validate=True` to first
        check the pipeline with a random sample from the input
        before running on the entire input.
        """
        #if distributed and not nested:
            ## construct proper pipeline
            #pass

        if validate and not nested:
            self.validate(input, n_jobs=n_jobs)

        if nested:
            self.parallel = self._serial
        else:
            self.parallel = Parallel(n_jobs=n_jobs)

        for op, pipe in self.pipes:
            try:
                print('calling', pipe)
                input = getattr(self, '_' + op)(pipe, input, **kwargs)
            except:
                logger.exception('Failed to execute pipe "{}{}"\nInput:\n{}'.format(
                    pipe,
                    pipe.sig,
                    get_example(input)))
                raise

        del self.parallel
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
        return Pipe(func, *args, **kwargs)

    @composition
    def map(self, func, *args, **kwargs):
        return Pipe(func, *args, **kwargs)

    @composition
    def map_dict(self, func, *args, **kwargs):
        return Pipe(func, *args, **kwargs)

    @composition
    def fork(self, *funcs):
        return Branches(funcs)

    @composition
    def split(self, *funcs):
        return Branches(funcs)

    @execution
    def _to(self, pipe, input, **kwargs):
        if not isinstance(input, tuple):
            input = (input,)
        return pipe.func(*input, **kwargs)

    @execution
    def _map(self, pipe, input, **kwargs):
        if not isinstance(input[0], tuple):
            input = [(i,) for i in input]
        return self.parallel(delayed(pipe.func)(*i, **kwargs) for i in input)

    @execution
    def _map_dict(self, pipe, input, **kwargs):
        return self.parallel(delayed(pipe.func)(*i, **kwargs) for i in input.items())

    @execution
    def _fork(self, branches, input, **kwargs):
        return tuple(self.parallel(delayed(b.func)(input, **kwargs) for b in branches))

    @execution
    def _split(self, branches, input, **kwargs):
        return tuple(self.parallel(delayed(b.func)(i, **kwargs) for b, i in zip(branches, input)))

    def _serial(self, stream):
        return [func(*args, **kwargs) for func, args, kwargs in stream]
