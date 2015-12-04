from functools import partial
from atoll import Atoll, Pipeline
from .metrics.common import merge_dicts
from .metrics.user import make_user, like_score, starred_score, discussion_score, moderated_prob
from .metrics.comment import make_comment, diversity_score


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

# TODO move this to atoll?
def mergeInKeys(key, data, key_name):
    data.update({key_name: key})
    return data

score_users = Pipeline(name='score_users').map(make_user)\
    .fork(community_score, organization_score, discuss_score, mod_prob)\
    .flatMap(None).reduceByKey(merge_dicts).map(partial(mergeInKeys, key_name='id'))
coral.register_pipeline('/users/score', score_users)

score_comments = Pipeline(name='score_comments').map(make_comment)\
    .map(diversity_score).map(partial(mergeInKeys, key_name='id'))
coral.register_pipeline('/comments/score', score_comments)
