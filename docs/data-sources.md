# Fuentes De Datos Evaluadas

Fecha de revision inicial: `2026-05-24`.

El dato mas dificil del proyecto es el historial de `price targets`
individuales con fecha, firma y target. Los precios historicos y datos
regulatorios tienen alternativas publicas o freemium mas amplias.

La investigacion publica inicial se concentrara en `U.S. Financials`, usando
`XLF` como benchmark sectorial inicial cuando la licencia de precios lo
permita. Esto responde a la hipotesis de que firmas especializadas en el sector
pueden comportarse distinto a firmas generalistas.

## Registro Formal De Gobernanza

La clasificación legible por máquina vive en
`data/samples/source_registry.csv` y se renderiza con `source-registry`.
Conserva por fuente su modo de acceso, estado técnico, revisión de términos o
licencia, política de publicación y referencia revisada.

Al `2026-05-24`, el inventario contiene 15 fuentes: 10 conectores o fixtures
implementados, 10 fuentes que aún exigen revisión de términos/licencia para
uso público real y 1 referencia bloqueada para colección automatizada. Esta
separación evita confundir "el endpoint responde" con "sus datos se pueden
redistribuir en un producto público".

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
Por eso TargetAudit no incluye un scraper. El comando `targets-import` acepta
exportaciones suministradas legalmente mediante un manifiesto que declara
proveedor, mapeo, referencia contractual y uso autorizado; toda fila sin
evidencia URL o campos evaluables queda rechazada antes del scorecard. El
fixture incluido es sintetico y no representa una licencia comercial real.

## Precios Ajustados Y Mercado

| Fuente | Uso Potencial | Consideracion |
|---|---|---|
| Alpha Vantage | Precios diarios ajustados, splits y dividendos | Adaptador implementado; `TIME_SERIES_DAILY_ADJUSTED` esta marcado premium y exige revision de publicacion |
| Nasdaq Data Link | Datasets publicos y premium | Explorar datasets concretos y sus licencias antes de elegir |
| Stooq / fuentes que lo reutilizan | Precio fin de dia para experimentacion | Validar terminos y calidad antes de publicacion |
| Proveedor comercial futuro | Precios punto-en-el-tiempo y acciones corporativas | Necesario si se ofrece servicio robusto de produccion |

TargetAudit requiere precios ajustados con `high`, `low` y `close`, porque un
target puede ser alcanzado intradia aun cuando el cierre no lo refleje.

El adaptador Alpha Vantage es cache-first y limita cada ejecucion en vivo a un
solo simbolo. La documentacion oficial revisada el `2026-05-24` indica un
limite estandar de 25 solicitudes diarias y clasifica
`TIME_SERIES_DAILY_ADJUSTED` como funcion premium. Dado que la respuesta
diaria ajustada expone `high`/`low` operados y `adjusted close`, TargetAudit
calcula `adjusted_high` y `adjusted_low` aplicando por fila
`adjusted_close / raw_close`. El codigo y el fixture sintetico son publicos;
un dataset real y resultados derivados no se publicaran hasta aprobar terminos
y derechos del plan contratado.

## Universo Historico

El scorecard admite `historical_universe.csv` para impedir que una muestra
retrospectiva seleccione solo companias que hoy continúan visibles. El fixture
del repositorio es sintetico. Para publicar resultados reales se requerira una
fuente autorizada de integrantes historicos que identifique ventanas de
membresia, ticker y sector vigentes en la fecha de cada target.

## Acciones Corporativas

Revisado al `2026-05-24`:

| Fuente | Senal Disponible | Uso Previsto |
|---|---|---|
| Nasdaq Daily List | Especificacion oficial contempla cambios de simbolo, stock splits y reverse splits | Candidato para normalizar acciones Nasdaq; revisar suscripcion/licencia antes de integrar |
| NYSE Corporate Actions | Pagina oficial de acciones corporativas con fecha de accion | Candidato para eventos de emisores NYSE |
| Comunicados del emisor / filings SEC | Confirmacion primaria puntual de split o cambio corporativo | Evidencia manual para casos bajo revision |

El demo de `corporate-actions-check` no declara eventos reales: emplea dos
acciones sintéticas para probar que un target que atraviesa un split o cambio
de ticker queda fuera del scoring protegido. La aplicación de factores reales
requerirá evidencia y una política de normalización explícita.

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

La ingesta de comunicados oficiales ya se representa mediante
`issuer_listing_confirmations.csv`. Su muestra inicial preserva dos hitos
declarados en el comunicado de Cerebras publicado el `2026-05-15`: trading de
`CBRS` iniciado el `2026-05-14` en Nasdaq Global Select Market y cierre de la
oferta el `2026-05-15`. Esta fuente confirma esos eventos, no el rendimiento
futuro de la accion.

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
| Australia | ASX Upcoming floats and listings | Nuevos listings con solicitud formal recibida, fecha anticipada y retiros | Feed HTML oficial implementado |
| Canada | TSX New Company Listings | Nuevas companias ya listadas | Feed HTML oficial implementado como confirmación |
| Singapur | SGX IPO Prospectus API | Prospectos IPO publicados | Feed JSON oficial implementado |

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
la última versión documental. Ahora clasifica el metadato `type` visible como
`prospectus_document_signal`, `admission_document_signal`,
`intention_to_float_notice` u `other_document_review`. La FCA indica que el
NSM no es un servicio en tiempo real; por eso las categorías sólo enrutan
revisión humana y `no_document_found` no descarta una cotización futura.

El conector ASX lee la tabla HTML de la página oficial
`https://www.asx.com.au/listings/upcoming-floats-and-listings`. ASX declara
que la página solo contiene nuevos listings para los que recibió una
solicitud formal, normalmente cerca de cuatro a seis semanas antes, y que
fechas/códigos propuestos pueden cambiar. TargetAudit conserva `anticipated`
y `withdrawn` sin interpretarlos como instrucción de inversión.

El conector TSX lee la tabla HTML oficial
`https://www.tsx.com/en/news/new-company-listings`. Sus filas registran
empresas que TSX ya muestra como nuevas cotizaciones y por ello solo asignan
el estado `listed`; no constituyen una señal previa de IPO.

La página oficial SGX `IPO Prospectus` y el API que la alimenta,
`https://api.sgx.com/ipoprospectus/v1.0/`, fueron verificados el
`2026-05-24`. El API mostró `JUSTCO HOLDINGS LIMITED` con fecha de cierre
`20 May 2026` y permite monitorear prospectos publicados. TargetAudit asigna
`prospectus_published`: esta evidencia no confirma admisión o negociación.

Para SEC se debe declarar el `User-Agent`, descargar solo lo necesario y
respetar la guia de acceso justo, que actualmente fija un maximo de 10
solicitudes por segundo.

## ETF Holdings Activity: Modulo En Cola

La propuesta de mostrar que posiciones aumentan o reducen los ETF es factible,
pero no debe presentarse como operacion en tiempo real si la fuente no lo
garantiza. La implementacion futura separara dos capas:

| Fuente | Frecuencia Publica Util | Uso Previsto |
|---|---|---|
| SEC `N-PORT` | Registro regulatorio publico con retraso; la publicacion publica disponible no es intradia | Evidencia historica auditable de cartera por fondo |
| ARK ETF holdings | ARK declara actualizacion diaria de holdings en su sitio | Primer conector diario para fondos activos transparentes |
| State Street SPDR holdings | Paginas oficiales indican descarga de todos los holdings diaria para fondos como `SPYM`/`XLU` | Segundo conector diario, incluyendo `XLF` si la descarga oficial es estable |
| iShares holdings | Paginas oficiales exponen `Download Holdings` con fecha de observacion | Conector por emisor tras verificar terminos y formato estable |

El dashboard mostrara cambios entre snapshots, por ejemplo aumento o
reduccion de acciones reportadas y de peso. No afirmara automaticamente que
un gestor "compro" o "vendio": cambios de participacion tambien pueden
reflejar creaciones/redenciones del ETF, acciones corporativas, derivados,
efectivo o ajustes de publicacion.

La primera version debe incluir fecha efectiva del holding, fecha de captura,
emisor, fondo, ticker de la posicion, acciones/peso anterior y actual,
diferencia y enlace a la descarga oficial. No se mezclara con recomendaciones
de compra o venta.

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
- Alpha Vantage premium and usage-limit reference: <https://www.alphavantage.co/premium/>
- Nasdaq Data Link docs: <https://docs.data.nasdaq.com/docs/getting-started>
- Nasdaq Daily List specifications: <https://www.nasdaqtrader.com/content/technicalSupport/specifications/dataproducts/dlcompletespec.pdf>
- NYSE Corporate Actions: <https://www.nyse.com/trade/corporate-actions>
- Historical S&P 500 experiment: <https://github.com/riazarbi/sp500-scraper>
- London Stock Exchange New Issues: <https://www.londonstockexchange.com/live-markets/new-issues>
- FCA National Storage Mechanism: <https://www.fca.org.uk/markets/primary-markets/regulatory-disclosures/national-storage-mechanism>
- HKEX New Listing Information - AP & PHIP: <https://www.hkexnews.hk/app/appindex.html>
- ASX Upcoming floats and listings: <https://www.asx.com.au/listings/upcoming-floats-and-listings>
- TSX New Company Listings: <https://www.tsx.com/en/news/new-company-listings>
- SGX IPO Prospectus: <https://www.sgx.com/securities/ipo-prospectus>
- SEC Form N-PORT: <https://www.sec.gov/files/formn-port.pdf>
- ARK ETF holdings update policy: <https://helpcenter.ark-funds.com/can-you-explain-the-date-listed-on-the-ark-etf-holdings-documents>
- State Street SPDR SPYM holdings: <https://www.ssga.com/us/en/individual/etfs/state-street-spdr-portfolio-sp-500-etf-spym>
