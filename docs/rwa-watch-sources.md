# RWA Watch: Exchanges And Base Sources

Review date: `2026-05-26`.

`RWA Watch` is a MarketWitness sandbox demonstrating how tokenized instruments
linked to stocks or ETFs could be observed. It uses redistributable synthetic
observations only. A tradeable token or CFD does not supply analyst price
target history and is not part of the Financials Scorecard.

## Review Method And Main Finding

The screened universe was the first 20 centralized exchanges displayed by
CoinGecko under `Trust Score` on the review date. This is a repeatable search
frame, not a trading recommendation.

The efficient architecture is `issuer-first`: understand the asset structure
and backing from the issuer, then use exchanges only as secondary evidence of
availability or liquidity. It avoids duplicating connectors for venues listing
the same issued instrument.

| Base Source | Official Evidence Found | Decision |
|---|---|---|
| xStocks / Backed Public API | Unauthenticated metadata, legal-document, NAV, market-data, and proof-of-reserves APIs; reviewed terms restrict automated retrieval/republication | Technical reference blocked from real collection without written authorization |
| Ondo Global Markets | Application-oriented market data and authenticated APIs requiring onboarding and `x-api-key` | Authorized candidate, not open free source; confirm eligibility and output rights |
| Compatible exchanges | Spot-market availability or liquidity for instruments | Secondary layer only; each venue requires its own rights review |

## Reviewed Exchange Summary

| Exchange Group | Relevant Finding | Treatment |
|---|---|---|
| Kraken and Bybit | Official `xStocks` materials; availability/jurisdiction restrictions stated | Blocked as public dashboard collection sources |
| Gate and Bitget | Published tokenized-stock or Ondo offerings | Secondary references pending output-rights confirmation |
| LBank | Announced an `xStocks` zone | Reference pending API confirmation |
| OKX and Gemini | Documented Web3/DEX or regional tokenized-stock routes with API limitations | Do not integrate as public connectors |
| Coinbase and Crypto.com | Brokerage stocks/ETFs for eligible users | Brokerage reference, not RWA or analyst-target feed |
| Binance, Bitstamp, Bitvavo, BingX, MEXC, HashKey, Upbit, KuCoin, Bitso, CoinW, Bullish | No confirmed suitable public tokenized-stock data path in the focused review | No connector |

## Pepperstone

Pepperstone provides derivatives and account-linked services rather than a
base xStocks/Ondo-style source:

| Product | Official Evidence | Decision |
|---|---|---|
| Share CFDs | Exposure to over 1,100 stock CFDs in 23 countries without share ownership | Do not treat as tokenized assets or target prices |
| TradingView | Attributed charting context | External visual context only |
| Trading API | REST API for pricing, liquidity, and account data | Optional user integration only; no confirmed open publishable feed |

## Technical Priority

1. Keep `RWA Watch Sandbox` operational with first-party fixtures only.
2. Obtain written display, retention, and derived-output authorization before
   any real `xStocks / Backed` adapter.
3. Confirm Ondo onboarding and output rights before enabling its documented
   price endpoints.
4. Keep Bybit and Kraken blocked for the global public edition; require terms
   confirmation for secondary venues.
5. Keep CFDs and brokerage products out of comparisons suggesting share
   ownership or analyst-history evidence.

## Official Sources

- CoinGecko exchanges: <https://www.coingecko.com/en/exchanges>
- xStocks API and terms: <https://docs.xstocks.fi/apis/openapi> and <https://xstocks.fi/documents/xstocks-terms-of-service.pdf>
- Ondo Global Markets: <https://docs.ondo.finance/ondo-global-markets/overview>
- Ondo API: <https://docs.ondo.finance/api-reference/overview>
- Bybit xStocks: <https://www.bybit.com/en/help-center/article/FAQ-xStocks-on-Bybit>
- Kraken xStocks: <https://www.kraken.com/xstocks>
- Gate xStocks: <https://www.gate.com/xstocks>
- Bitget Ondo announcement: <https://www.bitget.com/support/articles/12560603838361>
- LBank announcement: <https://www.lbank.com/support/articles/1956350560365969408>
- Pepperstone share CFDs: <https://pepperstone.com/en/markets/share-cfds/>
- Pepperstone Trading API: <https://pepperstone.com/en/platforms/integrations/api-trading/>
