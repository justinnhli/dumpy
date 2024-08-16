#!/bin/bash

set -euo pipefail

PYTHON3=$HOME/.local/share/venv/dumpy-test/bin/python3
$PYTHON3 -m coverage run -m pytest
$PYTHON3 -m coverage html
