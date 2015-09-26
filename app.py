import os
import yaml
import logging.config
from atoll.service import create_app

# setup logging
config_path = 'logging.yaml'
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        conf = yaml.load(f.read())
        logging.config.dictConfig(conf)
else:
    logging.basicConfig(level=logging.INFO)

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
