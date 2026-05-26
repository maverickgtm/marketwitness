# Volatility Intelligence Lab

Fecha de diseno y revision inicial: `2026-05-25`.

## Proposito

`Volatility Intelligence Lab` no intenta competir como una pantalla generica
de VIX. Su pregunta es distinta:

> Cuando aparece estres verificable en acciones, tecnologia, tasas o
> commodities, que ocurrio despues con activos monitorizados y eventos de
> listing confirmados?

La ruta `/dashboard/volatility` ya publica el diseno de investigacion y una
visualizacion externa atribuida de `VIX`. La API
`/api/v1/intelligence/volatility` publica las familias de indicadores y los
experimentos planificados. Todavia no descarga ni calcula resultados reales
de series Cboe o ICE.

## Familias De Volatilidad

| Fase | Indicadores | Funcion En El Laboratorio |
|---|---|---|
| 1 | `VIX`, `VIX1D`, `VIX9D`, `VIX3M` | Detectar estres de acciones y distinguir evento inmediato de riesgo persistente |
| 1 | `VXN` | Vincular volatilidad tecnologica con `QQQ` e IPOs tecnologicas/IA |
| 1 | `MOVE` | Investigar estres de tasas, curva Treasury, liquidez y condiciones de financiacion para IPOs |
| 2 | `VVIX`, `SKEW` | Estudiar volatilidad de la volatilidad y demanda de proteccion extrema |
| 2 | `OVX`, `GVZ` | Contrastar estres de petroleo y oro con energia/refugio |
| 3 | `VIX6M`, `VIX1Y` | Analizar persistencia estructural una vez validada la curva corta |

## Diseno De Episodios

El motor futuro debe conservar el umbral exacto, fecha de evento, series de
entrada, derechos de output, numero de episodios y ventanas comparadas. Los
primeros estudios son:

| Episodio | Pregunta | Ventanas |
|---|---|---|
| `vix_shock` | Como reaccionaron activos seleccionados despues de una subida fuerte de `VIX`? | mismo dia, 1, 5, 20 y 60 sesiones |
| `technology_stress_gap` | Que ocurrio con tecnologia/listings cuando `VXN` se separo de `VIX`? | 5, 20 y 60 sesiones |
| `rates_before_equities` | El estres `MOVE` precedio un regimen `VIX` y cambios en el pipeline IPO? | 5, 20 y 60 sesiones |
| `commodity_propagation` | Hubo propagacion hacia energia o refugio cuando `OVX`/`GVZ` subieron junto con equity volatility? | 1, 5 y 20 sesiones |

Cada salida debe informar mediana, frecuencia direccional, dispersion,
drawdown y muestra disponible. Nunca debe convertir una regularidad historica
en una instruccion de compra o venta.

## Diferencia Frente A Otros Dashboards

Herramientas revisadas como `TheVIXtrader` y `Volatilitaets-Zentrale` ya
presentan regimenes VIX, term structure y varias medidas cross-asset.
TargetAudit no gana copiando ese catálogo. La capa diferenciadora es:

- asociar episodios a filings y listings verificados de `IPO Watch`;
- estudiar tecnologia mediante `VXN` alrededor de candidatas de IPO;
- cruzar estres de tasas `MOVE` con clima de financiacion y Treasury;
- vincular evidencia ETF/ownership a las mismas ventanas cuando exista;
- publicar `Evidence Passports` y limites de cada conclusion.

## Fuentes Y Limites

| Fuente | Evidencia Disponible | Estado En TargetAudit |
|---|---|---|
| Cboe Historical Data for VIX and Other Volatility Indices | Pagina oficial que enlaza historia diaria para `VIX`, `VVIX`, `VIX9D`, `OVX` y `GVZ`, entre otros | Registrada para estudio; output derivado y almacenamiento público pendientes de revision de derechos |
| Cboe Index Dashboards / Data Feed | Familia temporal y oferta de datos de indices | Referencia oficial para alcance; no feed integrado |
| ICE BofA MOVE Index | Producto oficial de volatilidad del mercado de bonos con oferta intraday/diaria/historica | Fuente planificada; no activada sin autorizacion de display/output |
| TradingView widget | Display atribuido de `CBOE:VIX` | Visualizacion externa; no se almacena ni alimenta calculos |

Fuentes oficiales:

- Cboe Historical Data: <https://www.cboe.com/tradable_products/vix/vix_historical_data>
- Cboe Index Data Access: <https://www.cboe.com/us/indices/accessing-index-data/>
- ICE MOVE Index: <https://developer.ice.com/fixed-income-data-services/catalog/ice-data-indices-move-index>
- TradingView VIX chart: <https://www.tradingview.com/symbols/CBOE-VIX/>

Competidores utilizados para posicionamiento:

- TheVIXtrader: <https://thevixtrader.com/>
- Volatilitaets-Zentrale: <https://vix-zentrale.de/>
