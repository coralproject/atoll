import numpy as np
from .common import gamma_poission_model, beta_binomial_model
from ..models import User


def make_user(data):
    """
    Convert JSON (dict) data to a User object
    """
    return User(**data)


def like_score(user, k=1, theta=2):
    """
    Estimated number of likes a comment by this user will get
    """
    X = np.array([c.likes for c in user.comments])
    n = len(X)

    # we want to be conservative in our estimate of the poisson's lambda parameter
    # so we take the lower-bound of the 90% confidence interval (i.e. the 0.05 quantile)
    # rather than the expected value
    return user.id, {'community_score': gamma_poission_model(X, n, k, theta, 0.05)}


def starred_score(user, alpha=2, beta=2):
    """
    Probability that a comment by this user will be an editor's pick
    """
    # assume whether or not a comment is starred
    # is drawn from a binomial distribution parameterized by n, p
    # n is known, we want to estimate p
    y = sum(1 for c in user.comments if c.starred)
    n = len(user.comments)

    # again, to be conservative, we take the lower-bound
    # of the 90% credible interval (the 0.05 quantile)
    return user.id, {'organization_score': beta_binomial_model(y, n, alpha, beta, 0.05)}


def moderated_prob(user, alpha=2, beta=2):
    """
    Probability that a user's comment will be moderated
    """
    y = sum(1 for c in user.comments if c.moderated)
    n = len(user.comments)
    return user.id, {'moderation_prob': beta_binomial_model(y, n, alpha, beta, 0.05)}


def discussion_score(user, k=1, theta=2):
    """
    Estimated number of replies a comment by this user will get
    """
    X = np.array([c.n_replies for c in user.comments])
    n = len(X)
    return user.id, {'discussion_score': gamma_poission_model(X, n, k, theta, 0.05)}
