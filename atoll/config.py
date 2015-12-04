
"""
Loads the service configuration.
"""

import os
import yaml

conf = {
    'worker_broker': 'amqp://guest:guest@localhost/',
    'worker_backend': 'amqp',

    # this must be a _prebuilt_ spark archive, i.e. a spark binary package
    # you can build it and host it yourself if you like.
    'spark_binary': 'http://d3kbcqa49mib13.cloudfront.net/spark-1.5.0-bin-hadoop2.6.tgz',
    'zookeeper_host': '172.17.0.1:2181'
}

user_conf_path = os.environ.get('ATOLL_CONF', None)

if user_conf_path is not None:
    with open(user_conf_path, 'r') as f:
        conf.update(yaml.load(f))

namespace = globals()
for k, v in conf.items():
    namespace[k.upper()] = v
