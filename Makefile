.PHONY: install lint validate test build-samples mamba-bootstrap

RUN_IN_ENV := ./scripts/run-in-env.sh

install:
	$(RUN_IN_ENV) python -m pip install -e ".[dev]"

lint:
	$(RUN_IN_ENV) python -m ruff check app tests

validate:
	$(RUN_IN_ENV) teach validate

test:
	$(RUN_IN_ENV) python -m pytest -q

build-samples:
	$(RUN_IN_ENV) python scripts/build_representative_targets.py

mamba-bootstrap:
	./scripts/bootstrap_micromamba.sh
