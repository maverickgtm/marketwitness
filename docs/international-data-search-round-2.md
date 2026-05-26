# International No-Cost Search: Round 2

Review date: `2026-05-25`.

This round examined India, Mexico, Brazil, Argentina, Germany, Switzerland,
the Netherlands, and Italy for Open Edition expansion without requiring users
to pay.

## Executive Result

No free and publishable individual analyst-target database was identified.
Two structured regulatory sources were suitable for expanding Global Listings
Watch:

| Status | Coverage | Source | Decision |
|---|---|---|---|
| Implemented | Brazil | CVM `Portal Dados Abertos`: daily ODbL ZIP for public distribution offerings | `cvm-monitor` filters equity offers and joins daily diff; B3 must confirm listing |
| Implemented | Germany, Netherlands, Italy | ESMA `Prospectus III Securities` machine-to-machine service | `esma-monitor` filters `SHRS`, attributes source, and treats results as review evidence rather than trading |
| Medium | Netherlands | AFM approved-prospectus register with CSV/XML export since `2007` | National validation path for ESMA Amsterdam samples |
| Medium | Argentina | BYMA advertised no-cost `EOD` API and CNV AIF documents | Review output/republication rights before any prices lab |
| Medium | India | SEBI `Public Issues` offer documents | Manual/future path; no confirmed public API with clear automated reuse rights |
| Blocked | Mexico | BMV public offerings and prospectuses | Legal notice restricts reproduction and parsing without written authorization |

## Regional Findings

Brazil's CVM open-data portal is the most direct Latin American path: it
supports detection and review of equity offerings while keeping subsequent B3
listing confirmation separate.

ESMA Registers supports attributed retrieval and transformation disclosure.
The implemented EU monitor covers Germany through BaFin, the Netherlands
through AFM, and Italy through CONSOB. An approved/notified prospectus is a
regulatory signal, not proof that trading has begun.

Trendlyne and visible local/global consensus pages may assist manual research
but do not unlock public target rankings without explicit rights.

## Official Sources Reviewed

- CVM open-data portal: <https://dados.cvm.gov.br/>
- CVM public offerings: <https://dados.cvm.gov.br/dataset/oferta-distrib>
- B3 public-data hub: <https://www.b3.com.br/pt_br/dados/hub-de-dados-publicos/>
- ESMA registers: <https://www.esma.europa.eu/publications-and-data/databases-and-registers>
- ESMA A2A help: <https://registers.esma.europa.eu/publication/helpApp>
- ESMA legal notice: <https://registers.esma.europa.eu/publication/legalNoticePage>
- Netherlands AFM prospectuses: <https://www.afm.nl/nl-nl/sector/registers/meldingenregisters/goedgekeurde-prospectussen>
- Germany BaFin database: <https://www.bafin.de/DE/PublikationenDaten/Datenbanken/Prospektdatenbanken/Wertpapiere/wertpapiere_node.html>
- Italy CONSOB prospectuses: <https://www.consob.it/web/area-pubblica/prospetti1>
- India SEBI Public Issues: <https://www.sebi.gov.in/filings/public-issues.html>
- Mexico BMV offerings: <https://www.bmv.com.mx/es/listados-y-prospectos/ofertas-publicas>
- Argentina BYMA APIs: <https://www.byma.com.ar/en/products/data-products/market-data/apis>
- Switzerland SIX IPO information: <https://www.six-group.com/en/products-services/the-swiss-stock-exchange/listing/equities/ipo.html>
