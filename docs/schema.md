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
| `provider_id` | Si para nuevas corridas gobernadas | Identificador estable que enlaza la observacion con `source_registry.csv`; entradas historicas sin este campo quedan visibles como `unlinked` |

## Manifiesto De Importacion Autorizada

`targets-import` recibe una exportacion original y un manifiesto JSON fuera de
Git para producir `targets.csv`. El demo contiene archivos sinteticos
publicables; una exportacion real debe vivir en `data/private/` o `data/raw/`.

| Campo JSON | Requerido | Descripcion |
|---|---:|---|
| `provider_id` | Si | Prefijo estable usado en `observation_id` y escrito como linaje de la fila normalizada |
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

## `historical_universe.csv`

Registro de pertenencia al universo en la fecha historica de cada target. Una
ejecucion publica del scorecard debe suministrarlo mediante
`--universe-membership`; el demo contiene una muestra sintetica.

| Columna | Requerida | Descripcion |
|---|---:|---|
| `universe_id` | Si | Identificador unico del universo evaluado en el archivo |
| `ticker` | Si | Simbolo vigente durante la ventana de membresia |
| `company_name` | Si | Emisor identificado |
| `sector` | Si | Sector usado para segmentar durante esa ventana |
| `member_from` | Si | Inicio inclusivo de membresia, fecha ISO |
| `member_to` | No | Fin inclusivo; vacio si continuaba vigente |
| `source_provider` | Si | Fuente de la composicion historica |
| `source_url` | Si | Evidencia HTTPS revisable |
| `verified_on` | Si | Fecha en que se verifico la evidencia |

El cargador rechaza universos mezclados en un mismo archivo, ventanas
solapadas para el mismo ticker y fuentes sin URL HTTPS. `verified_on` registra
cuando se recopilo la evidencia: puede ser posterior al horizonte analizado en
una reconstruccion historica. Si se suministra el registro, una observacion no
incluida en su fecha de publicacion sale del scoring con
`outside_historical_universe`.

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
cualquier fila no evaluada. Cuando se aplica un universo historico, las filas
incluidas conservan `historical_universe_id` y
`historical_universe_source_url` para auditar su membresia. Cuando una firma
publica un target posterior para el mismo ticker antes del vencimiento, la
fila anterior queda excluida como `superseded_by_later_target` y conserva
`superseded_by_observation_id` y `superseded_on`.

Las filas evaluadas tambien contienen la simulacion operativa:

| Columna | Descripcion |
|---|---|
| `strategy_exit_reason` | `target_hit_limit` si sale al target o `horizon_close` al vencer |
| `strategy_exit_date` | Fecha de salida simulada |
| `strategy_exit_price` | Target ejecutado o cierre ajustado terminal |
| `strategy_gross_return_pct` | Retorno direccional antes de costos |
| `transaction_cost_bps_per_side` | Costo aplicado por cada lado |
| `strategy_net_return_pct` | Retorno neto despues de entrada y salida |
| `benchmark_strategy_net_return_pct` | Retorno neto del benchmark en la misma fecha de salida |
| `strategy_net_excess_return_pct` | Diferencia neta contra benchmark cuando puede alinearse |

El reporte agregado presenta el conteo de salidas con benchmark alineado para
que una media neta no oculte observaciones sin barra comparable en la fecha
de salida.

Los datasets reales nunca deben agregarse a Git dentro de `data/raw/` o
`data/private/`, carpetas deliberadamente ignoradas.

## Almacen Analitico DuckDB

`evaluate --database` conserva una corrida reproducible en una base DuckDB
local. La dependencia es opcional porque la generacion CSV/Markdown sigue
funcionando sin instalar paquetes externos:

```bash
python3 -m pip install -e ".[warehouse]"
```

| Tabla | Proposito |
|---|---|
| `evaluation_runs` | Parametros, fecha de corte, version metodologica, huella de entradas y conteos por estado de cada corrida |
| `run_assets` | Ruta, tamano, hash SHA-256 y `provider_id` declarado de cada entrada o artefacto producido |
| `evaluations` | Resultados tipados por fila, unidos a la corrida mediante `run_id` |

El `run_id` no puede sobreescribirse: una ejecucion corregida se registra como
una nueva corrida. El esquema usa tablas y tipos compatibles con una futura
migracion a PostgreSQL para la API publica; DuckDB es el almacen local de
analisis, no una autorizacion para publicar los datos guardados.
`evaluations.provider_id` conserva el enlace declarado por la observacion al
registro de fuentes; las bases creadas antes de este campo reciben una columna
vacia al volver a escribir y se presentan como linaje no enlazado.
`run_assets.provider_id` conserva la procedencia declarada de precios,
acciones corporativas y membresía histórica. Bases anteriores se leen con
procedencia vacía y no pueden superar una decisión de publicación hasta
generar una nueva corrida con activos trazables.

`evaluation_runs.methodology_version` sella las reglas aplicadas en la corrida
y `dataset_label` aporta una descripcion legible del conjunto evaluado.
`dataset_fingerprint` es un SHA-256 de un manifiesto ordenado compuesto por
rol, hash, tamano y `provider_id` de cada entrada (`targets`, `prices`,
universo y acciones cuando correspondan). Excluye artefactos derivados como
el CSV de evaluaciones y el reporte Markdown. Bases anteriores se leen con
esos sellos vacios y deben mostrarse como historicas sin versionar.

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

## `provider_approval_queue.csv`

Expediente de permisos de proveedores candidatos para el scorecard público.
No reemplaza `source_registry.csv`: un estado aprobado solo pasa la validación
si el registro de fuentes también permite salida pública.

| Columna | Requerida | Descripcion |
|---|---:|---|
| `provider_id` | Si | Identificador existente en `source_registry.csv` |
| `approval_status` | Si | `pending_terms_review`, `pending_license_quote`, `pending_written_permission`, `approved_public_output` o `rejected_public_output` |
| `priority` | Si | `critical`, `high` o `normal` |
| `requested_use` | Si | Uso preciso solicitado para el producto |
| `required_evidence` | Si | Documento o autorización todavía requerido |
| `promotion_criteria` | Si | Condición verificable para poder promover la fuente |
| `evidence_url` | Si | Página HTTPS oficial donde tramitar o verificar el permiso |
| `reviewed_on` | Si | Fecha ISO de la revisión |
| `review_note` | Si | Estado y siguiente acción del expediente |

## `provider_approval_decisions.csv`

Registro manual que transforma evidencia revisada en copias generadas de
`source_registry.csv` y `provider_approval_queue.csv`. El archivo base no se
modifica y cada aplicación escribe un reporte de resultados.

| Columna | Requerida | Descripcion |
|---|---:|---|
| `provider_id` | Si | Expediente existente en la cola de aprobaciones |
| `decision` | Si | `retain_pending`, `approve_public_output` o `reject_public_output` |
| `reviewed_on` | Si | Fecha ISO de la decisión |
| `evidence_url` | Si | Documento o página HTTPS revisada |
| `evidence_summary` | Si | Qué prueba o no prueba la evidencia |
| `new_integration_status` | Solo aprobación | `implemented` o `manual_verified`; nunca se infiere solo por tener licencia |
| `review_note` | Si | Decisión y alcance autorizado |

Una aprobación promueve el expediente a `approved_public_output` y genera una
fuente con `public_access_rules_documented` y
`source_link_and_derived_output`. Todavía debe pasar
`scorecard-readiness` y, para una corrida concreta, `scorecard-release`.

## `licensed_extensions.csv`

Catalogo informativo de opciones pagadas por el usuario para aportar targets
reales bajo su propia licencia. No es una tabla de ingestion ni constituye
aprobacion para publicar resultados.

| Columna | Requerida | Descripcion |
|---|---:|---|
| `extension_id` | Si | Identificador estable de opcion comercial |
| `extension_name`, `provider`, `data_class` | Si | Opcion y dato que podria aportar |
| `access_model` | Si | `paid_user_subscription`, `sales_contact_required` o `marketplace_subscription` |
| `price_display`, `price_basis` | Si | Precio encontrado o necesidad de cotizacion, con alcance verificable |
| `coverage` | Si | Cobertura historica declarada por la fuente oficial |
| `status` | Si | `available_byol` o `quote_required` |
| `allowed_mode` | Si | `individual_user_license` o `negotiated_license` |
| `public_output_status` | Si | Permiso pendiente o aprobado para resultados publicos |
| `official_url`, `pricing_url`, `terms_url` | Si | Evidencia HTTPS revisada |
| `reviewed_on`, `review_note` | Si | Fecha y conclusion de la revision |

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
| `market_code` | Si | Codigo unico: `LSE`, `HKEX`, `ASX`, `TSX`, `SGX`, `JPX`, `CVM`, `ESMA`, `KRX` |
| `market_name` | Si | Mercado o bolsa |
| `jurisdiction` | Si | Pais o jurisdiccion |
| `connector_status` | Si | `live_official_feed`, `verified_snapshot`, `priority_connector`, `planned_connector` o `restricted_research_only` |
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

## JPX New Listings HTML Feed

`jpx-monitor` parsea la tabla oficial de Tokyo Stock Exchange y produce:
`company_name`, `security_code`, `market_segment`, `approval_date`,
`listing_date`, `status`, `observed_on`, `source_url` y `outline_url`.

El estado es `approved_pending_listing` cuando JPX ya publico la aprobacion
pero la fecha de listing aun es futura, y `listed` cuando la fecha publicada
ya fue alcanzada. Este monitor confirma hitos JPX; no sustituye el futuro
collector de documentos de oferta `EDINET`.

## SGX IPO Prospectus JSON Feed

`sgx-monitor` consulta el API usado por la página oficial `IPO Prospectus` y
produce: `company_name`, `document_id`, `status`, `closing_date`,
`modified_date`, `prospectus_url`, `observed_on` y `source_url`.

El estado emitido es `prospectus_published`: prueba que SGX publicó un
documento de prospecto en su catálogo, pero no confirma por sí solo admisión,
inicio de negociación o una decisión de inversión.

## Global Listings Alerts

`global-alerts` normaliza los CSV actuales de `HKEX`, `LSE`, `ASX`, `TSX`,
`JPX` y `SGX`, los archiva bajo `history/YYYY-MM-DD/` cuando se usa
`--history-dir` y
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

## ETF Holdings Snapshots

`etf-holdings-activity` compara dos CSV normalizados del mismo fondo. Cada
snapshot contiene: `issuer`, `fund_symbol`, `fund_name`, `effective_date`,
`captured_on`, `position_ticker`, `position_name`, `shares`, `weight_pct`,
`source_frequency` y `source_url`.

`source_frequency` admite `synthetic_demo`, `daily_official`,
`official_snapshot` o `regulatory_periodic`. La fecha de captura no puede exceder el corte del
reporte, un snapshot no puede repetir ticker y la comparacion rechaza mezclar
capas de frecuencia distintas. `effective_date` puede ser posterior a
`captured_on` cuando la fuente declara esa convencion, como en el CSV ARK que
identifica holdings para el siguiente dia de negociacion.

El CSV de diferencias agrega: `previous_effective_date`,
`current_effective_date`, `previous_shares`, `current_shares`,
`shares_change`, `previous_weight_pct`, `current_weight_pct`,
`weight_change_pct` y `change_type`. Los tipos emitidos son `new_position`,
`increased`, `decreased`, `removed_position` y `weight_changed`; describen
cambios observados, no operaciones confirmadas.

## ARK Holdings Import

`ark-holdings-import` acepta el formato descargable de holdings ARK con los
campos `date`, `fund`, `company`, `ticker`, `cusip`, `shares` y `weight(%)`.
La salida es un snapshot normalizado de `ETF Holdings Snapshots`.

En una importacion oficial, `date` se conserva como `effective_date` y el
operador declara `captured_on`; el informe recuerda que ARK describe la fecha
del CSV como correspondiente al siguiente dia de negociacion. Un ticker vacio
se representa con su `CUSIP` para no perder una posicion identificable.

El indicador `--synthetic-fixture` esta reservado al demo versionado y evita
presentar fixtures de prueba como evidencia oficial diaria.

## State Street SPDR Holdings Import

`spdr-holdings-import` normaliza un CSV local con campos identificables como
`As Of`, `Fund Ticker`, `Name`, `Ticker`, `Shares Held` y `Weight`. La salida
es un snapshot normalizado que puede entrar a `etf-holdings-activity`.

El demo usa `XLF-DEMO` y `--synthetic-fixture`; nunca presenta esos registros
como holdings reales del fondo. Para evidencia oficial, la pagina `XLF`
declara descarga completa diaria, mientras la publicacion de sus datos queda
sujeta a revision y consentimiento aplicable.

## iShares IYF Holdings Import

`ishares-holdings-import` acepta un archivo de holdings descargado
manualmente de iShares. Busca una fila `Holdings as of` para establecer
`effective_date` y una tabla con `Ticker`, `Name`, `Asset Class`,
`Weight (%)` y `Shares` o `Quantity`.

La normalizacion inicial incluye solo filas de clase `Equity` o `Stock` y
cuenta filas omitidas, por ejemplo efectivo. El demo usa `IYF-DEMO` y
`--synthetic-fixture`. Para datos reales, el estado de gobernanza es
`manual_only`: los terminos BlackRock impiden recoleccion automatizada sin
permiso y la salida no debe redistribuir holdings oficiales. Los archivos
manuales reales se etiquetan `official_snapshot`, no `daily_official`, porque
la pagina confirma una fecha de holdings pero no se adopta como feed diario.
El importador rechaza una fecha efectiva posterior a `captured_on`.

## SEC N-PORT Import

`sec-nport-import` procesa XML publico `NPORT-P` o `NPORT-P/A`. Extrae
`regName`, `seriesName`, `seriesId`, `repPdEnd` y las inversiones
`invstOrSec` que expresan el balance en acciones (`NS`, `SH` o `SHARES`).

Para esas posiciones usa `ticker` cuando esta disponible y recurre a
`CUSIP:<id>` si no existe ticker. `balance` se normaliza como `shares` y
`pctVal` como `weight_pct`; la frecuencia de salida siempre es
`regulatory_periodic`, incluso para fixtures de prueba.

El reporte del importador cuenta inversiones totales y posiciones omitidas
por no estar expresadas en acciones. La omision evita presentar efectivo,
bonos o derivados como si fueran acciones comparables en el dashboard.

`sec-nport-collect` consulta los filings recientes del registrante mediante
el endpoint SEC submissions por `CIK`. Filtra formularios `NPORT-P` y
`NPORT-P/A`, construye el enlace del documento primario usando
`accessionNumber` y descarga candidatos en orden descendente de fecha.
Cuando submissions publica una ruta de visualizacion
`xslFormNPORT-P_X01/primary_doc.xml`, el colector recupera el XML crudo
`primary_doc.xml` del mismo accession en vez del HTML renderizado.
Un XML solo se archiva y normaliza cuando su campo `seriesId` coincide con
la serie solicitada. El reporte agrega `CIK`, accession, fecha de filing y
ruta del XML archivado.

## SEC N-PORT Quarterly Backfill

`sec-nport-datasets` analiza el catalogo HTML oficial y emite
`quarter,download_url`. Cuando se solicita `--download-quarter`, descarga el
ZIP publicado a almacenamiento local y extrae con nombres canonicos solo
`SUBMISSION.tsv`, `REGISTRANT.tsv`, `FUND_REPORTED_INFO.tsv`,
`FUND_REPORTED_HOLDING.tsv` e `IDENTIFIERS.tsv`. Rechaza rutas de archivo
inseguras y no reemplaza descargas existentes sin `--force`.

`sec-nport-sync` conserva un estado CSV con `quarter`, `download_url`,
`first_seen_on`, `last_seen_on`, `status`, `archive_path` y `extracted_dir`.
La inicializacion marca releases previas como `baseline_not_downloaded`;
releases observadas posteriormente pasan a `downloaded_new_release` tras una
descarga y extraccion validas. Un ZIP ya presente se marca `available_local`.
El estado se escribe atomicamente y solo sus directorios extraidos completos
pueden alimentar la regeneracion opcional del backfill.

`sec-nport-backfill` procesa directorios extraidos de los ZIP trimestrales
publicados por SEC. Consume cinco tablas tabuladas oficiales:
`SUBMISSION.tsv`, `REGISTRANT.tsv`, `FUND_REPORTED_INFO.tsv`,
`FUND_REPORTED_HOLDING.tsv` e `IDENTIFIERS.tsv`.

El acceso a un periodo se identifica por `ACCESSION_NUMBER`;
`FUND_REPORTED_HOLDING` se une a `IDENTIFIERS` por `HOLDING_ID` dentro de
cada directorio trimestral. `REPORT_DATE` se conserva como `effective_date`,
`UNIT` limita la normalizacion inicial a acciones, `BALANCE` se convierte en
`shares` y `PERCENTAGE` en `weight_pct`.

La salida incluye un CSV de holdings por periodo y un manifiesto con dataset,
serie, accession, filing date, report date, posiciones incluidas y omitidas.
Multiples `--dataset-dir` forman una serie historica, pero el comando rechaza
fechas efectivas duplicadas para exigir revision explicita de enmiendas.
