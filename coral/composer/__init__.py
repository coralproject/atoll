from flask import Flask
from . import routes


def create_app(package_name=__name__, static_folder='static', template_folder='templates', **config_overrides):
    """create the composer flask app"""
    app = Flask(package_name,
                static_url_path='/static',
                static_folder=static_folder,
                template_folder=template_folder)

    # Apply overrides.
    app.config.update(config_overrides)

    # Register blueprints.
    app.register_blueprint(routes.bp)

    return app
