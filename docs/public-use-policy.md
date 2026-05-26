# Public Use And Data Rights Policy

Policy version: `2026-05-25`.

## Scope

TargetAudit is an auditable research tool. Its demonstration rankings, filing
monitors, holdings differences, and tokenized-asset observations are not a
recommendation to buy, sell, or hold any security.

This policy is an internal product control for the GitHub edition. It is not
legal, tax, or investment advice and does not replace external legal review
before operating a public service with real data.

The application publishes this policy at `/dashboard/policy` and exposes its
structured state at `/api/v1/policy/public-use`. Blocked-provider counts and
statuses are derived from `data/samples/source_registry.csv`.

## Data Layers

| Layer | What May Be Shown | Boundary |
|---|---|---|
| Project-created sandbox | Fixtures and reproducible demonstration results | They are not real market findings or real-firm performance |
| Public regulatory monitors | Filings, prospectuses, documentary confirmations, and reported holdings under the registered policy | A filing is not a recommendation, completed listing, or real-time signal |
| Authorized extensions | Local analysis of files supplied by a user with documented rights | They do not enable public real-data rankings without public-output permission for every input |
| Attributed external display | TradingView `XLF` widget for visual context | TargetAudit does not store, export, or score widget content |

## Publication Rules

1. Do not publish real analyst rankings until target prices, adjusted prices,
   corporate actions, and the historical universe all have documented
   public-output rights.
2. Do not describe prospectuses, filings, or registered offerings as confirmed
   first trading or investment opportunities without separate evidence and
   non-recommendatory language.
3. Do not automate, store, or republish sources marked `blocked` or
   `manual_only` in Source Governance.
4. Do not commit API keys, provider downloads, request-identification emails,
   or private files.

## Visible Restricted Sources

The dashboard must show negative rights decisions rather than hiding them. As
of `2026-05-25`, these include:

- `MAS OPERA Public Offers`: an official manual reference for Singapore; its
  search requires a security code and its terms restrict automated collection,
  caching, and deep links without permission.
- `TipRanks`: a conceptual rankings reference, with no automated extraction.
- `xStocks / Backed`, `Bybit xStocks`, and `Kraken xStocks`: tokenized-asset
  references excluded from public collection under the recorded review.

The source registry, rather than this narrative list, is the operational source
of truth for later updates.

## Operator Responsibility

- Review applicable terms and regulatory requirements before enabling a live
  collector.
- Maintain SEC-required identification and respect fair-access rules for live
  requests.
- Obtain external legal review if the project is publicly deployed with real
  data, advertising, subscriptions, or third-party-facing signals.

## Relationship To Other Controls

- `Source Governance` classifies a source as usable, pending, manual, or
  blocked.
- `Scorecard Readiness` prevents real rankings without authorized production
  inputs.
- `Release Center` decides whether an individual run has enough sources,
  lineage, and quality for publication.
- `Operations Quality` validates technical integrity, but never grants data
  rights by itself.
