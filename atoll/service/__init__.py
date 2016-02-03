from flask import Flask
from atoll.service import errors


def create_app(package_name=__name__, static_folder='static', template_folder='templates', **config_overrides):
    app = Flask(package_name,
                static_url_path='/static',
                static_folder=static_folder,
                template_folder=template_folder)

    # Apply overrides.
    app.config.update(config_overrides)

    # Register blueprints.
    app.register_blueprint(errors.bp)

    if not app.debug:
        import logging
        fh = logging.FileHandler('/tmp/atoll.log') # TODO use more sensible location
        fh.setLevel(logging.WARNING)
        app.logger.addHandler(fh)

    return app
