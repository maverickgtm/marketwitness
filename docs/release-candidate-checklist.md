# GitHub Release Candidate Checklist

## Candidate Objective

Publish `MarketWitness Open Edition v0.1.0-rc.1` as an open, reproducible,
useful project without mandatory payments. This candidate demonstrates
evidence auditing, regulatory monitors, and a navigable dashboard; it does not
promise real analyst rankings or investment recommendations.

## Ready For The Candidate

- [x] Code licensed under MIT.
- [x] `DISCLAIMER.md`, public-use policy, and visible source boundaries.
- [x] `CONTRIBUTING.md`, `SECURITY.md`, issue templates, and pull request
  template.
- [x] Automated tests and GitHub Actions workflow for Python 3.9 and 3.12.
- [x] Reproducible Open Edition bundle and installable wheel without paid data.
- [x] Read-only dashboard and API with identifiable blocked sources.
- [x] Registry of 49 sources with permission and evidence classifications.
- [x] Official free presidential-event intake through `White House News RSS`
  and `Presidential Actions RSS`, with a deduplicated topic-triage artifact.
- [x] Official Treasury, macro-catalyst and CFTC positioning laboratories with
  explicitly non-prescriptive output boundaries.
- [x] SEC Insider Activity Lab with quarterly Forms `3`/`4`/`5`
  classification, issuer/owner search, anomaly holds and filing-review rules.

## Before Publishing The Repository

- [x] Run `make verify` and `make release-hygiene` from a local clean clone of
  the candidate branch.
- [ ] Retain a green GitHub Actions result on the candidate commit after
  pushing the public repository.
- [x] Publish three selected screenshots in `docs/assets/` and use them in
  `README.md`: IPO Watch, Global Listings, and Presidential Impact Lab.
- [ ] Create the GitHub repository with description, topics, and the correct
  link before adding permanent badges.
- [ ] Configure `MARKETWITNESS_SEC_USER_AGENT` and
  `MARKETWITNESS_MACRO_USER_AGENT` as repository secrets before enabling the
  official policy-monitor workflow.
- [ ] Enable `Private vulnerability reporting` under the GitHub `Security` tab.
- [x] Perform a final secret scan and confirm that email addresses, API keys,
  `data/private/`, `data/raw/`, and `build/` are not versioned.
- [x] Confirm the publishable `main` branch history contains only GitHub
  noreply author identities and no private permission draft.
- [ ] Push only the sanitized `main` branch. Do not use `git push --all` or
  publish local stash/backup refs, which may still retain pre-rewrite local
  history containing personal author identities.
- [ ] Create the `v0.1.0-rc.1` tag and release notes only after Actions passes
  from the public repository.

Run this publication hygiene check before pushing a public candidate:

```bash
make release-hygiene
```

It intentionally fails when tracked sensitive/generated files are present,
when non-placeholder email addresses appear in tracked files, or when commit
history still exposes non-`users.noreply.github.com` author emails.

## Not Blocking The Open Edition

- A publishable real history of price targets from firms such as Roth MKM,
  KBW, UBS, Barclays, or Citi. This is a future licensed extension.
- Proprietary Cboe/ICE historical series for VIX/VVIX/MOVE episodes.
- Activation of RWA data, issuer daily holdings, or commercial sources.

## Blocks Any Real-Data Claim

- Publishing real analyst rankings without output rights and per-observation
  evidence.
- Automating Truth Social, sources marked `restricted_no_collection`, or
  third-party White House Wire links.
- Presenting reaction, volatility, or listing studies as investment advice or
  proven causality.

## Verification Commands

```bash
python3 -m pip install -e ".[application]"
make verify
```

To review the built dashboard:

```bash
export MARKETWITNESS_DATABASE="build/demo/marketwitness.duckdb"
export MARKETWITNESS_SOURCE_REGISTRY="data/samples/source_registry.csv"
export MARKETWITNESS_PROVIDER_APPROVALS="data/samples/provider_approval_queue.csv"
export MARKETWITNESS_GENERATED_REPORTS="build/demo"
export MARKETWITNESS_LICENSED_EXTENSIONS="data/samples/licensed_extensions.csv"
python3 -m uvicorn marketwitness.api:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` and review `/dashboard/ipo`,
`/dashboard/global-listings`, `/dashboard/intelligence`,
`/dashboard/volatility`, `/dashboard/presidential-impact`,
`/dashboard/cot-positioning`, `/dashboard/insider-activity`, and
`/dashboard/policy`.
