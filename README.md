# Flyte Demo

aircraft etl example using Flyte, adapted from the [Prefect Tutorial Aircraft ETL Example](https://docs-v1.prefect.io/core/tutorial/01-etl-before-prefect.html)

## Getting started

Prerequisites:

- make
- node (required for pyright)
- python >= 3.10
- docker

To start:

- Install the [development environment](CONTRIBUTING.md#getting-started): `make install`
- Install flytectl: `make flytectl`

## Flyte Usage

Once the virtualenv has been created and activated, you can run the worklow locally, eg:

```
make run
```

To run in the [Flyte sandbox](https://docs.flyte.org/en/latest/deployment/deployment/sandbox.html):

```
## Start demo sandbox, mounting the current dir (ie: this repo)
make sandbox 

## Build the docker image and push it to the sandbox
make build

## Deploy, ie: register and execute
make deploy 

## Visualise the execution graph
make viz

## Monitor ie: get all executions
make ge
```

Interactive commands (eg: ash) won't work properly inside the sandbox (you don't get their output).
But you can run non-interactive commands, eg:

```
flytectl sandbox exec -- ls
```

Accessing kubes:

```
# set kubeconfig (if not using direnv)
export KUBECONFIG=$HOME/.flyte/config-sandbox.yaml

# set default namespace to aid debugging
kubectl config set-context --current --namespace=flytesnacks-development
```

Visit the UI: [http://localhost:30080/console](http://localhost:30080/console)

## FAQ

[What is the distinction between flytectl sandbox and flytectl demo](https://github.com/flyteorg/flyte/issues/2503)

## Troubleshooting

### Last Error: USER::containers with unready status: ... Back-off pulling image "aircraft:latest"

Don't use the tag `latest` because Kubes will try and pull, but the image won't exist. See [Error: ImagePullBackOff](https://docs.flyte.org/en/latest/community/troubleshoot.html#error-imagepullbackoff).
