#!/usr/bin/env bash

set -euxo pipefail

echo "Running linters and formatters..."

uv run ruff check --fix d8s_python/ tests/
uv run ruff format d8s_python/ tests/

# if the CONTEXT env var is "ci" (which is set in .github/workflows/lint.yml), validate that none of the files
# have been changed by the previous lint steps
if [ "${CONTEXT:-local}" = "ci" ]; then
    (git status | grep "nothing to commit") || { echo "Lint steps have changed files"; exit 1; };
fi

uv run mypy d8s_python/ tests/
uv run ruff check d8s_python/ tests/

echo "Done ✨ 🎉 ✨"
