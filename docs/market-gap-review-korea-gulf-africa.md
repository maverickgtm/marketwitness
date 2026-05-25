# Market Gap Review: Corea, Golfo Y Africa

Revision: `2026-05-25`.

Esta revision comprueba si quedaban centros bursatiles importantes sin
evaluar antes de pasar de investigacion a construccion de collectors. Se
examinaron Corea del Sur, Arabia Saudita, Emiratos Arabes Unidos y Sudafrica.

## Decision Ejecutiva

| Mercado | Hallazgo | Decision |
|---|---|---|
| Corea del Sur | `OpenDART` ofrece Open API para disclosures originales XML y búsqueda de emisiones `C001`/`C006`; `KRX OPEN API` limita sus resultados a uso no comercial y prohíbe entregar datos a terceros | `Korea Offering Watch` implementado con OpenDART; KRX excluido del output público |
| Arabia Saudita | Saudi Exchange/CMA publican informacion de IPO y prospectos visibles | No se confirmo API gratuita ni permiso de republicacion automatizada; mantener en observacion |
| Emiratos Arabes Unidos | DFM/ADX/SCA muestran IPOs, listings y divulgaciones | No se confirmo feed programatico reutilizable gratuito; mantener en observacion |
| Sudafrica | JSE `SENS` es servicio regulatorio, pero la documentacion revisada lo presenta mediante productos de informacion/suscriptores | No activar conector gratuito sin licencia clara |

## Corea Del Sur

Corea es el unico nuevo mercado que amerita incorporacion inmediata al mapa
de expansion. La Financial Supervisory Service opera `DART/OpenDART`, cuyo
sitio oficial indica que cualquier persona, empresa o institucion puede usar
la informacion mediante la Open API. La documentación oficial indica:

- descarga de reportes originales en XML para extraer y usar la informacion;
- datos de securities registration statements disponibles directamente;
- busqueda publica de offering disclosures, incluyendo valores de equity,
  fecha de suscripcion y fecha de filing.

Para confirmar mercado y aportar contexto posterior, `KRX OPEN API` declara
que su servicio permite desarrollar aplicaciones y servicios con datos del
Korea Exchange. Sin embargo, sus términos en inglés, revisados el
`2026-05-25`, limitan el uso a fines no comerciales, prohíben cobrar por los
resultados y prohíben proporcionar los datos KRX a terceros. Por ello no se
integra al output público de Open Edition.

Flujo previsto:

1. `OpenDART`: monitor implementado que detecta `C001` (registro de valores
   de capital) y `C006` (pequeña oferta pública de capital) con clave gratuita.
2. `KRX`: conservar como referencia no conectada mientras sus restricciones
   de datos a terceros impidan mostrar resultados en el dashboard público.
3. Mantener ofertas, listado y rendimiento como estados separados.

## Mercados En Observacion

| Mercado | Por Que Es Importante | Bloqueo Actual |
|---|---|---|
| Arabia Saudita / Tadawul | Mercado activo de IPOs regionales y privatizaciones | Se localizaron paginas oficiales, no una API gratuita reutilizable comprobada |
| Dubai / Abu Dhabi | DFM declara ser un destino regional central para IPO y dual listings | Paginas y divulgaciones visibles, sin permiso/API de ingesta publica confirmado |
| Sudafrica / JSE | Principal bolsa africana; `SENS` concentra anuncios regulatorios | El acceso programatico revisado aparece como producto para information subscribers |

Estas regiones merecen otra revision cuando encontremos portales open-data o
términos de API concretos. No deben retrasar collectors ya defendibles de
Japón, Brasil, Europa y Corea.

## Prioridad De Construccion Actualizada

1. `Japan IPO Filing Watch`: `EDINET` mas confirmacion `JPX New Listings`.
2. `Korea Offering Watch`: implementado sobre `OpenDART`; `KRX` excluido
   del output público salvo términos distintos o permiso escrito.
3. `Brazil Offering Watch`: implementado con `CVM Dados Abertos`.
4. `EU Prospectus Watch`: implementado con `ESMA Prospectus III Securities`
   filtrado a `SHRS`.

## Fuentes Oficiales Revisadas

- OpenDART English Open API: <https://engopendart.fss.or.kr/intro/main.do>
- DART Public Offering Information: <https://englishdart.fss.or.kr/dsbc006/main.do>
- KRX OPEN API introduction: <https://openapi.krx.co.kr/contents/OPP/INFO/OPPINFO001.jsp>
- KRX OPEN API services: <https://openapi.krx.co.kr/contents/OPP/INFO/service/OPPINFO004.cmd>
- KRX OPEN API English terms: <https://openapi.krx.co.kr/contents/OPP/INFO/OPPINFO005.jsp>
- Saudi Exchange IPO listings: <https://www.saudiexchange.sa/>
- Dubai Financial Market IPO listings: <https://www.dfm.ae/en/raise-capital/ipo-listings/overview>
- UAE Securities and Commodities Authority open data: <https://www.sca.gov.ae/en/open-data.aspx>
- JSE SENS Project: <https://clientportal.jse.co.za/technical-library/sens-project>
