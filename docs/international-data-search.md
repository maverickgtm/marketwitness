# International Search For No-Cost Data

Review date: `2026-05-25`.

This review extended the data search to the United Kingdom, Japan, Australia,
Hong Kong, Singapore, and mainland China. The goal was not to find pages that
display information, but sources that can support a free public edition
without copying data against their terms.

## Executive Result

No international free and publishable dataset solved the central missing
input: individual historical price targets for Wall Street firms covering U.S.
stocks.

Useful expansion routes were found:

| Priority | Source | Potential Contribution | Decision |
|---:|---|---|---|
| High | Japan FSA `EDINET` Documents API | Official no-cost regulatory-document API including securities registration statements; requires key and responsible access | Priority Japanese offer-document connector |
| Medium | `EDINET DB` | Japanese enrichment with advertised free plan and attributed public display | Secondary candidate; do not replace official EDINET |
| High | Singapore `MAS OPERA` / Open Data Licence review | Prospectuses and offer documents | No connector: OPERA terms and security code restrict automation; SGX remains implemented path |
| Medium | JPX `J-Quants API` | Adjusted Japanese OHLC and security listings; free plan advertised with two years and 12-week delay | Candidate Japan sandbox after public-output rights review |
| Medium | SGX `Analyst Research` | Contributed reports on Singapore stocks | Documentary reference, not reusable structured targets |
| Low | HKMA Open API | Free Hong Kong economic and money-market series | Future macro context only |

## Analyst Targets Remain Blocked

`AnalystCentral` advertises a free CSV with ten years of Wall Street ratings
and targets, but its terms prohibit republication, derivatives, and data
mining without written consent. ShareInvestor, SGX research, Wind, and
Minkabu provide useful visible research context but no open reusable target
history was identified.

The correct next action is a written permission request to AnalystCentral for
attributed aggregate output without raw-row redistribution.

## Prices, Universes, And ETF Evidence

- JPX `J-Quants` is technically valuable for a Japanese sandbox, subject to
  public-display/output confirmation.
- ASX, LSE, HKEX, SGX, and official China market-data routes reviewed are
  contractual or subscription paths for the needed price/reference data.
- International index services may support later local verticals, but they do
  not rebuild the historical `U.S. Financials` universe for free.
- Australian and Hong Kong ETF materials require rights review before
  automated republication. SEC N-PORT remains the defendable no-cost
  regulatory ETF path currently used by MarketWitness.

## Implementation Priorities

1. Use `EDINET` with a key, attribution, and access controls for Japanese
   offering-document monitoring.
2. Keep `MAS OPERA` manual and blocked; use implemented `SGX IPO Prospectus`.
3. Keep a disabled `J-Quants` prices-sandbox design until output rights are
   confirmed.
4. Pursue an `AnalystCentral` permission track for aggregate target research.

## Official Sources Reviewed

- AnalystCentral: <https://analystcentral.com/about-us/> and <https://analystcentral.com/terms-of-service>
- JPX J-Quants API: <https://www.jpx.co.jp/english/markets/other-data-services/j-quants-api/index.html>
- FSA EDINET Documents API: <https://disclosure2.edinet-fsa.go.jp/guide/static/disclosure/WZEK0090.html>
- EDINET DB API: <https://edinetdb.com/docs/api>
- ASX ReferencePoint: <https://www.asx.com.au/connectivity-and-data/information-services/reference-data>
- LSE Historical Data: <https://www.londonstockexchange.com/equities-trading/market-data/historical-data-products>
- HKEX Historical Data: <https://www.hkex.com.hk/Global/Exchange/FAQ/Market-Data/Getting-Market-Data/Historical-Data?sc_lang=en>
- HKMA Open API: <https://apidocs.hkma.gov.hk/abouthkmasapi/>
- SGX Historical Data: <https://www.sgx.com/data-connectivity/historical-data>
- MAS OPERA terms: <https://eservices.mas.gov.sg/opera/MASUserTerms.aspx>
- Wind Research Report Platform: <https://www.wind.com.cn/portal/en/RPP/index.html>
