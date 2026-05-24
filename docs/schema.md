# Esquema De Datos v0.1

## `targets.csv`

Una fila por price target publicado.

| Columna | Requerida | Descripcion |
|---|---:|---|
| `observation_id` | Si | Identificador unico estable |
| `ticker` | Si | Simbolo al momento del evento |
| `company_name` | Si | Nombre de la compania |
| `sector` | No | Sector para analisis futuro |
| `firm` | Si | Firma que publica el target |
| `analyst` | No | Nombre del analista cuando exista |
| `published_date` | Si | Fecha ISO `YYYY-MM-DD` |
| `price_target` | Si | Precio objetivo positivo |
| `rating` | No | Lenguaje original: Buy, Neutral, etc. |
| `horizon_days` | No | Horizonte; por defecto `365` |
| `benchmark_symbol` | No | Benchmark, por defecto `SPY` recomendado |
| `source_provider` | Si | Proveedor o fuente primaria |
| `source_url` | Si | Referencia verificable |

## Manifiesto De Importacion Autorizada

`targets-import` recibe una exportacion original y un manifiesto JSON fuera de
Git para producir `targets.csv`. El demo contiene archivos sinteticos
publicables; una exportacion real debe vivir en `data/private/` o `data/raw/`.

| Campo JSON | Requerido | Descripcion |
|---|---:|---|
| `provider_id` | Si | Prefijo estable usado en `observation_id` |
| `provider_name` | Si | Nombre legible del proveedor/exportacion |
| `source_provider` | Si | Valor escrito en las filas normalizadas |
| `exported_on` | Si | Fecha ISO de la exportacion |
| `obtained_via` | Si | Mecanismo autorizado de entrega |
| `license_reference` | Si | URL HTTPS de contrato, terminos o registro de autorizacion |
| `authorized_for_internal_research` | Si | Debe ser `true` para permitir importar |
| `authorized_for_public_output` | Si | Declaracion visible; no sustituye revision legal |
| `field_map` | Si | Mapeo de columnas externas a campos canonicos |
| `defaults` | Si | Sector, benchmark u horizonte si no vienen por fila |

El CSV de auditoria registra `export_record_id`, `observation_id`, `ticker`,
`firm`, `status`, `reason` y `source_url`. Una fila rechazada nunca se escribe
al archivo normalizado ni llega al scoring.

## `prices.csv`

Una fila por instrumento y dia. Debe contener barras ajustadas con la misma
convencion para todos los campos.

| Columna | Requerida | Descripcion |
|---|---:|---|
| `ticker` | Si | Simbolo compatible con `targets.csv` o benchmark |
| `date` | Si | Fecha ISO `YYYY-MM-DD` |
| `adjusted_high` | Si | Maximo diario ajustado |
| `adjusted_low` | Si | Minimo diario ajustado |
| `adjusted_close` | Si | Cierre diario ajustado |
| `source_provider` | Si | Fuente de precios |

Las barras con `NaN`, infinito, fechas duplicadas para el mismo ticker o
cierres fuera del rango `low`/`high` son rechazadas para impedir que datos
corruptos alteren el ranking.

`alpha-vantage-prices` genera este esquema desde la respuesta
`TIME_SERIES_DAILY_ADJUSTED`. Como el proveedor entrega maximos y minimos
operados junto con un cierre ajustado, normaliza por fila:
`adjusted_high = high * adjusted_close / close` y
`adjusted_low = low * adjusted_close / close`. Las respuestas en vivo se
cachean bajo `data/raw/`, fuera de Git.

## `corporate_actions.csv`

Registro de splits y cambios de ticker revisados contra evidencia. La muestra
del demo es sintética; los datos reales requieren fuente oficial o filing.

| Columna | Requerida | Descripcion |
|---|---:|---|
| `action_id` | Si | Identificador estable de la accion |
| `company_name` | Si | Nombre del emisor |
| `prior_ticker` | Si | Simbolo anterior o afectado |
| `current_ticker` | Si | Simbolo posterior; igual al anterior si solo hay split |
| `action_type` | Si | `stock_split`, `reverse_split` o `ticker_change` |
| `effective_date` | Si | Fecha efectiva ISO |
| `split_ratio_new` | Para splits | Numerador de la razon de acciones |
| `split_ratio_old` | Para splits | Denominador de la razon de acciones |
| `evidence_level` | Si | `exchange_notice`, `issuer_official_release`, `regulatory_filing` o `synthetic_demo` |
| `source_title` | Si | Titulo de la evidencia |
| `source_url` | Si | URL HTTPS revisable |
| `verified_on` | Si | Fecha de revision de evidencia |
| `review_note` | Si | Trabajo de comparabilidad requerido |

`corporate-actions-check` produce una cola CSV de observaciones cuyo horizonte
cruza una acción. Si el mismo registro se entrega a `evaluate`, dichas
observaciones se excluyen con `corporate_action_review_required`; la versión
actual no reescala automáticamente targets ni une series de tickers.

## Salida `evaluations.csv`

Contiene tanto observaciones evaluadas como excluidas o pendientes. Incluye
`reference_date` y `reference_price`, usados para definir la direccion
original del target sin reinterpretarla despues del movimiento inicial. La columna
`status` tiene valores `evaluated`, `excluded` o `pending`; `reason` explica
cualquier fila no evaluada.

Los datasets reales nunca deben agregarse a Git dentro de `data/raw/` o
`data/private/`, carpetas deliberadamente ignoradas.

## `source_registry.csv`

Registro transversal de fuentes consideradas por TargetAudit y su control de
uso antes de publicar un producto con datos reales.

| Columna | Requerida | Descripcion |
|---|---:|---|
| `provider_id` | Si | Identificador estable de proveedor o fuente |
| `provider_name` | Si | Nombre presentado en la auditoria |
| `data_class` | Si | Targets, precios, listings, documentos o acciones corporativas |
| `access_model` | Si | `public_endpoint`, `public_web_page`, `public_filing`, `official_release`, `commercial_api_candidate`, `freemium_api`, `manual_reference` o `synthetic_demo` |
| `integration_status` | Si | `implemented`, `manual_verified`, `candidate` o `excluded` |
| `license_status` | Si | `public_access_rules_documented`, `terms_review_required`, `restricted_no_collection` o `project_owned_synthetic` |
| `publication_policy` | Si | Regla aplicable al output público antes de distribuir datos |
| `official_url` | Si | Pagina oficial de la fuente |
| `reference_url` | Si | Política o referencia oficial revisada; puede ser la página fuente si la revisión legal queda pendiente |
| `reviewed_on` | Si | Fecha ISO del inventario |
| `review_note` | Si | Alcance y próximo control requerido |

La vista deriva estados operativos: `usable_with_policy`, `review_required`,
`license_required` o `blocked`. Un conector puede estar técnicamente
implementado y aun así requerir revisión antes de usarse en un dashboard
público con datos reales.

## `ipo_watch.csv`

Registro auditable para la pagina `IPO Watch`. A diferencia de los targets, no
produce un score ni una recomendacion operativa.

| Columna | Requerida | Descripcion |
|---|---:|---|
| `company_name` | Si | Empresa monitoreada |
| `cik` | No | Identificador SEC normalizado a 10 digitos para enlazar filings EDGAR |
| `theme` | Si | Vertical: Space/AI, AI hardware, software, crypto, retail |
| `status` | Si | `candidate_unverified`, `filed_public`, `listed` o `withdrawn` |
| `status_date` | Si | Fecha ISO del estado verificado o alta de candidata |
| `ticker` | Para `listed` | Simbolo confirmado |
| `exchange` | Para `listed` | Mercado confirmado |
| `filing_type` | No | Por ejemplo `S-1`, `424B4` o `IPO` |
| `evidence_level` | Si | Tipo de evidencia usada |
| `source_title` | Si | Titulo legible de la fuente |
| `source_url` | Si | Fuente o pagina oficial que debe revisarse |
| `next_event` | Si | Proximo hito que el monitor debe buscar |
| `risk_flags` | Si | Temas para due diligence, no consejo de inversion |

Una candidata no se eleva a `filed_public` por rumores o por una fecha
estimada en prensa: exige un filing publico o confirmacion primaria.

## SEC IPO Alerts

`sec-ipo-alerts` consume el CSV de `sec-ipo-discover`, conserva snapshots
fechados y enlaza un filing a `IPO Watch` solo cuando coincide un `CIK`
registrado. Produce: `company_name`, `cik`, `form`, `filed_date`,
`review_state`, `alert_type`, `watch_company`, `watch_status`,
`triage_category`, `triage_basis`, `review_priority`, `source_url` y
`review_action`.

Los tipos de alerta son:

- `new_filing_review`: filing SEC nuevo sin vínculo ya registrado.
- `watchlist_filing_review`: filing SEC nuevo cuyo `CIK` corresponde a una
  empresa seguida en `IPO Watch`.

Un vínculo por `CIK` sirve para enrutar la revisión y no cambia el estado
público del emisor sin inspeccionar la evidencia primaria.

El triage prioriza evidencia sin afirmar la naturaleza de la oferta:

- `watchlist_match`: coincidencia exacta de CIK; prioridad alta.
- `withdrawal_form_review`: el filing es `RW`; prioridad alta.
- `possible_spac_name_signal`: el nombre contiene `Acquisition Corp` o
  `Acquisition Co`; requiere confirmar estructura blank-check.
- `fund_or_etf_name_signal`: el nombre contiene `ETF`; requiere separar
  registro de fondo de una IPO operativa.
- `final_prospectus_review`: el filing es `424B4`.
- `issuer_filing_review`: no se asigna categoría por nombre; debe leerse.

## IPO Watch Manual SEC Reviews

`ipo-watch-review` recibe `sec-alerts.csv`, el registro anterior y un CSV de
decisiones humanas. Valida que `source_url` y `cik` coincidan exactamente con
una alerta antes de escribir una nueva copia de `ipo_watch.csv`.

El CSV de decisiones contiene: `source_url`, `cik`, `decision`,
`display_name`, `theme`, `reviewed_on`, `evidence_level`, `source_title`,
`next_event`, `risk_flags` y `review_note`.

`decision` admite:

- `confirm_filed_public`: promueve o confirma `filed_public` solo para un
  formulario de registro o prospecto final revisado.
- `confirm_withdrawn`: promueve o confirma `withdrawn` solo con formulario
  `RW` revisado.
- `retain_for_review`: conserva el caso sin cambio de estado.
- `reject_not_ipo`: registra que el filing no debe promoverse.

La salida de auditoria contiene `company_name`, `cik`, `decision`, `result`,
`prior_status`, `current_status`, `reviewed_on`, `source_url` y
`review_note`. Un filing descubierto o categorizado nunca modifica el tablero
sin este registro manual. La fecha `reviewed_on` no puede preceder la fecha
del filing SEC ni superar la fecha del reporte.

## `global_market_sources.csv`

Registro de fuentes oficiales y conectores internacionales para la pagina
`Global Listings Watch`. Describe cobertura, no eventos de empresas.

| Columna | Requerida | Descripcion |
|---|---:|---|
| `market_code` | Si | Codigo unico: `LSE`, `HKEX`, `ASX`, `TSX`, `SGX` |
| `market_name` | Si | Mercado o bolsa |
| `jurisdiction` | Si | Pais o jurisdiccion |
| `connector_status` | Si | `live_official_feed`, `verified_snapshot`, `priority_connector` o `planned_connector` |
| `official_source_name` | Si | Nombre de fuente primaria |
| `official_source_url` | Si | URL de consulta |
| `signal_type` | Si | Tipo de senal documental/listing disponible |
| `confirmation_rule` | Si | Regla necesaria antes de confirmar estado |
| `implementation_next` | Si | Trabajo requerido para activar el monitor |

## `lse_upcoming_issues.csv`

Formato de fallback manual para la tabla oficial `Upcoming issues` de LSE.
La ejecucion en vivo usa el componente JSON oficial y normaliza estos mismos
campos.

| Columna | Requerida | Descripcion |
|---|---:|---|
| `company_name` | Si | Nombre mostrado por LSE |
| `market` | Si | Segmento, por ejemplo `AIM` |
| `primary_offer` | Si | Oferta primaria visible o `TBC` |
| `secondary_offer` | Si | Oferta secundaria visible o `-` |
| `currency` | Si | Moneda informada por la tabla |
| `price_range` | Si | Rango publicado o `-` |
| `expected_first_trading` | Si | Fecha esperada en el texto oficial |
| `instrument_type` | Si | Tipo de instrumento |
| `observed_on` | Si | Fecha de captura |
| `source_url` | Si | URL de la pagina oficial |

## LSE Page JSON Feed

`lse-upcoming` consulta de forma predeterminada la respuesta oficial de la
pagina LSE y extrae el componente `type=upcoming-issues`, cuyo bloque
`upcomingissues.Items` incluye nombre, mercado, ofertas, fecha esperada,
tipo y enlace de detalle del emisor.

## FCA NSM Search Response

`lse-fca-check` consulta el índice público `fca-nsm-searchdata` del National
Storage Mechanism por cada `company_name` observado en LSE. Normaliza:
`company`, `headline`, `type`, `submitted_date`, `publication_date`,
`disclosure_id` y `download_link`. Su CSV de salida agrega
`evidence_class`, `classification_basis`, datos del documento seleccionado y
la fuente NSM.

El estado de coincidencia sigue distinguiendo:

- `document_found_review_required`: existe al menos un documento y se debe
  validar si constituye prospecto o evidencia de admisión.
- `no_document_found`: no apareció un documento en la consulta actual; no
  significa cancelación ni imposibilidad de cotizar.

Además, la clase documental usa solamente el metadato `type` visible de FCA:

- `prospectus_document_signal`: el tipo contiene `Prospectus`.
- `admission_document_signal`: contiene `Admission Document`.
- `intention_to_float_notice`: contiene `Intention to Float`; no equivale a
  prospecto o admisión.
- `other_document_review`: hay documento, pero el metadato no identifica una
  de las clases anteriores.

Estas clases sirven para ordenar revisión documental; no confirman que la
admisión se completó ni que haya iniciado negociación. El titular no crea una
clase por sí solo para evitar interpretar, por ejemplo, `No Prospectus
Required` como señal de prospecto.

## HKEX JSON Feeds

`hkex-monitor` normaliza los JSON oficiales de HKEXnews en un CSV con:
`company_name`, `status`, `event_date`, `stock_code`, `has_phip` y
`source_url`. Los estados conservan la taxonomia HKEX y separan el feed de
avance documental: `active`, `active_phip`, `inactive`, `listed` y
`returned`.

## ASX Upcoming HTML Feed

`asx-monitor` parsea cada tabla publicada dentro de `Upcoming floats and
listings` y produce un CSV con: `company_name`, `status`, `listing_date`,
`issue_price`, `issue_type`, `security_code`, `capital_to_be_raised`,
`expected_offer_close_date`, `observed_on` y `source_url`.

Los estados son `anticipated` cuando ASX publica fecha prevista y `withdrawn`
cuando la propia página marca la solicitud como retirada.

## TSX New Company Listings HTML Feed

`tsx-monitor` parsea la tabla oficial de nuevas compañías listadas y produce:
`company_name`, `symbols`, `listing_date`, `status`, `observed_on`,
`source_url` y `detail_url`. El único estado emitido es `listed`, ya que
esta fuente documenta cotizaciones completadas y no solicitudes futuras.

## SGX IPO Prospectus JSON Feed

`sgx-monitor` consulta el API usado por la página oficial `IPO Prospectus` y
produce: `company_name`, `document_id`, `status`, `closing_date`,
`modified_date`, `prospectus_url`, `observed_on` y `source_url`.

El estado emitido es `prospectus_published`: prueba que SGX publicó un
documento de prospecto en su catálogo, pero no confirma por sí solo admisión,
inicio de negociación o una decisión de inversión.

## Global Listings Alerts

`global-alerts` normaliza los CSV actuales de `HKEX`, `LSE`, `ASX`, `TSX` y
`SGX`, los archiva bajo `history/YYYY-MM-DD/` cuando se usa `--history-dir` y
compara contra la última captura anterior. Produce un CSV con:
`market`, `change_type`, `company_name`, `previous_status`, `current_status`,
`previous_detail`, `current_detail`, `review_action` y `source_url`.

`change_type` admite:

- `new`: evidencia que no estaba en la captura anterior.
- `changed`: el mismo registro tiene estado o detalle documental modificado.
- `removed_from_feed_review`: ya no aparece en el feed actual y debe
  investigarse; no equivale automáticamente a retiro o listing.

En HKEX la identidad comparada es un hito de ciclo de vida
(`company + status + event_date + stock_code`), porque el feed puede conservar
al mismo emisor en etapas oficiales distintas.

## `issuer_listing_confirmations.csv`

Registro curado de hitos que un emisor declara en un comunicado oficial. No
acepta notas de prensa secundarias como confirmación automática.

| Columna | Requerida | Descripcion |
|---|---:|---|
| `company_name` | Si | Emisor confirmado |
| `market` | Si | Mercado que el comunicado identifica |
| `ticker` | Si | Simbolo identificado por el comunicado |
| `event_type` | Si | `trading_started`, `offering_closed` o `listing_confirmed` |
| `event_date` | Si | Fecha ISO del hito declarado |
| `source_title` | Si | Titulo del comunicado oficial |
| `source_url` | Si | URL HTTPS del emisor |
| `verified_on` | Si | Fecha ISO de revision de la evidencia |
| `evidence_level` | Si | Actualmente `issuer_official_release` |
| `research_note` | Si | Resumen verificable de lo que confirma la fuente |

Una misma fuente puede confirmar mas de un hito y por eso puede aparecer en
varias filas. No se permite que la fecha de verificacion preceda el evento ni
que un reporte incluya evidencia posterior a su fecha de corte.
