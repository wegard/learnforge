.PHONY: install lint validate test build-samples

install:
	python3 -m pip install -e .[dev]

lint:
	ruff check app tests

validate:
	teach validate

test:
	pytest -q

build-samples:
	python scripts/build_representative_targets.py
