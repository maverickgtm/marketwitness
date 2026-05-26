# Continuous Operations Guide

## Open Edition Operating Principle

MarketWitness is built to run with redistributable fixtures and eligible public
evidence paths without a paid data subscription. Live collectors must follow
the source registry, public-use policy, and any required identification,
registration, cadence, and output-right rules.

The GitHub candidate does not publish real analyst rankings and does not treat
listing documents, ETF holding differences, volatility context, or public
statements as investment recommendations.

## Local Build And Dashboard

```bash
python3 -m pip install -e ".[application]"
make verify
make demo
export MARKETWITNESS_DATABASE="build/demo/marketwitness.duckdb"
export MARKETWITNESS_SOURCE_REGISTRY="data/samples/source_registry.csv"
export MARKETWITNESS_PROVIDER_APPROVALS="data/samples/provider_approval_queue.csv"
export MARKETWITNESS_GENERATED_REPORTS="build/demo"
export MARKETWITNESS_LICENSED_EXTENSIONS="data/samples/licensed_extensions.csv"
python3 -m uvicorn marketwitness.api:app --host 127.0.0.1 --port 8000
```

Review the dashboard at <http://127.0.0.1:8000/> and the publication controls
at `/dashboard/policy`, `/dashboard/governance`, `/dashboard/readiness`, and
`/dashboard/release`.

## SEC Identification

SEC live access requires an identifying `User-Agent` containing a monitored
contact address. Do not commit that address to public repository files:

```bash
export MARKETWITNESS_SEC_USER_AGENT="MarketWitness contact@example.com"
```

Use a real monitored address in your local runtime environment when making
live requests. Respect SEC fair-access guidance, request cadence, and caching
expectations. The repository fixtures require no SEC contact address.

## Operational Gates

| Control | Purpose | Blocking Condition |
|---|---|---|
| Source Governance | Classify access and output rights | Source is pending, manual-only, restricted, or blocked |
| Provider Approvals | Record written permission decisions | Required evidence has not been approved |
| Scorecard Readiness | Require productive target/price/action/universe sources | Any required class lacks public-output rights |
| Operations Quality | Check versioning, lineage, required inputs, and exclusion rates | Missing assets/provenance or unacceptable run quality |
| Release Center | Combine rights, provenance, and run quality | Any required control fails |

A technical `quality_pass` never grants publication rights.

## Analyst Scorecard Workflow

Real target rows may enter through `targets-import` only from an authorized
user-provided export and manifest. Keep provider files outside Git, normally
under ignored local storage such as `data/private/` or `data/raw/`.

A candidate public scoring run needs:

- target rows with per-observation evidence and provider linkage;
- adjusted price evidence with compatible output rights;
- corporate-action audit input;
- point-in-time historical universe membership;
- documented methodology version, run assets, and output permission.

The evaluator applies timing conventions, target-revision exclusion,
corporate-action guards, benchmark comparison, stated transaction costs, and
minimum-sample controls described in [Methodology](methodology.md).

## U.S. IPO Workflow

The intended progression is:

1. `sec-ipo-discover` identifies registration/prospectus/withdrawal-form
   candidates from SEC daily intake.
2. `sec-ipo-alerts` maintains snapshots and routes exact `CIK` watchlist
   matches for review.
3. `ipo-watch-review` applies a documented human decision.
4. `ipo-watch` renders the reviewed registry.

Discovery or triage does not promote a company to a verified status without a
recorded review decision.

## Global Listing Workflow

Implemented evidence workflows cover:

| Region | Monitor | Confirmation Boundary |
|---|---|---|
| London | LSE and FCA | Expected issue/document metadata requires review |
| Hong Kong | HKEX | Official AP/PHIP lifecycle signals |
| Australia | ASX | Upcoming or withdrawn listing evidence |
| Toronto | TSX | Published new listing confirmation only |
| Singapore | SGX | Prospectus publication, not trading confirmation |
| Tokyo | EDINET and JPX | Documents and exchange milestones separated |
| Brazil | CVM | Offering record, with later B3 confirmation needed |
| Europe | ESMA | Prospectus/admission metadata remains review evidence |
| South Korea | OpenDART | Offering filing, not KRX listing |

`global-alerts` compares current snapshots with prior history and reports new,
changed, or missing-from-feed records for review. Do not convert a removed
feed entry into a withdrawal or completed listing without primary evidence.

Restricted paths remain explicit: MAS OPERA is manual/blocked, SEDAR+
automated collection is not enabled, KRX output is excluded under reviewed
terms, and Russia is research-only due to sanctions and rights risk.

## ETF Evidence Workflow

The bundled demonstration compares normalized synthetic snapshots for ARKK,
XLF, and IYF. Local import adapters exist for issuer-shaped files, but real
issuer data must not be redistributed without authorization.

SEC N-PORT provides the regulatory path:

- `sec-nport-import` normalizes permitted XML positions as periodic evidence;
- `sec-nport-collect` obtains recent filings by `CIK` and `seriesId` using
  identified SEC access;
- `sec-nport-datasets` catalogs/extracts official quarterly dataset ZIPs;
- `sec-nport-sync` tracks newly observed releases;
- `sec-nport-backfill` creates historical periodic snapshots and manifests.

N-PORT output is periodic reported holdings evidence, never a daily portfolio
trade claim.

## Policy And Volatility Research

`Presidential Impact Lab` can begin future official-event intake from White
House News and Presidential Actions RSS. White House Wire is metadata-only
because linked content may be third party. Truth Social history or live
collection remains disabled without permission.

`Volatility Intelligence Lab` displays attributed FRED VIX context and
publishes experimental design. Do not publish calculated historical episodes
from Cboe or ICE sources until their storage and derived-output rights are
approved.

## Scheduled GitHub Artifact

`.github/workflows/open-edition-report.yml` runs `make verify` and builds the
Open Edition artifact each Monday at `12:17 UTC` or on manual dispatch. It
uses fixtures only, requires no secrets, and retains output temporarily. A
future live service requires separate deployment, source-rights validation,
security review, and legal review.

## Operational Limits

- Never commit API keys, provider downloads, personal request headers, or
  private evidence.
- Never activate a source whose registry status blocks collection or output.
- Never describe a filing, holding difference, volatility correlation, or
  public communication as a trading instruction.
- Never publish a real analyst ranking unless all required inputs and their
  derived-output rights pass Release Center review.
