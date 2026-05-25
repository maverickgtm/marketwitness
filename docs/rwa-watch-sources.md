# RWA Watch: Exchanges Y Fuentes Base

Revision: `2026-05-24`.

`RWA Watch` es un sandbox incluido en TargetAudit para demostrar como observar
instrumentos ligados a acciones o ETF mediante tokenizacion. Usa solamente
observaciones sinteticas redistribuibles. No es parte de `Financials
Scorecard`: un token negociable o un CFD no proporciona historial de `price
targets` de analistas.

## Metodo De Revision

El universo de cribado son los primeros 20 exchanges centralizados mostrados
por CoinGecko bajo `Trust Score` en la fecha de revision. Ese ranking permite
repetir la busqueda, pero no es una recomendacion de negociar en un exchange.

Por cada proveedor se busco documentacion oficial de acciones, ETF,
instrumentos tokenizados, CFD o API publicas. Que una pagina o API sea
accesible no demuestra permiso para conservar, republicar o mostrar sus datos
en un producto publico; cualquier conector queda sujeto a revision de
terminos.

## Hallazgo Principal

La arquitectura mas eficiente es `issuer-first`: obtener la estructura y
respaldo del activo del emisor, y despues utilizar exchanges como mercados
secundarios para contrastar disponibilidad o liquidez. Esto evita veinte
conectores duplicados para productos basados en la misma emision.

| Fuente Base | Evidencia Oficial Encontrada | Decision |
|---|---|---|
| xStocks / Backed Public API | Documenta APIs sin autenticacion para metadatos, documentacion legal, NAV, datos de mercado y proof of reserves; sus terminos limitan servicios a fines informativos/internos y restringen retrieval o republicacion automatizados | Referencia tecnica bloqueada; no recolectar ni publicar datos reales sin autorizacion escrita |
| Ondo Global Markets | Documenta datos de mercado para aplicaciones y APIs autenticadas; la integracion exige onboarding y `x-api-key` | Segundo candidato autorizado, no fuente gratuita abierta; confirmar acceso, elegibilidad y derechos de output |
| Exchanges compatibles | Pueden exponer mercado spot, disponibilidad o liquidez del instrumento | Capa secundaria solamente; Bybit queda bloqueado por sus restricciones de producto y otros venues requieren revision propia |

## Top 20 CEX Revisados

| # | Exchange | Producto Oficial Relevante Encontrado | Encaje Propuesto |
|---:|---|---|---|
| 1 | Coinbase Exchange | Coinbase Capital Markets ofrece stocks y funds para clientes elegibles de EE. UU. | Referencia de brokerage; no se confirmo feed RWA publico |
| 2 | Binance | No se confirmo una ruta vigente de acciones tokenizadas centralizadas en la revision focalizada | Monitorear, sin conector |
| 3 | Kraken | `xStocks` respaldados 1:1; su divulgacion oficial declara que no estan disponibles en Estados Unidos | Referencia secundaria bloqueada para dashboard publico global |
| 4 | Bitstamp by Robinhood | Robinhood publica stock tokens para clientes europeos; no se atribuye ese producto a una API de Bitstamp sin evidencia | Referencia solamente |
| 5 | OKX | Wallet/DEX ofrece rutas xStocks y Ondo; su ayuda indica que no estan disponibles en OKX CEX | Contexto DEX, no ingestion CEX |
| 6 | Gate | Publica `xStocks` y `Ondo Stocks` | Referencia secundaria; no se confirmo permiso de output publico |
| 7 | Bitget | Publica activos tokenizados Ondo de acciones y ETF de EE. UU.; sus terminos API son limitados y revocables | Referencia secundaria; no se confirmo permiso de output publico |
| 8 | Bitvavo | No se confirmo ruta oficial de acciones tokenizadas en la revision focalizada | Sin conector ahora |
| 9 | Bybit | `xStocks` Spot y API V5 con `symbolType=xstocks` y `xstockMultiplier`; sus terminos excluyen Estados Unidos y otras jurisdicciones | Referencia secundaria bloqueada para dashboard publico |
| 10 | BingX | Publica material sobre activos RWA, sin feed de acciones confirmado | Referencia solamente |
| 11 | MEXC | No se confirmo producto programatico oficial de acciones tokenizadas | Sin conector ahora |
| 12 | Crypto.com Exchange | App ofrece acciones y ETF a usuarios elegibles de EE. UU. | Referencia de brokerage; no feed publico confirmado |
| 13 | Gemini | Tokenized stocks de Dinari para la UE; su ayuda dice que no estan disponibles via API | No integrar como conector |
| 14 | HashKey Exchange | No se confirmo ruta publica oficial de acciones tokenizadas | Sin conector ahora |
| 15 | Upbit | No se confirmo ruta publica oficial de acciones tokenizadas | Sin conector ahora |
| 16 | KuCoin | No se confirmo ruta publica oficial de acciones tokenizadas | Sin conector ahora |
| 17 | Bitso | No se confirmo ruta publica oficial de acciones tokenizadas | Sin conector ahora |
| 18 | CoinW | No se confirmo ruta publica oficial de acciones tokenizadas | Sin conector ahora |
| 19 | LBank | Anuncio zona `xStocks` con 55 equities tokenizadas impulsadas por Backed | Venue de referencia; confirmar API antes de integrar |
| 20 | Bullish | No se confirmo ruta publica oficial de acciones tokenizadas | Sin conector ahora |

## Pepperstone

Pepperstone no es una fuente equivalente a xStocks u Ondo. Sus paginas
oficiales presentan exposicion mediante derivados y servicios vinculados a
cuenta:

| Producto | Evidencia Oficial | Decision |
|---|---|---|
| Share CFDs | Mas de 1,100 CFD de acciones en 23 paises; el instrumento no entrega propiedad de la accion | No usar como activo tokenizado ni como precio objetivo |
| TradingView | Integracion con una cuenta Pepperstone gratuita y miles de simbolos | Posible referencia visual privada, no fuente de redistribucion |
| Trading API | REST API para pricing, liquidez y datos de cuenta | Integracion opcional del usuario; no se confirmo feed abierto publicable |

## Prioridad Tecnica

1. Mantener operativo el `RWA Watch Sandbox` con fixtures propios y sin
   llamadas a proveedores externos.
2. Solicitar autorizacion escrita de display, retencion y output derivado
   antes de construir un adaptador real `xStocks / Backed`.
3. Confirmar contrato/onboarding y derechos de salida de `Ondo Global Markets`;
   sus endpoints de precios estan documentados para display, pero requieren
   API key.
4. Mantener Bybit y Kraken bloqueados para la edicion publica global, y pedir
   confirmacion contractual antes de usar Gate o Bitget como venues
   secundarios; LBank esta pendiente de confirmar API.
5. Mantener CFDs y productos de brokerage fuera de cualquier comparacion que
   sugiera propiedad de acciones o historial de analistas.

## Fuentes Oficiales

- CoinGecko exchanges: <https://www.coingecko.com/en/exchanges>
- xStocks API: <https://docs.xstocks.fi/apis/openapi>
- xStocks overview: <https://docs.xstocks.fi/about-xstocks/welcome-to-xstocks/overview>
- xStocks Terms of Service: <https://xstocks.fi/documents/xstocks-terms-of-service.pdf>
- Ondo Global Markets overview: <https://docs.ondo.finance/ondo-global-markets/overview>
- Ondo API reference: <https://docs.ondo.finance/api-reference/overview>
- Ondo API quickstart: <https://docs.ondo.finance/api-reference/quickstart>
- Ondo terms of service: <https://docs.ondo.finance/legal/terms-of-service>
- Ondo important notes: <https://docs.ondo.finance/ondo-global-markets/important-notes>
- Bybit xStocks: <https://www.bybit.com/en/help-center/article/FAQ-xStocks-on-Bybit>
- Bybit V5 instruments: <https://bybit-exchange.github.io/docs/v5/market/instrument>
- Bybit xStocks terms: <https://www.bybit.com/en/help-center/article/Terms-and-Conditions-xStocks>
- Kraken xStocks: <https://www.kraken.com/xstocks>
- Kraken xStocks risk disclosure: <https://www.kraken.com/legal/xstocks>
- Gate xStocks: <https://www.gate.com/xstocks>
- Gate tokenized stocks: <https://www.gate.com/es/tokenized-stocks>
- Gate user agreement: <https://www.gate.com/docs/agreement.pdf>
- Bitget Ondo announcement: <https://www.bitget.com/support/articles/12560603838361>
- Bitget Ondo expansion: <https://www.bitget.com/blog/articles/bitget-tokenized-stocks-etfs-ondo-expansion>
- Bitget API key terms: <https://www.bitget.com/support/articles/12560603797947>
- LBank xStocks announcement: <https://www.lbank.com/support/articles/21431592927001>
- Gemini tokenized stocks: <https://support.gemini.com/hc/en-us/articles/45788732343963-Tokenized-Stocks-Overview>
- OKX xStocks help: <https://web3.okx.com/en-eu/help/what-are-xstocks>
- Coinbase stocks overview: <https://help.coinbase.com/coinbase/trading-and-funding/stocks/overview>
- Crypto.com stocks and ETF: <https://help.crypto.com/en/articles/10441410-stocks-and-etfs>
- Pepperstone shares: <https://pepperstone.com/en/markets/shares/>
- Pepperstone Trading API: <https://pepperstone.com/en/platforms/integrations/trading-api/>
