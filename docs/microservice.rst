The microservice
================

A simple microservice server is included which allows you to post data to your pipelines from elsewhere.

Create an instance of the service like so:

.. code-block:: python

    from atoll import Atoll

    service = Atoll()

You can register your own pipelines using the provided ``register_pipeline`` method:

.. code-block:: python

    service.register_pipeline('/percent_vowel_endings', pipeline)

Once you have registered your pipelines, create the app and run it:

.. code-block:: python

    service.create_app()
    service.run(debug=True, port=5001)

Note that your pipelines must be registered *before* you run ``create_app``.

Then you can post data in the proper format (as a JSON object with your data at the ``data`` key) to that endpoint, which will be at ``/pipelines/percent_vowel_endings``::

    curl -X POST -H "Content-Type: application/json" -d '{"data": ["this is a test", "another test"]}' http://localhost:5001/pipelines/percent_vowel_endings
    {"results": [0.25, 0]}

(Assuming you are running the microservice locally on port 5001)

You can additionally specify a callback url to run the task asynchronously::

    curl -X POST -H "Content-Type: application/json" -d '{"data": ["this is a test", "another test"], "callback": "http://mysite.com/callback"}' http://localhost:5001/pipelines/percent_vowel_endings
    {"results": [0.25, 0]} will be POSTed to the callback url


.. _configuration:

Configuration
-------------

You can provide a configuration for the microservice in a YAML file. The default config is:

.. code-block:: yaml

    worker_broker: amqp://guest:guest@localhost/
    worker_backend: amqp

    # this must be a _prebuilt_ spark archive, i.e. a spark binary package
    # you can build it and host it yourself if you like.
    spark_binary: http://d3kbcqa49mib13.cloudfront.net/spark-1.5.0-bin-hadoop2.6.tgz
    zookeeper_host: 172.17.0.1:2181

The important option here is the ``worker_broker`` option, which specifies the connection string for the Celery broker.

You must specify the path to this config as an environment variable:

.. code-block:: bash

    export ATOLL_CONF=/path/to/my/config.yaml

