from collections import defaultdict


def apply_metric(obj, metric):
    """apply a metric to an object.
    returns the object's id with the labeled computed metric"""
    return obj.id, {metric.__name__: metric(obj)}


def merge_dicts(d1, d2):
    """merges/reduces two dictionaries"""
    d1.update(d2)
    return d1


def assign_id(id, data):
    """adds the id to the data dictionary"""
    data.update({"id": id})
    return data


def group_by_taxonomy(collection):
    """break a collection into groups based on taxonomies.
    entities may belong to multiple taxonomies.
    this assumes that:
        - the key for taxonomy is 'taxonomy'
        - taxonomies have the format: 'section:world;author:Foo Bar;section:politics'
    """
    groups = defaultdict(lambda: defaultdict(list))
    for entity in collection:
        for taxonomy in entity['taxonomy'].split(';'):
            # NOTE/TODO this does _not_ copy the entity,
            # it is a shared reference to it. Thus a change
            # to one will affect it elsewhere - should it be copied instead?
            type, name = taxonomy.split(':')
            groups[type][name].append(entity)
    return groups
