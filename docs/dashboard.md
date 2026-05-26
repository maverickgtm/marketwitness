# Dashboard Product Outline

The MarketWitness dashboard separates measured research, documentary monitoring,
external market context, and publication controls. A screen can be useful
without implying that the evidence supports a trade or a public real-data
ranking.

Every served dashboard page and generated report includes a persistent
`Home` / `All views` control. A reader can always return to the Open Edition
workspace or the report directory without relying on browser history.

## Primary Navigation

| Route | Purpose | Evidence Boundary |
|---|---|---|
| `/` and `/dashboard/open` | Open Edition landing terminal | Widgets are external context; metrics describe bundled workflows |
| `/dashboard/reports` | Fixed navigation for generated report pages | No arbitrary generated-file browsing |
| `/dashboard/ipo` | IPO Watch Center | Discovery, review, and confirmation remain distinct |
| `/dashboard/listings-radar` | Interactive IPO and global-change evidence queue | Watchlist is local research follow-up, never status confirmation |
| `/dashboard/official-change-log` | Official CVM/ESMA weekday artifact viewer | Empty until an official monitor artifact is loaded; changes remain review evidence |
| `/dashboard/global-listings` | International listing coverage and monitors | Each jurisdiction retains its confirmation rule |
| `/dashboard/etf` | ETF Evidence Center | Synthetic change examples are separated from SEC periodic evidence |
| `/dashboard/financials-evidence` | Financials evidence and release-gate sequence | Demo scorecard is not real analyst performance |
| `/dashboard/intelligence` | Cross-asset research workspace | Planned stored connectors are not live feeds |
| `/dashboard/market-context` | Cross-Asset Markets terminal with Treasury Curve Regime Explorer | Official Treasury 2Y/10Y observations support regime calculations; TradingView values are not stored or scored |
| `/dashboard/volatility` | VIX Reaction Explorer | Select rising/cooling scenarios and windows; no unlicensed episode calculations |
| `/dashboard/presidential-impact` | Presidential Impact Lab: event intake, official Treasury context and calculation sandbox | News/Actions RSS and Treasury 2Y/10Y session changes are observable context; broader reactions and Truth Social remain gated |
| `/dashboard/commons` | Evidence Passport Commons | Source rights and claim boundaries are visible |
| `/dashboard/policy` | Public Use Policy | Product control, not legal advice |
| `/dashboard/governance` | Source Governance | Technical integration does not imply publishability |
| `/dashboard/release` | Release Center | Combines readiness, lineage, and quality before output |

## Open Edition Home And Cross-Asset Markets

The home view communicates that the GitHub edition runs without purchased
data. It provides direct navigation to IPO, ETF, Analyst Scorecards, Global
Listings, tokenized-asset/RWA evidence and control views, along with official
TradingView `Ticker Tape` and `Market Overview` widgets labeled as attributed
external display. When the sidebar collapses, a compact quick-access bar keeps
the VIX, Presidential Impact, Crypto/Commodities, Analyst Scorecards, RWA and
contributor paths visible.

Its first product-selling section promotes four distinctive reasons to explore
the project: `VIX Reaction Explorer`, `Trump Communication Impact`, `Global IPO Radar`, and
`Evidence Commons`. The following `Core Departments` section provides direct
entry to IPO, ETF, Financials, Market Intelligence, Data Rights, and generated
report workflows so visitors do not have to discover the system through
documentation first.

`/dashboard/market-context` now starts with an interactive `Treasury Curve
Regime Explorer` over the official daily `2Y`, `10Y`, and derived `2s10s`
series. Users can choose 1-, 5-, 20-, or 60-session comparisons to inspect
curve regime, steepening or flattening and basis-point changes. It then adds
a TradingView `Advanced Chart` defaulting to `BINANCE:BTCUSDT` plus watchlists
for `BTC`, `ETH`, `WTI`, `Brent`, gold, silver, foreign exchange and equity
benchmarks. MarketWitness stores only the official Treasury artifact in this
view; it does not read, store, export, or score widget values.

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

`/dashboard/listings-radar` turns that evidence into an operational workspace:
users can search issuers or details, filter by U.S. IPO versus global-change
stream, market, state and observed date, open cited evidence, and save a
personal browser-local follow-up list. The list does not alter project data or
promote an evidence signal to a confirmed listing. `Monitor Status` makes the
bundle date and collection mode explicit, and filtered CSV export turns a
research view into a portable review queue. The `Official-source activation`
matrix separates the no-cost weekday CVM/ESMA artifact workflow from SEC
operator configuration, rights reviews and restricted markets. The weekday
artifact persists an earlier CVM/ESMA snapshot and reports new, changed or
removed-from-feed evidence requiring review.

The change log is available at `/dashboard/official-change-log` when the optional
`MARKETWITNESS_PUBLIC_MONITOR_REPORTS` directory contains a downloaded
monitoring artifact. Until then, the view explicitly reports that no official
run is loaded. Its API surface at `/api/v1/listings/public-change-log` exposes
counts and source-linked review rows without upgrading evidence to a listing.

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
Those dated alert rows feed `/dashboard/listings-radar`, where international
review tasks can be filtered beside the monitored U.S. IPO registry.

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
- `/dashboard/volatility` presents a FRED-attributed VIX display, an
  interactive rising-versus-cooling quantitative validation explorer with
  synthetic statistics, and planned real `VIX`/`VXN`/`MOVE`/commodity
  episode designs once rights permit them.
- `/dashboard/presidential-impact` presents the Donald Trump communication
  event-study design, human-readable White House source links, a searchable
  archived News/Presidential Actions RSS metadata queue with topic filters
  and a compact recent-first view expandable to the full archive,
  an `Observed Treasury Context` panel comparing the first two available
  official 2Y/10Y Treasury sessions after thematic communications, and a
  `Communication Reaction Sandbox` with theme, forward-window and calendar
  controls. Treasury movement is temporal context, not causal attribution;
  broader sandbox statistics remain project-authored validation paths.

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
- `/api/v1/listings/radar`
- `/api/v1/commons/passports`
- `/api/v1/intelligence/modules`
- `/api/v1/intelligence/volatility`
- `/api/v1/intelligence/treasury-regimes`
- `/api/v1/intelligence/policy-signals`
- `/api/v1/intelligence/policy-events`
- `/api/v1/intelligence/policy-reactions`
- `/api/v1/intelligence/policy-treasury-context`
- `/api/v1/policy/public-use`
- `/api/v1/extensions/licensed`
- run, governance, readiness, operations-quality, and scorecard-release
  endpoints used by the Financials/control screens.

The localized contributor gateway at `/dashboard/contribute?lang=en` also
supports Japanese, Brazilian Portuguese, Traditional Chinese, and Korean for
global source proposals. Documentation and the default interface remain
English.
