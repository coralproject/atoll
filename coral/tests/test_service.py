import json
import unittest
from datetime import datetime
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

    def _check_aggregates(self, agg):
        expected = {
            'max': float,
            'min': float,
            'mean': float,
            'std': float,
            'count': int
        }
        for k, t in expected.items():
            self.assertTrue(isinstance(agg[k], t))

    def _make_comment(self, n_replies=0, depth=1, **kwargs):
        if depth == 0:
            n_replies = 0

        self.counter += 1
        data = {
            '_id': self.counter,
            'user_id': self.counter,
            'starred': False,
            'status': 3, # rejected
            'parent_id': None,
            'body': 'Ours is a world in vertigo. It is a world that swarms with technological mediation, interlacing our daily lives with abstraction, virtuality, and complexity. XF constructs a feminism adapted to these realities: a feminism of unprecedented cunning, scale, and vision; a future in which the realization of gender justice and feminist emancipation contribute to a universalist politics assembled from the needs of every human, cutting across race, ability, economic standing, and geographical position.  No more futureless repetition on the treadmill of capital, no more submission to the drudgery of labour, productive and reproductive alike, no more reification of the given masked as critique.  Our future requires depetrification.  XF is not a bid for revolution, but a wager on the long game of history, demanding imagination, dexterity and persistence. ',
            'date_created': datetime.today().isoformat(),
            'children': [self._make_comment(n_replies=n_replies, depth=depth-1) for _ in range(n_replies)],
            'actions': [{
                'value': 10,
                'type': 'likes'
            }]
        }
        data.update(kwargs)
        return data

    def _flatten_thread(self, comments, parent_id=None):
        for comment in comments:
            if comment['children']:
                yield from self._flatten_thread(comment['children'], parent_id=comment['_id'])
            del comment['children']
            comment['parent_id'] = parent_id
            yield comment

    def test_users_score(self):
        data = [{
            '_id': 0,
            'comments': [self._make_comment()]
        }, {
            '_id': 1,
            'comments': [self._make_comment()]
        }]

        resp = self._call_pipeline('users/score', data)
        self.assertEquals(resp.status_code, 200)

        expected = {
            'id': int,
            'community_score': float,
            'discussion_score': float,
            'moderation_prob': float,
            'organization_score': float
        }
        resp_json = json.loads(resp.data.decode('utf-8'))
        for result in resp_json['results']['collection']:
            for k, t in expected.items():
                self.assertTrue(isinstance(result[k], t))
        for k, agg in resp_json['results']['aggregates'].items():
            self._check_aggregates(agg)

    def test_users_rolling(self):
        data = [{
            '_id': 0,
            'update': {
                'comments': [self._make_comment()]
            },
            'prev': {
                'community_score': 1.,
                'discussion_score': 1.,
                'moderation_prob': 0.,
                'organization_score': 1.
            }
        }, {
            '_id': 1,
            'update': {
                'comments': [self._make_comment()]
            },
            'prev': {
                'community_score': 1.,
                'discussion_score': 1.,
                'moderation_prob': 0.,
                'organization_score': 1.
            }
        }]

        resp = self._call_pipeline('users/rolling', data)
        self.assertEquals(resp.status_code, 200)

        expected = {
            'id': int,
            'community_score': float,
            'discussion_score': float,
            'moderation_prob': float,
            'organization_score': float
        }
        resp_json = json.loads(resp.data.decode('utf-8'))
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

        expected = {
            'id': int,
            'diversity_score': float,
            'readability_scores': dict
        }
        resp_json = json.loads(resp.data.decode('utf-8'))
        for result in resp_json['results']['collection']:
            for k, t in expected.items():
                self.assertTrue(isinstance(result[k], t))
        for k, agg in resp_json['results']['aggregates'].items():
            self._check_aggregates(agg)

    def test_assets_score(self):
        data = [{
            '_id': 0,
            'threads': [
                self._make_comment(n_replies=2, depth=2),
                self._make_comment(n_replies=2, depth=2)
            ]
        }, {
            '_id': 1,
            'threads': [
                self._make_comment(n_replies=2, depth=2),
                self._make_comment(n_replies=2, depth=2)
            ]
        }]

        # flatten threads
        for asset in data:
            threads = asset['threads']
            del asset['threads']
            asset['comments'] = [c for c in self._flatten_thread(threads)]

        resp = self._call_pipeline('assets/score', data)
        self.assertEquals(resp.status_code, 200)

        expected = {
            'id': int,
            'diversity_score': float,
            'discussion_score': float,
        }
        resp_json = json.loads(resp.data.decode('utf-8'))
        for result in resp_json['results']['collection']:
            for k, t in expected.items():
                self.assertTrue(isinstance(result[k], t))
        for k, agg in resp_json['results']['aggregates'].items():
            self._check_aggregates(agg)

    def test_comments_score_by_taxonomy(self):
        data = [
            self._make_comment(),
            self._make_comment()
        ]
        data[0]['taxonomy'] = 'section:politics;author:Foo Bar'
        data[1]['taxonomy'] = 'section:politics;author:Sup Yo'

        resp = self._call_pipeline('comments/score/taxonomy', data)
        self.assertEquals(resp.status_code, 200)

        expected_tags = ['section:politics', 'author:Foo Bar', 'author:Sup Yo']
        expected_keys = ['diversity_score', 'readability_scores.ari',
                         'readability_scores.coleman_liau_index', 'readability_scores.flesch_reading_ease',
                         'readability_scores.rix', 'readability_scores.smog_index',
                         'readability_scores.gunning_fog_index', 'readability_scores.flesch_kincaid_grade_level',
                         'readability_scores.lix']
        resp_json = json.loads(resp.data.decode('utf-8'))
        results = resp_json['results']

        for tag in expected_tags:
            for key in expected_keys:
                self._check_aggregates(results[tag][key])

    def test_assets_score_by_taxonomy(self):
        data = [{
            '_id': 0,
            'threads': [
                self._make_comment(n_replies=2, depth=2),
                self._make_comment(n_replies=2, depth=2)
            ]
        }, {
            '_id': 1,
            'threads': [
                self._make_comment(n_replies=2, depth=2),
                self._make_comment(n_replies=2, depth=2)
            ]
        }]

        # flatten threads
        for asset in data:
            threads = asset['threads']
            del asset['threads']
            asset['comments'] = [c for c in self._flatten_thread(threads)]

        data[0]['taxonomy'] = 'section:politics;author:Foo Bar'
        data[1]['taxonomy'] = 'section:politics;author:Sup Yo'

        resp = self._call_pipeline('assets/score/taxonomy', data)
        self.assertEquals(resp.status_code, 200)

        expected_tags = ['section:politics', 'author:Foo Bar', 'author:Sup Yo']
        expected_keys = ['diversity_score', 'discussion_score']
        resp_json = json.loads(resp.data.decode('utf-8'))
        results = resp_json['results']

        for tag in expected_tags:
            for key in expected_keys:
                self._check_aggregates(results[tag][key])

    def test_train_and_run_comments_model(self):
        comments = [self._make_comment(status=2, body='THIS IS GOOD') for _ in range(50)]
        comments += [self._make_comment(status=3, body='THIS IS MALICIOUS') for _ in range(50)]
        data = {
            'samples': comments,
            'name': 'test_model'
        }

        # training the model
        resp = self._call_pipeline('comments/model/moderation/train', data)
        self.assertEquals(resp.status_code, 200)

        expected = {
            'name': str,
            'notes': list,
            'performance': dict,
            'n_samples': int
        }
        resp_json = json.loads(resp.data.decode('utf-8'))
        for k, v in resp_json['results'].items():
            self.assertTrue(isinstance(v, expected[k]))

        # running the model
        resp = self._call_pipeline('comments/model/moderation/run', data)
        self.assertEquals(resp.status_code, 200)

        expected = {
            'id': int,
            'prob': float
        }
        resp_json = json.loads(resp.data.decode('utf-8'))
        for result in resp_json['results']:
            for k, t in expected.items():
                self.assertTrue(isinstance(result[k], t))
