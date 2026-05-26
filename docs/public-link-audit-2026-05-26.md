# Public Link Audit: Release Candidate v0.1.0-rc.1

Audit date: `2026-05-26`.

MarketWitness performs a pre-publication reference audit separately from its
offline test suite. The audit checks versioned documentation and the sample
registries that populate visible dashboard references, with an identified
`User-Agent` only where SEC or BLS access rules require one. Internal endpoint
prefixes, XML namespace identifiers and URL templates used by connector code
are not clickable public references and are therefore outside this check.

## Candidate Result

| Measurement | Result |
|---|---:|
| Unique referenced URLs inspected | 223 |
| Successful or redirected responses (`200`, `206`, `308`) | 167 |
| Intentional local/example placeholders skipped | 27 |
| Confirmed broken references (`404` or `410`) after correction | 0 |
| Responses retained for manual review (`403` or timeout) | 29 |

The manual-review group consists of sources that reject automated checks or
did not respond within the audit timeout. They are not treated as authorized
ingestion sources merely because a reference exists. Examples include blocked
or licensing-sensitive sources already governed in the registry, such as
Truth Social, FMP, GuruFocus, TipRanks and selected commercial or
exchange-facing pages.

## Corrections Made

- Replaced retired Massive Benzinga documentation with the current official
  Partners API overview.
- Replaced the unavailable AnaChart data-feed path with current official
  product and corporate-access pages.
- Replaced retired Pepperstone Shares and Trading API paths with current
  official Shares CFD and API Trading pages.
- Replaced the retired LBank support article with its accessible official
  tokenized-stock announcement.
- Removed misleading external SEC links from synthetic IPO fixtures; demo-only
  candidates now display as synthetic evidence without an external filing.

## Repeat The Audit

The online check is intentionally manual and is not run in continuous
integration because external sites can rate-limit automated validation.

```bash
export MARKETWITNESS_SEC_USER_AGENT="MarketWitness Research your-email@example.com"
make public-link-audit
```

The CSV evidence is written under `build/audits/`, which remains untracked.
