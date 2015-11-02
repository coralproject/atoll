import yaml
import importlib
from atoll.pipeline import Pipeline
from atoll.service.pipelines import register_pipeline


def load_pipeline_conf(path):
    """Loads a pipelines yaml config"""
    with open(path, 'r') as f:
        conf = yaml.load(f)
    for endpoint, pipeline in parse_pipelines(conf):
        register_pipeline(endpoint, pipeline)


def parse_pipeline(name, pipes, pipelines):
    """
    Parse a pipeline; other pipeline configs
    are passed in as `pipelines` to handle nested pipelines.
    """
    pipes = [parse_pipe(p, pipelines=pipelines) for p in pipes]
    return Pipeline(pipes, name=name)


def parse_pipe(pipe, pipelines={}):
    """Parse a pipe from a config"""
    if isinstance(pipe, str):
        if pipe in pipelines:
            return parse_pipeline(pipe, pipelines[pipe]['pipeline'], pipelines)
        else:
            func = import_pipe(pipe)
            if isinstance(func, type):
                func = func()
            if not callable(func):
                raise TypeError('Pipes must be callable')
            return func

    elif isinstance(pipe, dict):
        if 'branch' in pipe:
            return parse_pipe(pipe['branch'])

        (pipe, args), = pipe.items()
        func = import_pipe(pipe)

        if isinstance(func, type):
            func = func(**args)
        if not callable(func):
            raise TypeError('Pipes must be callable')
        #TODO this doesnt support args/kwargs for funcs
        return func

    elif isinstance(pipe, list):
        return tuple(parse_pipe(p) for p in pipe)


def import_pipe(pipe):
    """Import a pipe based on a module string"""
    mod, func_name = pipe.rsplit('.', 1)
    mod = importlib.import_module(mod)
    return getattr(mod, func_name)


def parse_pipelines(conf):
    """Parses a config"""
    pipelines = []
    for name, cfg in conf.items():
        endpoint = cfg['endpoint']
        pipeline = parse_pipeline(name, cfg['pipeline'], conf)
        pipelines.append((endpoint, pipeline))
    return pipelines
