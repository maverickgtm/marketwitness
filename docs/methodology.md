# Methodology v0.3.3

## Initial Vertical

`v0.3.3` prepares analysis for `U.S. Financials`, beginning with banks and
other financial companies with verifiable targets. The preferred real-pilot
sector benchmark is `XLF`. The engine remains general, but the first research
claim must not be framed as a multisector ranking.

## Research Questions

TargetAudit separates three questions:

1. **Target Hit Rate:** was the target reached during its horizon?
2. **Forecast Accuracy:** how close was the target to the terminal price?
3. **Signal Value:** did the direction implied by the target outperform its
   benchmark during the same period?

A high hit rate alone does not prove a profitable strategy.

## Observation Requirements

An observation is one target published by a firm for an instrument on a date.
It is evaluable only with a stable identifier, ticker, issuer, firm,
publication date, positive target, verifiable source reference, and sufficient
daily adjusted-price data. Analyst name and rating are retained when available
but are optional.

Real external targets enter only through an authorized export and a manifest
declaring provider, export date, license reference, and permitted internal
research use. This documents operational provenance; it does not authorize
public rankings until output rights are approved.

## Historical Universe And Revisions

A public real-data ranking must use point-in-time membership. A target outside
the supplied universe on its publication date is excluded as
`outside_historical_universe`. Membership supplies the period-correct sector
for segmented rankings.

When a firm publishes another valid target for the same ticker before the
original horizon expires, the earlier row is excluded as
`superseded_by_later_target`. It is treated as a withdrawn signal, not a
failure.

## Corporate Actions

Adjusted bars alone do not prove that a pre-split nominal target remains
comparable. When an audited corporate-action register is supplied, a horizon
crossing a `stock_split`, `reverse_split`, or `ticker_change` is excluded as
`corporate_action_review_required`. This version detects the issue; it does
not silently rescale targets or join ticker histories.

## Timing Conventions

- Default horizon: `365` calendar days after publication.
- Reference: last adjusted close on or before publication, no more than seven
  calendar days old.
- Entry: first adjusted close after publication, no more than seven calendar
  days later.
- Hit evaluation begins after the entry close; entry-day intraday moves are
  not counted retroactively.
- A target already crossed at executable entry is excluded as
  `target_crossed_before_entry`.
- Expiration uses the final available close on or before the expected horizon,
  within seven calendar days.
- An unexpired observation at calculation date is `pending`, not a failure.

## Hit Definition

Direction is derived against the reference price:

| Direction | Definition | Hit Rule |
|---|---|---|
| `up` | target above reference | Later adjusted daily high reaches or exceeds target within horizon |
| `down` | target below reference | Later adjusted daily low reaches or falls below target within horizon |
| `flat` | target equals reference | Excluded from directional scoring |

`days_to_target` is the calendar-day distance from executable entry to first
hit. A target hit is not a realized gain.

## Executable Backtest Convention

- Entry at the first eligible adjusted close after publication.
- Exit on hit at the exact target as a limit-order assumption, otherwise at
  the horizon adjusted close.
- Default cost is `10 bps` per side, configurable with
  `--transaction-cost-bps`.
- Net excess return uses the same direction and exit date for the benchmark
  where a benchmark bar exists.

This is a reproducible simulation, not evidence of actual execution. It does
not model slippage, short-borrow fees, taxes, separate dividends, or position
sizing.

## Metrics

Per evaluated observation:

- `hit`, `terminal_price`, and `terminal_absolute_error_pct`;
- `directional_return_pct`, `benchmark_directional_return_pct`, and
  `excess_return_pct`;
- `strategy_exit_reason`, `strategy_exit_date`, `strategy_exit_price`;
- gross return, cost per side, net return, and net excess return.

Per firm and eligible sector/direction segment:

- evaluated `N` and target hit rate;
- Wilson 95% confidence interval;
- mean terminal absolute error;
- median days to target for hits;
- average excess return and average simulated net/excess return;
- count of exits that could be aligned to a benchmark bar.

For `x` hits in `n` evaluated rows, TargetAudit reports a Wilson 95% interval
using `z = 1.959963984540054`:

```text
center = (p + z^2/(2n)) / (1 + z^2/n)
margin = z * sqrt(p(1-p)/n + z^2/(4n^2)) / (1 + z^2/n)
interval = [center - margin, center + margin]
```

where `p = x / n`. It quantifies sampling uncertainty, not source bias,
universe-selection bias, or dependence between observations.

## Ranking And Exclusions

A production public ranking should require at least `50` evaluable
observations per firm. The CLI permits lower development thresholds and the
report discloses the applied minimum. A subgroup must independently satisfy
the threshold.

Recorded exclusions include missing required fields or sources, non-positive
targets, missing or delayed reference/entry prices, target crossed before
entry, incomplete price or benchmark windows, flat targets, unresolved
corporate actions, historical-universe mismatch, and superseded targets.

## Reproducibility

Every report must record methodology version, `as_of` date, historical
universe identifier or its declared absence, superseded observations, exit and
cost rules, input files/providers, exclusions and reasons, and modified
parameters such as minimum sample.
