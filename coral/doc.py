import yaml
import inspect
from flask import Blueprint, jsonify, request
from .metrics import user, comment, asset

bp = Blueprint('doc', __name__, url_prefix='/doc')
supported_languages = ['en', 'de']

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


def prep_metrics(module, lang):
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

            # extract localized description (if one exists)
            # defaults to english, or None if there is no description at all.
            desc = meta.get('description', {})
            desc_local = desc.get(lang, desc.get('en'))

            metric = {
                'name': f,
                'description': desc_local,
                'type': meta.get('type'),
                'valid': types[meta.get('valid')]
            }
            metrics.append(metric)
        else:
            continue
    return metrics


@bp.route('/')
def index():
    lang = request.accept_languages.best_match(supported_languages, default='en')

    metrics = {
        'user': prep_metrics(user, lang),
        'comment': prep_metrics(comment, lang),
        'asset': prep_metrics(asset, lang),
    }

    return jsonify(metrics=metrics)
