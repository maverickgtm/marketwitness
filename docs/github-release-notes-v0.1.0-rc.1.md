# MarketWitness Open Edition v0.1.0-rc.1

MarketWitness is an evidence-first market intelligence workspace for people
who want a market dashboard that makes provenance, permissions and claim
boundaries visible.

This release candidate runs without a paid market-data subscription. It
combines reproducible demonstrations with public-source research modules and a
read-only local dashboard/API.

## Highlights

- Global IPO and listing-evidence monitoring across official-source workflows.
- Macro Catalyst Calendar from Federal Reserve and BLS scheduled-event sources.
- COT Positioning Lab for delayed official CFTC WTI, Gold and USD Index
  category exposure.
- Insider Activity Lab for SEC Forms `3`, `4` and `5` non-derivative
  classification with period, side and issuer/owner filters.
- Treasury Curve Regime Explorer and cross-asset TradingView context.
- Presidential Impact Lab with eligible White House official communication
  intake and explicit Truth Social collection restrictions.
- Evidence Passport Commons for contributors extending official-source
  coverage in additional markets.

## Trust Boundaries

- The repository does not publish real analyst rankings without authorized
  historical target data and compatible price/universe evidence.
- SEC insider `P`/`S` transaction codes may include private transactions.
  Rows dated after their filing and extraordinary declared values are excluded
  from public summary totals pending filing review.
- CFTC positioning is delayed aggregated reporting, not a trading instruction.
- VIX scenario calculations use clearly identified validation paths until
  rights-approved historical inputs are available.
- No result is investment advice.

## Try It Locally

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

Open <http://127.0.0.1:8000/dashboard/open>.

## Publishing Notes

Live SEC and BLS-backed monitors require privately configured identified
`User-Agent` secrets; no operator email is committed to the repository. Read
the [release checklist](release-candidate-checklist.md), [public-use
policy](public-use-policy.md), and [disclaimer](../DISCLAIMER.md) before
publishing or deploying the candidate.
