import inspect
from atoll import Pipeline
from atoll.service.tasks import pipeline_task
from .composer.parser.function import parse_func
from .metrics import user, comment, asset
from flask import Blueprint, request, jsonify

bp = Blueprint('darwin', __name__, url_prefix='/darwin')

def prep_metrics(module):
    """prep a metrics module by collecting its metric functions"""
    funcs = {}
    for f in dir(module):
        func = getattr(module, f)
        if inspect.isfunction(func) and inspect.getmodule(func) == module:
            funcs[f] = getattr(module, f)
        else:
            continue
    return funcs

domains = {mod.__name__.split('.')[-1]: mod for mod in [user, comment, asset]}
domain_names = list(domains.keys())


@bp.route('/<domain>', methods=['POST'])
def darwin(domain):
    if domain not in domain_names:
        return 'The domain "{}" was not found.'.format(domain), 404

    data = request.get_json()
    if 'data' not in data:
        return 'The POSTed JSON data is missing the "data" key.', 400
    input = data['data']

    if 'expr' not in data:
        return 'The POSTed JSON data is missing the "expr" key.', 400

    mod = domains[domain]
    mod_funcs = prep_metrics(mod)
    mod_names = list(mod_funcs.keys())

    try:
        func = parse_func(data['expr'], whitelist=mod_names, locals=mod_funcs)
    except ValueError as e:
        return str(e), 400

    pipeline = Pipeline().map(func)

    if 'callback' not in data:
        # execute serially because pickle cannot serialize
        # dynamically defined functions
        results = pipeline(input, serial=True)

        # jsonifying will be a problem, how to coerce into json reliably?
        return jsonify({
            'results': results
        })
    else:
        pipeline_task.delay(pipeline, input, data['callback'])
        return 'Pipeline job queued.', 202
