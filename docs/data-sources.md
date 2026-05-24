# Fuentes De Datos Evaluadas

Fecha de revision inicial: `2026-05-24`.

El dato mas dificil del proyecto es el historial de `price targets`
individuales con fecha, firma y target. Los precios historicos y datos
regulatorios tienen alternativas publicas o freemium mas amplias.

La investigacion publica inicial se concentrara en `U.S. Financials`, usando
`XLF` como benchmark sectorial inicial cuando la licencia de precios lo
permita. Esto responde a la hipotesis de que firmas especializadas en el sector
pueden comportarse distinto a firmas generalistas.

## Targets Y Ratings

| Fuente | Cobertura Declarada | Utilidad | Estado Para TargetAudit |
|---|---|---|---|
| Benzinga Analyst Ratings API | Acciones USA, historial desde 2013; firma, analista, rating y targets anterior/actual | Candidato principal para un pipeline real | Requiere revisar plan/licencia antes de almacenar o mostrar datos |
| Polygon / Benzinga endpoints | Ratings e insights historicos estructurados | Integracion moderna en una API de mercado | Expansion comercial; no asumida como gratuita |
| LSEG I/B/E/S | Historial institucional de estimaciones y recomendaciones | Fuente de investigacion de alta calidad | Candidata futura, probablemente costosa |
| Financial Modeling Prep | APIs de price-target summary/consensus e historical grades | Puede complementar o validar cobertura | Confirmar si entrega targets individuales historicos y limites del plan |
| MarketBeat | Historial, screener y ranking propios | Referencia metodologica y verificacion manual | Herramientas/exportaciones sujetas a suscripcion y terminos |
| TipRanks | Rankings y targets visibles en su producto | Referencia conceptual | No usar scraping; sus terminos restringen extraccion/copia |
| Finviz | Eventos visibles en paginas de acciones | Verificacion manual puntual | No adoptado como colector hasta revisar permisos de automatizacion |

### Conclusion Inicial

No se identifico una fuente abierta y claramente redistribuible que entregue,
de forma completa, price targets historicos individuales de firmas de EE. UU.
Por eso `v0.1` acepta CSV documentado y no incluye un scraper.

## Precios Ajustados Y Mercado

| Fuente | Uso Potencial | Consideracion |
|---|---|---|
| Alpha Vantage | Precios, splits, dividendos y listado historico/delisted | Tiene clave gratuita, pero endpoints ajustados y limites deben verificarse por plan al integrar |
| Nasdaq Data Link | Datasets publicos y premium | Explorar datasets concretos y sus licencias antes de elegir |
| Stooq / fuentes que lo reutilizan | Precio fin de dia para experimentacion | Validar terminos y calidad antes de publicacion |
| Proveedor comercial futuro | Precios punto-en-el-tiempo y acciones corporativas | Necesario si se ofrece servicio robusto de produccion |

TargetAudit requiere precios ajustados con `high`, `low` y `close`, porque un
target puede ser alcanzado intradia aun cuando el cierre no lo refleje.

## Fuentes Publicas Complementarias

| Fuente | Uso |
|---|---|
| SEC `data.sec.gov` | Identificacion de emisores, filings y enriquecimiento regulatorio; no contiene targets de analistas |
| SEC EDGAR archives | Trazabilidad de eventos y reportes publicos cuando correspondan |
| FRED | Series macroeconomicas y benchmarks agregados, sujeto a la serie seleccionada |

## IPO Watch: Verificacion Inicial

Revisado al `2026-05-24`:

| Empresa | Estado En TargetAudit | Evidencia |
|---|---|---|
| SpaceX | `filed_public` | Formulario `S-1` de Space Exploration Technologies Corp. presentado ante SEC el `2026-05-20` |
| Cerebras Systems | `listed` | Comunicado del emisor: comenzo a cotizar en Nasdaq como `CBRS` el `2026-05-14` y cerro su IPO el `2026-05-15` |
| Anthropic | `candidate_unverified` | No se incorpora como filing confirmado durante esta revision |
| OpenAI | `candidate_unverified` | No se incorpora como filing confirmado durante esta revision |
| Canva | `candidate_unverified` | No se incorpora como filing confirmado durante esta revision |
| Kraken | `candidate_unverified` | No se incorpora como filing confirmado durante esta revision |
| Shein | `candidate_unverified` | No se incorpora como filing confirmado durante esta revision |

El monitor futuro priorizara SEC EDGAR y anuncios oficiales. Las noticias
serviran para abrir una tarea de verificacion, no para cambiar por si solas el
estado mostrado.

Para descubrir emisores que no estaban en la lista inicial, el proyecto usa
los indices diarios EDGAR documentados por SEC. El resultado es una cola de
revision: un formulario de registro encontrado se considera posible evento,
no una IPO confirmada, hasta revisar el documento.

## Global Listings Watch: Fuentes Oficiales Identificadas

Revisado al `2026-05-24`:

| Mercado | Fuente Oficial | Senal Disponible | Estado TargetAudit |
|---|---|---|---|
| Reino Unido | London Stock Exchange `New issues` JSON | Upcoming issues con fecha esperada de trading y oferta prevista | Feed oficial implementado |
| Reino Unido | FCA National Storage Mechanism | Prospectos y documentos regulatorios aprobados/publicados | Consulta pública implementada para contraste LSE |
| Hong Kong | HKEX/HKEXnews New Listings - AP & PHIP | JSON oficiales de Active AP, Active PHIP, Inactive, Listed y Returned | Feed oficial implementado |
| Australia | ASX Upcoming floats and listings | Nuevos listings con solicitud formal recibida y fecha anticipada | Planificado |
| Canada | TSX New Company Listings | Nuevas companias ya listadas | Planificado |
| Singapur | SGX IPO Prospectus | Prospectos IPO publicados | Planificado |

Las etapas no son intercambiables entre jurisdicciones. Por ejemplo, un
`PHIP` de HKEX indica aprobacion en principio, mientras una aparicion en ASX
Upcoming Listings solo confirma que ASX recibio una solicitud formal y presenta
una fecha anticipada.

El conector HKEX consulta los endpoints JSON usados por la propia pagina
oficial, incluyendo:

- `https://www.hkexnews.hk/ncms/json/eds/appactive_app_sehk_e.json`
- `https://www.hkexnews.hk/ncms/json/eds/appactive_appphip_sehk_e.json`
- `https://www.hkexnews.hk/ncms/json/eds/appinactive_sehk_e.json`
- `https://www.hkexnews.hk/ncms/json/eds/applisted_sehk_e.json`
- `https://www.hkexnews.hk/ncms/json/eds/appreturned_sehk_e.json`

El conector LSE consulta el endpoint JSON que alimenta la pagina oficial:
`https://api.londonstockexchange.com/api/v1/pages?path=live-markets%2Fnew-issues`.
La muestra de pruebas fue observada el `2026-05-24`; la aparicion en
`Upcoming issues` es una senal esperada y todavia debe contrastarse con
documentos de admision o prospecto.

El contraste FCA NSM consulta el endpoint público utilizado por su formulario:
`https://api.data.fca.org.uk/search?index=fca-nsm-searchdata`. Busca el nombre
del emisor LSE en organizaciones divulgadoras o relacionadas y conserva solo
la última versión documental. La FCA indica que el NSM no es un servicio en
tiempo real; por eso `document_found_review_required` exige revisión humana y
`no_document_found` no descarta una cotización futura.

Para SEC se debe declarar el `User-Agent`, descargar solo lo necesario y
respetar la guia de acceso justo, que actualmente fija un maximo de 10
solicitudes por segundo.

## Repositorios Y Proyectos Encontrados

| Proyecto | Idea Aprovechable | Decision |
|---|---|---|
| `riazarbi/sp500-scraper` | Construccion de integrantes historicos para reducir sesgo de supervivencia | Evaluar licencia y calidad para un adaptador de universo |
| `janlukasschroeder/tipranks-api-v2` | Ejemplo de acceso a targets/consenso | No integrar: no muestra licencia y puede depender de endpoints/terminos ajenos |
| `datasets/s-and-p-500` | Serie historica agregada del indice | Puede servir para documentacion/benchmarks, no para integrantes historicos completos |

## Politica Del Proyecto

- El repositorio publica codigo, datos sinteticos y datos abiertos con licencia
  compatible.
- Los datasets comerciales se guardan fuera de Git y se cargan localmente.
- Todo conector documentara campos obtenidos, limites, terminos y fecha de
  revision.
- No se desarrollaran bypasses de paywalls, sesiones privadas ni scrapers
  contrarios a terminos del proveedor.

## Enlaces De Referencia

- Benzinga: <https://www.benzinga.com/apis/analyst-ratings-api/>
- Polygon/Benzinga: <https://polygon.io/docs/rest/partners/benzinga/analyst-ratings>
- LSEG I/B/E/S: <https://www.lseg.com/en/data-analytics/financial-data/company-data/ibes-estimates>
- Financial Modeling Prep: <https://site.financialmodelingprep.com/datasets/analyst-estimates-targets>
- SEC Developer Resources: <https://www.sec.gov/about/developer-resources>
- SEC SpaceX S-1 (May 20, 2026): <https://www.sec.gov/Archives/edgar/data/1181412/000162828026036936/spaceexplorationtechnologi.htm>
- Cerebras IPO closing release: <https://www.cerebras.ai/press-release/cerebras-systems-announces-closing-of-initial-public-offering>
- Alpha Vantage documentation: <https://www.alphavantage.co/documentation/>
- Nasdaq Data Link docs: <https://docs.data.nasdaq.com/docs/getting-started>
- Historical S&P 500 experiment: <https://github.com/riazarbi/sp500-scraper>
- London Stock Exchange New Issues: <https://www.londonstockexchange.com/live-markets/new-issues>
- FCA National Storage Mechanism: <https://www.fca.org.uk/markets/primary-markets/regulatory-disclosures/national-storage-mechanism>
- HKEX New Listing Information - AP & PHIP: <https://www.hkexnews.hk/app/appindex.html>
- ASX Upcoming floats and listings: <https://www.asx.com.au/listings/upcoming-floats-and-listings>
- TSX New Company Listings: <https://www.tsx.com/en/news/new-company-listings>
- SGX IPO Prospectus: <https://www.sgx.com/securities/ipo-prospectus>
