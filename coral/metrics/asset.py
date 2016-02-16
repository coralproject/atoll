import math
import numpy as np
from collections import defaultdict
from .common import beta_binomial_model, gamma_poission_model, requires_keys


@requires_keys('threads[].children')
def discussion_score(asset, k=1, theta=2):
    """
    description:
        en: Estimated number of comments this asset will get.
        de: Geschätzte Zahl der Kommentare dieser Vermögenswert erhalten.
    type: float
    valid: nonnegative
    """
    X = np.array([_max_thread_width(t) * _max_thread_depth(t) for t in asset['threads']])
    n = len(X)

    k = np.sum(X) + k
    t = theta/(theta*n + 1)

    return gamma_poission_model(X, n, k, theta, 0.05)


@requires_keys('threads[].children')
def diversity_score(asset, alpha=2, beta=2):
    """
    description:
        en: Probability that a new reply would be from a new user.
        de: Wahrscheinlichkeit, dass eine neue Antwort würde von einem neuen Benutzer sein.
    type: float
    valid: probability
    """
    X = set()
    n = 0
    for t in asset['threads']:
        users, n_comments = _unique_participants(t)
        X = X | users
        n += n_comments
    y = len(X)

    return beta_binomial_model(y, n, alpha, beta, 0.05)


def _max_thread_depth(thread):
    """compute the length deepest branch of the thread"""
    if not thread['children']:
        return 1
    return 1 + max([_max_thread_depth(reply) for reply in thread['children']])


def _max_thread_width(thread):
    """compute the widest breadth of the thread,
    that is the max number of replies a comment in the thread has received"""
    if not thread['children']:
        return 0
    return max(
        max([_max_thread_width(reply) for reply in thread['children']]),
        len(thread['children'])
    )


def _count_replies(thread):
    return 1 + sum(_count_replies(r) for r in thread['children'])


def _unique_participants(thread):
    """count unique participants and number of comments in a thread"""
    users = set([thread['user_id']])
    n_replies = 1 + len(thread['children'])
    for reply in thread['children']:
        r_users, r_replies = _unique_participants(reply)
        n_replies += r_replies
        users = users | r_users
    return users, n_replies


def _reconstruct_threads(asset):
    """reconstruct threads structure from a flat list of comments"""
    id = asset['_id']
    parents = defaultdict(list)
    for c in asset['comments']:
        p_id = c['parent_id'] # TODO mongo ids y/n?
        if isinstance(p_id, float) and math.isnan(p_id):
            p_id = id
        parents[p_id].append(c)

    threads = []
    for top_level_parent in sorted(parents[id], key=lambda p: p['date_created']):
        threads.append(_reconstruct_thread(top_level_parent, parents))
    asset['threads'] = threads
    return asset


def _reconstruct_thread(comment, parents):
    """recursively reconstruct a thread from comments"""
    id = comment['_id']
    thread = {
        'id': id,
        'user_id': comment['user_id'],
        'children': []
    }
    children = parents[id]
    for reply in sorted(children, key=lambda c: c['date_created']):
        thread['children'].append(_reconstruct_thread(reply, parents))
    return thread


