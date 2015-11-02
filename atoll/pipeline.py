import random
import logging
from hashlib import md5
import atoll.pipes as p
from atoll.friendly import get_example

logger = logging.getLogger(__name__)


class Pipeline(p._pipe):
    def __init__(self, pipes=[], **kwargs):
        self.__n_jobs = kwargs.get('n_jobs', 0)
        self._name = kwargs.get('name', None)
        self.expected_kwargs = []

        # TODO add distributed support
        self.distributed = False
        if self.distributed:
            raise Exception('distributed computing not yet supported')

        self.pipes = []
        for pipe in pipes:
            self.to(pipe)

    def __call__(self, input, validate=False, **kwargs):
        """
        Specify `validate=True` to first
        check the pipeline with a random sample from the input
        before running on the entire input.
        """
        if validate:
            self.validate(input)

        for pipe in self.pipes:
            try:
                output = pipe(input, **kwargs)
            except:
                logger.exception('Failed to execute pipe "{}{}"\nInput:\n{}'.format(pipe,
                                                                                    pipe.sig,
                                                                                    get_example(input)))
                raise
            input = output
        return output


    @property
    def n_jobs(self):
        return self.__n_jobs

    @n_jobs.setter
    def n_jobs(self, val):
        self.__n_jobs = val
        for pipe in self.pipes:
            pipe.n_jobs = val

    def __repr__(self):
        return ' -> '.join([str(pipe) for pipe in self.pipes])

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
        return md5('->'.join([str(pipe) for pipe in self.pipes]).encode('utf-8')).hexdigest()

    def validate(self, data, n=1):
        """
        Approximately validate the pipeline
        using a "canary" method, i.e. compute on
        a random sample and see if it doesn't break.

        Does not guarantee that the pipeline will run
        without error, but a good approximation.
        """
        sample = random.sample(data, n)
        self(sample, validate=False)

    # Pipeline composition methods
    def to(self, func, *args, **kwargs):
        assert((not isinstance(func, type)) and (callable(func)))

        self.expected_kwargs += kwargs.get('kwargs', [])

        if not isinstance(func, p._pipe) \
                and not isinstance(func, p._branches):
            self.pipes.append(p._pipe(0, func, *args, **kwargs))
        else:
            self.pipes.append(func)
        return self

    def map(self, func, *args, **kwargs):
        return self.to(p._map(self.n_jobs, func, *args, **kwargs), **kwargs)

    def map_dict(self, func, *args, **kwargs):
        return self.to(p._map_dict(self.n_jobs, func, *args, **kwargs), **kwargs)

    def fork(self, *funcs):
        return self.to(p._fork(self.n_jobs, funcs))

    def split(self, *funcs):
        return self.to(p._split(self.n_jobs, funcs))
