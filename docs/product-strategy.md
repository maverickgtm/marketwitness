# Estrategia De Producto

## Nombre Publico

**TargetAudit**

Tagline: **Auditable market intelligence: analyst targets and upcoming public
listings.**

El paquete tecnico conserva el nombre `targetaudit` para poder extenderse en
el futuro a otros verticales sin romper integraciones.

El producto tiene dos modulos complementarios:

- `Financials Scorecard`: auditoria sectorial de targets sobre financials.
- `IPO Watch`: monitoreo basado en fuentes de nuevas cotizaciones
  tecnologicas/estrategicas.
- `Global Listings Watch`: mapa y futuros conectores de listings fuera de
  Estados Unidos, comenzando por Londres y Hong Kong.

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
| TipRanks | Ratings, targets y rankings amplios para inversores | Ser reproducible y mostrar datos/exclusiones detras del score |
| MarketBeat | Rankings de analistas disponibles por suscripcion | Concentrarse en metodologia abierta y auditoria sectorial |
| Quiver Quantitative | Desempeno historico de analistas usando datos Benzinga | Examinar firmas especialistas contra generalistas dentro de financials |
| AnaChart | Charts y hit ratios de price targets publicos | Comparar precision con benchmark sectorial y versionar reglas |

La propuesta no es declarar que una plataforma existente esta equivocada. Es
ofrecer una investigacion publica, replicable y verticalizada:

> Cuando una firma opina sobre bancos y financials de EE. UU., ?su target fue
> preciso y aporto valor frente al sector?

`IPO Watch` agrega una pregunta distinta y separada:

> ?Que companias de alto interes realmente avanzaron hacia una cotizacion y
> que documentos/riesgos debe revisar un investigador antes de evaluarlas?

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
5. Reportes que siempre expongan `N`, exclusiones, benchmark y metodologia.

## Hipotesis Medibles

- `H1`: firmas especializadas en financials obtienen menor error terminal que
  firmas generalistas en el mismo universo y periodo.
- `H2`: un alto `target hit rate` no necesariamente implica retorno excedente
  positivo frente a `XLF`.
- `H3`: el desempeno difiere entre targets alcistas y bajistas.

Estas hipotesis son preguntas de investigacion, no conclusiones del producto.

## Riesgos De Negocio

- Los targets historicos detallados pueden exigir una licencia de datos paga.
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
