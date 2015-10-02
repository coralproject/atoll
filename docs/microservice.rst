The microservice
================

A simple microservice server is included which allows you to post data to your pipelines from elsewhere.

You can register your own pipelines using the provided ``register_pipeline`` function:

.. code-block:: python

    from atoll import register_pipeline
    register_pipeline('/percent_vowel_endings', pipeline)

Then you can post data in the proper format (as a JSON object with your data at the ``data`` key) to that endpoint, which will be at ``/pipelines/percent_vowel_endings``::

    curl -X POST -H "Content-Type: application/json" -d '{"data": ["this is a test", "another test"]}' http://localhost:5001/pipelines/percent_vowel_endings
    {"results": [0.25, 0]}

(Assuming you are running the microservice locally on port 5001)

You can additionally specify a callback url to run the task asynchronously::

    curl -X POST -H "Content-Type: application/json" -d '{"data": ["this is a test", "another test"], "callback": "http://mysite.com/callback"}' http://localhost:5001/pipelines/percent_vowel_endings
    {"results": [0.25, 0]} will be POSTed to the callback url
