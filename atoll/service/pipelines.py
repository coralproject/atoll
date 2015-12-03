from atoll.service.tasks import pipeline_task
from flask import Blueprint, request, abort, jsonify


def pipeline_blueprint():
    """
    Create the pipeline blueprint.
    (for consistency)
    """
    return Blueprint('pipelines', __name__,
                     url_prefix='/pipelines')


def register_pipeline(endpoint, pl, bp):
    """
    Register a pipeline at the specified endpoint.
    It will be available at `/pipelines/<endpoint>`.
    Pipelines must be registered _before_ the app is created!
    """
    def handler():
        data = request.get_json()
        if 'data' not in data:
            abort(400)
        input = data['data']

        if 'callback' not in data:
            results = pl(input)

            # jsonifying will be a problem, how to coerce into json reliably?
            return jsonify({
                'results': results
            })
        else:
            pipeline_task.delay(pl, input, data['callback'])
            return '', 202
    bp.add_url_rule(endpoint, pl.name, handler, methods=['POST'])
