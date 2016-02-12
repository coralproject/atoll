# atoll
### A microservice for data analysis pipelines

## Quickstart

### Environment

Ensure we have Python 3.4+

If your python environment is pre 3.4+, this will install python3 (on OSX), set up the environment without disrupting your current python install:
```
brew install python3
pip3 install virtualenv
virtualenv -p python3 ~/env/python3 --no-site-packages
```

Each time you want to use python3, just
```
source env/bin/activate
```

### Installation

Clone this repo somewhere on your system:
```
cd /where/you/want/it
git clone https://github.com/coralproject/atoll.git
pip install -r requirements.txt
```

### Run

```
python coral.py
```

The server will then run on port :5001

You should be able to see the docs here:

```
http://localhost:5001/doc
```

### Install via `pip`:

_Note: this does not install coral specific modules. This will only give you the pipeline framework!_

    pip install git+https://github.com/coralproject/atoll

`atoll` supports Python 3.4+

## Setup

When running `atoll` as a microservice, you can specify a YAML config file by setting the `ATOLL_CONF` env variable, e.g.

    export ATOLL_CONF=/path/to/my/conf.yaml

The default configuration is:

```yaml
worker_broker: amqp://guest:guest@localhost/
worker_backend: amqp
executor_host: 127.0.0.1:8786
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

---

## Notes

- Until `joblib` switches from `pickle` to `dill` for serialization (see <https://github.com/joblib/joblib/pull/240>) we can't use lambdas: functions used in pipelines must be defined at the top-level of a module.
