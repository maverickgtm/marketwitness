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

## Salida `evaluations.csv`

Contiene tanto observaciones evaluadas como excluidas o pendientes. La columna
`status` tiene valores `evaluated`, `excluded` o `pending`; `reason` explica
cualquier fila no evaluada.

Los datasets reales nunca deben agregarse a Git dentro de `data/raw/` o
`data/private/`, carpetas deliberadamente ignoradas.
