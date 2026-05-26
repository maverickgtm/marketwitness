# Security

## Scope

MarketWitness processes evidence files, makes optional requests to public
sources, and exposes a local read-only API/dashboard. Please privately report
issues that could allow:

- code execution or file writes when importing evidence;
- disclosure of credentials, data under `data/private/`, or `User-Agent`
  contact details;
- bypassing license, provenance, or publication-block controls;
- unexpected external requests from a connector.

## Reporting

Use a private vulnerability report from the repository's GitHub `Security`
tab. Do not publish keys, private data, or an exploitable proof of concept in
an issue. The maintainer must enable `Private vulnerability reporting` when
publishing the repository.

Include the version or commit, affected component, impact, minimal
reproduction steps, and a suggested fix when available.

## Data And Credentials

Do not commit API keys, downloaded provider files, datasets without
redistribution permission, or personal email addresses used to identify SEC
requests. The project reserves `data/private/`, `data/raw/`, `.env`, and
`build/` for local use.
