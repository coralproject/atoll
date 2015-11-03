import math
import numpy as np
from atoll import Pipeline
from collections import defaultdict
from examples.transform import reddit_map, nyt_map
from examples.common import beta_binomial_model, gamma_poission_model, standardize, load_data, merge_dicts, report, means


def reconstruct_thread(comment, parents):
    id = comment['id']
    thread = {
        'id': id,
        'user_id': comment['user_id'],
        'replies': []
    }
    replies = parents[id]
    for reply in sorted(replies, key=lambda c: c['created_at']):
        thread['replies'].append(reconstruct_thread(reply, parents))
    return thread


def max_thread_depth(thread):
    """
    Compute the length deepest branch of the thread.
    """
    if not thread['replies']:
        return 1
    return 1 + max([max_thread_depth(reply) for reply in thread['replies']])


def max_thread_width(thread):
    """
    Compute the widest breadth of the thread,
    that is the max number of replies a comment in the thread has received
    """
    if not thread['replies']:
        return 0
    return max(
        max([max_thread_width(reply) for reply in thread['replies']]),
        len(thread['replies'])
    )


def reconstruct_discussion(asset_id, comments):
    parents = defaultdict(list)
    for c in comments:
        p_id = c['parent_id']
        if isinstance(p_id, float) and math.isnan(p_id):
            p_id = asset_id
        parents[p_id].append(c)

    threads = []
    for top_level_parent in sorted(parents[asset_id], key=lambda p: p['created_at']):
        threads.append(reconstruct_thread(top_level_parent, parents))
    return asset_id, threads


def asset_discussion_score(threads, k=1, theta=2):
    X = np.array([max_thread_width(t) * max_thread_depth(t) for t in threads])
    n = len(X)

    k = np.sum(X) + k
    t = theta/(theta*n + 1)

    return {'discussion_score': gamma_poission_model(X, n, k, theta, 0.05)}


def unique_participants(thread):
    """
    Count unique participants and
    number of comments in a thread
    """
    users = set([thread['user_id']])
    n_replies = 1 + len(thread['replies'])
    for reply in thread['replies']:
        r_users, r_replies = unique_participants(reply)
        n_replies += r_replies
        users = users | r_users
    return users, n_replies


def asset_diversity_score(threads, alpha=2, beta=2):
    """
    Compute a diversity score for an asset's comments
    """
    X = set()
    n = 0
    for t in threads:
        users, n_comments = unique_participants(t)
        X = X | users
        n += n_comments
    y = len(X)

    return {'diversity_score': beta_binomial_model(y, n, alpha, beta, 0.05)}


def run():
    preprocess = Pipeline().mapValues(standardize, kwargs=['key_map']).to(report)

    discuss_score = Pipeline().mapValues(asset_discussion_score)
    diverse_score = Pipeline().mapValues(asset_diversity_score)
    pipeline = Pipeline()\
        .to(preprocess)\
        .map(reconstruct_discussion)\
        .fork(discuss_score, diverse_score)\
        .flatMap(None)\
        .reduceByKey(merge_dicts)\
        .fork(None, Pipeline().to(means, keys=['discussion_score', 'diversity_score']))
    print(pipeline)

    for dataset, key_map in [
        ('nyt_asset_sample.json', nyt_map),
        ('reddit_asset_sample.json', reddit_map),
    ]:
        print('\n',dataset,'\n')
        sample = load_data(dataset)
        scores, avgs = pipeline(sample, key_map=key_map)
        print('averages:', avgs)
        print('sample score:', scores[0])
