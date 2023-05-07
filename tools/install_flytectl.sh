#! /usr/bin/env bash

case "$(uname -s)" in
    "Darwin") brew install flyteorg/homebrew-tap/flytectl ;;
    "Linux") curl -sL https://ctl.flyte.org/install | sudo bash -s -- -b /usr/local/bin ;;
    *) echo "error: unknown arch $(uname -s)" && exit 42;;
esac
