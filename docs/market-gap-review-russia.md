# Market Gap Review: Russia

Review date: `2026-05-25`.

## Executive Decision

Russia is relevant to a global coverage map, but must not be activated as an
Open Edition collector at this time. MarketWitness records it as
`restricted_research_only`: an identified official-source path with explained
risk, without automated ingestion, IPO alerts, or position suggestions.

## Identified Official Sources

| Source | Potential Value | MarketWitness Restriction |
|---|---|---|
| Bank of Russia `Register of Russian Securities` | The Bank announced on `2025-09-03` a register containing shares and bonds, `ISIN`, state registration number, currency, and issuer information | Useful for documenting regulatory data existence; no automated access without legal review |
| Moscow Exchange `ISS` API | MOEX describes security metadata, transactions, quotations, and historical results; delayed data is advertised as free and real-time as subscribed | MOEX is OFAC-designated; no collector or redistribution is enabled |

## Sanctions Control

The U.S. Treasury stated on `2024-06-12` that `Moscow Exchange (MOEX)`,
`National Clearing Center (NCC)`, and `National Settlement Depository (NSD)`
were designated under `E.O. 14024` for operating in Russia's financial
services sector. Finding a free API therefore does not make integration,
publication, or investment-oriented use appropriate.

## Product Policy

- Show Russia in the coverage map as `restricted_research_only`.
- Do not automatically consume `MOEX ISS` or generate public snapshots.
- Do not offer buy, sell, or positioning recommendations for Russian
  securities.
- Do not promote this source to an operating feed without documented legal
  review of sanctions, data license, redistribution, and intended users.

## Official Sources

- Bank of Russia register announcement: <https://www.cbr.ru/eng/press/event/?id=26912>
- Moscow Exchange `ISS` API: <https://www.moex.com/a2920>
- U.S. Treasury designation, `2024-06-12`: <https://home.treasury.gov/news/press-releases/jy2404>
- OFAC Russia-related sanctions: <https://ofac.treasury.gov/sanctions-programs-and-country-information/russian-harmful-foreign-activities-sanctions>
