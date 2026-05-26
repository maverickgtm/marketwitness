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
- [x] Official free path for future presidential events through
  `White House News RSS` and `Presidential Actions RSS`.

## Before Publishing The Repository

- [ ] Run `make verify` from a clean clone and retain a green CI result on the
  candidate commit.
- [x] Publish three selected screenshots in `docs/assets/` and use them in
  `README.md`: IPO Watch, Global Listings, and Policy Signals.
- [ ] Create the GitHub repository with description, topics, and the correct
  link before adding permanent badges.
- [ ] Enable `Private vulnerability reporting` under the GitHub `Security` tab.
- [ ] Perform a final secret scan and confirm that email addresses, API keys,
  `data/private/`, `data/raw/`, and `build/` are not versioned.
- [ ] Publish from a clean or rewritten history: a private permission draft
  previously included a personal email address in local commits.
- [ ] Create the `v0.1.0-rc.1` tag and release notes only after Actions passes
  from the public repository.

## Not Blocking The Open Edition

- A publishable real history of price targets from firms such as Roth MKM,
  KBW, UBS, Barclays, or Citi. This is a future licensed extension.
- Proprietary Cboe/ICE historical series for VIX/VVIX/MOVE episodes.
- Activation of RWA data, issuer daily holdings, or commercial sources.
- An automatic White House RSS collector. The source is already approved as a
  candidate; the collector is a post-candidate improvement.

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
`/dashboard/volatility`, `/dashboard/policy-signals`, and
`/dashboard/policy`.
