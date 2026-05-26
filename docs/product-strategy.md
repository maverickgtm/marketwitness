# Product Strategy

## Public Name

**MarketWitness**

Tagline: **Evidence-first market intelligence for auditable research.**

The technical package remains `marketwitness`, allowing the product to extend to
other verticals without breaking integrations.

## Product Thesis

Established market products provide current targets, ratings, calendars, and
charts. It remains hard for a public researcher to verify:

- whether a historical target was actually reached;
- whether a firm added value against a same-sector benchmark;
- whether a specialist performed differently from a generalist;
- whether a conclusion relies on enough observations and publishable data;
- which official evidence confirms a listing or market event;
- how volatility or public communications relate to market reactions without
  overstating causality.

MarketWitness is an open, reproducible research system that treats evidence
rights and claim boundaries as product features.

## Open Edition Modules

| Module | Role | Public Boundary |
|---|---|---|
| Financials Scorecard | Auditable analyst-target method for U.S. Financials | Ships with redistributable fixtures; real rankings require authorized data |
| IPO Watch | Monitor strategic or high-interest listing candidates | Filings and review workflow do not imply a completed listing or trade idea |
| Global Listings Watch | Extend listing evidence beyond the United States | Each jurisdiction keeps its own confirmation rule |
| Evidence Passport Commons | Public protocol and API for source provenance and rights | A passport may be accepted before a connector is enabled |
| ETF Evidence Center | Study holdings evidence and changes | Periodic regulatory reports are separated from daily-trade claims |
| RWA Watch Sandbox | Model tokenized-asset observations | Live venue or issuer collection stays subject to documented rights |
| Market Intelligence | Organize events, context, and future connectors | Does not issue trading signals |
| Volatility Intelligence Lab | Examine volatility regimes across assets and events | Visible research workflow; proprietary series are not bundled |
| Policy Signal Impact Lab | Link verifiable public communications to event windows | Truth Social automation is blocked without permission |

## Differentiation

Competitors and adjacent products observed as of `2026-05-24`:

| Product | Visible Focus | MarketWitness Opportunity |
|---|---|---|
| TipRanks | Ratings, targets, and one-year success methodology | Provide reproducible method without incorporating unlicensed data |
| MarketBeat | Large recommendation history and subscription rankings | Use only as a market reference unless output rights are obtained |
| WallStreetZen | Proprietary analyst ranking | Demonstrate transparent sector-specific evaluation rules |
| Yahoo Finance / Investing.com | Visual rating and target lookup | Treat as manual references, not assumed ingestion rights |
| Finnhub / FMP | Programmatic trend or consensus endpoints | Enable future connectors only under explicit display/output terms |
| TradingView | Attributed embed widgets | Provide context displays separate from scoring inputs |
| FRED `VIXCLS` | Attributed volatility series | Make VIX context visible while keeping scoring evidence separate |
| Truth Social | Potential policy-event communications | Publish methodology and rights block until an authorized path exists |
| xStocks / Ondo / CEX venues | Tokenized instruments and trading venues | Demonstrate RWA model without claiming analyst-target supply |
| Quiver Quantitative | Historical analyst performance using Benzinga data | Investigate specialist versus generalist financials hypotheses |
| AnaChart | Price-target charts and hit ratios | Add benchmark comparison and versioned scoring rules |

The distinguishing public layer is **Evidence Passport Commons**: instead of
competing only on the number of signals, MarketWitness publishes provenance and
rights records, then invites global contributors to improve source cadence,
confirmation logic, and claim boundaries.

## Initial Market

### Universe

- U.S. financial companies with verifiable targets.
- Desired first real cohort: financial members of the `S&P 500` at each
  observation date.
- Regional-bank analysis only after a reliable point-in-time universe exists.

### Benchmarks

- Initial sector benchmark: `XLF`.
- Future broad benchmark: `SPY`.
- Sub-industry benchmarks only when universe membership and prices are
  consistently auditable.

### Initial Users

- Individual investors checking headlines about analyst ratings.
- Financial journalists and creators who need a citable method.
- Quantitative researchers who want to reproduce or challenge the score.
- Contributors who understand an official listing source in their market.

## Publishable MVP Standard

A serious public release should include:

1. A reproducible engine and tests.
2. A clearly labeled synthetic demonstration dataset.
3. Import paths for authorized target files and compatible price evidence.
4. A real Financials pilot only when each row has sufficient provenance and
   publication rights.
5. Reports disclosing `N`, Wilson 95% intervals, historical universe, target
   revisions, costs, exit rule, sector/direction segments, exclusions,
   benchmark, and method.

## Research Hypotheses

- `H1`: financial-sector specialists achieve lower terminal error than
  generalists over the same universe and period.
- `H2`: a high `target hit rate` does not necessarily imply positive excess
  return against `XLF`.
- `H3`: results differ between bullish and bearish targets.

These are research questions, not product conclusions.

## Policy Signal Impact Trace

The most distinctive proposed extension links verifiable public communications
to market-reaction windows without claiming causality. The initial case is
`Donald Trump / Truth Social` from `2025-01-20`.

Prior art exists: JPMorgan created the `Volfefe Index` in 2019 for tweets and
rates volatility, and services advertise monitoring of Truth Social. The
MarketWitness approach is different: every episode requires a source,
permission, timestamp, classification, window, asset set, exclusion rule, and
connection to verified IPO or listing evidence.

Truth Social is not bundled as a scraper. Its reviewed official terms restrict
automated means, systematic retrieval, and data mining without permission. The
dashboard and API publish the methodology and rights control now; live input
may proceed only through authorization or a licensed source. Official White
House RSS feeds provide the eligible free evidence path for official events.

## Business Risks

- Detailed historical targets may require paid data rights; they remain an
  optional extension rather than a GitHub requirement.
- A public report with a small sample can mislead even when computed
  correctly.
- Sector classification and historical constituents require point-in-time data
  to prevent hindsight bias.
- No score should be presented as investment advice.

## Market References

- TipRanks screener: <https://www.tipranks.com/screener/stock-ratings>
- MarketBeat analyst rankings: <https://www.marketbeat.com/all-access/analyst-rankings/>
- Quiver analyst ratings: <https://www.quiverquant.com/analysts/>
- AnaChart: <https://anachart.com/>
- State Street XLF: <https://www.ssga.com/us/en/intermediary/etfs/state-street-financial-select-sector-spdr-etf-xlf>
- S&P sectors: <https://www.spglobal.com/spdji/en/index-family/equity/us-equity/sp-sectors/>
