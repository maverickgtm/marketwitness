# Busqueda Internacional De Datos Gratuitos

Revision: `2026-05-25`.

Esta revision amplia la busqueda de datos para TargetAudit a Reino Unido,
Japon, Australia, Hong Kong, Singapur y China continental. El objetivo no es
encontrar paginas que simplemente muestren informacion, sino fuentes que
permitan construir una edicion publica gratuita sin copiar datos contra sus
terminos.

## Resultado Ejecutivo

No se encontro un dataset internacional gratuito y publicable que resuelva el
faltante central: historial individual de `price targets` para firmas de Wall
Street sobre acciones de Estados Unidos.

Si se encontraron rutas nuevas para ampliar el producto:

| Prioridad | Fuente | Que Podria Aportar | Decision Inicial |
|---:|---|---|---|
| Alta | FSA Japan `EDINET` Documents API | API oficial gratuita de documentos regulatorios, incluidos securities registration statements; requiere clave y acceso responsable | Incorporar Japon como conector prioritario y construir un collector atribuido de documentos de oferta |
| Media | `EDINET DB` | Enriquecimiento de datos japoneses; declara plan gratis y display publico con atribucion, sin redistribucion masiva | Mantener como candidato secundario, no sustituir la fuente oficial EDINET |
| Alta | MAS `OPERA` / Singapore Open Data Licence | Prospectos y documentos de ofertas de Singapur; la licencia abierta permite aplicaciones y analisis derivados para datasets cubiertos | Verificar dataset/API concreto de OPERA antes de ampliar IPO Watch |
| Media | JPX `J-Quants API` | Precios OHLC japoneses ajustados y listado de valores; plan gratis con dos anos de historial y retraso de 12 semanas | Buen candidato para laboratorio Japon; revisar permiso de output antes de publicar precios |
| Media | SGX `Analyst Research` | Informes aportados por firmas sobre acciones de Singapur | Referencia documental, no feed estructurado de targets |
| Baja | HKMA Open API | Series economicas y de mercado monetario de Hong Kong gratis y sin registro | Podria servir para contexto macro futuro; no resuelve targets, precios de acciones ni IPOs |

## Targets Individuales De Analistas

Esta categoria sigue siendo el bloqueo principal del `Financials Scorecard`
real.

| Mercado / Fuente | Hallazgo | Por Que No Activa Rankings Publicos |
|---|---|---|
| Reino Unido / `AnalystCentral` | Declara un CSV gratuito con 10 anos de ratings y price targets de Wall Street para mas de 8,500 acciones e indices | Sus terminos conceden uso personal y prohiben republicacion, derivados y data mining sin consentimiento escrito |
| Singapur / `ShareInvestor` | Publica consenso y target price agregado a partir de mas de 200 research houses, incluidas companias overseas | Es producto de membresia/terminal y no se encontro permiso para publicar su base historica |
| Singapur / SGX `Analyst Research` | Aloja informes de research contribuidos por firmas externas | Los documentos pueden orientar revision manual; no constituyen filas reutilizables con licencia para ranking |
| China / Wind Research Report Platform | Publica cobertura de mas de 4.5 millones de informes de cientos de fuentes, incluidos equities globales | Es plataforma profesional/licenciada, no dataset abierto para republicar targets |
| Japon / Minkabu | Muestra consenso y evolucion temporal de precios objetivo para acciones japonesas | Vista de producto, sin feed abierto y redistribuible identificado |

`AnalystCentral` merece una accion especifica: solicitar permiso escrito para
usar un subconjunto derivado y publicar resultados agregados sin distribuir
sus filas. Sin ese permiso, la afirmacion `100% Free` no supera las
restricciones de sus propios terminos.

## Precios Ajustados Y Acciones Corporativas

| Mercado | Fuente Oficial Revisada | Utilidad | Estado Gratuito / Publicable |
|---|---|---|---|
| Japon | JPX `J-Quants API` | OHLC ajustado/no ajustado, splits incorporados y listado historico de valores | Plan gratis: dos anos, retraso de 12 semanas; se debe confirmar display/output publico antes de conectarlo |
| Australia | ASX `ReferencePoint` | EOD oficial, corporate actions y factores de dilucion | Producto de datos para suscriptores; no ruta gratis de publicacion |
| Reino Unido | LSE Historical and Reference Data Products | End-of-day summary, Daily Official List y cambios por acciones corporativas | Data Shop/suscripcion; los terminos de market data controlan redistribucion |
| Hong Kong | HKEX Historical Data / Data Marketplace | Datos historicos, trade files, atributos diarios y descargas programaticas | Productos por suscripcion; no fuente gratis para el dashboard |
| Singapur | SGX Historical Data y SGXNews XML | Precios, anuncios y corporate actions estructurados | SGX ofrece prueba/contacto comercial; precios web gratuitos son solo para uso personal/no comercial |
| China | SSE/CIIS historical market data | Snapshots/K-line y datos historicos oficiales de Shanghai | Oferta de suscripcion; CIIS muestra precios comerciales para historia oficial |

El hallazgo japones es tecnicamente valioso, pero no reemplaza los precios
ajustados de acciones estadounidenses que se necesitan para puntuar Roth MKM,
KBW, Citi, UBS o Barclays.

## Universo Historico E Indices

Las bolsas internacionales ayudan a crear futuros verticales locales, no a
reconstruir gratuitamente el universo historico `U.S. Financials`.

| Fuente | Hallazgo | Decision |
|---|---|---|
| JPX Index Data Service / TOPIX | Constituents y cambios de componentes disponibles como servicios de datos; JPX indica licencias para provision a terceros | No usar como universo publico gratis |
| ASX ReferencePoint | Master List y referencias para instrumentos/corporate actions | Ruta contractual, no fuente abierta |
| HKEX Data Marketplace | Securities Attribute Daily Files y datos oficiales de referencia | Ruta contractual |
| CSI / SSE / SZSE | Constituyentes y anuncios visibles; servicios de market data operados/licenciados por entidades oficiales | Explorar solo para vertical chino futuro, despues de verificar licencia de reutilizacion |

## ETF Holdings

Australia y Hong Kong confirmaron que existen holdings o divulgaciones utiles,
pero no una licencia universal de republicacion diaria:

| Fuente | Hallazgo | Uso Prudente |
|---|---|---|
| Vanguard Australia | Paginas de ETF muestran holdings y broker basket con actualizaciones declaradas | Consulta de cobertura; revisar terminos antes de recolectar |
| Betashares Australia | Paginas de ETF ofrecen descarga CSV para ciertos fondos | Candidato para importador local, nunca ingestión publica automatica sin permiso |
| SFC / HKEX | Reglas de divulgacion continua para ETF autorizados en Hong Kong | Evidencia regulatoria, no feed consolidado de compras/ventas |

La ruta gratuita actualmente defendible en TargetAudit sigue siendo `SEC
N-PORT`, con frecuencia regulatoria y sin afirmar tiempo real.

## Fuentes Que Si Merecen Siguiente Implementacion

1. `Japan IPO Filing Watch`: implementar un collector sobre el API oficial
   `EDINET`, configurado con clave, atribucion y controles de acceso justo,
   para monitorear documentos de oferta japoneses separado de precios.
2. `Singapore Offer Document Watch`: localizar el dataset/API específico de
   `MAS OPERA` cubierto por la Singapore Open Data Licence y agregarlo como
   confirmacion regulatoria, complementaria al conector SGX existente.
3. `Japan Prices Sandbox`: preparar un adaptador `J-Quants` apagado por
   defecto, que solo se active tras confirmar atribucion y output publico del
   plan gratuito.
4. `AnalystCentral Permission Track`: enviar una solicitud de autorizacion
   para publicar estadisticas agregadas de una muestra, sin redistribuir el
   archivo fuente.

## Fuentes Oficiales Y Referencias Revisadas

- AnalystCentral about/data claim: <https://analystcentral.com/about-us/>
- AnalystCentral terms: <https://analystcentral.com/terms-of-service>
- JPX J-Quants API: <https://www.jpx.co.jp/english/markets/other-data-services/j-quants-api/index.html>
- JPX J-Quants plan announcement: <https://www.jpx.co.jp/corporate/news/news-releases/6020/20230403-01.html>
- JPX J-Quants 2026 enhancement: <https://www.jpx.co.jp/english/corporate/news/news-releases/6020/20260119.html>
- JPX TDnet overview: <https://www.jpx.co.jp/english/equities/listing/disclosure/tdnet/index.html>
- JPX TDnet paid services: <https://www.jpx.co.jp/english/markets/paid-info-listing/tdnet/>
- FSA EDINET Documents API guide: <https://disclosure2.edinet-fsa.go.jp/guide/static/disclosure/WZEK0090.html>
- EDINET DB API documentation: <https://edinetdb.com/docs/api>
- EDINET DB terms: <https://edinetdb.com/legal/terms>
- ASX ReferencePoint: <https://www.asx.com.au/connectivity-and-data/information-services/reference-data>
- LSE Historical Data Products: <https://www.londonstockexchange.com/equities-trading/market-data/historical-data-products>
- LSE market data terms: <https://docs.londonstockexchange.com/sites/default/files/documents/market-data-terms-conditions-2023-combined.pdf>
- HKEX Historical Data FAQ: <https://www.hkex.com.hk/Global/Exchange/FAQ/Market-Data/Getting-Market-Data/Historical-Data?sc_lang=en>
- HKMA Open API: <https://apidocs.hkma.gov.hk/abouthkmasapi/>
- SGX Historical Data: <https://www.sgx.com/data-connectivity/historical-data>
- SGX Securities personal-use price download: <https://www.sgx.com/research-education/securities>
- SGX Analyst Research: <https://www.sgx.com/research-education/analyst-research>
- MAS OPERA terms: <https://eservices.mas.gov.sg/opera/MASUserTerms.aspx>
- Singapore Open Data Licence: <https://data.gov.sg/open-data-licence>
- SSE market-data services: <https://www.sse.com.cn/transparency/services/index.shtml>
- SSE/CIIS historical products: <https://www.ciis.com.hk/hongkong/sc/historicaldata1/index.shtml>
- Wind Research Report Platform: <https://www.wind.com.cn/portal/en/RPP/index.html>
