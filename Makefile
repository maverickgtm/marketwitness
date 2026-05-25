PYTHONPATH := src
PYTHON := python3

.PHONY: test demo package verify clean

test:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s tests -v

demo:
	mkdir -p build/demo
	rm -f build/demo/targetaudit.duckdb
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit targets-import \
		--export data/samples/authorized-target-export.csv \
		--manifest data/samples/authorized-target-export-manifest.json \
		--output build/demo/authorized-targets.csv \
		--audit build/demo/authorized-targets-audit.csv \
		--report build/demo/authorized-targets-import.md \
		--html build/demo/authorized-targets-import.html \
		--as-of 2026-05-24
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit evaluate \
		--targets build/demo/authorized-targets.csv \
		--prices data/samples/prices.csv \
		--universe-membership data/samples/historical_universe.csv \
		--prices-provider-id synthetic-demo \
		--universe-provider-id synthetic-demo \
		--output build/demo/evaluations.csv \
		--report build/demo/report.md \
		--database build/demo/targetaudit.duckdb \
		--run-id demo-financials-2025-01-01 \
		--dataset-label "Authorized target export + synthetic Financials prices" \
		--minimum-sample 1 \
		--transaction-cost-bps 10 \
		--as-of 2025-01-01
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit evaluate \
		--targets data/samples/targets_revisions.csv \
		--prices data/samples/prices_revisions.csv \
		--universe-membership data/samples/historical_universe.csv \
		--prices-provider-id synthetic-demo \
		--universe-provider-id synthetic-demo \
		--output build/demo/evaluations-target-revisions.csv \
		--report build/demo/report-target-revisions.md \
		--database build/demo/targetaudit.duckdb \
		--run-id demo-target-revisions-2025-01-01 \
		--dataset-label "Synthetic target revision audit" \
		--minimum-sample 1 \
		--transaction-cost-bps 10 \
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
		--as-of 2026-05-25
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit issuer-confirmations \
		--registry data/samples/issuer_listing_confirmations.csv \
		--report build/demo/issuer-confirmations.md \
		--html build/demo/issuer-confirmations.html \
		--as-of 2026-05-24
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit provider-approval-review \
		--registry data/samples/source_registry.csv \
		--approvals data/samples/provider_approval_queue.csv \
		--decisions data/samples/provider_approval_decisions.csv \
		--output-registry build/demo/provider-reviewed-source-registry.csv \
		--output-approvals build/demo/provider-reviewed-approval-queue.csv \
		--output build/demo/provider-approval-review-outcomes.csv \
		--report build/demo/provider-approval-review-outcomes.md \
		--html build/demo/provider-approval-review-outcomes.html \
		--as-of 2026-05-24
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit source-registry \
		--registry build/demo/provider-reviewed-source-registry.csv \
		--report build/demo/source-registry.md \
		--html build/demo/source-registry.html \
		--as-of 2026-05-24
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit open-edition \
		--registry build/demo/provider-reviewed-source-registry.csv \
		--report build/demo/open-edition.md \
		--html build/demo/open-edition.html \
		--as-of 2026-05-24
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit rwa-watch \
		--snapshot data/samples/rwa-watch-synthetic.csv \
		--report build/demo/rwa-watch.md \
		--html build/demo/rwa-watch.html \
		--as-of 2026-05-24
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit licensed-extensions \
		--catalog data/samples/licensed_extensions.csv \
		--report build/demo/licensed-extensions.md \
		--html build/demo/licensed-extensions.html \
		--as-of 2026-05-24
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit provider-approvals \
		--registry build/demo/provider-reviewed-source-registry.csv \
		--approvals build/demo/provider-reviewed-approval-queue.csv \
		--report build/demo/provider-approvals.md \
		--html build/demo/provider-approvals.html \
		--as-of 2026-05-24
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit scorecard-readiness \
		--registry build/demo/provider-reviewed-source-registry.csv \
		--report build/demo/scorecard-readiness.md \
		--html build/demo/scorecard-readiness.html \
		--as-of 2026-05-24
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit sec-nport-datasets \
		--catalog-file data/samples/sec-nport-catalog.html \
		--output build/demo/nport-dataset-catalog.csv \
		--report build/demo/nport-dataset-catalog.md
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit sec-nport-sync \
		--catalog-file data/samples/sec-nport-catalog.html \
		--state build/demo/nport-sync-state.csv \
		--storage-dir build/demo/nport-sync-storage \
		--report build/demo/nport-sync.md \
		--as-of 2026-05-24 \
		--series-id S000DEMO01 \
		--fund-symbol XLF-REG-DEMO \
		--data-set-label "Synchronized synthetic fixtures" \
		--output-dir build/demo/nport-sync-backfill \
		--manifest build/demo/nport-sync-backfill-manifest.csv \
		--backfill-report build/demo/nport-sync-backfill.md \
		--synthetic-fixture
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit ark-holdings-import \
		--snapshot data/samples/ark-holdings-previous.csv \
		--fund-symbol ARKK-DEMO \
		--fund-name "Synthetic ARK-format ETF" \
		--captured-on 2026-05-22 \
		--source-url https://example.invalid/ark-demo/2026-05-22 \
		--synthetic-fixture \
		--output build/demo/ark-holdings-previous.csv \
		--report build/demo/ark-holdings-previous-import.md
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit ark-holdings-import \
		--snapshot data/samples/ark-holdings-current.csv \
		--fund-symbol ARKK-DEMO \
		--fund-name "Synthetic ARK-format ETF" \
		--captured-on 2026-05-23 \
		--source-url https://example.invalid/ark-demo/2026-05-23 \
		--synthetic-fixture \
		--output build/demo/ark-holdings-current.csv \
		--report build/demo/ark-holdings-current-import.md
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit spdr-holdings-import \
		--snapshot data/samples/spdr-xlf-holdings-previous.csv \
		--fund-symbol XLF-DEMO \
		--fund-name "Synthetic Financials ETF" \
		--captured-on 2026-05-22 \
		--source-url https://example.invalid/spdr-demo/2026-05-22 \
		--synthetic-fixture \
		--output build/demo/spdr-xlf-holdings-previous.csv \
		--report build/demo/spdr-xlf-holdings-previous-import.md
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit spdr-holdings-import \
		--snapshot data/samples/spdr-xlf-holdings-current.csv \
		--fund-symbol XLF-DEMO \
		--fund-name "Synthetic Financials ETF" \
		--captured-on 2026-05-23 \
		--source-url https://example.invalid/spdr-demo/2026-05-23 \
		--synthetic-fixture \
		--output build/demo/spdr-xlf-holdings-current.csv \
		--report build/demo/spdr-xlf-holdings-current-import.md
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit etf-holdings-activity \
		--previous build/demo/spdr-xlf-holdings-previous.csv \
		--current build/demo/spdr-xlf-holdings-current.csv \
		--output build/demo/etf-holdings-activity.csv \
		--report build/demo/etf-holdings-activity.md \
		--html build/demo/etf-holdings-activity.html \
		--as-of 2026-05-24
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit ishares-holdings-import \
		--snapshot data/samples/ishares-iyf-holdings-previous.csv \
		--fund-symbol IYF-DEMO \
		--fund-name "Synthetic iShares Financials ETF" \
		--captured-on 2026-05-24 \
		--source-url https://example.invalid/ishares/iyf/2026-05-22 \
		--synthetic-fixture \
		--output build/demo/ishares-iyf-holdings-previous.csv \
		--report build/demo/ishares-iyf-holdings-previous-import.md
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit ishares-holdings-import \
		--snapshot data/samples/ishares-iyf-holdings-current.csv \
		--fund-symbol IYF-DEMO \
		--fund-name "Synthetic iShares Financials ETF" \
		--captured-on 2026-05-24 \
		--source-url https://example.invalid/ishares/iyf/2026-05-23 \
		--synthetic-fixture \
		--output build/demo/ishares-iyf-holdings-current.csv \
		--report build/demo/ishares-iyf-holdings-current-import.md
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit etf-holdings-activity \
		--previous build/demo/ishares-iyf-holdings-previous.csv \
		--current build/demo/ishares-iyf-holdings-current.csv \
		--output build/demo/etf-holdings-iyf-activity.csv \
		--report build/demo/etf-holdings-iyf-activity.md \
		--html build/demo/etf-holdings-iyf-activity.html \
		--as-of 2026-05-24
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit sec-nport-import \
		--snapshot data/samples/nport-xlf-previous.xml \
		--fund-symbol XLF-REG-DEMO \
		--captured-on 2026-05-24 \
		--source-url https://example.invalid/sec/nport-xlf-previous.xml \
		--synthetic-fixture \
		--output build/demo/nport-xlf-previous.csv \
		--report build/demo/nport-xlf-previous-import.md
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit sec-nport-collect \
		--cik 0000000001 \
		--series-id S000DEMO01 \
		--fund-symbol XLF-REG-DEMO \
		--captured-on 2026-05-24 \
		--archive-dir build/demo/nport-history \
		--submissions-file data/samples/sec-nport-submissions.json \
		--document-dir data/samples \
		--synthetic-fixture \
		--output build/demo/nport-xlf-current.csv \
		--report build/demo/nport-xlf-current-import.md
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit etf-holdings-activity \
		--previous build/demo/nport-xlf-previous.csv \
		--current build/demo/nport-xlf-current.csv \
		--output build/demo/etf-holdings-regulatory-activity.csv \
		--report build/demo/etf-holdings-regulatory-activity.md \
		--html build/demo/etf-holdings-regulatory-activity.html \
		--as-of 2026-05-24
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit sec-nport-backfill \
		--dataset-dir data/samples/nport-dataset/2025q4 \
		--dataset-dir data/samples/nport-dataset/2026q1 \
		--series-id S000DEMO01 \
		--fund-symbol XLF-REG-DEMO \
		--captured-on 2026-05-24 \
		--data-set-label "2025-Q4 to 2026-Q1 synthetic fixtures" \
		--source-url https://example.invalid/sec/nport-data-sets \
		--synthetic-fixture \
		--output-dir build/demo/nport-backfill \
		--manifest build/demo/nport-backfill-manifest.csv \
		--report build/demo/nport-backfill.md
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit etf-holdings-activity \
		--previous build/demo/nport-backfill/xlf-reg-demo-2025-12-31.csv \
		--current build/demo/nport-backfill/xlf-reg-demo-2026-03-31.csv \
		--output build/demo/etf-holdings-regulatory-history.csv \
		--report build/demo/etf-holdings-regulatory-history.md \
		--html build/demo/etf-holdings-regulatory-history.html \
		--as-of 2026-05-24
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit alpha-vantage-prices \
		--ticker ACBK \
		--snapshot data/samples/alpha-vantage-daily-adjusted.json \
		--output build/demo/alpha-vantage-prices.csv \
		--report build/demo/alpha-vantage-prices.md \
		--html build/demo/alpha-vantage-prices.html \
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
		--universe-membership data/samples/historical_universe.csv \
		--prices-provider-id synthetic-demo \
		--corporate-actions-provider-id synthetic-demo \
		--universe-provider-id synthetic-demo \
		--output build/demo/evaluations-actions-guarded.csv \
		--report build/demo/report-actions-guarded.md \
		--database build/demo/targetaudit.duckdb \
		--run-id demo-actions-guarded-2025-01-01 \
		--dataset-label "Synthetic corporate-action guarded evaluation" \
		--minimum-sample 1 \
		--transaction-cost-bps 10 \
		--as-of 2025-01-01
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit operations-quality \
		--database build/demo/targetaudit.duckdb \
		--report build/demo/operations-quality.md \
		--html build/demo/operations-quality.html \
		--maximum-excluded-rate 0.50 \
		--as-of 2026-05-24
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit scorecard-release \
		--registry build/demo/provider-reviewed-source-registry.csv \
		--database build/demo/targetaudit.duckdb \
		--run-id demo-actions-guarded-2025-01-01 \
		--report build/demo/scorecard-release.md \
		--html build/demo/scorecard-release.html \
		--maximum-excluded-rate 0.80 \
		--as-of 2026-05-24
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
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m targetaudit jpx-monitor \
		--snapshot data/samples/jpx-new-listings.html \
		--output build/demo/jpx-monitor.csv \
		--report build/demo/jpx-monitor.md \
		--html build/demo/jpx-monitor.html \
		--as-of 2026-05-25
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
		--jpx build/demo/jpx-monitor.csv \
		--sgx build/demo/sgx-monitor.csv \
		--previous-dir data/samples/global-alerts-previous \
		--output build/demo/global-alerts.csv \
		--report build/demo/global-alerts.md \
		--html build/demo/global-alerts.html \
		--as-of 2026-05-25

package:
	mkdir -p build/dist
	$(PYTHON) -m pip wheel --no-deps --no-build-isolation . -w build/dist

verify: test demo package

clean:
	rm -rf build
