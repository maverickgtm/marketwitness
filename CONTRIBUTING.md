# Contributing

Thank you for helping make MarketWitness verifiable and useful.

## Ground Rules

- Do not add third-party datasets without documenting the license and
  redistribution permission.
- Document every new metric in `docs/methodology.md` and include tests.
- Do not present a firm as "best" without disclosing the sample, period, and
  benchmark.
- The initial public vertical is `U.S. Financials`; proposals for other
  sectors must explain their source, universe, and benchmark.
- Preserve original sources or auditable identifiers for every real
  observation.

## Development

```bash
make verify
```

To propose a data source, open an issue describing historical coverage, fields,
usage limits, cost, and redistribution conditions. Use the GitHub
`Data source proposal` template to record this evidence consistently.

The main edition must preserve at least one no-cost functional path: public
regulatory sources, redistributable fixtures, and contributed data with
documented rights are preferred. A commercial connector may be added as an
optional extension, never as a requirement for basic use.

## Evidence Passport Commons

MarketWitness welcomes global contributors who can expand its network of
official evidence sources. Before proposing code for a new source, prepare an
`Evidence Passport` through the `Data source proposal` template. It must
identify:

- the official source and evidence class;
- terms, license, or permission for public derived output;
- update frequency or publication cadence;
- the confirmation rule and the claim the source does not prove;
- any cost, key, or registration requirement.

Accepted passports can be incorporated into the public registry and
`/api/v1/commons/passports`. A connector is implemented only once its public
use is defensible. This separation lets people contribute without purchasing
datasets or writing Python.

Before proposing public output or a new collector, read the
[Public Use And Data Rights Policy](docs/public-use-policy.md): a source
marked blocked or manual must not be automated through a contribution.

## Security And Privacy

Do not include API keys, `.env` files, downloads in `data/raw/`, private
evidence, or the email used in SEC request headers. Report security issues
privately according to [SECURITY.md](SECURITY.md).
