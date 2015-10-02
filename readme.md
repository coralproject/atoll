# atoll
### A microservice for data analysis pipelines

## Installation

Install via `pip`:

    pip install git+https://github.com/coralproject/atoll

`atoll` supports both Python 3 and Python 2.7, but Python 3 is recommended.

## Setup

When running `atoll` as a microservice, you can provide the following configuration files:

#### `service.yaml`

Expected at `/etc/atoll/conf/service.yaml`. This configures the service itself.

The important option here is the `worker_host` option, which specifies the hostname or IP of the Celery broker. By default, this value is `localhost`.

#### `pipelines.yaml`

Expected at `/etc/atoll/conf/pipelines.yaml`. This provides an easy way of composing pipelines.

An example:

```yaml
MyPipelineName:
    endpoint: /my_pipeline_endpoint
    pipeline:
        - some_module.PipeA: # with kwargs
            arg1: foo
            arg2: 10
        - another_module.PipeB
        - [PipeC, PipeD] # branch
AnotherPipeline:
    endpoint: /another_pipeline
    pipeline:
        - PipeE
        - MyPipelineName # nested pipelines
```

The pipes will automatically be imported, if they exist, the pipeline will be automatically constructed, if it is valid, and then that pipeline will be registered to the specified endpoint.


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
