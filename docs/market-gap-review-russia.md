# Market Gap Review: Rusia

Revision: `2026-05-25`.

## Decision Ejecutiva

Rusia es un mercado relevante para el mapa global, pero no debe activarse como
collector de `Open Edition` en este momento. TargetAudit lo registra como
`restricted_research_only`: fuente oficial identificada y riesgo explicado,
sin ingesta automatica, alertas de IPO ni sugerencias de posiciones.

## Fuentes Oficiales Identificadas

| Fuente | Valor Potencial | Restriccion Para TargetAudit |
|---|---|---|
| Bank of Russia `Register of Russian Securities` | El Banco de Rusia anuncio el `2025-09-03` un registro con acciones y bonos, `ISIN`, numero estatal de registro, moneda e informacion del emisor | Sirve para documentar la existencia de datos regulatorios; no se implementa acceso automatizado sin revision legal |
| Moscow Exchange `ISS` API | MOEX declara acceso a descripciones de securities, operaciones, cotizaciones y resultados historicos; datos demorados gratuitos y tiempo real por suscripcion | La contraparte MOEX esta designada por OFAC; no se activa collector ni redistribucion |

## Control De Sanciones

El Departamento del Tesoro de Estados Unidos informo el `2024-06-12` que
`Moscow Exchange (MOEX)`, `National Clearing Center (NCC)` y `National
Settlement Depository (NSD)` fueron designadas conforme a `E.O. 14024` por
operar en el sector de servicios financieros de la economia rusa.

La pagina vigente de OFAC para sanciones relacionadas con Rusia continua
publicando licencias y acciones recientes, incluidas acciones en abril y mayo
de `2026`. Por tanto, encontrar una API gratuita no equivale a que su
integracion, publicacion o uso para orientar inversiones sea apropiado.

## Politica Del Producto

- Mostrar Rusia en el mapa de cobertura como `restricted_research_only`.
- No consumir automaticamente `MOEX ISS` ni generar snapshots publicos.
- No ofrecer recomendaciones de compra, venta o posicionamiento sobre
  securities rusos.
- No promover esta fuente a feed operativo sin revision legal documentada de
  sanciones, licencia de datos, redistribucion y usuarios objetivo.

## Fuentes Oficiales Revisadas

- Bank of Russia, registro de valores rusos: <https://www.cbr.ru/eng/press/event/?id=26912>
- Moscow Exchange, `ISS` API: <https://www.moex.com/a2920>
- U.S. Treasury, designacion de infraestructura financiera rusa, `2024-06-12`: <https://home.treasury.gov/news/press-releases/jy2404>
- OFAC, programa de sanciones relacionadas con Rusia: <https://ofac.treasury.gov/sanctions-programs-and-country-information/russian-harmful-foreign-activities-sanctions>
