import json
import unittest
from coral import coral
from atoll.service.tasks import celery

# force celery to be synchronous for testing
celery.conf.update(CELERY_ALWAYS_EAGER=True)

test_config = {
    'TESTING': True
}

class ServiceTest(unittest.TestCase):
    def setUp(self):
        self.app = coral.create_app(**test_config)
        self.client = self.app.test_client()
        self.counter = 0

    def tearDown(self):
        self.app = None

    def _call_pipeline(self, endpoint, data):
        headers = [('Content-Type', 'application/json')]
        return self.client.post('/pipelines/{}'.format(endpoint),
                                 data=json.dumps({'data': data}),
                                 headers=headers)

    def _make_comment(self, n_replies=0, depth=1):
        if depth == 0:
            n_replies = 0

        self.counter += 1
        return {
            'id': self.counter,
            'likes': 10,
            'starred': False,
            'moderated': True,
            'parent_id': None,
            'content': 'foo',
            'replies': [self._make_comment(n_replies=n_replies, depth=depth-1) for _ in range(n_replies)]
        }

    def test_users_score(self):
        data = [{
            'id': 0,
            'comments': [self._make_comment()]
        }, {
            'id': 1,
            'comments': [self._make_comment()]
        }]

        resp = self._call_pipeline('users/score', data)
        self.assertEquals(resp.status_code, 200)

        resp_json = json.loads(resp.data.decode('utf-8'))

        expected = {
            'id': int,
            'community_score': float,
            'discussion_score': float,
            'moderation_prob': float,
            'organization_score': float
        }
        for result in resp_json['results']:
            for k, t in expected.items():
                self.assertTrue(isinstance(result[k], t))

    def test_comments_score(self):
        data = [
            self._make_comment(),
            self._make_comment()
        ]

        resp = self._call_pipeline('comments/score', data)
        self.assertEquals(resp.status_code, 200)

        resp_json = json.loads(resp.data.decode('utf-8'))

        expected = {
            'id': int,
            'diversity_score': float,
        }
        for result in resp_json['results']:
            for k, t in expected.items():
                self.assertTrue(isinstance(result[k], t))
