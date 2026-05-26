# Data Schema v0.1

This document describes the canonical files and generated records used by
TargetAudit. Real provider exports belong outside Git unless redistribution
rights are documented.

## Scorecard Inputs

### `targets.csv`

One row per published price target.

| Column | Required | Meaning |
|---|---:|---|
| `observation_id` | Yes | Stable unique identifier |
| `ticker`, `company_name`, `firm` | Yes | Instrument, issuer, and publishing firm |
| `analyst`, `rating`, `sector` | No | Optional published/context fields |
| `published_date`, `price_target` | Yes | ISO event date and positive target |
| `horizon_days`, `benchmark_symbol` | No | Horizon and benchmark defaults |
| `source_provider`, `source_url` | Yes | Verifiable evidence reference |
| `provider_id` | Required for governed runs | Stable link to `source_registry.csv` |

### Authorized Import Manifest

`targets-import` converts a user-provided authorized export to canonical rows.
Its JSON manifest identifies `provider_id`, `provider_name`,
`source_provider`, `exported_on`, `obtained_via`, `license_reference`,
`authorized_for_internal_research`, `authorized_for_public_output`,
`field_map`, and `defaults`. A normalized import is not itself permission to
publish public rankings.

### `prices.csv`

| Column | Required | Meaning |
|---|---:|---|
| `ticker`, `date` | Yes | Instrument and ISO date |
| `adjusted_high`, `adjusted_low`, `adjusted_close` | Yes | Comparable adjusted daily bar |
| `source_provider` | Yes | Price provenance |

Rows with non-finite values, duplicate ticker dates, or closes outside the
high/low range are rejected.

### `historical_universe.csv`

| Column | Required | Meaning |
|---|---:|---|
| `universe_id`, `ticker`, `company_name`, `sector` | Yes | Point-in-time cohort identity |
| `member_from`, `member_to` | Start required | Inclusive membership window |
| `source_provider`, `source_url`, `verified_on` | Yes | Auditable evidence |

Mixed universes, overlapping windows for a ticker, and missing HTTPS evidence
are rejected.

### `corporate_actions.csv`

| Column | Required | Meaning |
|---|---:|---|
| `action_id`, `company_name`, `prior_ticker`, `current_ticker` | Yes | Affected issuer/instruments |
| `action_type`, `effective_date` | Yes | `stock_split`, `reverse_split`, or `ticker_change` and date |
| `split_ratio_new`, `split_ratio_old` | For splits | Adjustment ratio |
| `evidence_level`, `source_title`, `source_url`, `verified_on`, `review_note` | Yes | Audit evidence |

A target horizon crossing a recorded action is guarded for review; this
version does not automatically rescale it.

## Evaluation Output And Warehouse

`evaluations.csv` retains evaluated, excluded, and pending observations,
reference/entry/terminal values, exclusion reasons, historical-universe links,
supersession links, hit metrics, and simulated strategy exit/cost/benchmark
fields.

When `evaluate --database` is used, DuckDB stores:

| Table | Purpose |
|---|---|
| `evaluation_runs` | Run parameters, `as_of`, methodology version, dataset fingerprint, and status counts |
| `run_assets` | Input/output path, size, SHA-256, role, and declared provider |
| `evaluations` | Typed row-level evaluation output linked by `run_id` |

`run_id` is immutable. A corrected run receives a new identifier.

## Governance Files

### `source_registry.csv`

Records `provider_id`, name, `data_class`, access model, integration status,
license status, publication policy, official/reference URLs, review date, and
review note. The UI derives states such as usable, review required, license
required, and blocked.

### `provider_approval_queue.csv` And Decisions

The queue records provider, approval status, priority, requested use, required
evidence, promotion criteria, evidence URL, review date, and note.
`provider_approval_decisions.csv` records an explicit
`retain_pending`, `approve_public_output`, or `reject_public_output` decision.
Approval produces reviewed copies; it never silently edits base governance or
bypasses scorecard readiness/release controls.

### `licensed_extensions.csv`

Informational catalog of paid user options, including provider, data class,
access model, visible pricing, stated coverage, allowed mode, public-output
status, source URLs, and review decision. It is not an ingestion table.

## IPO And Global Listings

### `ipo_watch.csv`

| Field Group | Meaning |
|---|---|
| `company_name`, `cik`, `theme` | Watched entity identity |
| `status`, `status_date`, optional `ticker`/`exchange` | Verified research state |
| `filing_type`, `evidence_level`, `source_title`, `source_url` | Primary evidence |
| `next_event`, `risk_flags` | Research work, not trade advice |

Statuses are `candidate_unverified`, `filed_public`, `listed`, or
`withdrawn`. Promotion requires primary evidence and documented review.

`sec-ipo-discover`, `sec-ipo-alerts`, and `ipo-watch-review` produce discovery,
triage, and audited human-decision records. An exact `CIK` link routes review
but does not change status automatically.

### `global_market_sources.csv`

The market registry identifies `market_code`, market, jurisdiction, connector
status, official source name/URL, signal type, confirmation rule, and next
implementation step.

Implemented normalized global feeds include:

| Monitor | Core Record Identity | Claim Boundary |
|---|---|---|
| LSE/FCA | issuer/document metadata | Review signal, not completed admission |
| HKEX | company plus lifecycle status/date/code | Official stage, not investment decision |
| ASX | company/upcoming listing row | Anticipated date may change |
| TSX | company/listing record | Completed-listing confirmation |
| JPX | company/security/listing date | Exchange milestone, distinct from filing |
| EDINET | `document_id` | Japanese regulatory filing only |
| SGX | prospectus document | Published document only |
| CVM | `offering_id` | Brazilian offering record, not B3 listing |
| ESMA | `document_id + isin` | European prospectus/admission review |
| OpenDART | `filing_id` | Korean offering filing review |

`global-alerts` archives daily snapshots and reports `new`, `changed`, or
`removed_from_feed_review`; missing feed rows are not automatically
withdrawals or listings.

`issuer_listing_confirmations.csv` stores curated official issuer milestones:
company, market, ticker, `event_type`, event date, official source, verified
date, evidence level, and research note.

## ETF Holdings Records

Normalized snapshots contain issuer, fund symbol/name, effective and captured
dates, position ticker/name, shares, weight, frequency, and source URL.
`source_frequency` distinguishes `synthetic_demo`, `daily_official`,
`official_snapshot`, and `regulatory_periodic`.

The activity comparator emits prior/current values, differences, and
`new_position`, `increased`, `decreased`, `removed_position`, or
`weight_changed`. These are observed differences, not confirmed manager
transactions.

Import paths exist for:

- ARK-shaped local CSV snapshots;
- State Street SPDR/XLF-shaped local CSV snapshots;
- manually downloaded iShares/IYF snapshots;
- SEC `NPORT-P` or `NPORT-P/A` XML;
- SEC quarterly N-PORT dataset catalog, synchronization, and backfill files.

N-PORT normalizes equity-share positions only and always labels them
`regulatory_periodic`. Archived provider/raw files remain outside Git.
