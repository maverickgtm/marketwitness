# Fuentes De Datos Evaluadas

Fecha de revision inicial: `2026-05-24`.

El dato mas dificil del proyecto es el historial de `price targets`
individuales con fecha, firma y target. Los precios historicos y datos
regulatorios tienen alternativas publicas o freemium mas amplias.

La investigacion publica inicial se concentrara en `U.S. Financials`, usando
`XLF` como benchmark sectorial inicial cuando la licencia de precios lo
permita. Esto responde a la hipotesis de que firmas especializadas en el sector
pueden comportarse distinto a firmas generalistas.

## Alcance Gratuito Principal

`Open Edition` no depende de proveedores comerciales. Funciona offline con
fixtures redistribuibles y, para operación live sin cuota, utiliza las fuentes
regulatorias registradas como aptas: SEC EDGAR, SEC N-PORT y FCA NSM. Las
fuentes de targets, precios o universo comercial quedan listadas como caminos
opcionales para usuarios que posean derechos suficientes.

El catalogo `data/samples/licensed_extensions.csv` registra esas rutas
voluntarias con precios publicos encontrados y limites de publicacion. No es
una fuente de ingestion ni contiene credenciales o datasets adquiridos.

## Registro Formal De Gobernanza

La clasificación legible por máquina vive en
`data/samples/source_registry.csv` y se renderiza con `source-registry`.
Conserva por fuente su modo de acceso, estado técnico, revisión de términos o
licencia, política de publicación y referencia revisada.

El expediente de trabajo complementario vive en
`data/samples/provider_approval_queue.csv` y se renderiza con
`provider-approvals`. Mantiene la evidencia pendiente y el criterio de
promoción para los candidatos del scorecard; no modifica automáticamente la
política de una fuente.

Cuando existe una decisión documentada, `provider-approval-review` escribe
copias revisadas de ambos registros y su auditoría. El fixture inicial
documenta que la página premium de Alpha Vantage todavía no demuestra permiso
de salida pública y por eso conserva el expediente pendiente.

Al `2026-05-24`, el inventario contiene 26 fuentes: 15 conectores o fixtures
implementados, 19 fuentes que aun exigen revision de terminos/licencia para
uso público real, 1 integracion limitada a descarga manual y 1 referencia
bloqueada para colección automatizada. Esta separación evita confundir "el
endpoint responde" con "sus datos se pueden redistribuir en un producto
público".

## Targets Y Ratings

| Fuente | Cobertura Declarada | Utilidad | Estado Para TargetAudit |
|---|---|---|---|
| Benzinga Analyst Ratings API | Acciones USA, historial desde 2013; firma, analista, rating y targets anterior/actual | Candidato principal para un pipeline real | Cotizacion/licencia directa requerida |
| Massive / Benzinga Analyst Ratings Expansion | Ratings y targets estructurados; documentacion desde 2011-12-08 | Ruta voluntaria para un usuario con licencia propia | `USD 99/month` individual visible; no autoriza ranking publico compartido |
| MarketBeat All Access | Mas de un millon de recomendaciones y export CSV para hasta seis meses recientes | Piloto privado economico y verificacion de cobertura | `USD 249/year` o `USD 29/month`; no cubre por si solo evaluacion a un ano ni redistribucion |
| WallStreetZen Premium | Rankings propios sobre mas de 4,000 analistas | Benchmark privado para contrastar metodologia | `USD 19.50/month` anual; exportaciones solo para investigacion interna, no redistribucion |
| GuruFocus | Analyst estimates de Refinitiv/Morningstar segun FAQ | Candidato para revision de cobertura | No confirmar como feed de targets individuales; licencia comercial para redistribuir |
| Finnhub | `Recommendation Trends` y `Price Target` declarados en cobertura Enterprise | Potencial conector programatico de consenso/target | Derechos de redistribucion declarados para Enterprise con cotizacion; plan gratis no basta para publicacion |
| Financial Modeling Prep | `Price Target Summary` y `Price Target Consensus` documentados | Potencial validacion programatica agregada | Display o redistribucion exige acuerdo especifico; confirmar granularidad historica individual |
| LSEG I/B/E/S | Historial institucional de estimaciones y recomendaciones | Fuente de investigacion de alta calidad | Candidata futura, probablemente costosa |
| MarketBeat | Historial, screener y ranking propios | Referencia metodologica y verificacion manual | Herramientas/exportaciones sujetas a suscripcion y terminos |
| TipRanks | Rankings y targets visibles; su FAQ mide ratings Buy por un ano | Benchmark metodologico cercano a TargetAudit | No usar scraping; requerir licencia/API institucional para datos |
| Finviz | Eventos visibles en paginas USA; Elite anuncia export/API access | Verificacion manual puntual | `USD 39.50/month` o `USD 299.50/year`; no adoptar como colector sin derechos de output |
| StockAnalysis.com | Paginas `Analysts` y datos derivados de multiples fuentes | Verificacion visual puntual | Terminos permiten snippets atribuidos, no republicar contenido completo |
| Koyfin | Charts y estimaciones de consenso visibles | Referencia visual y graficos citables | No API; estimates y valuation restringidos de descarga por proveedor |
| WSJ / CNBC | Vistas y cobertura editorial sobre recomendaciones | Contexto manual | No feed documentado para ingestión/publicacion |
| Yahoo Finance | Recomendaciones/targets visibles con proveedores declarados | Verificacion visual puntual | No redistribuir informacion de Yahoo Finance; no integrar scraper |
| Investing.com | Ratings visibles en interfaz | Verificacion visual puntual | Sus terminos prohiben almacenamiento/redistribucion sin permiso escrito |

### Conclusion Inicial

No se identifico una fuente abierta y claramente redistribuible que entregue,
de forma completa, price targets historicos individuales de firmas de EE. UU.
Por eso TargetAudit no incluye un scraper. El comando `targets-import` acepta
exportaciones suministradas legalmente mediante un manifiesto que declara
proveedor, mapeo, referencia contractual y uso autorizado; toda fila sin
evidencia URL o campos evaluables queda rechazada antes del scorecard. El
fixture incluido es sintetico y no representa una licencia comercial real.
Las alternativas pagadas y sus limites se documentan en
`docs/licensed-extensions.md`.

TradingView queda fuera de la tabla de targets porque su oportunidad es
distinta: ofrece widgets gratuitos que pueden integrarse en una pagina
publica manteniendo la atribucion original. Es adecuado para contexto visual
de mercado, no para almacenar o puntuar historial de analistas:
<https://www.tradingview.com/widget-docs/widgets/charts/> y
<https://www.tradingview.com/policies/>.

## Activos Tokenizados Y RWA Watch

La revision del Top 20 de exchanges centralizados por CoinGecko Trust Score y
de Pepperstone se conserva en
[RWA Watch: Exchanges Y Fuentes Base](rwa-watch-sources.md). La conclusion
tecnica cambia la prioridad: conviene integrar primero la fuente emisora del
activo y usar exchanges solamente como venues secundarios.

| Fuente O Grupo | Que Ofrece | Encaje En TargetAudit |
|---|---|---|
| `xStocks / Backed Public API` | Recursos sin autenticacion para metadatos, precio subyacente/mercado, documentacion legal y proof of reserves | Candidato base preferido para `RWA Watch`, pendiente de terminos de display y retencion |
| `Ondo Global Markets` | Mas de 200 acciones y ETF tokenizados con ruta API/SDK documentada | Segunda familia candidata, pendiente de acceso y derechos publicos |
| Bybit, Kraken, Gate y Bitget | Venues oficiales que anuncian xStocks u Ondo tokenizados | Candidatos secundarios para contrastar mercado despues de validar terminos |
| LBank | Zona xStocks anunciada con activos impulsados por Backed | Referencia de venue hasta confirmar API |
| Gemini y OKX | Gemini declara que su producto no esta disponible via API; OKX dirige estos activos a DEX/wallet y no a su CEX | Referencia de cobertura, no conectores |
| Pepperstone | CFDs de acciones y APIs vinculadas a cuenta | Contexto privado de derivados, excluido de la capa emisora |

Esta linea tampoco resuelve la pregunta inicial de analistas: activos
tokenizados, CFD y productos de brokerage no entregan un historial de
pronosticos de Roth MKM, KBW, UBS, Citi o Barclays.

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

La documentación oficial de Alpha Vantage consultada el `2026-05-24`
mantiene `TIME_SERIES_DAILY_ADJUSTED` como función `Premium` y describe que
entrega OHLCV operado, cierre ajustado y eventos históricos de split/dividendo:
<https://www.alphavantage.co/documentation/>.
Su API `NEWS_SENTIMENT` cubre noticias historicas y live, incluidas noticias
de IPO; sin embargo, los terminos revisados conceden acceso personal no
comercial salvo acuerdo escrito. No se debe presentar como sustituto gratuito
publicable de ratings de analistas:
<https://www.alphavantage.co/terms_of_service/>.

## Universo Historico

El scorecard admite `historical_universe.csv` para impedir que una muestra
retrospectiva seleccione solo companias que hoy continúan visibles. El fixture
del repositorio es sintetico. Para publicar resultados reales se requerira una
fuente autorizada de integrantes historicos que identifique ventanas de
membresia, ticker y sector vigentes en la fecha de cada target.

S&P Dow Jones Indices identifica oficialmente paquetes licenciados de datos de
constituyentes y de acciones corporativas. Como el universo inicial deseado es
Financials dentro del `S&P 500`, `sp-dji-constituents` queda registrado como
candidato de producción sujeto a derechos explícitos, no como fuente gratuita
ya habilitada: <https://www.spglobal.com/spdji/en/about-us/data-index-licensing/>.

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

Nasdaq describe su `Daily List` como un producto de datos de acciones
corporativas con cambios de nombre/símbolo, dividendos y stock splits:
<https://nasdaqtrader.com/Trader.aspx?id=DailyListPD>. La disponibilidad de
la descripción técnica no equivale a licencia de distribución.

SEC `data.sec.gov` permanece útil para corroborar disclosures o filings
puntuales mediante APIs públicas sin clave, siguiendo Fair Access. Sus APIs
documentadas cubren submissions y datos XBRL extraídos, no un feed completo
de precios ajustados ni un historial de membresía sectorial:
<https://www.sec.gov/search-filings/edgar-application-programming-interfaces>.

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

## ETF Holdings Activity: Modulo Inicial

La propuesta de mostrar que posiciones aumentan o reducen los ETF es factible,
pero no debe presentarse como operacion en tiempo real si la fuente no lo
garantiza. El comparador de snapshots y la pagina de dashboard ya estan
implementados con datos sinteticos distribuibles. Tambien existen
importadores locales de archivos ARK y State Street SPDR/XLF, sin distribuir
sus holdings reales. Las fuentes reales se separan en dos capas:

| Fuente | Frecuencia Publica Util | Uso Previsto |
|---|---|---|
| SEC `N-PORT` | Registro regulatorio publico; submissions recientes por CIK y datasets actualizados trimestralmente, no intradia | Catalogo/descarga local de ZIP, sincronizacion incremental, importador XML, colector EDGAR y backfill tabular implementados para posiciones en acciones |
| ARK ETF holdings | ARK declara actualizacion diaria de holdings en su sitio | Importador CSV local implementado; publicacion real pendiente de permiso |
| State Street SPDR holdings | La pagina oficial `XLF` indica `Download All Holdings: Daily` | Importador local `XLF` implementado; publicacion real pendiente de consentimiento escrito |
| iShares `IYF` holdings | La pagina oficial expone holdings de un ETF de acciones financieras estadounidenses con fecha de observacion | Importador local implementado; descarga automatica prohibida sin permiso conforme a terminos BlackRock |

El dashboard mostrara cambios entre snapshots, por ejemplo aumento o
reduccion de acciones reportadas y de peso. No afirmara automaticamente que
un gestor "compro" o "vendio": cambios de participacion tambien pueden
reflejar creaciones/redenciones del ETF, acciones corporativas, derivados,
efectivo o ajustes de publicacion.

La primera version implementada incluye fecha efectiva del holding, fecha de
captura, emisor, fondo, ticker de la posicion, acciones/peso anterior y
actual, diferencia y enlace a la evidencia declarada. No se mezcla con
recomendaciones de compra o venta. En ARK el parser local ya esta disponible,
pero la pagina de materiales indica restricciones de reproduccion que impiden
incluir holdings oficiales en el repositorio sin permiso. Los siguientes
conectores se habilitaran solo tras confirmar formato estable y politica de
uso. State Street indica en la pagina oficial de `XLF` que los holdings son
sujetos a cambio, no son recomendacion de compra o venta y la obra no puede
reproducirse sin consentimiento escrito. El fixture prueba el contrato de
campos; la primera descarga local autorizada debe confirmar sus encabezados
antes de una ejecucion real. El motor rechaza
comparar snapshots de capas diferentes, por ejemplo una lectura diaria contra
un registro regulatorio periodico.

El importador `SEC NPORT-P` conserva `repPdEnd` como fecha efectiva, el
nombre de serie y el identificador de serie. En esta etapa normaliza
unicamente inversiones expresadas en unidades de acciones (`NS`/`SH`) y
reporta cuantas posiciones en otras unidades quedaron fuera; no inventa
equivalencias para efectivo, bonos o derivados.

El colector `sec-nport-collect` obtiene la lista reciente de filings del
registrante desde la API publica SEC submissions, descarga documentos
`NPORT-P` candidatos y solo conserva el XML que confirma la `seriesId`
solicitada. La ventana reciente es adecuada para monitoreo continuo; un
backfill historico amplio usa los datasets trimestrales publicados por la SEC.
El comando `sec-nport-backfill` consume las tablas oficiales extraidas,
permite agregar varios trimestres y produce snapshots por `REPORT_DATE` mas
un manifiesto de accesiones. No selecciona automaticamente entre periodos
duplicados o enmiendas.

El comando `sec-nport-datasets` obtiene del catalogo oficial las URL de cada
ZIP trimestral, descarga un trimestre solicitado con `User-Agent` SEC y
extrae unicamente las cinco tablas requeridas por el backfill. Los ZIP y TSV
reales permanecen en `data/raw/` y no se versionan.
El comando `sec-nport-sync` inicializa un estado local sin descargar el
historico existente y, en revisiones posteriores, descarga unicamente ZIP
publicados por primera vez desde esa linea base. Puede regenerar la serie
N-PORT de un fondo con los trimestres ya disponibles localmente.
En la verificacion del `2026-05-24`, el catalogo oficial publico `26`
releases, desde `2019q4` hasta `2026q1`.

El importador `ishares-holdings-import` procesa un archivo `IYF` descargado
manualmente, detecta la fecha `Holdings as of`, normaliza posiciones equity y
registra posiciones no equity omitidas. La pagina oficial de `IYF` muestra
holdings, acciones y peso, pero los terminos BlackRock revisados el
`2026-05-24` prohíben el uso de agentes automaticos para monitorizar o copiar
materiales del sitio sin permiso; por tanto no existe un fetch ni una tarea
recurrente iShares en TargetAudit.

El filing oficial `NPORT-P` de `SELECT SECTOR SPDR TRUST` consultado para
esta integracion identifica a `The Financial Select Sector SPDR Fund`
(`XLF`) con `CIK 0001064641` y `seriesId S000006411`, por lo que es el
primer fondo regulatorio configurado para ejecucion operativa.

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
- Massive/Benzinga: <https://massive.com/docs/rest/stocks/benzinga/analyst-ratings>
- Massive pricing: <https://massive.com/pricing>
- Massive individual market-data terms: <https://massive.com/legal/market_data_terms_individual>
- MarketBeat FAQ: <https://www.marketbeat.com/faq/>
- MarketBeat terms: <https://www.marketbeat.com/terms/>
- WallStreetZen plans: <https://www.wallstreetzen.com/plans>
- WallStreetZen terms: <https://www.wallstreetzen.com/terms-of-service>
- GuruFocus FAQ: <https://www.gurufocus.com/faq>
- GuruFocus term of use: <https://www.gurufocus.com/term-of-use>
- Finnhub enterprise licensing: <https://finnhub.io/pricing-startups-and-enterprise>
- Financial Modeling Prep analyst estimates: <https://site.financialmodelingprep.com/developer/docs/analyst-estimates-api/?direct=true>
- Financial Modeling Prep display licensing: <https://intelligence.financialmodelingprep.com/pricing-plans?direct=true>
- TipRanks FAQ: <https://www.tipranks.com/faq>
- Finviz FAQ and pricing: <https://finviz.com/help/faq>
- StockAnalysis.com terms: <https://stockanalysis.com/terms-of-use/>
- Koyfin API FAQ: <https://www.koyfin.com/help/faq/can-i-get-the-data-via-api/>
- Koyfin download restrictions: <https://www.koyfin.com/help/faq/can-i-download-data/>
- TradingView chart widgets: <https://www.tradingview.com/widget-docs/widgets/charts/>
- TradingView policies: <https://www.tradingview.com/policies/>
- Bybit xStocks FAQ: <https://www.bybit.com/en/help-center/article/FAQ-xStocks-on-Bybit>
- Bybit V5 instruments info: <https://bybit-exchange.github.io/docs/v5/market/instrument>
- Bybit TradFi contracts: <https://www.bybitglobal.com/en/help-center/article/Contracts-Available-on-TradFi-MT5-and-Specifications>
- Bybit restricted jurisdictions: <https://www.bybit.com/en/help-center/article/Service-Restricted-Countries>
- CoinGecko exchanges: <https://www.coingecko.com/en/exchanges>
- xStocks API: <https://docs.xstocks.fi/apis/openapi>
- xStocks overview: <https://docs.xstocks.fi/about-xstocks/welcome-to-xstocks/overview>
- Ondo Global Markets overview: <https://docs.ondo.finance/ondo-global-markets/overview>
- Ondo API integration: <https://docs.ondo.finance/ondo-global-markets/minting-and-redemption/minting-and-redemption-through-api>
- Kraken xStocks: <https://www.kraken.com/xstocks>
- Gate xStocks: <https://www.gate.com/xstocks>
- Bitget Ondo announcement: <https://www.bitget.com/support/articles/12560603838361>
- LBank xStocks announcement: <https://www.lbank.com/support/articles/21431592927001>
- Gemini tokenized stocks: <https://support.gemini.com/hc/en-us/articles/45788732343963-Tokenized-Stocks-Overview>
- OKX xStocks help: <https://web3.okx.com/en-eu/help/what-are-xstocks>
- Coinbase stocks overview: <https://help.coinbase.com/coinbase/trading-and-funding/stocks/overview>
- Crypto.com stocks and ETF: <https://help.crypto.com/en/articles/10441410-stocks-and-etfs>
- Pepperstone shares: <https://pepperstone.com/en/markets/shares/>
- Pepperstone Trading API: <https://pepperstone.com/en/platforms/integrations/trading-api/>
- Yahoo Finance data providers: <https://help.yahoo.com/kb/SLN2310.html>
- Investing.com terms: <https://www.investing.com/about-us/terms-and-conditions>
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
- SEC Form N-PORT Data Sets: <https://www.sec.gov/data-research/sec-markets-data/form-n-port-data-sets>
- SEC N-PORT dataset readme: <https://www.sec.gov/files/nport_readme.pdf>
- ARK ETF holdings update policy: <https://helpcenter.ark-funds.com/can-you-explain-the-date-listed-on-the-ark-etf-holdings-documents>
- State Street SPDR XLF holdings page: <https://www.ssga.com/us/en/intermediary/etfs/state-street-financial-select-sector-spdr-etf-xlf>
- State Street SPDR SPYM holdings: <https://www.ssga.com/us/en/individual/etfs/state-street-spdr-portfolio-sp-500-etf-spym>
