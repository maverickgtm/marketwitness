# Dashboard Product Outline

The MarketWitness dashboard separates measured research, documentary monitoring,
external market context, and publication controls. A screen can be useful
without implying that the evidence supports a trade or a public real-data
ranking.

## Primary Navigation

| Route | Purpose | Evidence Boundary |
|---|---|---|
| `/` and `/dashboard/open` | Open Edition landing terminal | Widgets are external context; metrics describe bundled workflows |
| `/dashboard/reports` | Fixed navigation for generated report pages | No arbitrary generated-file browsing |
| `/dashboard/ipo` | IPO Watch Center | Discovery, review, and confirmation remain distinct |
| `/dashboard/global-listings` | International listing coverage and monitors | Each jurisdiction retains its confirmation rule |
| `/dashboard/etf` | ETF Evidence Center | Synthetic change examples are separated from SEC periodic evidence |
| `/dashboard/financials-evidence` | Financials evidence and release-gate sequence | Demo scorecard is not real analyst performance |
| `/dashboard/intelligence` | Cross-asset research workspace | Planned stored connectors are not live feeds |
| `/dashboard/market-context` | Cross-Asset Markets terminal | TradingView displays context only; values are not stored or scored |
| `/dashboard/volatility` | Volatility Intelligence Lab | External VIX display; no unlicensed episode calculations |
| `/dashboard/presidential-impact` | Presidential Impact Lab: Donald Trump communication study | White House RSS eligible; Truth Social collection blocked without permission |
| `/dashboard/commons` | Evidence Passport Commons | Source rights and claim boundaries are visible |
| `/dashboard/policy` | Public Use Policy | Product control, not legal advice |
| `/dashboard/governance` | Source Governance | Technical integration does not imply publishability |
| `/dashboard/release` | Release Center | Combines readiness, lineage, and quality before output |

## Open Edition Home And Cross-Asset Markets

The home view communicates that the GitHub edition runs without purchased
data. It provides direct navigation to IPO, ETF, Financials, Global Listings,
and control views, along with official TradingView `Ticker Tape` and `Market
Overview` widgets labeled as attributed external display.

Its first product-selling section promotes four distinctive reasons to explore
the project: `VIX Stress Lab`, `Trump Communication Impact`, `Global IPO Radar`, and
`Evidence Commons`. The following `Core Departments` section provides direct
entry to IPO, ETF, Financials, Market Intelligence, Data Rights, and generated
report workflows so visitors do not have to discover the system through
documentation first.

`/dashboard/market-context` adds a TradingView `Advanced Chart` defaulting to
`BINANCE:BTCUSDT` plus watchlists for `BTC`, `ETH`, `WTI`, `Brent`, gold,
silver, foreign exchange and equity benchmarks. MarketWitness does not read,
store, export, or score widget values. The dashboard remains usable offline
while third-party visual content may require Internet access.

## Research Workspaces

### Financials Evidence Center

This center orders the audit chain:

1. authorized target-import audit;
2. adjusted-price evidence;
3. corporate-action guard;
4. operations-quality snapshot;
5. release-decision snapshot;
6. synthetic scorecard exploration.

`/dashboard/financials` exposes evaluated/excluded/pending counts, firm
ranking, Wilson intervals, target-direction filters, ticker/firm detail,
timeline evidence, CSV output, run comparison, and exclusion reasons.

### IPO Watch Center

IPO Watch follows research states rather than position calls:

| State | Meaning |
|---|---|
| `Monitor` | Candidate without confirmed public filing |
| `Review Filing` | Public filing found; primary evidence requires review |
| `Observe Listing` | Listing/debut confirmed; post-event history may be gathered |
| `Eligible for Study` | Enough permitted history exists for a defined study |

The workflow joins SEC universal discovery, triage alerts, documented manual
review, the watchlist, global-monitor evidence, and issuer confirmations.
Finding a filing never changes a company state without a documented decision.

### Global Listings Watch

| Market | Evidence Path | Implemented Treatment |
|---|---|---|
| United Kingdom | LSE new issues and FCA NSM | Upcoming issues and document classes remain review signals |
| Hong Kong | HKEX/HKEXnews AP/PHIP feeds | Official lifecycle statuses retained |
| Australia | ASX upcoming floats/listings | Anticipated or withdrawn evidence |
| Canada | TSX new company listings | Completed listing confirmation; SEDAR+ automation blocked |
| Singapore | SGX IPO Prospectus | Published prospectus review; MAS OPERA manual/blocked |
| Japan | EDINET and JPX New Listings | Filing detection separated from JPX approval/listing |
| Brazil | CVM open offering data | Equity offering review; B3 confirmation still needed |
| Europe | ESMA Prospectus III `SHRS` | German, Dutch, and Italian review evidence |
| South Korea | OpenDART `C001`/`C006` | Offering-filing review; KRX public output excluded |
| Russia | Bank of Russia/MOEX references | `restricted_research_only`; no automated collection |

`/dashboard/global-alerts` compares daily evidence snapshots; new, changed, or
removed entries are review tasks rather than automatically confirmed listings.

### ETF Evidence Center

The ETF center makes frequency visible:

- `/dashboard/etf/arkk-demo`, `/dashboard/etf/xlf-demo`, and
  `/dashboard/etf/iyf-demo` use synthetic comparisons only.
- `/dashboard/etf/nport-recent` and `/dashboard/etf-regulatory` show SEC
  N-PORT periodic evidence.
- `/dashboard/etf/nport-catalog` and `/dashboard/etf/nport-sync` show
  controlled quarterly catalog/synchronization operation.

A difference in reported holdings is described as an observed change, never a
confirmed manager buy or sell without additional evidence.

### RWA, Market Intelligence, Volatility, And Policy

- `/dashboard/rwa-watch` demonstrates token/reference observations with
  synthetic data; live xStocks, Ondo, and venue feeds remain rights-gated.
- `/dashboard/intelligence` maps Pre-IPO, volatility, policy, regimes, macro,
  insiders, ownership, and futures-positioning layers; planned sources are not
  described as collected values.
- `/dashboard/volatility` presents a FRED-attributed VIX display and planned
  `VIX`/`VXN`/`MOVE`/commodity episode designs.
- `/dashboard/presidential-impact` presents the Donald Trump communication
  event-study design, official White House RSS intake path, and visible Truth
  Social collection block.

## Controls

| View | Question Answered |
|---|---|
| Source Governance | Which sources are usable, pending, licensed, manual, or blocked? |
| Provider Approvals | What written evidence is required before promoting a candidate source? |
| Scorecard Readiness | Are targets, prices, corporate actions, and universe inputs public-output ready? |
| Operations Quality | Does a run have complete versioned, traceable technical input? |
| Release Center | May this particular run support public real-data output? |

## API Surface

The read-only FastAPI layer serves dashboard state from generated reports,
registry files, and DuckDB runs. Key contracts include:

- `/api/v1/open-edition`
- `/api/v1/commons/passports`
- `/api/v1/intelligence/modules`
- `/api/v1/intelligence/volatility`
- `/api/v1/intelligence/policy-signals`
- `/api/v1/policy/public-use`
- `/api/v1/extensions/licensed`
- run, governance, readiness, operations-quality, and scorecard-release
  endpoints used by the Financials/control screens.

The localized contributor gateway at `/dashboard/contribute?lang=en` also
supports Japanese, Brazilian Portuguese, Traditional Chinese, and Korean for
global source proposals. Documentation and the default interface remain
English.
