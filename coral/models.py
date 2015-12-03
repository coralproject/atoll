class Base():
    def __init__(self, **kwargs):
        for k in self.attrs:
            setattr(self, k, kwargs[k])


class User(Base):
    attrs = ['id']

    def __init__(self, **kwargs):
        self.comments = [Comment(**c) for c in kwargs.pop('comments', [])]
        super().__init__(**kwargs)


class Comment(Base):
    attrs = ['replies', 'n_replies', 'likes', 'starred', 'moderated', 'content']

    def __init__(self, **kwargs):
        if 'n_replies' not in kwargs:
            kwargs['n_replies']= len(kwargs['replies'])
        super().__init__(**kwargs)


class Thread(Base):
    pass #TODO
