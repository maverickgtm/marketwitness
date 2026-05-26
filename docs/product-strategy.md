# Estrategia De Producto

## Nombre Publico

**TargetAudit**

Tagline: **Auditable market intelligence: analyst targets and upcoming public
listings.**

El paquete tecnico conserva el nombre `targetaudit` para poder extenderse en
el futuro a otros verticales sin romper integraciones.

La edición principal debe funcionar sin comprar datasets. Tiene modulos
complementarios:

- `Financials Scorecard`: sandbox auditable sobre financials con datos
  redistribuibles; admite datos autorizados como extensión.
- `IPO Watch`: monitoreo basado en fuentes públicas regulatorias de nuevas cotizaciones
  tecnologicas/estrategicas.
- `Global Listings Watch`: mapa y futuros conectores de listings fuera de
  Estados Unidos, comenzando por Londres y Hong Kong.
- `Evidence Passport Commons`: protocolo publico y API de fichas de fuente y
  derechos, extensible por contributors antes de activar nuevos conectores.
- `RWA Watch Sandbox`: pagina funcional con evidencia sintetica sobre acciones
  y ETF tokenizados; los conectores reales de `xStocks / Backed`, `Ondo` y
  venues quedan condicionados a derechos escritos de uso publico.
- `Market Intelligence`: workspace de eventos, contexto y posicionamiento que
  ordena la integracion futura de cripto seleccionada, energia, tasas,
  catalizadores macro, insiders y CFTC sin emitir senales de operacion.
- `Volatility Intelligence Lab`: investigacion de episodios `VIX`, tecnologia
  (`VXN`), tasas (`MOVE`) y commodities, enlazada a filings/listings
  verificados en lugar de duplicar un dashboard de volatilidad.
- `Policy Signal Impact Lab`: caso inicial Donald Trump / Truth Social para
  estudiar comunicaciones y reacciones de mercado con un bloqueo explicito
  de ingesta automatica hasta obtener derechos.

## Problema

Los inversores pueden encontrar targets actuales y rankings generales en
productos establecidos, pero resulta dificil comprobar:

- si un target historico realmente llego a cumplirse;
- si la firma mejoro a un benchmark del mismo sector;
- si un especialista sectorial supero a una firma generalista;
- si la conclusion depende de pocas observaciones o de datos no auditables.

## Diferenciacion

Competidores observados al `2026-05-24`:

| Producto | Enfoque Visible | Oportunidad Para TargetAudit |
|---|---|---|
| TipRanks | Ratings, targets y metodologia de exito a un ano | Benchmark metodologico directo; ser reproducible sin incorporar datos sin derechos |
| MarketBeat | Mas de un millon de recomendaciones y rankings por suscripcion; export reciente anunciado hasta seis meses | Piloto privado de cobertura, no fuente suficiente para score a un ano ni publicacion sin licencia |
| WallStreetZen | Ranking propio sobre mas de 4,000 analistas | Benchmark metodologico privado, no feed historico confirmado |
| Yahoo Finance / Investing.com | Consulta visual de ratings y targets | Referencia manual solamente; sus terminos no sustentan ingestion o redistribucion |
| Finnhub / FMP | Endpoints programaticos de tendencia o consenso de target | Conectores futuros solo bajo licencia explicita de display/redistribucion |
| TradingView | Widgets gratuitos con atribucion conservada | `Market Pulse` y `Market Context` implementados para benchmarks y `XLF`, separados del motor de targets |
| FRED `VIXCLS` | Grafica externa atribuida con cita requerida | VIX visible en `Volatility Lab` y `Policy Signal Impact Lab`, separado de calculos |
| Truth Social | Comunicaciones publicas relevantes para event studies | Caso Donald Trump documentado; coleccion automatica bloqueada por terminos hasta permiso escrito |
| xStocks / Ondo / venues CEX | Emisores de activos tokenizados y mercados como Bybit, Kraken, Gate y Bitget | `RWA Watch Sandbox` ya demuestra el modelo; xStocks queda bloqueado por terminos y ningun venue suministra analyst targets |
| Quiver Quantitative | Desempeno historico de analistas usando datos Benzinga | Examinar firmas especialistas contra generalistas dentro de financials |
| AnaChart | Charts y hit ratios de price targets publicos | Comparar precision con benchmark sectorial y versionar reglas |

La propuesta no es declarar que una plataforma existente esta equivocada. Es
ofrecer una investigacion publica, replicable y verticalizada:

La diferencia transversal nueva es `Evidence Passport Commons`: en vez de
competir primero por mas senales, el proyecto publica fichas de procedencia y
derechos, e invita a la comunidad global a enriquecer cadencia y limites de
afirmacion. La version `0.1` no declara completo ese enriquecimiento; expone
el registro de fuente y derechos ya controlado.

> Cuando una firma opina sobre bancos y financials de EE. UU., ?su target fue
> preciso y aporto valor frente al sector?

`IPO Watch` agrega una pregunta distinta y separada:

> ?Que companias de alto interes realmente avanzaron hacia una cotizacion y
> que documentos/riesgos debe revisar un investigador antes de evaluarlas?

`Market Intelligence` agrega contexto alrededor de esos eventos:

> ?Que regimen de tasas, energia, activos digitales y posicionamiento
> declarado rodeaba un evento verificado, con que fuente y frecuencia?

`Volatility Intelligence Lab` refina esa pregunta frente a competidores que
ya visualizan `VIX` y term structure:

> ?Como se propagaron episodios de estres hacia activos e IPOs verificadas,
> y que evidencia permite sostener esa lectura?

`Policy Signal Impact Lab` plantea una hipotesis especialmente visible:

> ?Que cambio en volatilidad y activos vinculados despues de una comunicacion
> publica verificable, con que ventana y con que evidencia?

Una expansión posterior de activos tokenizados preguntaria:

> ?Que instrumentos ligados a acciones o ETF aparecen en mercados on-chain,
> bajo que estructura, y cuanto se desvia su precio de la referencia?

La revision de fuentes y venues para esa expansion se documenta en
[RWA Watch: Exchanges Y Fuentes Base](rwa-watch-sources.md).

## Mercado Inicial

### Universo v1

- Companias estadounidenses del sector financiero con targets verificables.
- Primera cohorte deseada: financials pertenecientes historicamente al
  `S&P 500` en cada fecha de observacion.
- Analisis separado posterior para bancos regionales, una vez que exista
  universo punto-en-el-tiempo fiable.

### Benchmarks

- Benchmark sectorial inicial: `XLF`, ETF que sigue el Financial Select Sector
  Index.
- Benchmark amplio secundario futuro: `SPY`.
- Benchmarks de subindustria se activaran solo cuando el universo y la fuente
  de precios puedan auditarse consistentemente.

### Usuario Inicial

- Inversores individuales que quieren comprobar titulares de analyst ratings.
- Periodistas y creadores financieros que necesitan citar una metodologia.
- Analistas cuantitativos interesados en reproducir o discutir el score.

## Producto MVP Publicable

Un release publico serio debe incluir:

1. Motor reproducible y tests, ya iniciado en `v0.1`.
2. Un dataset demostrativo sintetico claramente etiquetado.
3. Un importador para targets autorizados y precios con licencia compatible.
4. Un informe real piloto de financials solo cuando cada fila tenga fuente y
   permisos adecuados.
5. Reportes que siempre expongan `N`, intervalo Wilson 95%, universo
   historico, revisiones de targets, costos y regla de salida, segmentos de
   sector/direccion, exclusiones, benchmark y metodologia.

## Hipotesis Medibles

- `H1`: firmas especializadas en financials obtienen menor error terminal que
  firmas generalistas en el mismo universo y periodo.
- `H2`: un alto `target hit rate` no necesariamente implica retorno excedente
  positivo frente a `XLF`.
- `H3`: el desempeno difiere entre targets alcistas y bajistas.

Estas hipotesis son preguntas de investigacion, no conclusiones del producto.

## Riesgos De Negocio

- Los targets historicos detallados pueden exigir una licencia de datos paga;
  por ello son una extensión opcional y no requisito de la edición GitHub.
- Un reporte publico con muestra pequena puede inducir a error aun si el
  calculo es correcto.
- Las clasificaciones sectoriales y componentes historicos requieren datos
  punto-en-el-tiempo para evitar sesgo retrospectivo.
- No se debe presentar ningun score como recomendacion de inversion.

## Referencias De Mercado

- TipRanks screener: <https://www.tipranks.com/screener/stock-ratings>
- MarketBeat analyst rankings: <https://www.marketbeat.com/all-access/analyst-rankings/>
- Quiver analyst ratings: <https://www.quiverquant.com/analysts/>
- AnaChart: <https://anachart.com/>
- State Street XLF: <https://www.ssga.com/us/en/intermediary/etfs/state-street-financial-select-sector-spdr-etf-xlf>
- S&P sectors: <https://www.spglobal.com/spdji/en/index-family/equity/us-equity/sp-sectors/>
## Policy Signal Impact Lab

La propuesta mas distintiva agregada al producto es vincular comunicaciones
publicas verificables con ventanas de reaccion de mercado sin fingir
causalidad. El primer caso es `Donald Trump / Truth Social` desde
`2025-01-20`, bajo el nombre metodologico `Policy Signal Impact Trace`.

Existe prior art: JPMorgan creo el `Volfefe Index` en 2019 para tweets y
volatilidad de tasas, y `Trump & Dump` anuncia monitoreo de Truth Social. La
ventaja que TargetAudit puede construir es otra: cada episodio exige fuente,
permiso, timestamp, clasificacion, ventana, activos, exclusiones y enlace con
IPOs/listings verificadas.

Truth Social no se incorpora como scraper: sus terminos oficiales revisados
restringen medios automatizados, recuperacion sistematica y data mining sin
permiso. La pagina y API se publican ahora como metodologia y control de
derechos; un feed live solo procede con autorizacion o fuente licenciada.
