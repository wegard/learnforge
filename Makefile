.PHONY: install validate test build-samples

install:
	python3 -m pip install -e .[dev]

validate:
	teach validate

test:
	pytest

build-samples:
	teach build iv-intuition --audience student --lang en --format html
	teach build iv-intuition --audience student --lang nb --format html
	teach build lecture-04 --audience teacher --lang nb --format revealjs
	teach build lecture-04 --audience teacher --lang nb --format pdf
	teach build ec202 --audience student --lang nb --format html
