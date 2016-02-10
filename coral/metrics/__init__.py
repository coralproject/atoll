import numpy as np
from collections import defaultdict


def apply_metric(obj, metric):
    """apply a metric to an object.
    returns the object's id with the labeled computed metric"""
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


def aggregates(objs):
    """computes descriptive statistics over the aggregates of metrics computed for the collection"""
    aggs = defaultdict(list)
    for metrics in objs:
        for k, v in _flatten(metrics):
            if k == 'id':
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
