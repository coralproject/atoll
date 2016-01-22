import numpy as np
from .common import gamma_poission_model, beta_binomial_model
from ..models import User


def make(data):
    """convert json (dict) data to a user object"""
    return User(**data)


def community_score(user, k=1, theta=2):
    """
    description:
        en: Estimated number of likes a comment by this user will get.
        de: Geschätzte Zahl der Gleichen Kommentar dieses Benutzers erhalten.
    type: float
    valid: nonnegative
    """
    X = np.array([c.likes for c in user.comments])
    n = len(X)

    # we want to be conservative in our estimate of the poisson's lambda parameter
    # so we take the lower-bound of the 90% confidence interval (i.e. the 0.05 quantile)
    # rather than the expected value
    return gamma_poission_model(X, n, k, theta, 0.05)


def organization_score(user, alpha=2, beta=2):
    """
    description:
        en: Probability that a comment by this user will be an editor's pick.
        de: Wahrscheinlichkeit, dass ein Kommentar dieses Benutzers holen eines Editors können.
    type: float
    valid: probability
    """
    # assume whether or not a comment is starred
    # is drawn from a binomial distribution parameterized by n, p
    # n is known, we want to estimate p
    y = sum(1 for c in user.comments if c.starred)
    n = len(user.comments)

    # again, to be conservative, we take the lower-bound
    # of the 90% credible interval (the 0.05 quantile)
    return beta_binomial_model(y, n, alpha, beta, 0.05)


def moderation_prob(user, alpha=2, beta=2):
    """
    description:
        en: Probability that one of this user's comments will be moderated.
        de: Wahrscheinlichkeit, dass eine der Kommentare des Nutzers, moderiert wird.
    type: float
    valid: probability
    """
    y = sum(1 for c in user.comments if c.moderated)
    n = len(user.comments)
    return beta_binomial_model(y, n, alpha, beta, 0.05)


def discussion_score(user, k=1, theta=2):
    """
    description:
        en: Estimated number of replies a comment by this user will get.
        de: Geschätzte Zahl der Antworten Kommentar dieses Benutzers erhalten.
    type: float
    valid: nonnegative
    """
    X = np.array([len(c.children) for c in user.comments])
    n = len(X)
    return gamma_poission_model(X, n, k, theta, 0.05)


def mean_likes_per_comment(user):
    """
    description:
        en: Mean likes per comment.
        de: Durchschnitts Gleichen pro Kommentar.
    type: float
    valid: nonnegative
    """
    return np.mean([c.likes for c in user.comments])


def mean_replies_per_comment(user):
    """
    description:
        en: Mean replies per comment.
        de: Durchschnitts Antworten per Kommentar.
    type: float
    valid: nonnegative
    """
    return np.mean([len(c.children) for c in user.comments])


def percent_replies(user):
    """
    description:
        en: Percent of comments that are replies.
        de: Prozent der Kommentare, die Antworten gibt.
    type: float
    valid: probability
    """
    return sum(1 if c.parent_id is not None else 0 for c in user.comments)/len(user.comments)


def mean_words_per_comment(user):
    """
    description:
        en: Mean words per comment.
        de: Durchschnitts Wörter pro Kommentar.
    type: float
    valid: nonnegative
    """
    return np.mean([len(c.content.split(' ')) for c in user.comments])
