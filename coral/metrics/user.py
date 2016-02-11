import numpy as np
from .common import gamma_poission_model, beta_binomial_model, requires_keys


def action_vals(actions, type):
    return [a['value'] for a in actions if a['type'] == type]


@requires_keys('comments[].actions')
def community_score(user, k=1, theta=2):
    """
    description:
        en: Estimated number of likes a comment by this user will get.
        de: Geschätzte Zahl der Gleichen Kommentar dieses Benutzers erhalten.
    type: float
    valid: nonnegative
    """
    X = np.array([sum(action_vals(c['actions'], 'like')) for c in user['comments']])
    n = len(X)

    # we want to be conservative in our estimate of the poisson's lambda parameter
    # so we take the lower-bound of the 90% confidence interval (i.e. the 0.05 quantile)
    # rather than the expected value
    return gamma_poission_model(X, n, k, theta, 0.05)


@requires_keys('comments[].starred')
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
    y = sum(1 for c in user['comments'] if c.get('starred', False))
    n = len(user['comments'])

    # again, to be conservative, we take the lower-bound
    # of the 90% credible interval (the 0.05 quantile)
    return beta_binomial_model(y, n, alpha, beta, 0.05)


@requires_keys('comments[].status')
def moderation_prob(user, alpha=2, beta=2):
    """
    description:
        en: Probability that one of this user's comments will be moderated.
        de: Wahrscheinlichkeit, dass eine der Kommentare des Nutzers, moderiert wird.
    type: float
    valid: probability
    """
    # key: 1->unmoderated, 2->accepted, 3->rejected, 4->escalated
    y = sum(1 for c in user['comments'] if c.get('status', 1) in [3,4])
    n = len(user['comments'])
    return beta_binomial_model(y, n, alpha, beta, 0.05)


@requires_keys('comments[].children')
def discussion_score(user, k=1, theta=2):
    """
    description:
        en: Estimated number of replies a comment by this user will get.
        de: Geschätzte Zahl der Antworten Kommentar dieses Benutzers erhalten.
    type: float
    valid: nonnegative
    """
    X = np.array([len(c.get('children', [])) for c in user['comments']])
    n = len(X)
    return gamma_poission_model(X, n, k, theta, 0.05)


@requires_keys('comments[].likes')
def mean_likes_per_comment(user):
    """
    description:
        en: Mean likes per comment.
        de: Durchschnitts Gleichen pro Kommentar.
    type: float
    valid: nonnegative
    """
    return np.mean([c.get('likes', 0) for c in user['comments']])


@requires_keys('comments[].children')
def mean_replies_per_comment(user):
    """
    description:
        en: Mean replies per comment.
        de: Durchschnitts Antworten per Kommentar.
    type: float
    valid: nonnegative
    """
    return np.mean([len(c.get('children', [])) for c in user['comments']])


@requires_keys('comments[].parent_id')
def percent_replies(user):
    """
    description:
        en: Percent of comments that are replies.
        de: Prozent der Kommentare, die Antworten gibt.
    type: float
    valid: probability
    """
    return sum(1 if c.get('parent_id', '') else 0 for c in user['comments'])/len(user['comments'])


@requires_keys('comments[].body')
def mean_words_per_comment(user):
    """
    description:
        en: Mean words per comment.
        de: Durchschnitts Wörter pro Kommentar.
    type: float
    valid: nonnegative
    """
    return np.mean([len(c.get('body', '').split(' ')) for c in user['comments']])
