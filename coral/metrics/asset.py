import numpy as np
from .common import beta_binomial_model, gamma_poission_model
from ..models import Asset


def make(data):
    """convert json (dict) data to a Asset object"""
    return Asset(**data)


def discussion_score(asset, k=1, theta=2):
    """discussion score is the predicted discussion score for a new thread in the asset"""
    X = np.array([max_thread_width(t) * max_thread_depth(t) for t in asset.threads])
    n = len(X)

    k = np.sum(X) + k
    t = theta/(theta*n + 1)

    return gamma_poission_model(X, n, k, theta, 0.05)


def diversity_score(asset, alpha=2, beta=2):
    """compute a diversity score for an asset's comments"""
    X = set()
    n = 0
    for t in asset.threads:
        users, n_comments = unique_participants(t)
        X = X | users
        n += n_comments
    y = len(X)

    return beta_binomial_model(y, n, alpha, beta, 0.05)


def max_thread_depth(thread):
    """compute the length deepest branch of the thread"""
    if not thread.children:
        return 1
    return 1 + max([max_thread_depth(reply) for reply in thread.children])


def max_thread_width(thread):
    """compute the widest breadth of the thread,
    that is the max number of replies a comment in the thread has received"""
    if not thread.children:
        return 0
    return max(
        max([max_thread_width(reply) for reply in thread.children]),
        len(thread.children)
    )


def count_replies(thread):
    return 1 + sum(count_replies(r) for r in thread.children)


def unique_participants(thread):
    """count unique participants and number of comments in a thread"""
    users = set([thread.user_id])
    n_replies = 1 + len(thread.children)
    for reply in thread.children:
        r_users, r_replies = unique_participants(reply)
        n_replies += r_replies
        users = users | r_users
    return users, n_replies
