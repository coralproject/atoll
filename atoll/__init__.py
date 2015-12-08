from atoll.pipeline import Pipeline
from atoll.service import create_app
from atoll.service.pipelines import register_pipeline, pipeline_blueprint


class Atoll():
    def __init__(self):
        self.pipeline_bp = pipeline_blueprint()
        self.blueprints = []

    def register_pipeline(self, endpoint, pipeline):
        """
        Register a pipeline at the specified endpoint.
        It will be available at `/pipelines/<endpoint>`.
        Pipelines must be registered _before_ the app is created!
        """
        register_pipeline(endpoint, pipeline, self.pipeline_bp)

    def create_app(self, **app_config):
        self.app = create_app(**app_config)
        self.app.register_blueprint(self.pipeline_bp)
        for bp in self.blueprints:
            self.app.register_blueprint(bp)
        return self.app

    def run(self, port=5001, debug=False):
        self.app.run(debug=debug, port=port)
