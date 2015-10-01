import yaml
import importlib
from atoll import Pipeline, register_pipeline
from atoll.pipeline import MetaPipe


def load_conf(path):
    """Loads a yaml config"""
    with open(path, 'r') as f:
        conf = yaml.load(f)
    return parse_conf(conf)


def parse_pipe(pipe):
    """Parse a pipe from a config"""
    if isinstance(pipe, str):
        pipe_cls = import_pipe(pipe)
        return pipe_cls()

    elif isinstance(pipe, dict):
        if 'branch' in pipe:
            return parse_pipe(pipe['branch'])

        (pipe, args), = pipe.items()
        pipe_cls = import_pipe(pipe)
        return pipe_cls(**args)

    elif isinstance(pipe, list):
        return tuple(parse_pipe(p) for p in pipe)


def import_pipe(pipe):
    """Import a pipe based on a module string"""
    mod, cls = pipe.rsplit('.', 1)
    mod = importlib.import_module(mod)
    pipe_cls = getattr(mod, cls)
    if type(pipe_cls) is not MetaPipe:
        raise TypeError('Pipes must subclass atoll.Pipe')
    return pipe_cls


def parse_conf(conf):
    """Parses a config"""
    pipelines = []
    for name, cfg in conf.items():
        endpoint = cfg['endpoint']
        pipes = [parse_pipe(p) for p in cfg['pipeline']]
        pipeline = Pipeline(pipes, name=name)
        register_pipeline(endpoint, pipeline)
        pipelines.append((endpoint, pipeline))
    return pipelines
