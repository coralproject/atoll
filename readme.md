# atoll
### A microservice for data analysis pipelines

`atoll` requires Python 3.4+.

## Installation

You can use `atoll` in your own projects as well! Install the latest version like so (at this point in development, the PyPi version may not be up-to-date):

    pip install git+https://github.com/coralproject/atoll

_Note: this does not install Coral-specific modules. This will only give you the pipeline framework!_

## Configuration

When running `atoll` as a microservice, you can specify a YAML config file by setting the `ATOLL_CONF` env variable, e.g.

    export ATOLL_CONF=/path/to/my/conf.yaml

The default configuration is:

```yaml
worker_broker: amqp://guest:guest@localhost/
worker_backend: amqp
executor_host: 127.0.0.1:8786
```

The `worker_broker` and `worker_backend` options define how `celery`, which is used to handle requests, is configured.

The `executor_host` is for distributed computation of pipelines - see the "Distributed" section below.

## Setup

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

## Distributed computing support

NOTE: Distributed computing support is still somewhat experimental, at this moment it supports the full `atoll` pipeline API but its stability is not guaranteed.

`atoll` can run its pipelines either on a single computer with multiprocessing or across a cluster (using the [`distributed`](https://github.com/dask/distributed) library).

To run pipelines across a cluster, you will need to provide the following configuration option:

- `executor_host`: where the cluster executor is, by default, `127.0.0.1:8786`

See the config above for an example.

Then, to run a pipeline on the cluster, just pass `distributed=True` when calling the pipeline, e.g:

```python
pipeline = Pipeline().map(foo).map(bar)
results = pipeline(input, distributed=True)
```

### Setting up a cluster

Setting up a cluster is fairly easy - just setup the necessary (virtual) environment on and passwordless SSH access to each worker node.

Then, from the leader (i.e. the executor) machine, run:

    dcluster <worker ip> <worker ip> ...

The IP of this executor machine is what goes in the `executor_host` configuration option.

Refer to the [`distributed` documentation](http://distributed.readthedocs.org/en/latest/quickstart.html) for more details.

## Deployment

To deploy, clone this repo then `cd` into `deploy`.

First, run `setup.sh` to setup your local machine for deployment.

Then setup the git ssh keys and server key in the `deploy/keys` folder (ask me for them if necessary).

You may need to edit `hosts.ini` to point to the proper servers.

Then you should be able to run `deploy.sh <ENV NAME>` to deploy the Coral Atoll instance, where `ENV NAME` is one of `[development production]`.

Once you deploy, you can run `test.py` to sanity-check that the service is working properly.

See `deploy/readme.md` for more info.

## Documentation

See the docs: (hosted docs coming soon)

For now, you can build them yourself:

    git submodule update --init
    cd docs
    make clean; make html

Then open `_build/html/index.html`


## Development

If you are interested in contributing to `atoll`, great! Here's how you can get it setup for development.

Ensure that you have Python 3.4 or later installed on your system.

For OSX, this can be accomplished with `brew`:

    brew install python3

A virtual environment is recommended as well:

    pip3 install virtualenv
    virtualenv -p python3 ~/env/atoll --no-site-packages

Then activate the `virtualenv`:

    source ~/env/atoll/bin/activate

Then clone this repo somewhere on your system:

    git clone https://github.com/coralproject/atoll.git

Install the requirements:

    pip install -r requirements.txt

To run the `coral-atoll` instance, change into the repo directory and run:

    python coral.py

The server will then run at `localhost:5001`.

---

## Notes

- Until `joblib` switches from `pickle` to `dill` for serialization (see <https://github.com/joblib/joblib/pull/240>) we can't use lambdas: functions used in pipelines must be defined at the top-level of a module.
