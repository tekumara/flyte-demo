# aircraft

aircraft etl example using Flyte, adapted from the [Prefect Tutorial Aircraft ETL Example](https://docs.prefect.io/core/tutorial/01-etl-before-prefect.html)

## Prerequisites

- make
- node (required for pyright. Install via `brew install node`)
- python >= 3.7

## Getting started

To get started run `make install`. This will:

- install git hooks for formatting & linting on git push
- create the virtualenv in _.venv/_
- install this package in editable mode

Then run `make` to see the options for running checks, tests etc.

`. .venv/bin/activate` activates the virtualenv. When the requirements in `setup.py` change, the virtualenv is updated by the make targets that use the virtualenv.

Install flytectl:

```
brew install flyteorg/homebrew-tap/flytectl
```

## Flyte Usage

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
pyflyte --pkgs aircraft package -f --image aircraft:v1

# tell flytectl where to find the config file (if not using direnv)
export FLYTECTL_CONFIG=$HOME/.flyte/config-sandbox.yaml

# Register
flytectl register files --project flyteexamples --domain development --archive flyte-package.tgz --version v1

# Visualise the execution graph
flytectl get workflows --project flyteexamples --domain development aircraft.02_etl_flow.main --version v1 -o doturl

# Create execution spec from launchplan
flytectl get launchplan -p flyteexamples -d development aircraft.02_etl_flow.main --execFile exec.yaml

# Execute
flytectl create execution --project flyteexamples --domain development --execFile exec.yaml

# Monitor
flytectl get execution --project flyteexamples --domain development [name]
```

Accessing kubes:

```
# set kubeconfig (if not using direnv)
export KUBECONFIG=$HOME/.flyte/k3s/k3s.yaml

# set default namespace to aid debugging
kubectl config set-context --current --namespace=flyteexamples-development
```

Visit the UI: [http://localhost:30081/console](http://localhost:30081/console)

For more info see [Building Large Apps - Deploy to the Cloud](https://docs.flyte.org/projects/cookbook/en/latest/auto/larger_apps/larger_apps_deploy.html)

## Known issues

[What is the distinction between flytectl sandbox and flytectl demo](https://github.com/flyteorg/flyte/issues/2503)

## Troubleshooting

### [LIMIT_EXCEEDED] limit exceeded

[Increase the storage](https://github.com/flyteorg/flyte/discussions/1342) of the sandbox.
