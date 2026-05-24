# TargetAudit

Plataforma abierta para evaluar, con datos verificables, la precision historica y
la utilidad economica de los `price targets` publicados por analistas financieros
de acciones estadounidenses.

TargetAudit nace de una pregunta sencilla: si una firma publica un precio
objetivo para una accion, ?ese pronostico se cumplio y una estrategia basada en
el habria superado una alternativa pasiva?

## Estado Del Proyecto

`v0.1` es un motor de investigacion reproducible:

- Importa observaciones de targets desde CSV.
- Exige firma, ticker, fecha, target y fuente para evaluar una observacion.
- Evalua targets alcistas y bajistas con precios diarios ajustados.
- Calcula acierto, dias hasta target, error al vencimiento y retorno frente a
  un benchmark.
- Genera un ranking que muestra el numero de observaciones y aplica una muestra
  minima configurable.
- Incluye datos sinteticos y pruebas automatizadas; no distribuye datos
  comerciales.

Todavia no es un ranking de mercado listo para decisiones de inversion. Para
publicar resultados reales hacen falta observaciones historicas licenciadas o
documentadas una por una y precios ajustados cuya licencia permita su uso.

## Inicio Rapido

Requiere Python 3.11 o superior. No requiere instalar paquetes para ejecutar el
demo.

```bash
make test
make demo
```

El demo escribe:

```text
build/demo/evaluations.csv
build/demo/report.md
```

El primer adaptador de fuente publica obtiene el mapa de ticker/CIK de la SEC.
La SEC exige identificar el trafico automatizado con un contacto real:

```bash
PYTHONPATH=src python3 -m targetaudit sec-company-map \
  --user-agent "TargetAudit tu-email@example.com" \
  --output data/raw/sec-company-map.csv
```

Tambien puede ejecutarse directamente:

```bash
PYTHONPATH=src python3 -m targetaudit evaluate \
  --targets data/samples/targets.csv \
  --prices data/samples/prices.csv \
  --output build/demo/evaluations.csv \
  --report build/demo/report.md \
  --minimum-sample 1 \
  --as-of 2025-01-01
```

## Principios

- **Trazabilidad:** ninguna observacion sin fuente verificable entra al
  analisis.
- **Reproducibilidad:** metodologia versionada, datos de entrada conservados y
  resultados regenerables.
- **Sin promesas de inversion:** acertar targets no equivale a generar alpha.
- **Datos legales:** el codigo es abierto; los datasets se publican solo cuando
  su licencia lo permite.
- **Comparabilidad:** se mostraran muestra, sector, benchmark y limitaciones,
  no solo porcentajes llamativos.

## Estructura

```text
src/targetaudit/       Motor de validacion, evaluacion, ranking y CLI
tests/                  Pruebas unitarias
data/samples/           Dataset sintetico para demostrar el flujo
docs/                   Metodologia, fuentes, esquema y roadmap
.github/workflows/      Integracion continua
```

## Siguientes Versiones

- `v0.2`: conectores para precios publicos/freemium y cache local.
- `v0.3`: normalizacion de firmas, acciones corporativas e integrantes
  historicos del universo.
- `v0.4`: API con FastAPI y base DuckDB/PostgreSQL.
- `v0.5`: dashboard web, filtros por sector y paginas de firma/accion.
- `v1.0`: pipeline actualizado periodicamente con una fuente de targets cuya
  licencia permita el producto publico.

Consulta [la metodologia](docs/methodology.md),
[las fuentes evaluadas](docs/data-sources.md) y
[el roadmap](docs/roadmap.md) antes de utilizar datos reales.

## Aviso

TargetAudit es software de investigacion. No ofrece asesoramiento financiero ni
recomendaciones de compra o venta. Ver [DISCLAIMER.md](DISCLAIMER.md).

## Licencia

El codigo se publica bajo la licencia MIT. Los datos de terceros mantienen sus
propias licencias y no quedan cubiertos por la licencia del codigo.
