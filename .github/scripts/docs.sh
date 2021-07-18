#!/usr/bin/env bash
set -euo pipefail

sphinx-apidoc -f -o docs/source/pydoc aiosql
sphinx-build -b html docs/source docs/build
