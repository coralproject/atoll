from flask import Blueprint

bp = Blueprint('errors', __name__)


@bp.app_errorhandler(404)
def not_found(error):
    return 'Not found', 404


@bp.app_errorhandler(500)
def internal_error(error):
    return 'Internal error', 500


@bp.app_errorhandler(400)
def bad_request(error):
    return 'Bad request', 400
