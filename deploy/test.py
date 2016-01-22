import json
import requests
from datetime import datetime


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

resp = requests.post('http://10.0.4.21/pipelines/users/score', json={'data':data})

assert resp.status_code == 200
print(json.dumps(resp.json(), sort_keys=True, indent=2))
