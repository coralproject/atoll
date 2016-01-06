import math
from dateutil.parser import parse
from collections import defaultdict


class ModelValidationException(Exception):
    pass


class Base():
    def __init__(self, **kwargs):
        for k in self.attrs:
            # self.__validate(k, kwargs[k])
            setattr(self, k, kwargs[k])

    @classmethod
    def __validate(cls, attr, value):
        typ = cls.attrs[attr]
        if not isinstance(value, typ):
            raise ModelValidationException(
                '{} must be of type {}, not {}.'.format(attr, typ, type(value)))


class User(Base):
    attrs = ['id', 'comments']

    def __init__(self, **kwargs):
        kwargs['comments'] = [Comment(**c) for c in kwargs['comments']]
        super().__init__(**kwargs)


class Comment(Base):
    attrs = ['id', 'parent_id', 'children',
             'likes', 'starred', 'moderated', 'content',
             'date_created', 'user_id']

    def __init__(self, **kwargs):
        kwargs['children'] = [Comment(**c) for c in kwargs['children']]
        kwargs['date_created'] = parse(kwargs['date_created'])
        super().__init__(**kwargs)


class Asset(Base):
    attrs = ['id', 'threads']

    def __init__(self, **kwargs):
        # instead of 'threads', can pass in a flat list of 'comments'
        # we reconstruct flat comments into the thread structure here
        if 'threads' not in kwargs:
            comments = [Comment(**c) for c in kwargs['comments']]
            kwargs['threads'] = self._reconstruct_threads(comments)
        else:
            kwargs['threads'] = [Comment(**c) for c in kwargs['threads']]
        super().__init__(**kwargs)

    def _reconstruct_threads(self, comments):
        """reconstruct threads structure from a flat list of comments"""
        parents = defaultdict(list)
        for c in comments:
            p_id = c.parent_id
            if isinstance(p_id, float) and math.isnan(p_id):
                p_id = self.id
            parents[p_id].append(c)

        threads = []
        for top_level_parent in sorted(parents[self.id], key=lambda p: p.date_created):
            threads.append(self._reconstruct_thread(top_level_parent, parents))
        return threads

    def _reconstruct_thread(self, comment, parents):
        """recursively reconstruct a thread from comments"""
        id = comment['id']
        thread = {
            'id': id,
            'user_id': comment['user_id'],
            'children': []
        }
        children = parents[id]
        for reply in sorted(children, key=lambda c: c['date_created']):
            thread['children'].append(self._reconstruct_thread(reply, parents))
        return thread


class Thread(Base):
    pass #TODO
