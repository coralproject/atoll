def extract_history(input):
    """extract the past metrics"""
    prev = input['prev']
    prev['prev'] = True
    return input['_id'], prev


def extract_latest(input):
    """extract the update data, from which we compute new metrics"""
    latest = input['latest']
    latest['_id'] = input['_id']
    return latest


def rolling_mean(d1, d2, alpha=0.5):
    """computes rolling means, decaying the past by alpha.
    the past metrics are identified by the `prev` key.
    any keys present in the update dict that are not in the past
    dict are carried over."""

    # figure out which dict is the previous metrics
    if 'prev' in d1 and d1['prev']:
        prev, update = d1, d2
    else:
        prev, update = d2, d1
    del prev['prev']

    new = {}
    for k, v in prev.items():
        if k in update:
            new[k] = v + (alpha * (update[k] - v))
        else:
            new[k] = v

    for k in set(update.keys()) - set(new.keys()):
        new[k] = update[k]

    return new


