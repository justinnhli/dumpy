#!/bin/bash

set -euo pipefail

mypylint.py dumpy tests demos 2>&1 | grep -v 'no-name-in-module' | grep -v 'import-error'
