"""
quick stop-gap hardcoded endpoint for getting metric documentation
"""

from flask import Blueprint, jsonify

bp = Blueprint('doc', __name__, url_prefix='/doc')

@bp.route('/')
def index():
    return jsonify(metrics=[{
        'name': 'diversity_score',
        'entity': 'comment',
        'description': 'Probability that a new reply would be from a new user.',
        'type': 'float',
        'valid': {
            'type': 'range',
            'min': 0,
            'max': 1,
            'min_inclusive': True,
            'max_inclusive': True
        }
    }, {
        'name': 'community_score',
        'entity': 'user',
        'description': 'Estimated number of likes a comment by this user will get.',
        'type': 'float',
        'valid': {
            'type': 'range',
            'min': 0,
            'max': None,
            'min_inclusive': True,
            'max_inclusive': False
        }
    }])
