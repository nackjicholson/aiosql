#!/usr/bin/env bash

set -euo pipefail

# add sphinx specific entries when generating the doc so that pypi will not complain

cat >> docs/source/index.rst <<EOF


Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   Getting Started <getting-started>
   Defining SQL Queries <defining-sql-queries>
   Advanced Topics <advanced-topics>
   Database Driver Adapters <database-driver-adapters>
   Contributing <contributing>
   API <pydoc/modules>
EOF

sphinx-apidoc -f -o docs/source/pydoc aiosql
sphinx-build -b html docs/source docs/build
