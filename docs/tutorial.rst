Tutorial
========

Let's try defining some of our own pipes and a pipeline.

In this example, we will create a pipeline for computing "discussion scores" for comments sections.

We will be using pre-generated data available here:

https://github.com/CoralProject/atoll/raw/master/examples/threads.json

This is a JSON dump representing a fake comments sections for a few articles.

The data looks something like this:

.. code-block:: json

    [
        [
            {
                "body": "ifhmyuhoru lktlglydmq...",
                "user": "nbczfjtvxe",
                "replies": [
                    {
                        "body": "bqzwssfthc liekxllsnd...",
                        "user": "vtkgnkuhmp",
                        "replies": []
                    },
                    {
                        "body": "tkxlcltvbe mdwyilohof...",
                        "user": "xnhtqgxzvx",
                        "replies": []
                    }
                ]
            },
            ...
        ],
        ...
    ]

The complete example is available at:

https://github.com/CoralProject/atoll/raw/master/examples/discussion_score.py


Converting the raw data
-----------------------

Things will be easier on us if we can take the data and structure it in a more convenient way.

Let's define a ``Thread`` class that we'll use for our pipes.

.. code-block:: python

    class Thread():
        def __init__(self, length, participants):
            self.length = length
            self.participants = participants

        def __repr__(self):
            return 'Thread(len={},users={})'.format(self.length,
                                                    self.participants)

Our discussion score will be based just on the thread length and the number of participants in the thread, so that's all we will need for our class.

Now we want to take that raw JSON data and transform them into instances of this ``Thread`` class.

We can write a function to do that:

.. code-block:: python

    def make_thread(article):
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
            l, n = self.count_thread(r, seen_users)
            thread_length += l
            unique_users += n
        return thread_length, unique_users

There's a lot going on here, but basically this counts up the unique users and comments in a thread.

Now we can load our data, define a new pipeline, and see if the transformation works.

.. code-block:: python

    import json
    from atoll import Pipeline

    with open('threads.json', 'r') as f:
        raw_data = json.load(f)

    pipeline = Pipeline().map(make_threads)
    threads = pipeline(raw_data)
    print(threads)

You should see output like::

    [[Thread(len=2,users=2), Thread(len=3,users=3), ...


Computing the discussion score
------------------------------

Now we can start defining the pipes that will compute our discussion score.

Our discussion score will be a combination of a length score, based on the thread's length, and a diveristy score, based on the number of unique participants in the thread.

For the length score, we will just compute the mean thread length for an article:

.. code-block:: python

    def length_score(threads):
        """Computes a thread length score for a comments section"""
        # on avg, how long is a thread
        return sum(t.length for t in threads)/len(threads)

We can define the diversity score in a similar manner; we compute the mean of the mean participant length per thread for an article:

.. code-block:: python

    def diversity_score(threads):
        """Computes a discussion score for a comments section"""
        # on avg, how many people are in a thread
        return sum(t.participants/t.length for t in threads)/len(threads)

Note that division works differently in Python 2; if you are using Python 2, add this to the top of your script:

.. code-block:: python

    from __future__ import division

Let's try building a pipeline with these new pipes and check that it works:

.. code-block:: python

    # define the nested pipelines
    length_p = Pipeline().map(length_score)
    diversity_p = Pipeline().map(diversity_score)

    # then the complete pipeline
    pipeline = Pipeline().map(make_threads).fork(length_p, diversity_p)
    outputs = pipeline(raw_data)
    print(outputs)

You should get output that looks like::

    ([3.89, 4.01, 5.14, 4.27, 3.49, 4.06, 4.0, 4.5, 4.72, 3.9], [0.9334127792142499, 0.9366252358752358, 0.9229765858378006, 0.934963918090853, 0.9422580932139755, 0.9435349533507429, 0.943411459363527, 0.9312625049118184, 0.9237472061686964, 0.9350028305028306])

We are left with two scores, but we want to combine them to a single score. We can define one last pipe - a reduce pipe - to do so.

We'll keep things simple and say that ``discussion_score = length_score * diversity_score``.

.. code-block:: python

    def discussion_score(length_scores, diversity_scores):
        return [l*d for l, d in zip(length_scores, diversity_scores)]

Then we can combine everything into our final Pipeline:

.. code-block:: python

    pipeline = Pipeline().map(make_threads).fork(length_p, diversity_p).reduce(discussion_score)
    discussion_scores = pipeline(raw_data)
    print(discussion_scores)

With final output that's something like::

    [3.6309757111434324, 3.7558671958596954, 4.7440996512062945, 3.9922959302479417, 3.2884807453167744, 3.8307519106040155, 3.773645837454108, 4.190681272103182, 4.360086813116247, 3.646511038961039]

