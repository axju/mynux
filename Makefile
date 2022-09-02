#* Variables
SHELL := /usr/bin/env bash
PYTHON := python
PYTHONPATH := `pwd`

#* Installation
.PHONY: install
install:
	poetry install -n
	poetry run pre-commit install

.PHONY: pre-commit-install
pre-commit-install:
	poetry run pre-commit install

#* Formatters
.PHONY: codestyle
codestyle:
	poetry run pyupgrade --exit-zero-even-if-changed --py37-plus **/*.py
	poetry run isort --settings-path pyproject.toml mynux
	poetry run black --config pyproject.toml mynux

.PHONY: formatting
formatting: codestyle

#* Linting
.PHONY: test
test:
	PYTHONPATH=$(PYTHONPATH) poetry run pytest -c pyproject.toml --cov-report=html tests/

.PHONY: coverage
coverage:
	PYTHONPATH=$(PYTHONPATH) poetry run pytest -c pyproject.toml --cov-report=html tests/
	poetry run coverage-badge -o assets/images/coverage.svg -f

.PHONY: pylint
pylint:
	poetry run pylint --rcfile pyproject.toml mynux/

.PHONY: mypy
mypy:
	poetry run mypy --config-file pyproject.toml -p mynux

.PHONY: check-safety
check-safety:
	poetry check
	poetry run safety check --full-report
	poetry run bandit -r -c pyproject.toml mynux

.PHONY: test-all
test-all: test mypy pylint check-safety

.PHONY: tox
tox:
	poetry run tox
