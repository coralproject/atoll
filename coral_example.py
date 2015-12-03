import requests

users = [{
    'id': 0,
    'comments': [{
        'id': 0,
        'content': 'foo',
        'likes': 10,
        'starred': False,
        'moderated': True,
        'replies': []
    }]
}, {
    'id': 1,
    'comments': [{
        'id': 1,
        'content': 'bar',
        'likes': 20,
        'starred': True,
        'moderated': False,
        'replies': []
    }]
}]

r = requests.post('http://localhost:5001/pipelines/users/score', json={'data': users})
print(r.json())
