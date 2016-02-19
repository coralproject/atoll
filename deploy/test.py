import sys
import json
import requests
from datetime import datetime

host = sys.argv[1]


data = [{
    '_id': 0,
    'comments': [{
        '_id': 0,
        'user_id': 0,
        'content': 'foo',
        'actions': [
            {'type': 'likes', 'value': 10},
            {'type': 'starred', 'value': False}
        ],
        'status': 3,
        'children': [],
        'date_created': datetime.today().isoformat(),
        'parent_id': None
    }]
}, {
    '_id': 1,
    'comments': [{
        '_id': 1,
        'user_id': 1,
        'content': 'bar',
        'actions': [
            {'type': 'likes', 'value': 20},
            {'type': 'starred', 'value': True}
        ],
        'status': 2,
        'children': [],
        'date_created': datetime.today().isoformat(),
        'parent_id': None
    }]
}]

# if using a self-signed cert, set verify=False. otherwise, it should be verify=True
resp = requests.post('https://{}/pipelines/users/score'.format(host), json={'data':data}, verify=False)

assert resp.status_code == 200
print(json.dumps(resp.json(), sort_keys=True, indent=2))
