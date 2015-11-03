# atoll
### A microservice for data analysis pipelines

## Installation

Install via `pip`:

    pip install git+https://github.com/coralproject/atoll

`atoll` supports both Python 3 and Python 2.7, but Python 3 is recommended (Python 2.7 support is not fully tested).

## Setup

When running `atoll` as a microservice, you can provide the following configuration files:

#### `service.yaml`

Expected at `/etc/atoll/conf/service.yaml`. This configures the service itself.

The important option here is the `worker_host` option, which specifies the hostname or IP of the Celery broker. By default, this value is `localhost`.

## Usage

See the docs: (hosted docs coming soon)

For now, you can build them yourself:

    cd docs
    make clean; make html

Then open `_build/html/index.html`

## Development

If you are running the microservice and using asynchronous requests (i.e. callbacks), you need a Celery stack.

The provided `run` script makes it easy to get this up and running. Install Docker if you do not have it, and then the following commands are available:

    # Pull the necessary Docker images
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

To run a pipeline across a Spark cluster, there are a few prerequisites:

- A Spark cluster managed by Zookeeper ([see here](https://github.com/ftzeng/docker-mesos-pyspark-hdfs) for some Docker files to get you going, [see here](http://spaceandtim.es/code/mesos_spark_zookeeper_hdfs_docker) for more details)
- A config file at `/etc/atoll/conf/distrib.yaml` which specifies:
    - `spark_binary`: Where to fetch a Spark binary archive
    - `zookeeper_host`: The `ip:port` of your Zookeeper host

An example config:

```yaml
spark_binary: http://d3kbcqa49mib13.cloudfront.net/spark-1.5.0-bin-hadoop2.6.tgz
zookeeper_host: 172.17.0.1:2181
```

Note that if you are using Docker for your cluster, you may need to export the following env variables before running your pipeline:

```bash
export LIBPROCESS_IP=$(ifconfig docker0 | grep 'inet addr:' | cut -d: -f2 | awk '{print $1}')
export PYSPARK_PYTHON=/usr/bin/python3
```

Then, to run a pipeline on the cluster, just pass `distributed=True` when calling the pipeline, e.g:

```python
pipeline = Pipeline().map(foo).map(bar)
results = pipeline(input, distributed=True)
```

This support is still being worked on; it currently only supports Mesos clusters.
