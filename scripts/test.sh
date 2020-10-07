#!/bin/bash

set -e

poetry run python -m black --check obschartpybackend tests
poetry run python -m mypy obschartpybackend tests
pyright
