.PHONY: help format install lint test

help:
	@grep '^\.PHONY' Makefile | cut -d' ' -f2- | tr ' ' '\n'

format:
	poetry run isort --profile black .
	poetry run black .

install:
	# TODO: Remove. Workaround for
	# https://github.com/frictionlessdata/frictionless-py/issues/908
	# https://github.com/danthedeckie/simpleeval/issues/90
	# https://github.com/danthedeckie/simpleeval/pull/91
	poetry run pip install 'setuptools==57.5.0'
	poetry install

lint:
	poetry run isort --profile black -c --diff .
	poetry run black --check .
	poetry run flake8 .

test:
	poetry run coverage run --source=datapackage_to_datasette ./run_tests.py
	poetry run coverage xml
