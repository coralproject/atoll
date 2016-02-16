Pipelines
=========

Defining pipes
--------------

Pipes are just defined as (pickleable) functions:

.. code-block:: python

    def count_length(input):
        return len(input)

"Pickleable" currently means they must be functions defined at the top-level of a module. No lambda support yet.

Defining pipelines
------------------

Pipelines are defined just by creating an instance of the ``Pipeline`` class and then using pipeline operators to attach functions:

.. code-block:: python

    from atoll import Pipeline

    def tokenize(input, delimiter=' '):
        return input.split(delimiter)

    pipeline = Pipeline().map(tokenize).map(count_length)

Pipelines are intended for working on collections, so most of the operators have that in mind:

- ``map``
- ``mapValues``
- ``forkMap``
- ``flatMap``
- ``flatMapValues``
- ``reduce``
- ``reduceByKey``

There is additionally the ``to`` operator which passes all of the input to the specified function, rather than applying it individually over the collection. This is useful for chaining pipelines together (see "Nested pipelines" below).

They are called just by calling the pipeline with your input data:

.. code-block:: python

    data = [
        'Coral reefs are diverse underwater ecosystems',
        'Coral reefs are built by colonies of tiny animals'
    ]
    pipeline(data)
    # >>> [6,9]


Nested pipelines
----------------

Pipelines may also be nested in each other:

.. code-block:: python

    def lowercase(input):
        return input.lower()

    nested_pipeline = Pipeline().map(lowercase).to(pipeline)
    nested_pipeline(data)
    # >>> [6,9]


Branching pipelines
-------------------

Pipelines can be branched out to other nested pipelines.

For example, say you have a common data processing pipeline needed for a few other tasks.

You can define the common pipeline first:

.. code-block:: python

    common = Pipeline().map(lowercase).map(tokenize)

Then define pipelines for the other tasks:

.. code-block:: python

    def count_coral(input):
        return input.count('coral')

    task_a = Pipeline().map(count_length)
    task_b = Pipeline().flatMap(count_vowels)

    branching_pipeline = common.fork(task_a, task_b)

    results_a, results_b = branching_pipeline(data)
    # >>> [6,9], [1,1]

The ``fork`` method duplicates inputs across the specified pipelines while avoiding redundant computation. For instance, in the example above, the ``common`` pipeline is executed only once.

Forking supports identity pipes (passed in as ``None``), pipelines, and (non-pipeline) callables. If a non-pipeline callable (e.g. a function) is used, it will be connected using the default ``to`` operator.

The ``forkMap`` method does the same as the ``fork`` method, except the default operator used for non-pipeline callables is ``map``.

We can also ``reduce`` the results of branching pipelines if we want:

.. code-block:: python

    from operator import add
    reduced_pipeline = branching_pipeline.reduce(add)
    results = reduced_pipeline(data)
    # >>> [6,9,1,1]

In addition to ``fork`` and ``forkMap``, there are also the ``split`` and ``splitMap`` operators. If the output of the previous pipe is a collection, these operators take each element from that collection and send it to a different function. For example:

.. code-block:: python

    def double(x):
        return x*2

    def triple(x):
        return x*3

    pipeline = Pipeline().forkMap(double, triple).split(len, sum)
    results = pipeline([1,2,3,4])
    # >>> [4, 30]


Identity pipes
--------------

Occasionally you may want to pass on data without modifying it.

For instance, you may want to fork a pipeline but return the output from the pipe preceding the fork as well, e.g.

.. code-block:: python

    branching_pipeline = common.fork(task_a, task_b, None)
    result_a, result_b, result_c = branching_pipeline(data)
    # >>> [6, 9], [1, 1], [['coral', 'reefs', 'are', 'diverse', 'underwater', 'ecosystems'], ['coral', 'reefs', 'are', 'built', 'by', 'colonies', 'of', 'tiny', 'animals']]

Specifying a pipe as ``None`` inserts an "identity" pipe which does just that - it just returns the input.


Naming pipelines
----------------

It's a best practice to name your pipelines something descriptive so you know what it does:

.. code-block:: python

    pipeline = Pipeline(name='Tokenizer').map(lowercase).map(tokenize)


Runtime keyword arguments
-------------------------

Sometimes you may want to define a pipeline but want to be able to supply keyword arguments which vary the function of some of its pipes.

For instance, you might have a couple datasets from different sources that have similar information.

You could define a pipeline for each that can properly handle each dataset's format, or you can define a single pipeline that varies depending on how it's called, like so:

.. code-block:: python

    from operator import add

    data_a = [1, 2, 3, 4]
    data_b = ['1', '2', '3', '4']

    def identity(x): return x

    def standardize(input, transform_func=identity):
        return transform_func(input)

    # This tells the pipeline to expect a kwarg called 'transform_func'
    pipeline = Pipeline().map(standardize, kwargs=['transform_func']).reduce(add)

    # Now that we're calling the pipe, specify the kwarg
    results_a = pipeline(data_a, transform_func=identity)
    # >>> 10

    # Now that we're calling the pipe, specify the kwarg
    results_b = pipeline(data_b, transform_func=int)
    # >>> 10


Parallelization and distributed computing
-----------------------------------------

Pipes and branches in a pipelines can be executed in parallel (using multiprocessing) by specifying a non-zero value for ``n_jobs`` when running the pipeline:

.. code-block:: python

    results_a, results_b = branching_pipeline(data, n_jobs=2)
    # >>> [6,9], [1,1]

Pipes and branches can also be executed in a distributed fashion across a cluster using the ``distributed`` library.

You will likely also want to specify your own configuration. See :ref:`configuration`. Then main configuration option is where the executor host is (by default, it assumes ``127.0.0.1:8786``).

Then, to run a pipeline on the cluster, just pass ``distributed=True`` when calling the pipeline, e.g:

.. code-block:: python

    pipeline = Pipeline().map(lowercase).map(tokenize)
    results = pipeline(data, distributed=True)

