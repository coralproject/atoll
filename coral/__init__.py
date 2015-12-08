from functools import partial
from atoll import Atoll, Pipeline
from .metrics.common import merge_dicts
from .metrics import user, comment, asset
from .darwin import bp as darwin_bp

def id_pair_w_key(obj, **kwargs):
    f = kwargs['_func']
    k = kwargs['_key']
    return obj.id, {k: f(obj)}


coral = Atoll()

"""
example input: [{
    'id': 1,
    'comments': [{ ... }]
}, ...]
"""

# TODO add some kind of fork->map support
community_score = Pipeline().map(partial(id_pair_w_key, _func=user.like_score, _key='community_score'))
organization_score = Pipeline().map(partial(id_pair_w_key, _func=user.starred_score, _key='organization_score'))
discuss_score = Pipeline().map(partial(id_pair_w_key, _func=user.discussion_score, _key='discussion_score'))
mod_prob = Pipeline().map(partial(id_pair_w_key, _func=user.moderated_prob, _key='moderation_prob'))

# TODO move this to atoll?
def mergeInKeys(key, data, key_name):
    data.update({key_name: key})
    return data

score_users = Pipeline(name='score_users').map(user.make)\
    .fork(community_score, organization_score, discuss_score, mod_prob)\
    .flatMap(None).reduceByKey(merge_dicts).map(partial(mergeInKeys, key_name='id'))
coral.register_pipeline('/users/score', score_users)

score_comments = Pipeline(name='score_comments').map(comment.make)\
    .map(partial(id_pair_w_key, _func=comment.diversity_score, _key='diversity_score')).map(partial(mergeInKeys, key_name='id'))
coral.register_pipeline('/comments/score', score_comments)

asset_discuss_score = Pipeline().map(partial(id_pair_w_key, _func=asset.discussion_score, _key='discussion_score'))
asset_diversity_score = Pipeline().map(partial(id_pair_w_key, _func=asset.diversity_score, _key='diversity_score'))

score_assets = Pipeline(name='score_assets').map(asset.make)\
    .fork(asset_discuss_score, asset_diversity_score)\
    .flatMap(None).reduceByKey(merge_dicts).map(partial(mergeInKeys, key_name='id'))
coral.register_pipeline('/assets/score', score_assets)

coral.blueprints.append(darwin_bp)
