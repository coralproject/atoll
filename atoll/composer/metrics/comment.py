from atoll.composer.metrics.common import beta_binomial_model


def diversity(comment, alpha=2, beta=2):
    """Probability that a new reply would be from a new user"""
    seen_users = set()

    unique_participants = []
    for r in comment.replies:
        if r.user not in seen_users:
            unique_participants.append(1)
            seen_users.add(r.user)
        else:
            unique_participants.append(0)

    y = sum(unique_participants)
    n = len(comment.replies)

    # again, to be conservative, we take the lower-bound
    # of the 90% credible interval (the 0.05 quantile)
    return beta_binomial_model(y, n, alpha, beta, 0.05)
