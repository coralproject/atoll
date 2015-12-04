import math
from datetime import datetime
from collections import defaultdict


class Base():
    def __init__(self, **kwargs):
        for k in self.attrs:
            setattr(self, k, kwargs[k])


class User(Base):
    attrs = ['id', 'comments']

    def __init__(self, **kwargs):
        kwargs['comments'] = [Comment(**c) for c in kwargs['comments']]
        super().__init__(**kwargs)


class Comment(Base):
    attrs = ['id', 'parent_id', 'replies', 'n_replies',
             'likes', 'starred', 'moderated', 'content',
             'created_at', 'user_id']

    def __init__(self, **kwargs):
        if 'n_replies' not in kwargs:
            kwargs['n_replies']= len(kwargs['replies'])
        kwargs['replies'] = [Comment(**c) for c in kwargs['replies']]
        kwargs['created_at'] = datetime.fromtimestamp(kwargs['created_at'])
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
        for top_level_parent in sorted(parents[self.id], key=lambda p: p.created_at):
            threads.append(self._reconstruct_thread(top_level_parent, parents))
        return threads

    def _reconstruct_thread(self, comment, parents):
        """recursively reconstruct a thread from comments"""
        id = comment['id']
        thread = {
            'id': id,
            'user_id': comment['user_id'],
            'replies': []
        }
        replies = parents[id]
        for reply in sorted(replies, key=lambda c: c['created_at']):
            thread['replies'].append(self._reconstruct_thread(reply, parents))
        return thread


class Thread(Base):
    pass #TODO
