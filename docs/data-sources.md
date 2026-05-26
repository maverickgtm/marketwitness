# Evaluated Data Sources

Review baseline: `2026-05-25`.

## Data Policy

MarketWitness distinguishes between technically reachable information and data
that may support public output. A visible page or free API does not by itself
authorize collection, retention, republication, or derived rankings.

Operational decisions live in `data/samples/source_registry.csv`; the
narrative below summarizes why sources exist in the product.

## Open Edition Evidence Paths

| Data Need | Primary No-Cost Path | Use Boundary |
|---|---|---|
| U.S. IPO/document monitoring | SEC EDGAR | Identified fair-access requests; filing begins review |
| ETF regulatory holdings | SEC N-PORT | Periodic reported evidence, not daily trades |
| United Kingdom listing documents | LSE and FCA NSM | Upcoming/document signals require review |
| Hong Kong listings | HKEX/HKEXnews | Official lifecycle signals retained |
| Australia listings | ASX official page | Anticipated dates are not confirmed trading |
| Canada completed listings | TSX official new listings | SEDAR+ automation excluded without permission |
| Singapore documents | SGX IPO Prospectus | MAS OPERA remains manual/blocked |
| Japan offerings/listings | EDINET and JPX | Filing detection separate from listing confirmation |
| Brazil offerings | CVM open-data ZIP | B3 evidence still required for listing |
| European prospectuses | ESMA Prospectus III | `SHRS` review evidence for Germany, Netherlands, Italy |
| South Korean offerings | OpenDART | KRX data not republished under reviewed terms |
| Official presidential events | White House RSS | Wire links remain metadata only |

## Analyst Targets And Ratings

No no-cost source with sufficient public-output rights was found for a real
individual-firm historical target ranking. The key statuses are:

| Source | Role | Status |
|---|---|---|
| AnalystCentral | Advertised no-cost historical U.S. target dataset | Written-permission candidate only |
| Massive/Benzinga | Structured U.S. ratings expansion | Optional bring-your-own-license route |
| MarketBeat | Lower-cost recent ratings/export reference | Private pilot only; recent horizon is insufficient alone |
| WallStreetZen | Existing ranking/method benchmark | No confirmed target-row ingestion route |
| Finnhub and FMP | Programmatic consensus/target endpoints | Display/output rights require agreement |
| TipRanks, Yahoo Finance, Investing.com, Finviz, Koyfin | Useful visible research references | Manual/reference use only without written rights |

Read [Final No-Cost Scan For Historical Target Data](final-free-target-data-scan.md)
and [Optional Licensed Extensions](licensed-extensions.md).

## Prices, Corporate Actions, And Universe

Real public analyst scoring also needs compatible adjusted prices, corporate
actions, and point-in-time universe membership. Alpha Vantage was considered
for local adjusted-price adaptation, but a free-access path does not by itself
grant public derived-output rights. Index membership and market-data products
from major exchanges or index providers generally require additional rights
review or licensing.

These inputs remain explicitly required by `Scorecard Readiness` and
`Release Center`; missing rights cannot be hidden behind a technically
successful calculation.

## ETF, RWA, And Cross-Asset Context

- SEC N-PORT is the current defensible public regulatory ETF evidence route.
- Issuer daily holdings imports remain local or synthetic until collection and
  output permissions are established.
- xStocks/Backed, Bybit, and Kraken paths remain blocked for public live
  collection under reviewed restrictions; Ondo, Gate, and Bitget remain
  candidates requiring rights confirmation.
- TradingView widgets are attributed external display only.
- FRED VIX context is displayed with required citation and is not treated as
  a calculated MarketWitness series in this candidate.
- Cboe/ICE volatility history remains pending rights review for real derived
  episode output.
- U.S. Treasury daily par yield curve XML now supplies attributed official
  `2Y`, `10Y`, and derived `2s10s` observations for policy context and the
  Cross-Asset Treasury Curve Regime Explorer.

## Official Reference Set

- SEC EDGAR: <https://www.sec.gov/search-filings>
- SEC N-PORT datasets: <https://www.sec.gov/data-research/sec-markets-data/form-n-port-data-sets>
- U.S. Treasury Daily Interest Rate XML Feed: <https://home.treasury.gov/treasury-daily-interest-rate-xml-feed>
- FCA NSM: <https://data.fca.org.uk/#/nsm/nationalstoragemechanism>
- London Stock Exchange: <https://www.londonstockexchange.com/>
- HKEX: <https://www.hkex.com.hk/>
- ASX: <https://www.asx.com.au/>
- TSX: <https://www.tsx.com/en/news/new-company-listings>
- SGX IPO Prospectus: <https://www.sgx.com/securities/ipo-prospectus>
- JPX New Listings: <https://www.jpx.co.jp/english/listing/stocks/new/index.html>
- EDINET: <https://disclosure2.edinet-fsa.go.jp/>
- CVM Open Data: <https://dados.cvm.gov.br/>
- ESMA registers: <https://www.esma.europa.eu/publications-and-data/databases-and-registers>
- OpenDART: <https://engopendart.fss.or.kr/>
- White House RSS: <https://www.whitehouse.gov/news/feed/>
- FRED VIXCLS: <https://fred.stlouisfed.org/series/VIXCLS>
