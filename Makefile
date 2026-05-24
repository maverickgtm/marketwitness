PYTHONPATH := src
PYTHON := python3

.PHONY: test demo clean

test:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s tests -v

demo:
	mkdir -p build/demo
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit evaluate \
		--targets data/samples/targets.csv \
		--prices data/samples/prices.csv \
		--output build/demo/evaluations.csv \
		--report build/demo/report.md \
		--minimum-sample 1 \
		--as-of 2025-01-01

clean:
	rm -rf build
