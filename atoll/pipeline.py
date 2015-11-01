import logging
from hashlib import md5
import atoll.pipes as p

logger = logging.getLogger(__name__)


def get_example(input):
    """
    Produce an "example" out of some input.
    """
    if isinstance(input, tuple):
        return '({})'.format(','.join('{}'.format(get_example(i)) for i in input))
    if isinstance(input, dict):
        return '{{{}}}'.format(','.join('{}:{}'.format(k, get_example(v)) for k, v in input.items()))
    if hasattr(input, '__iter__') and not isinstance(input, str):
        example = next(iter(input))
        return '[{},...]'.format(get_example(example))
    else:
        example = input
    return str(example)


class Pipeline():
    def __init__(self, pipes=[], **kwargs):
        self.__n_jobs = kwargs.get('n_jobs', 0)
        self._name = kwargs.get('name', None)

        # TODO add distributed support
        self.distributed = False
        if self.distributed:
            raise Exception('distributed computing not yet supported')

        self.pipes = []
        for pipe in pipes:
            self.to(pipe)

    def __call__(self, input):
        for pipe in self.pipes:
            try:
                output = pipe(input)
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

    # Pipeline composition methods
    def to(self, func, *args, **kwargs):
        assert((not isinstance(func, type)) and (callable(func)))
        if not isinstance(func, p._pipe) \
                and not isinstance(func, p._branches):
            self.pipes.append(p._pipe(0, func, *args, **kwargs))
        else:
            self.pipes.append(func)
        return self

    def map(self, func, *args, **kwargs):
        return self.to(p._map(self.n_jobs, func, *args, **kwargs))

    def map_dict(self, func, *args, **kwargs):
        return self.to(p._map_dict(self.n_jobs, func, *args, **kwargs))

    def fork(self, *funcs):
        return self.to(p._fork(self.n_jobs, funcs))

    def split(self, *funcs):
        return self.to(p._split(self.n_jobs, funcs))
