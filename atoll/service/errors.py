from flask import Blueprint, jsonify

bp = Blueprint('errors', __name__)


@bp.app_errorhandler(404)
def not_found(error):
    return 'Not found', 404


@bp.app_errorhandler(500)
def internal_error(error):
    """return more helpful info on 500"""
    data = {
        'type': type(error).__name__,
        'message': str(error)
    }
    if hasattr(error, 'data'):
        data['data'] = error.data

    return jsonify(data), 500


@bp.app_errorhandler(400)
def bad_request(error):
    return 'Bad request', 400
