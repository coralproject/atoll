from datetime import datetime
from functools import partial


def convert_dt(pattern, dt):
    return datetime.strptime(dt, pattern).timestamp() if dt is not None else None


"""
until joblib switches from pickle to dill for serialization
(see https://github.com/joblib/joblib/pull/240)
we can't have any lambdas, functions must be defined at the top-level of a module.
"""


def zero(x):
    return 0


def check_nyt_status(status):
    return True if status == '3' else False

def check_reddit_moderated(reason):
    return True if reason is not None else False

def check_wapo_moderated(x):
    return False if x == 'Untouched' else True


nyt_map = {
    'commentBody': 'body',
    'createDate': {
        'key': 'created_at',
        'transform': partial(convert_dt, '%Y-%m-%d %H:%M:%S'),
    },
    'userID': 'user_id',
    'recommendationCount': {
        'key': 'likes',
        'transform': int
    },
    'editorsSelection': 'starred',
    'statusID': {
        'key': 'moderated',
        'transform': check_nyt_status
    },

    'commentID': 'id',
    'parentID': 'parent_id',
    'assetID': 'asset_id',

    # getting n_replies for reddit comments is tricky, for now just set to 0
    'showCommentExcerpt': { # w/e key
        'key': 'n_replies',
        'transform': zero
    }
}

reddit_map = {
    'body': 'body',
    'created_utc': 'created_at',
    'author': 'user_id',
    'score': 'likes',
    'gilded': { # not really "editors selection" but reddit's equivalent
        'key': 'starred',
        'transform': bool
    },
    'removal_reason': {
        'key': 'moderated',
        'transform': check_reddit_moderated
    },

    'id': 'id',
    'parent_id': 'parent_id',
    'link_id': 'asset_id',

    # getting n_replies for reddit comments is tricky, for now just set to 0
    'score_hidden': { # w/e key
        'key': 'n_replies',
        'transform': zero
    }
}

wapo_map = {
    'object.content': 'body',
    'object.published': {
        'key': 'created_at',
        'transform': partial(convert_dt, '%Y-%m-%dT%H:%M:%SZ')
    },
    'actor.id': 'user_id',
    'object.accumulators.repliesCount': {
        'key': 'n_replies',
        'default': 0,
        'transform': int
    },
    'object.accumulators.likesCount': {
        'key': 'likes',
        'default': 0,
        'transform': int
    },

    # not sure if this is accurate
    'object.status': {
        'key': 'moderated',
        'transform': check_wapo_moderated
    },

    # doesn't seem to be an equivalent to editors selection, so just use w/e
    'object': {
        'key': 'starred',
        'transform': zero
    }
}



