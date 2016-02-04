def apply_metric(obj, metric):
    """apply a metric to an object.
    returns the object's id with the labeled computed metric"""

    # TODO are we using mongo ids or what?
    try:
        id = obj['id']
    except KeyError:
        id = obj['_id']
    return id, {metric.__name__: metric(obj)}


def merge_dicts(d1, d2):
    """merges/reduces two dictionaries"""
    d1.update(d2)
    return d1


def assign_id(id, data):
    """adds the id to the data dictionary"""
    data.update({'id': id})
    return data


def prune_none(data):
    """removes keys where the value is `None`,
    i.e. metrics which could not be computed"""
    return {k: v for k, v in data.items() if v is not None}
