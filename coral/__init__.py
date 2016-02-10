from functools import partial
from atoll import Atoll, Pipeline
from .metrics import user, comment, asset, apply_metric, merge_dicts, assign_id, prune_none, aggregates, rolling


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
    .reduceByKey(merge_dicts)
coral.register_pipeline('/users/score', Pipeline(name='score_users').to(score_users).map(assign_id).map(prune_none).to(aggregates))

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


rolling_mean_users = Pipeline(name='rolling_mean_users')\
    .forkMap(rolling.extract_latest, rolling.extract_history)\
    .split(score_users, None).flatMap()\
    .reduceByKey(rolling.rolling_mean)\
    .map(assign_id).map(prune_none)
coral.register_pipeline('/users/rolling', rolling_mean_users)


from .doc import bp as doc_bp
coral.blueprints.append(doc_bp)
