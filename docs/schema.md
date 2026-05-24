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

## Salida `evaluations.csv`

Contiene tanto observaciones evaluadas como excluidas o pendientes. Incluye
`reference_date` y `reference_price`, usados para definir la direccion
original del target sin reinterpretarla despues del movimiento inicial. La columna
`status` tiene valores `evaluated`, `excluded` o `pending`; `reason` explica
cualquier fila no evaluada.

Los datasets reales nunca deben agregarse a Git dentro de `data/raw/` o
`data/private/`, carpetas deliberadamente ignoradas.

## `ipo_watch.csv`

Registro auditable para la pagina `IPO Watch`. A diferencia de los targets, no
produce un score ni una recomendacion operativa.

| Columna | Requerida | Descripcion |
|---|---:|---|
| `company_name` | Si | Empresa monitoreada |
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
`disclosure_id` y `download_link`.

El resultado asigna uno de dos estados:

- `document_found_review_required`: existe al menos un documento y se debe
  validar si constituye prospecto o evidencia de admisión.
- `no_document_found`: no apareció un documento en la consulta actual; no
  significa cancelación ni imposibilidad de cotizar.

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
