# Volatility Intelligence Lab

Initial design and review date: `2026-05-25`.

## Purpose

`Volatility Intelligence Lab` does not aim to be a generic VIX screen. Its
question is:

> When verifiable stress appears in equities, technology, rates, or
> commodities, what happens next to monitored assets and confirmed listing
> events?

`/dashboard/volatility` publishes the research design and an attributed
external VIX visualization. `/api/v1/intelligence/volatility` publishes the
indicator families and planned experiments. No real Cboe or ICE series are
downloaded or scored in this release.

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
regimes, term structure, and cross-asset measures. TargetAudit differentiates
itself by connecting volatility episodes to verified `IPO Watch` evidence,
technology listings, rates-financing context, ETF evidence when permitted, and
explicit Evidence Passports and claim boundaries.

## Sources And Limits

| Source | Evidence Available | TargetAudit State |
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
