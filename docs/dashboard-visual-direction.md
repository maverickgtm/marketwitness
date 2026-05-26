# Dashboard Visual Direction

Review date: `2026-05-25`.

## Objective

MarketWitness should feel like a useful research terminal, not a collection of
unrelated reports. The visual experience must make key modules and controls
immediately visible while separating auditable evidence from third-party
market context.

## Applied Principles

| Principle | MarketWitness Decision |
|---|---|
| Purpose and KPIs visible on arrival | The home view opens with the Open Edition promise, status metrics, and primary modules. |
| Stable navigation hierarchy | A sidebar separates workspace, evidence, and control areas. |
| Market context without report clutter | `Market Pulse` and the ticker strip are labeled external visual context. |
| Dedicated cross-asset research view | `/dashboard/market-context` starts with an official Treasury curve-regime explorer, followed by a BTC-first chart and crypto, commodity, FX, and benchmark lenses. |
| Clear data origin | Treasury calculations cite the official feed; TradingView panels state that they do not feed scoring. |
| Graceful offline state | External areas display a loading/information state when widgets are unavailable. |

## TradingView Widgets

Only official embedded widgets with visible attribution are used:

| Surface | Widget | Use |
|---|---|---|
| `/dashboard/open` | `Ticker Tape` | Compact benchmark, Financials, and major-stock context |
| `/dashboard/open` | `Market Overview` | Initial macro view in `Benchmarks` and `AI Leaders` tabs |
| `/dashboard/market-context` | `Ticker Tape` | Quick orientation across crypto, metals, energy and USD |
| `/dashboard/market-context` | `Advanced Chart` | Interactive inspection starting with `BINANCE:BTCUSDT` |
| `/dashboard/market-context` | `Market Overview` | Visual crypto, commodity, FX and index comparison |

MarketWitness does not read widget values, store them in DuckDB, export them, or
treat them as evidence for targets, IPOs, or holdings changes.

Above those widgets, `Treasury Curve Regime Explorer` calculates `2Y`, `10Y`
and `2s10s` context from the official Treasury artifact with selectable
session windows. Its observed rates are distinct from the external widgets
and do not become a trading recommendation.

## Next Visual Phase

1. Extend the premium visual language across secondary reports.
2. Extend first-party visualizations over publishable data, beginning with
   Treasury curve history, document counts by market and approval states.
3. Produce launch captures and complete responsive review before publishing.

## Official Design And Integration Sources

- TradingView ticker widgets: <https://www.tradingview.com/widget-docs/widgets/tickers/>
- TradingView Market Overview: <https://www.tradingview.com/widget-docs/widgets/watchlists/market-overview/>
- TradingView Symbol Overview: <https://www.tradingview.com/widget-docs/widgets/charts/symbol-overview/>
- TradingView integration tutorial: <https://www.tradingview.com/widget-docs/tutorials/build-page/widget-integration/>
- U.S. Treasury Daily Interest Rate XML Feed: <https://home.treasury.gov/treasury-daily-interest-rate-xml-feed>
