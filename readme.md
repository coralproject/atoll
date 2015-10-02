# atoll
### A microservice for data analysis pipelines

## Installation

Install via `pip`:

    pip install git+https://github.com/coralproject/atoll

`atoll` supports both Python 3 and Python 2.7, but Python 3 is recommended.

## Setup

(config options will be here)

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
