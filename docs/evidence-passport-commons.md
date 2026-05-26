# Evidence Passport Commons

Review date: `2026-05-25`.

## Distinctive Proposal

`Evidence Passport Commons` is an open network of verifiable records for
market-intelligence sources. MarketWitness begins with the trust question behind
any result:

> Where did this evidence originate, what right permits it to be displayed,
> how often does it change, and what claim can it not support by itself?

The product decision is to make provenance and rights public, contributable,
and queryable through an API.

## What A Passport Contains

| Block | Question Answered | Example |
|---|---|---|
| Identity | What official source and evidence class is this? | SEC N-PORT / ETF regulatory holdings |
| Rights | May it be collected, retained, or used for public derived output? | `source_link_and_derived_output` |
| Cadence | Is it a filing, periodic snapshot, or continuous feed? | Quarterly regulatory, not daily activity |
| Claim boundary | What does this source not prove? | A prospectus does not confirm first trading |

Version `0.1` publishes origin, rights, state, and review notes from the
audited governance registry. Structured cadence and source-specific claim
boundaries remain an open contribution mission for inherited records.

```text
GET /api/v1/commons/passports
/dashboard/commons
```

## Why It Can Matter On GitHub

A contributor does not need to purchase data. Someone familiar with an
official source in Japan, the United Kingdom, Brazil, Hong Kong, Singapore,
South Korea, or a new market can document its terms and confirmation rule
before writing a connector.

The contribution path is:

1. Locate the official source and terms page.
2. Document fields, access cost, and update cadence.
3. State which public output is permitted.
4. Define the evidence claim boundary.
5. Implement a connector only after passport approval.

## Positioning And Sustainability

Platforms such as OpenBB, Stocknear, and AnaChart offer broad market tooling,
visual workflows, or analyst-target history. MarketWitness does not claim to
surpass their breadth or licensed datasets. The Commons provides a different
public layer: verify whether data can be used and what it means before turning
it into an alert, score, screen, or integration.

The registry and API should remain open. Possible future paid services can
coexist with that commitment: hosted monitoring, private workspaces using a
customer's own licensed data, institutional lineage support, or sponsored
official connectors with transparent rules.

## Trust Rule

An approved passport never converts evidence into financial advice. It enables
a documented way to read and, when rights permit, display facts derived from a
source.
