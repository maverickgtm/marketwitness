# Market Gap Review: South Korea, Gulf Markets, And Africa

Review date: `2026-05-25`.

## Executive Decision

| Market | Finding | Decision |
|---|---|---|
| South Korea | `OpenDART` offers an Open API for original XML disclosures and equity issuance searches; `KRX OPEN API` restricts third-party output | `Korea Offering Watch` implemented with OpenDART; KRX excluded from public output |
| Saudi Arabia | Saudi Exchange/CMA publish visible IPO and prospectus information | Observe; no confirmed free API with automated republication permission |
| United Arab Emirates | DFM/ADX/SCA show IPO, listing, and disclosure material | Observe; no confirmed reusable no-cost programmatic feed |
| South Africa | JSE `SENS` is a regulatory announcement service presented through information/subscriber products | Do not enable a free connector without clear licensing |

## South Korea

The Financial Supervisory Service's `DART/OpenDART` documentation states that
people, companies, and institutions can use its information through the Open
API, including original XML reports, securities registration statements, and
offering disclosures.

The implemented `OpenDART` monitor detects `C001` equity securities
registrations and `C006` small public equity offerings using a free key.
`KRX OPEN API` remains unconnected because its reviewed terms restrict use to
non-commercial purposes and prohibit supplying KRX data to third parties.
Offering, listing, and performance remain separate states.

## Current Priority

1. Japan: `EDINET` plus `JPX New Listings`.
2. South Korea: implemented `OpenDART`, with KRX excluded from public output.
3. Brazil: implemented CVM open-data offering monitor.
4. Europe: implemented ESMA `Prospectus III Securities` monitor filtered to
   `SHRS`.

## Official Sources

- OpenDART Open API: <https://engopendart.fss.or.kr/intro/main.do>
- DART Public Offering Information: <https://englishdart.fss.or.kr/dsbc006/main.do>
- KRX OPEN API: <https://openapi.krx.co.kr/contents/OPP/INFO/OPPINFO001.jsp>
- KRX terms: <https://openapi.krx.co.kr/contents/OPP/INFO/OPPINFO005.jsp>
- Saudi Exchange: <https://www.saudiexchange.sa/>
- Dubai Financial Market IPO listings: <https://www.dfm.ae/en/raise-capital/ipo-listings/overview>
- UAE SCA open data: <https://www.sca.gov.ae/en/open-data.aspx>
- JSE SENS Project: <https://clientportal.jse.co.za/technical-library/sens-project>
