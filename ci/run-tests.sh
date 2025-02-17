#!/bin/bash

set -euo pipefail

# set python3 executable
PYTHON3=$HOME/.local/share/venv/dumpy/bin/python3
# run tests
$PYTHON3 -m coverage run -m pytest -v "$@"
# generate coverage report if all tests were run
$PYTHON3 -m coverage html
