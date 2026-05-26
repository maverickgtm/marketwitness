# MarketWitness Open Edition

The GitHub edition must run without purchasing data or subscribing to
commercial APIs.

## Product Promise

| Mode | Data | Data Cost | Purpose |
|---|---|---:|---|
| Offline showcase | Project-created fixtures | None | Exercise Financials, RWA, audits, reports, API, and dashboard |
| Public monitors | Public regulatory/source workflows under recorded rules | None | Follow listing and periodic holdings evidence |
| Authorized extension | Files supplied by a user with documented rights | Not required by MarketWitness | Run private analysis without redistributing restricted data |

The repository does not promise a real analyst ranking built from commercial
data. Optional routes are disclosed at `/dashboard/extensions`, while
`/dashboard/policy` explains collection and publication boundaries.

TradingView widgets provide attributed external market context. They are not
stored, exported, or used as scoring evidence.

## Included Capabilities

| Capability | Included Workflow | Critical Boundary |
|---|---|---|
| Financials Scorecard Sandbox | Synthetic target evaluation, exclusions, benchmarks, quality, and release gating | No real-firm performance claim |
| U.S. IPO Filing Watch | SEC-shaped discovery, triage, review, and watchlist workflow | Live SEC calls require identified `User-Agent`; a filing is not an investment signal |
| Global Listings Watch | Official-source monitor design and implemented evidence paths for multiple jurisdictions | Jurisdiction-specific confirmation rules remain separate |
| ETF Regulatory Holdings | Synthetic holding differences plus SEC N-PORT periodic workflow | Not daily or real-time manager trading |
| Public Document Checks | FCA NSM corroboration flow | Documentation does not automatically prove admission/trading |
| RWA Watch Sandbox | Synthetic token/reference observations | No real xStocks, Ondo, or venue collection |
| Cross-Asset Markets | TradingView views for BTC, ETH, metals, energy, FX and benchmarks | External visual context only; no stored or scored widget values |
| Market Intelligence | Planned cross-asset sources and operating boundaries | No new live values or position recommendation |
| Volatility Intelligence Lab | VIX display and episode-design API | Cboe/ICE derived output pending rights |
| Presidential Impact Lab | Donald Trump communication-event methodology and official White House RSS intake path | Truth Social automation blocked without permission |
| Evidence Passport Commons | Public source/rights registry and contribution path | A passport is not investment advice |

## Run Without Data Fees

```bash
python3 -m pip install -e ".[application]"
make verify
make demo
export MARKETWITNESS_DATABASE="build/demo/marketwitness.duckdb"
export MARKETWITNESS_SOURCE_REGISTRY="data/samples/source_registry.csv"
export MARKETWITNESS_PROVIDER_APPROVALS="data/samples/provider_approval_queue.csv"
export MARKETWITNESS_GENERATED_REPORTS="build/demo"
export MARKETWITNESS_LICENSED_EXTENSIONS="data/samples/licensed_extensions.csv"
python3 -m uvicorn marketwitness.api:app --host 127.0.0.1 --port 8000
```

Open <http://127.0.0.1:8000/>. Key routes are documented in
[README.md](../README.md) and [Dashboard Product Outline](dashboard.md).

For permitted live SEC access, provide an identifying contact outside Git:

```bash
export MARKETWITNESS_SEC_USER_AGENT="MarketWitness contact@example.com"
```

No paid API key is required for SEC connector workflows.

## Periodic GitHub Report

`.github/workflows/open-edition-report.yml` generates a tested Open Edition
copy each Monday at `12:17 UTC` and on manual dispatch. It runs `make verify`
and retains a downloadable artifact for 30 days containing demonstration
output under `build/demo/` and the installable wheel under `build/dist/`.

The workflow requires no secrets or paid subscriptions because it processes
redistributable repository fixtures only. It does not query live filings,
include real issuer holdings, or publish a real analyst ranking.

## Optional Extensions

Commercial or user-licensed evidence is architecture-ready but is not required
to install or use public modules. Read [Optional Licensed
Extensions](licensed-extensions.md) for documented paths and
[Public Use And Data Rights Policy](public-use-policy.md) for output limits.
