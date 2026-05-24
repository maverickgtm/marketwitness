PYTHONPATH := src
PYTHON := python3

.PHONY: test demo package verify clean

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
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit ipo-watch \
		--registry data/samples/ipo_watch.csv \
		--report build/demo/ipo-watch.md \
		--html build/demo/ipo-watch.html \
		--as-of 2026-05-24

package:
	mkdir -p build/dist
	$(PYTHON) -m pip wheel --no-deps --no-build-isolation . -w build/dist

verify: test demo package

clean:
	rm -rf build
