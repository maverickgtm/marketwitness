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
| Listings Radar / U.S. IPO Filing Watch | Search, filters, filtered CSV export, visible monitor cadence, browser-local follow-up list, SEC-shaped discovery, triage and reviewed watchlist workflow | Live SEC calls require identified `User-Agent`; a filing is not an investment signal |
| Global Listings Watch | Official-source monitor design, dated evidence-change queue and interactive radar feed for multiple jurisdictions | Jurisdiction-specific confirmation rules remain separate |
| ETF Regulatory Holdings | Synthetic holding differences plus SEC N-PORT periodic workflow | Not daily or real-time manager trading |
| Public Document Checks | FCA NSM corroboration flow | Documentation does not automatically prove admission/trading |
| RWA Watch Sandbox | Synthetic token/reference observations | No real xStocks, Ondo, or venue collection |
| Cross-Asset Markets | Official Treasury 2Y/10Y curve-regime explorer plus TradingView views for BTC, ETH, metals, energy, FX and benchmarks | Treasury observations are stored context; widget values are not stored or scored |
| Macro Catalyst Calendar | Official FOMC meetings and selected BLS CPI, PPI, payrolls and JOLTS release schedule | Event times are known context, not release forecasts or positions |
| COT Positioning Lab | Official CFTC benchmark-category positioning for WTI, Gold and U.S. Dollar Index with weekly comparisons | COT reports are delayed aggregated exposure, not trading instructions |
| Insider Activity Lab | SEC Form 3/4/5 non-derivative P/S classification with issuer/owner and period filters | P/S codes may include private transactions; check original filings before interpretation |
| Market Intelligence | Planned cross-asset sources and operating boundaries | No new live values or position recommendation |
| VIX Reaction Explorer | VIX display, rising/cooling scenarios and episode-design API | Cboe/ICE derived output pending rights |
| Presidential Impact Lab | Official White House archive, Treasury 2Y/10Y session context and themed calculation sandbox | Treasury changes are observational only; synthetic paths, Truth Social and broader reactions retain visible gates |
| Evidence Passport Commons | Public source/rights registry and contribution path | A passport is not investment advice |

## Run Locally Without Data Fees

To explore the hosted product without installing anything, open the
[public MarketWitness demo](https://marketwitness-43-157-95-145.nip.io/dashboard/open).
The commands below are only for a local clone of the repository.

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

After launching the app, open <http://127.0.0.1:8000/> on the same machine
running the command. Key routes are documented in
[README.md](../README.md) and [Dashboard Product Outline](dashboard.md).

For permitted live SEC access, provide an identifying contact outside Git:

```bash
export MARKETWITNESS_SEC_USER_AGENT="MarketWitness contact@example.com"
```

No paid API key is required for SEC connector workflows.
Official BLS/FOMC schedule collection is also free, but BLS requires an
identified contact request. Set `MARKETWITNESS_MACRO_USER_AGENT` locally or as
a GitHub Actions secret; no personal email is stored in the public codebase.

## Periodic GitHub Report

`.github/workflows/open-edition-report.yml` generates a tested Open Edition
copy each Monday at `12:17 UTC` and on manual dispatch. It runs `make verify`
and retains a downloadable artifact for 30 days containing demonstration
output under `build/demo/` and the installable wheel under `build/dist/`.

The workflow requires no secrets or paid subscriptions because it processes
redistributable repository fixtures only. It does not query live filings,
include real issuer holdings, or publish a real analyst ranking.

The Listings Radar exposes that same boundary in-product through `Monitor
Status`: its automatic refresh refers to this artifact schedule, not an
always-on market data service. Users can re-read a locally rebuilt bundle and
export the filtered evidence queue as CSV.

`.github/workflows/public-listings-monitor.yml` is a separate weekday
official-source capture for Brazil CVM and Europe ESMA only. Both sources are
registered as usable for attributed derived output. Its downloadable artifact
contains offering or prospectus evidence for review, never a completed listing
claim or a position recommendation. After the first observation, it also
includes a `Public Listings Change Log` comparing the newest capture against
the latest earlier retained CVM/ESMA snapshot.

When that artifact is downloaded into `build/public-monitor/` or configured
through `MARKETWITNESS_PUBLIC_MONITOR_REPORTS`, the local app exposes it at
`/dashboard/official-change-log`. Without an artifact the page remains
available but explicitly reports that no official run is loaded.

`.github/workflows/public-presidential-events-monitor.yml` collects official
White House News/Presidential Actions metadata, official Treasury daily
2Y/10Y par-yield observations, and official Federal Reserve/BLS schedule
metadata, delayed CFTC positioning, and quarterly SEC insider classifications
on weekdays. Once its artifact is loaded through
`MARKETWITNESS_POLICY_MONITOR_REPORTS`, Presidential Impact displays
session-to-session basis-point context for thematic events, Macro Catalyst
Calendar exposes upcoming known release times, and COT Positioning exposes
delayed weekly CFTC benchmark-category context and Insider Activity exposes
priced P/S disclosure totals separately from other transaction codes. None
predicts an outcome, attributes causation, or recommends a trade.
The quarterly SEC insider artifact is cached between scheduled weekday runs
and refreshed by manual workflow dispatch when a new SEC release is available.

## Optional Extensions

Commercial or user-licensed evidence is architecture-ready but is not required
to install or use public modules. Read [Optional Licensed
Extensions](licensed-extensions.md) for documented paths and
[Public Use And Data Rights Policy](public-use-policy.md) for output limits.
