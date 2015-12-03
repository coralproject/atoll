from atoll import Atoll, Pipeline
from .metrics.common import merge_dicts
from .metrics.user import make_user, like_score, starred_score, discussion_score, moderated_prob


coral = Atoll()

"""
example input: [{
    'id': 1,
    'comments': [{ ... }]
}, ...]
"""

# TODO add some kind of fork->map support
community_score = Pipeline().map(like_score)
organization_score = Pipeline().map(starred_score)
discuss_score = Pipeline().map(discussion_score)
mod_prob = Pipeline().map(moderated_prob)

# TODO clean this up
def assemble(id, data):
    data.update({'id': id})
    return data

score_users = Pipeline(name='score_users').map(make_user)\
    .fork(community_score, organization_score, discuss_score, mod_prob)\
    .flatMap(None).reduceByKey(merge_dicts).map(assemble)

coral.register_pipeline('/users/score', score_users)

