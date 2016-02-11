from .readability import Readability
from .common import beta_binomial_model, requires_keys


@requires_keys('children[].user')
def diversity_score(comment, alpha=2, beta=2):
    """
    description:
        en: Probability that a new reply would be from a new user.
        de: Wahrscheinlichkeit, dass eine neue Antwort würde von einem neuen Benutzer sein.
    type: float
    valid: probability
    """
    seen_users = set()
    unique_participants = []
    for r in comment['children']:
        if r['user'] not in seen_users:
            unique_participants.append(1)
            seen_users.add(r['user'])
        else:
            unique_participants.append(0)

    y = sum(unique_participants)
    n = len(comment['children'])

    # again, to be conservative, we take the lower-bound
    # of the 90% credible interval (the 0.05 quantile)
    return beta_binomial_model(y, n, alpha, beta, 0.05)


@requires_keys('body')
def readability_scores(comment):
    """
    description:
        en: A variety of readability scores (limited language support).
        de: Eine Vielzahl von Lesbarkeit (begrenzte Sprachunterstützung).
    type: dict
    valid: nonnegative
    """
    r = Readability(comment['body'])
    return {
        'ari': r.ARI(),
        'flesch_reading_ease': r.FleschReadingEase(),
        'flesch_kincaid_grade_level': r.FleschKincaidGradeLevel(),
        'gunning_fog_index': r.GunningFogIndex(),
        'smog_index': r.SMOGIndex(),
        'coleman_liau_index': r.ColemanLiauIndex(),
        'lix': r.LIX(),
        'rix': r.RIX()
    }



