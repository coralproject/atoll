from functools import partial
from atoll import Atoll, Pipeline
from .metrics.common import merge_dicts
from .metrics import user, comment, asset


coral = Atoll()

"""
example input: [{
    'id': 1,
    'comments': [{ ... }]
}, ...]
"""

# TODO add some kind of fork->map support
community_score = Pipeline().map(user.like_score)
organization_score = Pipeline().map(user.starred_score)
discuss_score = Pipeline().map(user.discussion_score)
mod_prob = Pipeline().map(user.moderated_prob)

# TODO move this to atoll?
def mergeInKeys(key, data, key_name):
    data.update({key_name: key})
    return data

score_users = Pipeline(name='score_users').map(user.make_user)\
    .fork(community_score, organization_score, discuss_score, mod_prob)\
    .flatMap(None).reduceByKey(merge_dicts).map(partial(mergeInKeys, key_name='id'))
coral.register_pipeline('/users/score', score_users)

score_comments = Pipeline(name='score_comments').map(comment.make_comment)\
    .map(comment.diversity_score).map(partial(mergeInKeys, key_name='id'))
coral.register_pipeline('/comments/score', score_comments)

asset_discuss_score = Pipeline().map(asset.discussion_score)
asset_diversity_score = Pipeline().map(asset.diversity_score)

score_assets = Pipeline(name='score_assets').map(asset.make_asset)\
    .fork(asset_discuss_score, asset_diversity_score)\
    .flatMap(None).reduceByKey(merge_dicts).map(partial(mergeInKeys, key_name='id'))
coral.register_pipeline('/assets/score', score_assets)
