from flask import Blueprint, jsonify
from .metrics import MetricException

bp = Blueprint('coral_errors', __name__)


@bp.app_errorhandler(MetricException)
def metric_exception(error):
    resp = {
        'metric': error.metric,
        'type': error.type,
        'message': error.message,
        'data': error.data
    }
    return jsonify(resp), 500
