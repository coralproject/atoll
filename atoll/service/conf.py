import os
import yaml
import importlib
from atoll.pipeline import Pipeline, MetaPipe
from atoll.service.pipelines import register_pipeline

CONF_BASE = '/etc/atoll/conf'
SERVICE_CONF = {
    'worker_host': 'localhost'
}

service_conf_path = os.path.join(CONF_BASE, 'service.yaml')
if os.path.exists(service_conf_path):
    with open(service_conf_path, 'r') as f:
        SERVICE_CONF.update(yaml.load(f))


def load_pipeline_conf(path):
    """Loads a pipelines yaml config"""
    with open(path, 'r') as f:
        conf = yaml.load(f)
    return parse_pipelines(conf)


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


def parse_pipelines(conf):
    """Parses a config"""
    pipelines = []
    for name, cfg in conf.items():
        endpoint = cfg['endpoint']
        pipeline = parse_pipeline(name, cfg['pipeline'], conf)
        register_pipeline(endpoint, pipeline)
        pipelines.append((endpoint, pipeline))
    return pipelines
