# Direccion Visual Del Dashboard

Revision: `2026-05-25`

## Objetivo

TargetAudit debe sentirse como un terminal de investigacion util, no como una
coleccion de reportes sueltos. La experiencia visual tiene dos obligaciones:

1. hacer visibles en segundos los modulos, estados y controles mas relevantes;
2. mantener separada la evidencia auditable de cualquier contexto visual
   cargado desde terceros.

## Referencias Aplicadas

La primera renovacion implementa principios comunes de dashboards financieros:

| Principio | Decision en TargetAudit |
|---|---|
| KPI y proposito visibles al entrar | La portada abre con promesa, metricas de Open Edition y cuatro modulos principales. |
| Jerarquia estable de navegacion | La portada incorpora una barra lateral para workspace, evidencia y controles. |
| Contexto de mercado sin saturar reportes | `Market Pulse` y la franja de tickers solo aparecen como contexto visual atribuido. |
| Grafico profundo en una vista dedicada | `/dashboard/market-context` conserva el grafico avanzado `XLF` y suma una lente comparativa lateral. |
| Claridad sobre origen de datos | Cada panel de TradingView se rotula como display externo que no alimenta scoring. |
| Degradacion sin Internet | Los espacios externos muestran un estado de carga informativo mientras el widget no esta disponible. |

## Widgets TradingView

Solo se utilizan widgets oficiales incrustados con atribucion visible:

| Superficie | Widget | Uso |
|---|---|---|
| `/dashboard/open` | `Ticker Tape` | Contexto compacto de benchmarks, Financials y grandes acciones seguidas. |
| `/dashboard/open` | `Market Overview` | Vista macro inicial en pestanas `Benchmarks` y `AI Leaders`. |
| `/dashboard/market-context` | `Ticker Tape` | Orientacion rapida antes de abrir el grafico sectorial. |
| `/dashboard/market-context` | `Advanced Chart` | Inspeccion interactiva de `AMEX:XLF`. |
| `/dashboard/market-context` | `Market Overview` | Comparacion visual de Financials y benchmarks. |

Estos widgets cargan desde TradingView. TargetAudit no lee sus valores, no los
almacena en DuckDB, no los exporta y no los considera evidencia para evaluar
targets, IPOs o cambios de holdings.

## Siguiente Fase Visual

La misma direccion debe extenderse progresivamente sin rehacer el alcance de
datos:

1. llevar el shell de navegacion y las tarjetas premium a `IPO Watch`,
   `Global Listings` y `ETF Evidence`;
2. crear graficos propios exclusivamente para datos que TargetAudit ya puede
   publicar, como conteos de documentos por mercado o estados de aprobacion;
3. producir capturas de lanzamiento y revisar responsive design antes de
   publicar el repositorio.

## Fuentes Oficiales De Diseno E Integracion

- TradingView, widgets de ticker:
  <https://www.tradingview.com/widget-docs/widgets/tickers/>
- TradingView, widget Market Overview:
  <https://www.tradingview.com/widget-docs/widgets/watchlists/market-overview/>
- TradingView, widget Symbol Overview:
  <https://www.tradingview.com/widget-docs/widgets/charts/symbol-overview/>
- TradingView, tutorial de integracion:
  <https://www.tradingview.com/widget-docs/tutorials/build-page/widget-integration/>
