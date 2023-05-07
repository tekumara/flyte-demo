# Flyte Demo

aircraft etl example using Flyte, adapted from the [Prefect Tutorial Aircraft ETL Example](https://docs.prefect.io/core/tutorial/01-etl-before-prefect.html)

## Prerequisites

- make
- node (required for pyright)
- python >= 3.10
- docker

## Getting started

To get started run `make install`. This will:

- install git hooks for formatting & linting on git push
- create the virtualenv in _.venv/_
- install this package in editable mode

Then run `make` to see the options for running checks, tests etc.

`. .venv/bin/activate` activates the virtualenv. When the requirements in `setup.py` change, the virtualenv is updated by the make targets that use the virtualenv.

Install flytectl:

```
make install-flytectl
```

## Flyte Usage

Once the virtualenv has been created and activated, you can run the worklow locally, eg:

```
make run
```

To run in the [Flyte sandbox](https://docs.flyte.org/en/latest/deployment/sandbox.html):

```
## Start sandbox, mounting the current dir (ie: this repo)
make sandbox 

## Build the docker image inside the sandbox
make build

## Deploy, ie: register and execute
make deploy 

## Visualise the execution graph
make viz

## Monitor
flytectl get execution --project flyteexamples --domain development [name]
```

Interactive commands (eg: bash) won't work properly inside the sandbox (you don't get their output).
But you can run non-interactive commands, eg:

```
flytectl sandbox exec -- ls /root
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

### \[LIMIT_EXCEEDED\] limit exceeded

[Increase the storage](https://github.com/flyteorg/flyte/discussions/1342) of the sandbox.

### Last Error: USER::containers with unready status: ... Back-off pulling image "aircraft:latest"

Don't use the tag `latest` because Kubes will try and pull, but the image won't exist. See [Error: ImagePullBackOff](https://docs.flyte.org/en/latest/community/troubleshoot.html#error-imagepullbackoff).
