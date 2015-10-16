Tutorial
========

Let's try defining some of our own pipes and a pipeline.

In this example, we will create a pipeline for computing a "discussion score" for a comments section.

We will be using pre-generated data available here:

https://github.com/CoralProject/atoll/raw/master/examples/threads.json

This is a JSON dump representing a fake comments section.

The data looks something like this:

.. code-block:: json

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

We can write a pipe to do that.

First, we need to import the ``Pipe`` class:

.. code-block:: python

    from atoll import Pipe

When defining a new pipe, the first considerations are:

- What input type will this pipe accept?
- What type will this pipe output?

In our case, we are only concerned with thread length and number of participants, so the only information in our raw data that we care about are the ``replies`` and the ``user`` keys. So as input, we want a list of dictionaries with those keys.

The ``user`` key will just be a string, but the ``replies`` key will be recursive, in that it can contain more of these dictionaries. Atoll uses the special type ``t.self`` to indicate a recursive type.

Because we are building the pipe to transform our raw data into ``Thread`` objects, we know we need to output a list of them.

Thus we can define our pipe like so:

.. code-block:: python

    from atoll import t

    class ThreadsTransform(Pipe):
        input = [{
            'user': str,
            'replies': [t.self]
        }]
        output = [Thread]

Now the last step in defining a pipe is defining what it does. We implement the ``__call__`` method to do so:

.. code-block:: python

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

There's a lot going on here, but basically this counts up the unique users and comments in a thread.

Now we can load our data, define a new pipeline, and see if the transformation works.

.. code-block:: python

    import json
    from atoll import Pipeline

    with open('threads.json', 'r') as f:
        raw_data = json.load(f)

    pipeline = Pipeline([ThreadsTransform()])
    threads = pipeline(raw_data)
    print(threads)

You should see output like::

    [Thread(len=2,users=2), Thread(len=3,users=3), ...


Computing the discussion score
------------------------------

Now we can start defining the pipes that will compute our discussion score.

Our discussion score will be a combination of a length score, based on the thread's length, and a diveristy score, based on the number of unique participants in the thread.

The diversity score is a bit simpler, so let's start with that.

The diversity score pipe takes in a list of our ``Thread`` objects and gives us a float (it computes a diversity score for the entire comments section rather than for each individual thread):

.. code-block:: python

    class DiversityScore(Pipe):
        input = [Thread]
        output = float

The diversity score will just be computed as the mean number of participants across threads:

.. code-block:: python

    class DiversityScore(Pipe):
        input = [Thread]
        output = float

        def __call__(self, threads):
            return sum(t.participants/t.length for t in threads)/len(threads)

Note that division works differently in Python 2; if you are using Python 2, add this to the top of your script:

.. code-block:: python

    from __future__ import division

We can define the length score pipe in a similar manner. It takes the same input and gives the same output as the diversity score pipe:

.. code-block:: python

    class LengthScore(Pipe):
        input = [Thread]
        output = float

The length score is computed in a more complex way, beyond the scope of this tutorial, but basically it gives higher scores for comments sections that have consistently long threads:

.. code-block:: python

    import numpy as np

    class LengthScore(Pipe):
        input = [Thread]
        output = float

        def __call__(self, threads):
            X = np.array([t.length for t in threads])
            n = len(X)
            return ((n/(n + self.beta)) * (np.sum(X)/n)) + \
                (self.beta/(n+self.beta) * (self.alpha/self.beta))

Note that the ``__call__`` method refers to two class attributes, ``self.alpha`` and ``self.beta``, which we have not yet defined. These are parameters that can be tweaked, so we want them to be defined when the pipe is created.

We can do this by defining the class's ``__init__`` method like any Python class:

.. code-block:: python

    class LengthScore(Pipe):
        input = [Thread]
        output = float

        def __init__(self, alpha=1, beta=2):
            self.alpha = alpha
            self.beta = beta

        # rest of the class

Let's try building a pipeline with these new pipes and check that it works:

.. code-block:: python

    pipeline = Pipeline([
        ThreadsTransform(),
        (LengthScore(alpha=1, beta=2), DiversityScore())
    ])
    outputs = pipeline(raw_data)
    print(outputs)

Note that we are using Atoll's branching syntax to send the output of the ``ThreadsTransform`` pipe to both the ``LengthScore`` and ``DiversityScore`` pipes.

You should get output that looks like::

    (4.3137254901960782, 0.93327945665445655)

We are left with two scores, but we want to combine them to a single score. We can define one last pipe to do so.

Let's say we want to weight the length score by the root of the diversity score, that is:

.. math::

    \text{discussion_score} = \text{length_score} \sqrt{\text{diversity_score}}

This new pipe will take in two inputs, the float scores from the ``LengthScore`` and ``DiversityScore`` pipes, and combine them into a single float output:

.. code-block:: python

    import math

    class RootWeight(Pipe):
        input = (float, float)
        output = float

        def __call__(self, weight, value):
            return math.sqrt(weight) * value

Then we can combine everything into our final Pipeline:

.. code-block:: python

    pipeline = Pipeline([
        ThreadsTransform(),
        (LengthScore(alpha=1, beta=2), DiversityScore()),
        RootWeight()
    ])
    discussion_score = pipeline(raw_data)
    print(discussion_score)

With final output that's something like::

    1.93837570837

