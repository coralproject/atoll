from functools import partial
from atoll import Atoll, Pipeline
from .metrics import user, comment, asset, apply_metric, merge_dicts, assign_id, prune_none, aggregates


coral = Atoll()

score_users = Pipeline(name='score_users')\
    .forkMap(
        partial(apply_metric, metric=user.community_score),
        partial(apply_metric, metric=user.organization_score),
        partial(apply_metric, metric=user.discussion_score),
        partial(apply_metric, metric=user.moderation_prob),
        partial(apply_metric, metric=user.mean_likes_per_comment),
        partial(apply_metric, metric=user.mean_replies_per_comment),
        partial(apply_metric, metric=user.mean_words_per_comment),
        partial(apply_metric, metric=user.percent_replies),
    ).flatMap()\
    .reduceByKey(merge_dicts).map(assign_id).map(prune_none).to(aggregates)
coral.register_pipeline('/users/score', score_users)

score_comments = Pipeline(name='score_comments')\
    .forkMap(
        partial(apply_metric, metric=comment.diversity_score),
        partial(apply_metric, metric=comment.readability_scores)
    ).flatMap()\
    .reduceByKey(merge_dicts).map(assign_id).map(prune_none).to(aggregates)
coral.register_pipeline('/comments/score', score_comments)

score_assets = Pipeline(name='score_assets')\
    .map(asset.reconstruct_threads)\
    .forkMap(
        partial(apply_metric, metric=asset.discussion_score),
        partial(apply_metric, metric=asset.diversity_score)
    ).flatMap()\
    .reduceByKey(merge_dicts).map(assign_id).map(prune_none).to(aggregates)
coral.register_pipeline('/assets/score', score_assets)


# TODO move darwin elsewhere
from .darwin import bp as darwin_bp
coral.blueprints.append(darwin_bp)

# TODO/TEMP documentation endpoint
from .doc import bp as doc_bp
coral.blueprints.append(doc_bp)
