from __future__ import division

import json
from atoll import Pipeline


class Thread():
    def __init__(self, length, participants):
        self.length = length
        self.participants = participants

    def __repr__(self):
        return 'Thread(len={},users={})'.format(self.length,
                                                self.participants)


def make_threads(article):
    return [Thread(*count_thread(t)) for t in article]


def count_thread(comment, seen_users=None):
    """Counts the length of a thread and its unique users"""
    thread_length = 1
    unique_users = 0
    if seen_users is None:
        seen_users = []
    if comment['user'] not in seen_users:
        unique_users += 1
        seen_users.append(comment['user'])
    for r in comment['replies']:
        l, n = count_thread(r, seen_users)
        thread_length += l
        unique_users += n
    return thread_length, unique_users


def length_score(threads):
    """Computes a thread length score for a comments section"""
    # on avg, how long is a thread
    return sum(t.length for t in threads)/len(threads)


def diversity_score(threads):
    """Computes a discussion score for a comments section"""
    # on avg, how many people are in a thread
    return sum(t.participants/t.length for t in threads)/len(threads)


def discussion_score(length_scores, diversity_scores):
    return [l*d for l, d in zip(length_scores, diversity_scores)]


with open('examples/threads.json', 'r') as f:
    raw_data = json.load(f)

length_p = Pipeline().map(length_score)
diversity_p = Pipeline().map(diversity_score)
pipeline = Pipeline().map(make_threads).fork(length_p, diversity_p).reduce(discussion_score)

print('The pipeline:')
print(pipeline)
discussion_scores = pipeline(raw_data)
print('Scores:', discussion_scores)

