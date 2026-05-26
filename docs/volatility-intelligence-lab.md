# VIX Reaction Explorer

Initial design and review date: `2026-05-25`.

## Purpose

`VIX Reaction Explorer` does not aim to be a generic VIX screen. Its
question is:

> When verifiable stress appears in equities, technology, rates, or
> commodities, what happens next to monitored assets and confirmed listing
> events?

`/dashboard/volatility` publishes the **VIX Reaction Explorer** and an
attributed external VIX visualization. Visitors can select `VIX rises` or
`VIX cools`, choose a same-day, 1-, 5-, 20-, or 60-session horizon, and see
calculated median return, positive-frequency, worst-episode, and dispersion
metrics for a clearly labeled project-authored validation sample. Equity,
crypto, energy, haven, IPO, and ETF lenses remain available for interpretation.
The explorer also exposes calendar-period controls: `Full sample`, `2025`,
`2026 YTD`, `Last 180 days`, or custom start/end dates. Filtering recalculates
every visible statistic using only the included authored checkpoints and shows
their exact dates.
`/api/v1/intelligence/volatility` publishes the same scenarios, validation
results, period metadata, indicator families, and planned experiments. It
accepts optional `start` and `end` ISO-date query parameters. No real Cboe or
ICE series are downloaded or scored in this release.

## Visible Reaction Explorer

The explorer exposes the original research idea directly instead of hiding it
in methodology cards.

| Scenario | Research Question | Visible Lenses |
|---|---|---|
| `VIX rises` | Does stress propagate, or does the move remain isolated? | `SPY`/`QQQ`/`XLF`, `BTC`/`ETH`, energy/havens, IPO and ETF evidence |
| `VIX cools` | Does risk appetite return, or do broader conditions remain weak? | `SPY`/`QQQ`/`XLF`, `BTC`/`ETH`, energy/havens, IPO and ETF evidence |

The full-sample quantitative table contains six synthetic validation
checkpoints for each scenario/window combination, dated between `2025-01-20`
and `2026-05-25`. Selected ranges reduce that sample and recalculate the
statistics. These dates label project-authored calculation paths; they are not
claims that a historical VIX trigger occurred on those dates. Real reaction
statistics remain gated until public derived-output rights or an appropriately
licensed input path is approved.

## Volatility Families

| Phase | Indicators | Lab Purpose |
|---|---|---|
| 1 | `VIX`, `VIX1D`, `VIX9D`, `VIX3M` | Separate immediate equity stress from persistent risk |
| 1 | `VXN` | Connect technology volatility to `QQQ` and technology/AI IPO candidates |
| 1 | `MOVE` | Examine rates stress, Treasury conditions, and IPO financing climate |
| 2 | `VVIX`, `SKEW` | Study volatility-of-volatility and tail-protection demand |
| 2 | `OVX`, `GVZ` | Compare oil and gold stress with energy/safe-haven context |
| 3 | `VIX6M`, `VIX1Y` | Examine structural persistence after short-curve validation |

## Episode Design

| Episode | Question | Windows |
|---|---|---|
| `vix_shock` | How did selected assets react after a sharp `VIX` move? | same day, 1, 5, 20, and 60 sessions |
| `technology_stress_gap` | What happened to technology/listings when `VXN` diverged from `VIX`? | 5, 20, and 60 sessions |
| `rates_before_equities` | Did `MOVE` stress precede a `VIX` regime and IPO-pipeline changes? | 5, 20, and 60 sessions |
| `commodity_propagation` | Did stress propagate toward energy or gold when `OVX`/`GVZ` rose with equity volatility? | 1, 5, and 20 sessions |

Future outputs must disclose threshold, event date, input series, output
rights, episode count, windows, medians, directional frequency, dispersion,
drawdown, and available sample. Historical regularities are never buy/sell
instructions.

## Difference From Volatility Dashboards

Products such as `TheVIXtrader` and `Volatilitaets-Zentrale` already show VIX
regimes, term structure, and cross-asset measures. MarketWitness differentiates
itself by connecting volatility episodes to verified `IPO Watch` evidence,
technology listings, rates-financing context, ETF evidence when permitted, and
explicit Evidence Passports and claim boundaries.

## Sources And Limits

| Source | Evidence Available | MarketWitness State |
|---|---|---|
| Cboe Historical Data | Official daily history links for `VIX`, `VVIX`, `VIX9D`, `OVX`, `GVZ`, and others | Registered for research; public derived-output and storage rights pending review |
| Cboe Index Data Access | Index family and data-feed offering | Official scope reference; no integrated feed |
| ICE BofA MOVE Index | Official fixed-income volatility offering | Planned source; not activated without display/output authorization |
| FRED `VIXCLS` graph | Attributed VIX display from `2025-01-20` | External visualization with citation required; not stored or calculated |

Sources:

- Cboe Historical Data: <https://www.cboe.com/tradable_products/vix/vix_historical_data>
- Cboe Index Data Access: <https://www.cboe.com/us/indices/accessing-index-data/>
- ICE MOVE Index: <https://developer.ice.com/fixed-income-data-services/catalog/ice-data-indices-move-index>
- FRED VIXCLS: <https://fred.stlouisfed.org/series/VIXCLS>
- TheVIXtrader: <https://thevixtrader.com/>
- Volatilitaets-Zentrale: <https://vix-zentrale.de/>
