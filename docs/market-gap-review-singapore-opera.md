# Market Gap Review: Singapore MAS OPERA

Revision: `2026-05-25`.

## Decision

TargetAudit no implementara un collector automatico sobre `MAS OPERA` en la
edicion publica gratuita. `SGX IPO Prospectus` permanece como la ruta
automatizada de Singapur; `MAS OPERA` queda registrado como referencia manual
oficial y bloqueado para recoleccion.

## Evidencia Revisada

- `OPERA` es el repositorio oficial de prospectos y documentos de oferta de
  Monetary Authority of Singapore.
- La consulta publica `Public Offers` solicita un `Security Code`, por lo que
  no expone una ruta estable de ingestion automatica verificada.
- Los terminos `OPERA`, actualizados el `2026-04-18`, restringen robots u
  otras aplicaciones de retrieval sin permiso escrito, asi como caching y
  almacenamiento de contenido; tambien limitan enlaces directos a contenido.
- La Singapore Open Data Licence solo resuelve reutilizacion para datasets
  efectivamente cubiertos. No se identifico un dataset/API de prospectos
  `OPERA` publicado bajo esa licencia.

## Tratamiento En Producto

- No hacer scraping de `Public Offers`, no intentar sortear el codigo de
  seguridad y no archivar documentos `OPERA` en el dashboard publico.
- Mostrar `MAS OPERA Public Offers` en `Source Registry` como
  `restricted_no_collection` y `source_link_only`.
- Continuar el monitor `SGX IPO Prospectus` como senal documental:
  un prospecto publicado requiere revision y no confirma admission o trading.

## Fuentes Oficiales

- MAS OPERA: <https://eservices.mas.gov.sg/opera/Public/WelcomePage.aspx>
- MAS OPERA Public Offers: <https://eservices.mas.gov.sg/opera/PublicOffers.aspx>
- MAS OPERA Terms of Use: <https://eservices.mas.gov.sg/opera/MASUserTerms.aspx>
- Singapore Open Data Licence: <https://data.gov.sg/open-data-licence>
- SGX IPO Prospectus: <https://www.sgx.com/securities/ipo-prospectus>
