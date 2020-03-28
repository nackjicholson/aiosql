#!/bin/sh -e


if [ -z "$POSTGRES_DSN" ] ; then
    echo "Variable POSTGRES_DSN must be set."
    exit 1
fi

set -x

PYTHONPATH=. pytest --ignore venv -W ignore::DeprecationWarning
