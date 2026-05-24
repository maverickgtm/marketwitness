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
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit sec-ipo-discover \
		--date 2026-05-20 \
		--index-file data/samples/sec-master-sample.idx \
		--output build/demo/sec-ipo-discovery.csv \
		--report build/demo/sec-ipo-discovery.md
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit sec-ipo-alerts \
		--discovery build/demo/sec-ipo-discovery.csv \
		--watchlist data/samples/ipo_watch.csv \
		--previous-history-dir data/samples/sec-alerts-history \
		--history-dir build/demo/sec-history \
		--output build/demo/sec-alerts.csv \
		--report build/demo/sec-alerts.md \
		--html build/demo/sec-alerts.html \
		--as-of 2026-05-20
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit ipo-watch-review \
		--alerts build/demo/sec-alerts.csv \
		--registry data/samples/ipo_watch.csv \
		--decisions data/samples/sec-review-decisions.csv \
		--output-registry build/demo/ipo-watch-reviewed.csv \
		--output build/demo/sec-review-outcomes.csv \
		--report build/demo/sec-review-outcomes.md \
		--html build/demo/sec-review-outcomes.html \
		--as-of 2026-05-20
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit ipo-watch \
		--registry build/demo/ipo-watch-reviewed.csv \
		--report build/demo/ipo-watch.md \
		--html build/demo/ipo-watch.html \
		--as-of 2026-05-24
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit global-listings \
		--sources data/samples/global_market_sources.csv \
		--report build/demo/global-listings.md \
		--html build/demo/global-listings.html \
		--as-of 2026-05-24
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit issuer-confirmations \
		--registry data/samples/issuer_listing_confirmations.csv \
		--report build/demo/issuer-confirmations.md \
		--html build/demo/issuer-confirmations.html \
		--as-of 2026-05-24
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit corporate-actions-check \
		--targets data/samples/targets.csv \
		--actions data/samples/corporate_actions.csv \
		--output build/demo/corporate-actions.csv \
		--report build/demo/corporate-actions.md \
		--html build/demo/corporate-actions.html \
		--as-of 2026-05-24
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit evaluate \
		--targets data/samples/targets.csv \
		--prices data/samples/prices.csv \
		--corporate-actions data/samples/corporate_actions.csv \
		--output build/demo/evaluations-actions-guarded.csv \
		--report build/demo/report-actions-guarded.md \
		--minimum-sample 1 \
		--as-of 2025-01-01
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit lse-upcoming \
		--page-file data/samples/lse-new-issues-page.json \
		--output build/demo/lse-upcoming.csv \
		--report build/demo/lse-upcoming.md \
		--html build/demo/lse-upcoming.html \
		--as-of 2026-05-24
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit lse-fca-check \
		--lse-page-file data/samples/lse-new-issues-page.json \
		--nsm-fixture data/samples/fca-nsm-results.json \
		--output build/demo/lse-fca-check.csv \
		--report build/demo/lse-fca-check.md \
		--html build/demo/lse-fca-check.html \
		--as-of 2026-05-24
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit hkex-monitor \
		--snapshot-dir data/samples/hkex \
		--output build/demo/hkex-monitor.csv \
		--report build/demo/hkex-monitor.md \
		--html build/demo/hkex-monitor.html \
		--as-of 2026-05-24
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit asx-monitor \
		--snapshot data/samples/asx-upcoming.html \
		--output build/demo/asx-monitor.csv \
		--report build/demo/asx-monitor.md \
		--html build/demo/asx-monitor.html \
		--as-of 2026-05-24
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit tsx-monitor \
		--snapshot data/samples/tsx-new-listings.html \
		--output build/demo/tsx-monitor.csv \
		--report build/demo/tsx-monitor.md \
		--html build/demo/tsx-monitor.html \
		--as-of 2026-05-24
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit sgx-monitor \
		--snapshot data/samples/sgx-ipo-prospectus.json \
		--output build/demo/sgx-monitor.csv \
		--report build/demo/sgx-monitor.md \
		--html build/demo/sgx-monitor.html \
		--as-of 2026-05-24
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit global-alerts \
		--hkex build/demo/hkex-monitor.csv \
		--lse build/demo/lse-upcoming.csv \
		--asx build/demo/asx-monitor.csv \
		--tsx build/demo/tsx-monitor.csv \
		--sgx build/demo/sgx-monitor.csv \
		--previous-dir data/samples/global-alerts-previous \
		--output build/demo/global-alerts.csv \
		--report build/demo/global-alerts.md \
		--html build/demo/global-alerts.html \
		--as-of 2026-05-24

package:
	mkdir -p build/dist
	$(PYTHON) -m pip wheel --no-deps --no-build-isolation . -w build/dist

verify: test demo package

clean:
	rm -rf build
