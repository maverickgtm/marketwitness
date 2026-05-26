# Policy Signal Impact Lab

Review date: `2026-05-25`.

## Proposal

`Policy Signal Impact Lab` studies whether a verifiable public communication
coincides with later changes in volatility or related assets. Its initial
designed case is `Donald Trump / Truth Social`, beginning at the second-term
start date of `2025-01-20`.

The working measurement name is **Policy Signal Impact Trace**. It is not
published as a quantitative index because MarketWitness does not possess an
authorized ingested history of the communications.

## Differentiation

The idea has prior art:

| Precedent | Existing Work | MarketWitness Difference |
|---|---|---|
| JPMorgan `Volfefe Index` (2019) | Analyzed Donald Trump tweets and rates volatility, especially 2Y/5Y Treasuries | Event-level public traceability, disclosed windows, multiple assets, and links to IPO/listing evidence |
| `Trump & Dump` (reviewed `2026-05-25`) | Advertises Truth Social monitoring and market correlation with a manipulation score | No manipulation or causality claim without reproducible evidence; visible rights controls |

Each real episode must disclose its source and permission, topic
classification, measured assets and windows, exclusions or delays, and the
observational nature of the result.

## Measurement Design

`/dashboard/policy-signals` and `/api/v1/intelligence/policy-signals` publish
the initial design:

| Layer | Initial Lenses |
|---|---|
| Equity beta | S&P 500, Nasdaq-100, and sector ETFs |
| Risk temperature | External daily FRED `VIXCLS` chart |
| Policy transmission | Treasury curve, USD, WTI, and Brent |
| Frontier markets | BTC, ETH, and monitored IPO/listing candidates |

Proposed windows are same session, next session, and `5`, `20`, and `60`
sessions. Real results require a verifiable timestamp, public reference,
documented rights, and permitted market data for each window.

## Truth Social Boundary

Truth Social is relevant but is not enabled as a feed. Its official terms
reviewed on `2026-05-25` restrict automated access, systematic content
retrieval, scraping or data mining, and commercial use without permission.

MarketWitness therefore registers `truth-social-public-content` as
`restricted_no_collection`: it does not download history, reproduce post
texts, or offer real-time monitoring without written permission or an
authorized provider with sufficient rights.

## Eligible No-Cost Route: White House RSS

| Feed | Verification | MarketWitness Use |
|---|---|---|
| `https://www.whitehouse.gov/news/feed/` | Active official RSS; hourly-update declaration and White House-signed entries | Candidate primary source for statements, fact sheets, and official news |
| `https://www.whitehouse.gov/presidential-actions/feed/` | Active official RSS; includes executive orders, memoranda, and proclamations | Candidate primary source for formal decisions |
| `https://www.whitehouse.gov/wire/feed/` | Active official RSS linking to outside media | Title, timestamp, and external URL radar only; do not import third-party article bodies |

Government-produced White House material follows the site's copyright policy;
third-party linked material remains subject to its own conditions. Official
RSS should therefore be implemented before any Truth Social extension.

## VIX Display

The lab uses an FRED-hosted image for `CBOE Volatility Index: VIX [VIXCLS]`
from `2025-01-20`. FRED labels it `Copyrighted: Citation Required`; visible
attribution and a link are retained. It is external context and is not
ingested for calculations in this release.

## Sources

- Truth Social Terms of Service: <https://help.truthsocial.com/legal/terms-of-service/>
- White House News RSS: <https://www.whitehouse.gov/news/feed/>
- White House Presidential Actions RSS: <https://www.whitehouse.gov/presidential-actions/feed/>
- White House Wire RSS: <https://www.whitehouse.gov/wire/feed/>
- White House copyright policy: <https://www.whitehouse.gov/copyright/>
- FRED `VIXCLS`: <https://fred.stlouisfed.org/series/VIXCLS>
- Bloomberg, JPMorgan `Volfefe Index`: <https://www.bloomberg.com/news/articles/2019-09-09/jpmorgan-creates-volfefe-index-to-track-trump-tweet-impact>
- CNBC, JPMorgan `Volfefe Index`: <https://www.cnbc.com/2019/09/08/donald-trump-is-tweeting-more-and-its-impacting-the-bond-market.html>
- Trump & Dump: <https://www.trumpanddump.app/>
