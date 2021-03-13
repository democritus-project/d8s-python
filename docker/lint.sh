#!/usr/bin/env bash

set -euxo pipefail

echo "Running linters and formatters..."

isort democritus_python/ tests/

black democritus_python/ tests/

mypy democritus_python/ tests/

pylint --fail-under 9 democritus_python/*.py

flake8 democritus_python/ tests/

bandit -r democritus_python/

# we run black again at the end to undo any odd changes made by any of the linters above
black democritus_python/ tests/
