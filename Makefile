include *.mk
include .envrc

v ?= v1

## Install flytectl (requires sudo)
install-flytectl:
	tools/install_flytectl.sh
	
## Run locally
run: $(venv)
	$(venv)/bin/python aircraft/etl_flow.py

## Start sandbox, mounting the current dir (ie: this repo)
sandbox:
	flytectl sandbox start --source .

## Build docker image within sandbox
build:
	flytectl sandbox exec -- docker build /root --tag aircraft:$(v)

## Deploy, ie: register and execute
deploy: $(venv)
# Package (serialise to protobuf)
	$(venv)/bin/pyflyte --pkgs aircraft package -f --image aircraft:$(v)

# Register
	rm -f exec.yaml
	flytectl register files --project flyteexamples --domain development --archive flyte-package.tgz --version $(v)

# Create execution spec from launchplan
	flytectl get launchplan -p flyteexamples -d development aircraft.etl_flow.main --execFile exec.yaml

# Execute
	flytectl create execution --project flyteexamples --domain development --execFile exec.yaml

	@echo Visit the UI: http://localhost:30081/console/projects/flyteexamples/executions?domain=development&duration=all

# Visualise the execution graph
viz: $(venv)
	flytectl get workflows --project flyteexamples --domain development aircraft.etl_flow.main --version $(v) -o doturl
