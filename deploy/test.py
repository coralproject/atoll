import sys
import json
import requests
from datetime import datetime

host = sys.argv[1]


data = [{
    'id': 0,
    'comments': [{
        'id': 0,
        'user_id': 0,
        'content': 'foo',
        'likes': 10,
        'starred': False,
        'moderated': True,
        'children': [],
        'date_created': datetime.today().isoformat(),
        'parent_id': None
    }]
}, {
    'id': 1,
    'comments': [{
        'id': 1,
        'user_id': 1,
        'content': 'bar',
        'likes': 20,
        'starred': True,
        'moderated': False,
        'children': [],
        'date_created': datetime.today().isoformat(),
        'parent_id': None
    }]
}]

# if using a self-signed cert, set verify=False. otherwise, it should be verify=True
resp = requests.post('https://{}/pipelines/users/score'.format(host), json={'data':data}, verify=False)

assert resp.status_code == 200
print(json.dumps(resp.json(), sort_keys=True, indent=2))
