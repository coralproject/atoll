class Base():
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class User(Base):
    def __init__(self, **kwargs):
        self.comments = [Comment(**c) for c in kwargs.pop('comments', [])]
        super().__init__(**kwargs)


class Comment(Base):
    def __init__(self, **kwargs):
        if 'n_replies' not in kwargs:
            self.n_replies = len(kwargs['replies'])
        super().__init__(**kwargs)


class Thread(Base):
    pass
