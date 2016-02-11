from functools import partial
from atoll import Atoll, Pipeline
from .nlp import train_moderation_model, run_moderation_model
from .metrics import user, comment, asset, apply_metric, merge_dicts, assign_id, prune_none, aggregates, rolling, taxonomy


coral = Atoll()

# simple moderation classification model
coral.register_pipeline('/comments/model/moderation/train', train_moderation_model)
coral.register_pipeline('/comments/model/moderation/run', run_moderation_model)

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
    .reduceByKey(merge_dicts)
coral.register_pipeline('/comments/score', Pipeline(name='score_comments').to(score_comments).map(assign_id).map(prune_none).to(aggregates))

score_comments_by_taxonomy = Pipeline(name='score_comments_by_taxonomy')\
    .forkMap(None, taxonomy.extract_taxonomy)\
    .split(score_comments, None).flatMap()\
    .reduceByKey(merge_dicts).map(assign_id)\
    .to(taxonomy.group_by_taxonomy).mapValues(taxonomy.taxonomy_aggregates).to(dict)
coral.register_pipeline('/comments/score/taxonomy', score_comments_by_taxonomy)

score_assets = Pipeline(name='score_assets')\
    .map(asset.reconstruct_threads)\
    .forkMap(
        partial(apply_metric, metric=asset.discussion_score),
        partial(apply_metric, metric=asset.diversity_score)
    ).flatMap()\
    .reduceByKey(merge_dicts)
coral.register_pipeline('/assets/score', Pipeline(name='score_assets').to(score_assets).map(assign_id).map(prune_none).to(aggregates))

score_assets_by_taxonomy = Pipeline(name='score_assets_by_taxonomy')\
    .forkMap(None, taxonomy.extract_taxonomy)\
    .split(score_assets, None).flatMap()\
    .reduceByKey(merge_dicts).map(assign_id)\
    .to(taxonomy.group_by_taxonomy).mapValues(taxonomy.taxonomy_aggregates).to(dict)
coral.register_pipeline('/assets/score/taxonomy', score_assets_by_taxonomy)

rolling_score_users = Pipeline(name='rolling_score_users')\
    .forkMap(rolling.extract_update, rolling.extract_history)\
    .split(score_users, None).flatMap()\
    .reduceByKey(rolling.rolling_score)\
    .map(assign_id).map(prune_none)
coral.register_pipeline('/users/rolling', rolling_score_users)


from .doc import bp as doc_bp
coral.blueprints.append(doc_bp)
