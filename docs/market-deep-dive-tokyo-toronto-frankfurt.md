# Deep Dive: Tokyo, Toronto, And Frankfurt

Review date: `2026-05-25`.

This review strengthens confirmation rules in three markets already represented
in Global Listings Watch, without duplicating connectors where a regional
official path is stronger.

## Executive Decision

| Market | Official Finding | TargetAudit Decision |
|---|---|---|
| Tokyo | `JPX New Listings` publishes listing date, approval date, issuer, code, segment, and offering data; `EDINET` provides earlier regulatory documents | JPX and EDINET monitors with daily diff are implemented |
| Toronto | `TSX New Company Listings` confirms new listings; `SEDAR+` restricts scraping, automation, and database building without permission | Keep TSX completed-listing feed and block automated SEDAR+ prospective expansion |
| Frankfurt | BaFin publishes approved prospectuses and directs users to ESMA; ESMA offers an attributable A2A path for Germany | Use `esma-monitor` for `SHRS`; retain BaFin as documentary corroboration rather than duplicate connector |

## Tokyo

The correct evidence chain is:

1. `EDINET` detects a securities registration statement or other offering
   document.
2. `JPX New Listings` confirms listing approval or a listed date on Tokyo
   Stock Exchange.

`jpx-monitor` distinguishes `approved_pending_listing` from `listed` using the
published date and links to the official outline. `edinet-monitor` filters
official codes `030`, `040`, and `050`, requires a free key for live requests,
and uses only a synthetic fixture in the demo. Filing evidence never becomes
listing confirmation automatically.

JPX `TDnet API` is not part of Open Edition because its published base fee is
`JPY 70,000` per month plus variable retrieval charges.

## Toronto

`TSX New Company Listings` remains the official confirmation source for
completed listings. A prospective-document path through `SEDAR+` is not
implemented because its terms restrict automated reproduction of multiple
public records and building a database without permission.

## Frankfurt

BaFin describes approved prospectus requirements and exposes a national
database. Since `ESMA Prospectus III` already supports attributed regional
ingestion for Germany, the Netherlands, and Italy, TargetAudit avoids a
duplicative Frankfurt collector. ESMA metadata opens review; later
exchange/market evidence must separately confirm admission or first trading.

## Official Sources

- JPX New Listings: <https://www.jpx.co.jp/english/listing/stocks/new/index.html>
- JPX TDnet API: <https://www.jpx.co.jp/english/markets/paid-info-listing/tdnet/02.html>
- FSA EDINET Documents API: <https://disclosure2.edinet-fsa.go.jp/guide/static/disclosure/WZEK0090.html>
- TSX New Company Listings: <https://www.tsx.com/en/news/new-company-listings>
- SEDAR+ Terms of Use: <https://sedarplus.ca/onlinehelp/terms-of-use/>
- BaFin securities prospectuses: <https://www.bafin.de/DE/Aufsicht/Prospekte/Wertpapiere/prospektewertpapiere_node.html>
- ESMA Prospectus III A2A help: <https://registers.esma.europa.eu/publication/helpApp>
