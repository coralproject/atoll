from flask import Blueprint

bp = Blueprint('errors', __name__)


@bp.app_errorhandler(404)
def not_found(error):
    return 'Not found'


@bp.app_errorhandler(500)
def internal_error(error):
    return 'Internal error'
