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

Note that you can only branch to other pipelines.

We can also ``reduce`` the results of branching pipelines if we want:

.. code-block:: python

    from operator import add
    reduced_pipeline = branching_pipeline.reduce(add)
    results = reduced_pipeline(data)
    # >>> [6,9,1,1]


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


Pipeline validation
-------------------

If you are about to process a lot of data, you don't want runtime errors occuring deep in your pipeline.

To help mitigate this, you can "validate" a pipeline by either passing in your data to the pipeline's ``validate`` method:

.. code-block:: python

    pipeline.validate(data)

Or by running your pipeline with ``validate=True``:

.. code-block:: python

    pipeline(data, validate=True)

This will draw a random sample from your dataset and try running the pipeline.


Parallelization and distributed computing
-----------------------------------------

Pipes and branches in a pipelines can be executed in parallel (using multiprocessing) by specifying a non-zero value for ``n_jobs`` when running the pipeline:

.. code-block:: python

    results_a, results_b = branching_pipeline(data, n_jobs=2)
    # >>> [6,9], [1,1]

Pipes and branches can also be executed in a distributed fashion across a cluster by using (Py)Spark.

Currently, only a Mesos cluster managed by Zookeeper is supported.

`See here https://github.com/ftzeng/docker-mesos-pyspark-hdfs`_ for some Docker files to help you setup a cluster to work with (`see here http://spaceandtim.es/code/mesos_spark_zookeeper_hdfs_docker`_ for more details)).

You should also create a config file at ``/etc/atoll/conf/distrib.yaml`` which specifies:
    - ``spark_binary``: Where to fetch a Spark binary archive
    - ``zookeeper_host``: The ``ip:port`` of your Zookeeper host

For example:

.. code-block:: yaml

    spark_binary: http://d3kbcqa49mib13.cloudfront.net/spark-1.5.0-bin-hadoop2.6.tgz
    zookeeper_host: 172.17.0.1:2181

Note that if you are using Docker for your cluster, you may need to export the following env variables before running your pipeline:

.. code-block:: bash

    export LIBPROCESS_IP=$(ifconfig docker0 | grep 'inet addr:' | cut -d: -f2 | awk '{print $1}')
    export PYSPARK_PYTHON=/usr/bin/python3

Then, to run a pipeline on the cluster, just pass ``distributed=True`` when calling the pipeline, e.g:

.. code-block:: python

    pipeline = Pipeline().map(lowercase).map(tokenize)
    results = pipeline(data, distributed=True)

