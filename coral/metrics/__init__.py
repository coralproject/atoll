import numpy as np
from collections import defaultdict


class MetricException(Exception):
    def __init__(self, original_exp, metric, data):
        message = str(original_exp)
        super().__init__(message)
        self.message = message
        self.metric = metric
        self.data = data
        self.type = type(original_exp).__name__


def apply_metric(obj, metric):
    """apply a metric to an object.
    returns the object's id with the labeled computed metric"""
    try:
        id = obj['_id']
        return id, {metric.__name__: metric(obj)}

    # re-raise as something to catch
    except Exception as e:
        raise MetricException(e, metric.__name__, obj)


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


def aggregates(objs):
    """computes descriptive statistics over the
    aggregates of metrics computed for the collection"""
    aggs = defaultdict(list)
    for metrics in objs:
        for k, v in _flatten(metrics):
            if k == 'id' or not isinstance(v, (float, int)):
                continue
            else:
                aggs[k].append(v)

    for k, v in aggs.items():
        aggs[k] = {
            'max': max(v),
            'min': min(v),
            'mean': np.mean(v),
            'std': np.std(v),
            'count': len(v),
        }

    return {
        'collection': objs,
        'aggregates': aggs
    }


def _flatten(d, parent_key='', sep='.'):
    """flattens a dictionary into a list of (k, v) tuples."""
    items = []
    for k, v in d.items():
        k_ = '{}{}{}'.format(parent_key, sep, k) if parent_key else k
        if isinstance(v, dict):
            items.extend(_flatten(v, k_, sep=sep))
        else:
            items.append((k_, v))
    return items
