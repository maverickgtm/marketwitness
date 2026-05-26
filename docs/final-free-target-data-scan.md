# Ultimo Barrido Gratuito De Targets Historicos

Revision: `2026-05-25`.

## Objetivo

Antes del lanzamiento publico se hizo una ultima busqueda internacional para
encontrar una fuente gratuita de `price targets` historicos, individualizados
por firma o analista y con derechos suficientes para publicar resultados
derivados en TargetAudit.

Se buscaron proveedores de Estados Unidos y rutas locales en Japon, Corea,
Hong Kong, Singapur, Brasil, India, Reino Unido y Alemania. Los repositorios
de GitHub se trataron solo como pistas tecnicas: una libreria que consulta una
pagina de terceros no concede derechos sobre sus datos.

## Resultado Ejecutivo

No se encontro un dataset gratuito que podamos activar legalmente para
publicar rankings reales de Roth MKM, KBW, UBS, Citi, Barclays u otras firmas.

El hallazgo mas cercano a la idea original es `AnalystCentral`: anuncia un CSV
gratuito con diez anos de ratings y price targets de acciones de Wall Street.
Sin embargo, sus propios terminos limitan el contenido a uso personal y
prohiben data mining, scraping, republicacion y trabajos derivados sin
consentimiento escrito. Por tanto, puede convertirse en una solicitud de
permiso, pero no en una integracion de Open Edition.

## Candidatos Revisados

| Fuente | Cobertura Relevante | Costo Visible | Decision Para TargetAudit |
|---|---|---:|---|
| AnalystCentral | CSV de ratings y targets de Wall Street, 10 anos, mas de 8,500 acciones e indices anunciados | Gratuito para miembros | `permission_candidate`: contactar para permiso escrito; no descargar ni publicar resultados con los terminos actuales |
| Intrinio / Zacks Target Prices | Consenso de targets USA, mas de 20 anos, API/CSV/S3/Snowflake | Cotizacion; historia requiere pago unico | Extension licenciada, no Open Edition y no fila individual por firma confirmada |
| QUICK Data Factory | Ratings y targets de companias japonesas, campos actual/anterior e historia desde enero de 2003 | Contrato mensual | Gran candidato japones para usuario licenciado; no gratuito |
| FnGuide / FnSpace | Research y consenso coreano; series extensas y API de consenso | FnConsensus `KRW 165,000/mes`; API desde `KRW 70,000/mes` academia | No gratuito; licencia publicada limita datos a uso personal/interno y no exposicion a terceros |
| Webull OpenAPI | Target alto, bajo, medio y mediano para acciones USA | Requiere `x-app-key`; precio/derechos no confirmados | Solo consenso actual documentado; no demuestra historia individual ni derechos de output publico |
| StocksSG / SGinvestors | Consenso o cambios recientes de targets en acciones SGX | Pagina visible | Referencia manual; no se encontro API ni licencia de republicacion para un ranking |
| FMP | Consensus y ratings historicos estructurados | Free para pruebas; display/redistribucion bajo acuerdo | Ya clasificado como extension contractual, no fuente publica gratuita |
| GitHub wrappers de TipRanks/Yahoo | Acceso tecnico a endpoints o paginas existentes | Codigo gratuito | Excluidos: el codigo no transfiere derechos sobre los datos subyacentes |

## Hallazgo Util: Solicitar Permiso Sin Exigir Pago

La unica via gratuita todavia plausible para el ranking inicial es solicitar a
`AnalystCentral` una autorizacion escrita y acotada. Una autorizacion usable
deberia permitir, al menos:

1. Descargar o recibir una muestra historica con fecha, ticker, firma,
   analista cuando exista, target y recomendacion.
2. Conservar el dataset localmente para evaluación reproducible.
3. Publicar exclusivamente salidas derivadas agregadas, con atribucion,
   metodologia y enlaces de origen.
4. Publicar un pequeno dataset de ejemplo o fixtures derivados si lo autorizan.
5. Ejecutar el reporte en GitHub Actions o establecer claramente que el dato
   real solo se procesa en instalaciones privadas autorizadas.

Mientras esa autorizacion no exista, TargetAudit mantiene el importador y el
release gate preparados, pero no activa la fuente.

## Consecuencia Para El Lanzamiento

La conclusion no reduce el valor de Open Edition:

- el motor de evaluacion y la auditoria son ejecutables y probados;
- el dashboard muestra exactamente que falta para habilitar datos reales;
- IPO Watch y los monitores regulatorios globales aportan evidencia publica
  sin comprar datos;
- el nuevo portal `/dashboard/contribute?lang=en` abre colaboracion
  internacional en cinco idiomas para descubrir conectores o permisos
  verificables.

La promesa publica correcta sigue siendo: **TargetAudit comprueba evidencia y
expone cuando una conclusion todavia no se puede publicar.**

## Fuentes Revisadas

- AnalystCentral, oferta de datos: <https://analystcentral.com/about-us/>
- AnalystCentral, terminos: <https://analystcentral.com/terms-of-service>
- Intrinio, Target Prices: <https://intrinio.com/products/target-prices>
- QUICK Data Factory, ratings y targets japoneses:
  <https://corporate.quick.co.jp/data-factory/product/data054/>
- QUICK APIs, uso sujeto a contrato:
  <https://corporate.quick.co.jp/en/apis/>
- FnGuide, planes de research y consenso: <https://www.fnguide.com/Payment/Purchase>
- FnSpace, licencia y precios API:
  <https://help-fnspace.fnguide.com/ko/articles/FnSpace-%EC%84%9C%EB%B9%84%EC%8A%A4-%EC%9D%B4%EC%9A%A9-%EC%9A%94%EA%B8%88-%EB%B0%8F-%EB%9D%BC%EC%9D%B4%EC%84%A0%EC%8A%A4-%EC%A0%95%EC%B1%85-%EC%95%88%EB%82%B4-1a2bb37e>
- Webull, Analyst Target Price API:
  <https://developer.webull.com/apis/docs/reference/get-analyst-target-price>
- Financial Modeling Prep, Analyst Estimates and Targets:
  <https://site.financialmodelingprep.com/datasets/analyst-estimates-targets>
- SGinvestors, target prices visibles:
  <https://sginvestors.io/analysts/target-price/latest>
