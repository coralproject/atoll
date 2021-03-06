import random
import inspect
from ..metrics import user, comment, asset
from .parser import parse
from flask import Blueprint, render_template, request, jsonify

bp = Blueprint('composer', __name__)


def prep_metrics(module):
    """prep a metrics module by collecting its metric functions
    and assigning colors"""
    funcs = {}
    colors = {}
    for f in dir(module):
        func = getattr(module, f)
        if not f.startswith('_') and inspect.isfunction(func) and inspect.getmodule(func) == module:
            color = '#{:02X}{:02X}{:02X}'.format(
                random.randint(0,255),
                random.randint(0,255),
                random.randint(0,255)
            )
            funcs[f] = getattr(module, f)
            colors[f] = color
        else:
            continue
    return funcs, colors


user_metrics, user_colors = prep_metrics(user)
comment_metrics, comment_colors = prep_metrics(comment)
asset_metrics, asset_colors = prep_metrics(asset)

# list for consistent ordering
metrics = [
    ('user_metrics', user_metrics),
    ('comment_metrics', comment_metrics),
    ('asset_metrics', asset_metrics)
]


@bp.route('/')
def index():
    return render_template('composer.html', metrics=metrics)


@bp.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.get_json()
    expr = data['expr']
    users = data['users']

    results, texes, expr_tex = parse(expr, users, user_metrics, user_colors)
    return jsonify(
        results=results,
        texes=texes,
        expr_tex=expr_tex
    )


# mock data endpoint
@bp.route('/data')
def data():
    id = int(request.args['id'])
    # TODO get user by id
    # for now, reutrn nothing
    return jsonify(results={})
