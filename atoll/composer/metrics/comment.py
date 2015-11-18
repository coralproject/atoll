

def n_words(comment):
    """The number of words in the comment body"""
    return len(comment.body.split(' '))


def n_likes(comment):
    """The number of likes the comment has"""
    return comment.likes
