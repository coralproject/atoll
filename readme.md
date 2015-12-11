# atoll
### A microservice for data analysis pipelines

## Installation

Install via `pip`:

    pip install git+https://github.com/coralproject/atoll

`atoll` supports Python 3.4+

## Setup

When running `atoll` as a microservice, you can specify a YAML config file by setting the `ATOLL_CONF` env variable, e.g.

    export ATOLL_CONF=/path/to/my/conf.yaml

The default configuration is:

```yaml
worker_broker: amqp://guest:guest@localhost/
worker_backend: amqp

# this must be a _prebuilt_ spark archive, i.e. a spark binary package
# you can build it and host it yourself if you like.
spark_binary: http://d3kbcqa49mib13.cloudfront.net/spark-1.5.0-bin-hadoop2.6.tgz
zookeeper_host: 172.17.0.1:2181
```

## Usage

See the docs: (hosted docs coming soon)

For now, you can build them yourself:

    git submodule update --init
    cd docs
    make clean; make html

Then open `_build/html/index.html`

## Development

If you are running the microservice and using asynchronous requests (i.e. callbacks), you need a Celery stack.

The provided `run` script makes it easy to get this up and running. Install Docker if you do not have it, and then the following commands are available:

    # Pull the necessary Docker images,
    # setup the Docker containers
    ./run setup

    # Start the RabbitMQ container (the Celery broker)
    ./run rabbitmq

    # Start a Celery worker
    ./run worker

    # View the cluster status
    ./run status

    # Spin down the stack
    ./run stop

## (Py)Spark support

`atoll` can run its pipelines either on a single computer with multiprocessing or across a Spark cluster.

To run a pipeline across a Spark cluster you must have a Spark cluster managed by Zookeeper ([see here](https://github.com/ftzeng/docker-mesos-pyspark-hdfs) for some Docker files to get you going, [see here](http://spaceandtim.es/code/mesos_spark_zookeeper_hdfs_docker) for more details).

Additionally, you will likely want to provide a config (see above) which specifies:

- `spark_binary`: Where to fetch a Spark binary archive
- `zookeeper_host`: The `ip:port` of your Zookeeper host

See the config above for an example.

Note that if you are using Docker for your cluster, you may need to export the following env variables before running your pipeline:

    export LIBPROCESS_IP=$(ifconfig docker0 | grep 'inet addr:' | cut -d: -f2 | awk '{print $1}')
    export PYSPARK_PYTHON=/usr/bin/python3

Then, to run a pipeline on the cluster, just pass `distributed=True` when calling the pipeline, e.g:

```python
pipeline = Pipeline().map(foo).map(bar)
results = pipeline(input, distributed=True)
```

This support is still being worked on; it currently only supports Mesos clusters.

## Deployment

To deploy, clone this repo then `cd` into `deploy`.

First, run `setup.sh` to setup your local machine for deployment.

Then setup the git ssh keys and server key in the `deploy/keys` folder (ask me for them if necessary).

You may need to edit `hosts.ini` to point to the proper servers.

Then you should be able to run `deploy.sh <ENV NAME>` to deploy the Coral Atoll instance, where `ENV NAME` is one of `[development production]`.

Once you deploy, you can run `test.py` to sanity-check that the service is working properly.

See `deploy/readme.md` for more info.

---

## Notes

- Until `joblib` switches from `pickle` to `dill` for serialization (see <https://github.com/joblib/joblib/pull/240>) we can't use lambdas: functions used in pipelines must be defined at the top-level of a module.
