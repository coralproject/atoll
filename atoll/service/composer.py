import random
import inspect
from atoll.composer.parser import parse
from atoll.composer.metrics import user
from flask import Blueprint, render_template, request, jsonify

bp = Blueprint('composer', __name__, url_prefix='/composer')


def prep_metrics(module):
    funcs = {}
    colors = {}
    for f in dir(module):
        func = getattr(module, f)
        if inspect.isfunction(func) and inspect.getmodule(func) == module:
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


@bp.route('/')
def index():
    return render_template('composer.html',
                           user_metrics=user_metrics)


class User():
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@bp.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.get_json()
    expr = data['expr']
    users = [User(comments=d) for d in data['users']]

    results, texes, expr_tex = parse(expr, users, user_metrics, user_colors)
    return jsonify(
        results=results,
        texes=texes,
        expr_tex=expr_tex
    )


# temporary
@bp.route('/data')
def data():
    import json
    with open('example_users.json', 'r') as f:
        data = json.load(f)
    return jsonify(users=data)
