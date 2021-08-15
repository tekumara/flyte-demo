# aircraft

aircraft etl example using Flyte, adapted from the [Prefect Tutorial Aircraft ETL Example](https://docs.prefect.io/core/tutorial/01-etl-before-prefect.html)

## Development

### Prerequisites

- make
- node (required for pyright. Install via `brew install node`)
- python >= 3.7

### Getting started

To get started run `make install`. This will:

- install git hooks for formatting & linting on git push
- create the virtualenv in _.venv/_
- install this package in editable mode

Then run `make` to see the options for running checks, tests etc.

`. .venv/bin/activate` activates the virtualenv. When the requirements in `setup.py` change, the virtualenv is updated by the make targets that use the virtualenv.

### Usage

Once the virtualenv has been created and activated, you can run the scripts locally, eg:

```
python aircraft/02_etl_flow.py
```

To run in the [Flyte sandbox](https://docs.flyte.org/en/latest/deployment/sandbox.html):

```
# Start sandbox, mounting the current dir (ie: this repo)
flytectl sandbox start --source .

# Build the docker container inside the sandbox
flytectl sandbox exec -- docker build . --tag aircraft:v1

# Package (serialise to protobuf)
pyflyte package --image aircraft:v1

# Register 
flytectl register files --project flyteexamples --domain development --archive flyte-package.tgz --version v1

# Create execution spec from launchplan
flytectl get launchplan -p flyteexamples -d development aircraft.02_etl_flow.main --execFile exec.yaml

# Execute
fytectl create execution --project flytesnacks --domain development --execFile exec.yaml
```
