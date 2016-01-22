from functools import partial
from atoll import Atoll, Pipeline
from .metrics import user, comment, asset, apply_metric, merge_dicts, assign_id, group_by_taxonomy


coral = Atoll()

# users
score_users = Pipeline(name='score_users').map(user.make)\
    .forkMap(
        partial(apply_metric, metric=user.community_score),
        partial(apply_metric, metric=user.organization_score),
        partial(apply_metric, metric=user.discussion_score),
        partial(apply_metric, metric=user.moderation_prob),
    ).flatMap()\
    .reduceByKey(merge_dicts).map(assign_id)
coral.register_pipeline('/users/score', score_users)


from collections import defaultdict
def compute_means(inputs):
    """computes means for a set of taxonomy-tagged inputs
    `inputs` is something like:
        [('world', [{'some_metric': 0.1}, {'some_metric': 0.5}, ...]),
         ('sports', [{'some_metric': 0.1}, {'some_metric': 0.5}, ...]),
         ...]
    """
    means = {}
    for taxonomy, items in inputs:
        means[taxonomy] = defaultdict(list)
        for item in items:
            for k, v in item.items():
                if k != 'id':
                    k = 'mean_{}'.format(k)
                    means[taxonomy][k].append(v)
        for metric, vals in means[taxonomy].items():
            means[taxonomy][metric] = sum(vals)/len(vals)
    return means

score_users_by_taxonomy = Pipeline(name='score_users_by_taxonomy').to(group_by_taxonomy)\
                            .mapValues(Pipeline().mapValues(score_users)).mapValues(compute_means)
coral.register_pipeline('/users/score/taxonomies', score_users_by_taxonomy)

# comments
score_comments = Pipeline(name='score_comments').map(comment.make)\
    .map(partial(apply_metric, metric=comment.diversity_score)).map(assign_id)
coral.register_pipeline('/comments/score', score_comments)

score_comments_by_taxonomy = Pipeline(name='score_comments_by_taxonomy').to(group_by_taxonomy)\
                                .mapValues(Pipeline().mapValues(score_comments)).mapValues(compute_means)
coral.register_pipeline('/comments/score/taxonomies', score_comments_by_taxonomy)

# assets
score_assets = Pipeline(name='score_assets').map(asset.make)\
    .forkMap(
        partial(apply_metric, metric=asset.discussion_score),
        partial(apply_metric, metric=asset.diversity_score)
    ).flatMap()\
    .reduceByKey(merge_dicts).map(assign_id)
coral.register_pipeline('/assets/score', score_assets)

score_assets_by_taxonomy = Pipeline(name='score_assets_by_taxonomy').to(group_by_taxonomy)\
                            .mapValues(Pipeline().mapValues(score_assets))
coral.register_pipeline('/assets/score/taxonomies', score_assets_by_taxonomy)

# TODO move darwin elsewhere
from .darwin import bp as darwin_bp
coral.blueprints.append(darwin_bp)

# TODO/TEMP documentation endpoint
from .doc import bp as doc_bp
coral.blueprints.append(doc_bp)
