#!/usr/bin/env bash
set -euo pipefail

python -m build --sdist
python -m build --wheel
