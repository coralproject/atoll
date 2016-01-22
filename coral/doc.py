import yaml
import inspect
from flask import Blueprint, jsonify
from .metrics import user, comment, asset

bp = Blueprint('doc', __name__, url_prefix='/doc')


types = {
    'nonnegative': {
        'type': 'range',
        'min': 0,
        'max': None,
        'min_inclusive': True,
        'max_inclusive': False
    },
    'probability': {
        'type': 'range',
        'min': 0,
        'max': 1,
        'min_inclusive': True,
        'max_inclusive': True
    }
}


def prep_metrics(module):
    """extract metric functions from a module"""
    metrics = []
    ignore = ['make'] # funcs to ignore
    for f in dir(module):
        func = getattr(module, f)
        if not f.startswith('_') and f not in ignore \
            and inspect.isfunction(func) \
            and inspect.getmodule(func) == module:
            # parse the metric metadata from its docstring
            # should be yaml
            meta = yaml.load(func.__doc__)
            metric = {
                'name': f,
                'description': meta.get('description'),
                'type': meta.get('type'),
                'valid': types[meta.get('valid')]
            }
            metrics.append(metric)
        else:
            continue
    return metrics

metrics = {
    'user': prep_metrics(user),
    'comment': prep_metrics(comment),
    'asset': prep_metrics(asset),
}

@bp.route('/')
def index():
    return jsonify(metrics=metrics)
