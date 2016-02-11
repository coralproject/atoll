from collections import defaultdict
from coral.metrics import aggregates


def group_by_taxonomy(collection):
    """break a collection into groups based on taxonomies.
    entities may belong to multiple taxonomies.
    this assumes that:
        - the key for taxonomy is 'taxonomy'
        - taxonomies have the format: 'section:world;author:Foo Bar;section:politics'
    """
    groups = defaultdict(list)
    for entity in collection:
        for taxonomy in entity['taxonomy'].split(';'):
            groups[taxonomy].append(entity.copy())
    return dict(groups)


def extract_taxonomy(input):
    """extract the taxonomy"""
    return input['_id'], {'taxonomy': input['taxonomy']}


def taxonomy_aggregates(objs):
    """extract only the aggregate metrics for each taxonomy"""
    return aggregates(objs)['aggregates']
