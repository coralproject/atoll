import os
import yaml

CONF_BASE = '/etc/atoll/conf'
SERVICE_CONF = {
    'worker_host': 'localhost'
}

service_conf_path = os.path.join(CONF_BASE, 'service.yaml')
if os.path.exists(service_conf_path):
    with open(service_conf_path, 'r') as f:
        SERVICE_CONF.update(yaml.load(f))
