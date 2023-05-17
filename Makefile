include *.mk
include .envrc

v ?= v1
image = localhost:30000/aircraft:$(v)

## Install flytectl (requires sudo)
flytectl:
	tools/install_flytectl.sh

## Run locally
run: $(venv)
	$(venv)/bin/pyflyte run aircraft/etl_flow.py main

~/.flyte/sandbox/config.yaml: infra/config.yaml
	mkdir -p ~/.flyte/sandbox
	cp infra/config.yaml ~/.flyte/sandbox/config.yaml

## Create demo sandbox
sandbox: ~/.flyte/sandbox/config.yaml
	flytectl demo start

## Tail sandbox logs
sandbox-logs:
	docker logs -f flyte-sandbox

## Start the sandbox
start:
	docker start flyte-sandbox

## Reload sandbox (useful after changing config.yaml)
reload: ~/.flyte/sandbox/config.yaml
	flytectl demo reload

## Build docker image and push to the sandbox docker registry
build:
	docker build --push --tag $(image) .

## Deploy, ie: register and execute
deploy: $(venv)
# Package (serialise to protobuf)
	$(venv)/bin/pyflyte --pkgs aircraft package -f --image $(image)

# Register
	rm -f exec.yaml
	flytectl register files --project flytesnacks --domain development --archive flyte-package.tgz --version $(v)

# Create execution spec from launchplan
	flytectl get launchplan -p flytesnacks -d development aircraft.etl_flow.main --execFile exec.yaml

# Execute
	flytectl create execution --project flytesnacks --domain development --execFile exec.yaml

	@echo Visit the UI: http://localhost:30080/console/projects/flytesnacks/executions?domain=development&duration=all

# Visualise the execution graph
viz: $(venv)
	flytectl get workflows --project flytesnacks --domain development aircraft.etl_flow.main --version $(v) -o doturl

# Get all executions
ge:
	flytectl get execution --project flytesnacks --domain development

# Get task definitions for version
gt:
# filter use jq until https://github.com/flyteorg/flyte/issues/3679
	flytectl get task -p flytesnacks -d development -o json | jq 'map(select(.id.version == "$(v)"))'

