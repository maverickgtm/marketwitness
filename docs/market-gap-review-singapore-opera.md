# Market Gap Review: Singapore MAS OPERA

Review date: `2026-05-25`.

## Decision

TargetAudit will not implement an automatic collector for `MAS OPERA` in the
free public edition. `SGX IPO Prospectus` remains Singapore's automated path;
`MAS OPERA` is recorded as an official manual reference blocked from
collection.

## Reviewed Evidence

- `OPERA` is the Monetary Authority of Singapore's official repository for
  prospectuses and offering documents.
- Its public `Public Offers` query requests a `Security Code`, so it does not
  expose a verified stable automation route.
- `OPERA` terms updated on `2026-04-18` restrict robots or other retrieval
  applications without written permission, as well as caching, storage, and
  direct links to content.
- The Singapore Open Data Licence governs datasets actually released under it;
  no `OPERA` prospectus dataset/API covered by that licence was identified.

## Product Treatment

- Do not scrape `Public Offers`, attempt to bypass the security code, or
  archive `OPERA` documents in the public dashboard.
- Show `MAS OPERA Public Offers` in `Source Registry` as
  `restricted_no_collection` and `source_link_only`.
- Continue `SGX IPO Prospectus` as documentary signal: a published prospectus
  requires review and does not confirm admission or trading.

## Official Sources

- MAS OPERA: <https://eservices.mas.gov.sg/opera/Public/WelcomePage.aspx>
- MAS OPERA Public Offers: <https://eservices.mas.gov.sg/opera/PublicOffers.aspx>
- MAS OPERA Terms of Use: <https://eservices.mas.gov.sg/opera/MASUserTerms.aspx>
- Singapore Open Data Licence: <https://data.gov.sg/open-data-licence>
- SGX IPO Prospectus: <https://www.sgx.com/securities/ipo-prospectus>
