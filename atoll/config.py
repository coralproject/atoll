
"""
Loads the service configuration.
"""

import os
import yaml

conf = {
    'worker_broker': 'amqp://guest:guest@localhost/',
    'worker_backend': 'amqp',
    'executor_host': '127.0.0.1:8786'
}

user_conf_path = os.environ.get('ATOLL_CONF', None)

if user_conf_path is not None:
    with open(user_conf_path, 'r') as f:
        conf.update(yaml.load(f))

namespace = globals()
for k, v in conf.items():
    namespace[k.upper()] = v
