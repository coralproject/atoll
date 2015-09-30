from __future__ import division

import json
import math
import numpy as np
from atoll import Pipe, Pipeline


class Thread():
    def __init__(self, length, participants):
        self.length = length
        self.participants = participants

    def __repr__(self):
        return 'Thread(len={},users={})'.format(self.length,
                                                self.participants)


class ThreadsTransform(Pipe):
    input = [{
        'user': str,
        'replies': ['self']
    }]
    output = [Thread]

    def __call__(self, input):
        return [Thread(*self.count_thread(c)) for c in input]

    def count_thread(self, comment, seen_users=None):
        thread_length = 1
        unique_users = 0
        if seen_users is None:
            seen_users = []
        if comment['user'] not in seen_users:
            unique_users += 1
            seen_users.append(comment['user'])
        for r in comment['replies']:
            l, n = self.count_thread(r, seen_users)
            thread_length += l
            unique_users += n
        return thread_length, unique_users


class LengthScore(Pipe):
    """
    Computes a thread length score for a comments section
    """
    input = [Thread]
    output = float

    def __init__(self, alpha=1, beta=2):
        self.alpha = alpha
        self.beta = beta

    def __call__(self, threads):
        # alpha and beta are priors for the gamma prior
        # see below for more info

        X = np.array([t.length for t in threads])
        n = len(X)

        # this is the posterior mean (i.e. the expected lambda parameter for the poisson)
        # which is also the expected value for the poisson distribution itself
        # since the gamma distribution is a conjugate prior for the poisson,
        # we get this mean analytically
        return ((n/(n + self.beta)) * (np.sum(X)/n)) + \
            (self.beta/(n+self.beta) * (self.alpha/self.beta))


class DiversityScore(Pipe):
    """
    Computes a discussion score for a comments section
    """
    input = [Thread]
    output = float

    def __call__(self, threads):
        # on avg, how many people are in a thread
        mean_participant_ratio = np.mean([t.participants/t.length for t in threads])
        return mean_participant_ratio


class RootWeight(Pipe):
    """
    Root-weights the right input with the left input
    """
    input = (float, float)
    output = float

    def __call__(self, weight, value):
        return math.sqrt(weight) * value


with open('examples/threads.json', 'r') as f:
    raw_data = json.load(f)

pipeline = Pipeline([
    ThreadsTransform(),
    (LengthScore(alpha=1, beta=2), DiversityScore()),
    RootWeight()
])

print('The pipeline:')
print(pipeline)
score = pipeline(raw_data)
print('Output:', score)
