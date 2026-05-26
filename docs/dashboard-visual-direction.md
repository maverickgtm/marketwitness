# Dashboard Visual Direction

Review date: `2026-05-25`.

## Objective

TargetAudit should feel like a useful research terminal, not a collection of
unrelated reports. The visual experience must make key modules and controls
immediately visible while separating auditable evidence from third-party
market context.

## Applied Principles

| Principle | TargetAudit Decision |
|---|---|
| Purpose and KPIs visible on arrival | The home view opens with the Open Edition promise, status metrics, and primary modules. |
| Stable navigation hierarchy | A sidebar separates workspace, evidence, and control areas. |
| Market context without report clutter | `Market Pulse` and the ticker strip are labeled external visual context. |
| Dedicated deep charting view | `/dashboard/market-context` contains the advanced `XLF` chart and comparison lens. |
| Clear data origin | TradingView panels state that they do not feed scoring. |
| Graceful offline state | External areas display a loading/information state when widgets are unavailable. |

## TradingView Widgets

Only official embedded widgets with visible attribution are used:

| Surface | Widget | Use |
|---|---|---|
| `/dashboard/open` | `Ticker Tape` | Compact benchmark, Financials, and major-stock context |
| `/dashboard/open` | `Market Overview` | Initial macro view in `Benchmarks` and `AI Leaders` tabs |
| `/dashboard/market-context` | `Ticker Tape` | Quick orientation before sector chart review |
| `/dashboard/market-context` | `Advanced Chart` | Interactive inspection of `AMEX:XLF` |
| `/dashboard/market-context` | `Market Overview` | Visual Financials and benchmark comparison |

TargetAudit does not read widget values, store them in DuckDB, export them, or
treat them as evidence for targets, IPOs, or holdings changes.

## Next Visual Phase

1. Extend the premium visual language across secondary reports.
2. Build first-party charts only for data TargetAudit can publish, such as
   document counts by market or approval states.
3. Produce launch captures and complete responsive review before publishing.

## Official Design And Integration Sources

- TradingView ticker widgets: <https://www.tradingview.com/widget-docs/widgets/tickers/>
- TradingView Market Overview: <https://www.tradingview.com/widget-docs/widgets/watchlists/market-overview/>
- TradingView Symbol Overview: <https://www.tradingview.com/widget-docs/widgets/charts/symbol-overview/>
- TradingView integration tutorial: <https://www.tradingview.com/widget-docs/tutorials/build-page/widget-integration/>
