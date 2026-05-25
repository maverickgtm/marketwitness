# Busqueda Internacional Gratuita: Ronda 2

Revision: `2026-05-25`.

Esta ronda examina India, Mexico, Brasil, Argentina, Alemania, Suiza,
Paises Bajos e Italia para ampliar TargetAudit sin exigir pagos a quienes
usen la edicion publica.

## Resultado Ejecutivo

No se encontro una base gratuita y publicable de `price targets` individuales
de bancos o analistas que habilite el ranking principal. Si aparecieron dos
fuentes regulatorias estructuradas y defendibles para ampliar `Global Listings
Watch`:

| Prioridad | Cobertura | Fuente | Decision |
|---:|---|---|---|
| Alta | Brasil | CVM `Portal Dados Abertos`: ofertas publicas de distribucion en datasets estructurados y API | Agregar como conector prioritario para documentos/eventos de ofertas; requiere collector y validacion final de atribucion del dataset |
| Alta | Alemania, Paises Bajos e Italia | ESMA `Prospectus III`: registros de prospectos con servicios machine-to-machine | Agregar un solo conector regional; su aviso legal autoriza reproducir informacion del registro con fuente y rotulo para transformaciones |
| Media | Paises Bajos | AFM registro de prospectos aprobados con exportacion CSV/XML desde `2007` | Referencia nacional especialmente clara; puede validar muestras de ESMA para Amsterdam |
| Media | Argentina | BYMA API `EOD` anunciada sin costo y CNV AIF publica hechos/prospectos | Explorar precios EOD en laboratorio separado; aun falta confirmar derechos de output/republicacion |
| Media | India | SEBI `Public Issues` publica draft/red herring/final offer documents | Fuente documental manual o futura; no se confirmo API publica ni licencia de reutilizacion automatizada |
| Baja | Suiza | SIX publica reglas y avisos de listings, pero su market data requiere acuerdos de licencia | Mantener en exploracion documental; no activar precios ni collector publico |
| Bloqueada | Mexico | BMV publica ofertas y prospectos visibles | Su aviso legal prohibe reproduccion y parsing sin autorizacion escrita |

## Targets Individuales De Analistas

La busqueda local tampoco resolvio la tabla de targets necesaria para medir
firmas estadounidenses.

| Mercado / Fuente | Hallazgo | Uso Prudente |
|---|---|---|
| India / Trendlyne | Declara consenso, target prices y estimaciones para unas 900 companias indias | Producto de plataforma; no se encontro permiso de exportacion/publicacion para construir ranking |
| Brasil / Investing.com Brasil | Muestra consenso, rango e historial de revisiones de target para acciones B3 | Referencia visual; los terminos ya revisados de Investing.com no habilitan ingesta publica |
| Alemania, Suiza, Paises Bajos e Italia | Plataformas globales muestran consenso en acciones locales | No se identifico dataset abierto de filas historicas por analista |
| Mexico y Argentina | No se identifico API oficial de recomendaciones o targets | Ningun cambio para `Financials Scorecard` |

Estas fuentes pueden ayudar a investigar manualmente mercados locales, pero no
deben mezclarse con el ranking real hasta contar con derechos expresos.

## Brasil

El `Portal Dados Abertos CVM` es el hallazgo mas directo de America Latina.
El catalogo oficial incluye `Ofertas Publicas de Distribuicao`, con ofertas de
acciones, fondos, debentures y otros instrumentos registradas o dispensadas de
registro. El portal informa formatos estructurados y acceso por API.

Uso previsto:

- detectar nuevas ofertas brasileñas o cambios documentados;
- conservar identificadores y evidencia oficial para revision;
- confirmar cotizacion/listado posteriormente mediante una evidencia de B3;
- no interpretar una oferta registrada como recomendacion de inversion.

El `Hub de dados publicos` de B3 confirma que la bolsa ofrece datos visibles
de ofertas, empresas listadas, eventos corporativos y series. Para el primer
collector conviene usar CVM como fuente regulatoria abierta y no suponer
derechos sobre cada producto de B3.

## Union Europea

`ESMA Registers` ofrece servicios A2A para recuperar datos de sus repositorios,
incluido `Prospectus III`, y documenta campos como emisor, ISIN, autoridad,
tipo de documento y fechas. Su aviso legal autoriza reproducir la informacion
del registro si se reconoce la fuente y, cuando se transforme o republique,
se indica explicitamente la transformacion.

Esto permite implementar un `EU Prospectus Watch` filtrado a:

- Alemania, con `BaFin` como autoridad competente;
- Paises Bajos, con `AFM`, cuyo registro nacional tambien exporta CSV/XML;
- Italia, con `CONSOB`, que mantiene la consulta publica de prospectos.

Un prospecto aprobado o notificado es una senal regulatoria, no prueba por si
solo que el instrumento ya este negociando.

## Fuentes Aun No Activables

| Pais | Fuente Revisada | Motivo Para No Activar |
|---|---|---|
| Mexico | BMV ofertas publicas y prospectos | El aviso legal prohibe copiar, reproducir o extraer mediante parsing sin autorizacion previa por escrito |
| India | SEBI Public Issues / BSE IPO pages | Hay documentos y paginas publicas, pero no se confirmo un feed/API publico con derechos claros de republicacion |
| Argentina | BYMA APIs / CNV AIF | BYMA anuncia API EOD sin costo, pero la reutilizacion publica de outputs debe revisarse antes de integrarla |
| Suiza | SIX / SIX Exchange Regulation | Precios y datos historicos dependen de acuerdos de market data; falta confirmar una exportacion documental abierta para IPO Watch |

## Siguientes Implementaciones

1. `Brazil Offering Watch`: crear adaptador de fixtures para el dataset
   `Ofertas Publicas de Distribuicao` de CVM y separar ofertas de acciones de
   deuda, fondos y otros instrumentos.
2. `EU Prospectus Watch`: crear adaptador de fixtures del registro `Prospectus
   III` de ESMA, inicialmente filtrado a Alemania, Paises Bajos e Italia.
3. `Argentina EOD Review`: confirmar terminos de la API gratis `BYMA EOD`
   antes de incorporarla como laboratorio de precios.
4. `Mexico Permission Track`: solo reconsiderar BMV si entrega autorizacion
   escrita para extraer y publicar metadata derivada de ofertas.

## Fuentes Oficiales Revisadas

- Brasil CVM Portal Dados Abertos: <https://dados.cvm.gov.br/>
- Brasil CVM ofertas publicas: <https://dados.cvm.gov.br/dataset/?groups=ofertas-publicas>
- Brasil B3 Hub de dados publicos: <https://www.b3.com.br/pt_br/dados/hub-de-dados-publicos/>
- ESMA databases and registers: <https://www.esma.europa.eu/publications-and-data/databases-and-registers>
- ESMA A2A help / Prospectus III: <https://registers.esma.europa.eu/publication/helpApp>
- ESMA legal notice: <https://registers.esma.europa.eu/publication/legalNoticePage>
- Netherlands AFM approved prospectuses: <https://www.afm.nl/nl-nl/sector/registers/meldingenregisters/goedgekeurde-prospectussen>
- Germany BaFin prospectus database: <https://www.bafin.de/DE/PublikationenDaten/Datenbanken/Prospektdatenbanken/Wertpapiere/wertpapiere_node.html>
- Italy CONSOB national prospectuses: <https://www.consob.it/web/area-pubblica/prospetti1>
- India SEBI Public Issues: <https://www.sebi.gov.in/filings/public-issues.html>
- India NSE data policy: <https://www.nseindia.com/static/market-data/nse-data-policy>
- Mexico BMV ofertas publicas: <https://www.bmv.com.mx/es/listados-y-prospectos/ofertas-publicas>
- Mexico BMV aviso legal: <https://www.bmv.com.mx/es/aviso-legal>
- Argentina BYMA Market Data APIs: <https://www.byma.com.ar/en/products/data-products/market-data/apis>
- Argentina CNV AIF: <https://www.cnv.gov.ar/SitioWeb/Home/AIF>
- Switzerland SIX IPO information: <https://www.six-group.com/en/products-services/the-swiss-stock-exchange/listing/equities/ipo.html>
- Switzerland SIX market data services: <https://www.six-group.com/en/products-services/the-swiss-stock-exchange/market-data/data-services.html>
