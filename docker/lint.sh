#!/usr/bin/env bash

set -euxo pipefail

echo "Running linters and formatters..."

isort d8s_python/ tests/

black d8s_python/ tests/

# mypy d8s_python/ tests/

pylint --fail-under 9 d8s_python/*.py

flake8 d8s_python/ tests/
