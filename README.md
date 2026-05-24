# TargetAudit

**Auditable market intelligence: analyst targets and upcoming public listings.**

Plataforma abierta para evaluar, con datos verificables, la precision historica y
la utilidad economica de los `price targets` publicados por analistas financieros
en bancos y companias financieras cotizadas en Estados Unidos.

TargetAudit nace de una pregunta sencilla: si una firma publica un precio
objetivo para una accion, ?ese pronostico se cumplio y una estrategia basada en
el habria superado una alternativa pasiva?

## Especializacion Inicial

La primera linea de investigacion es `U.S. Financials`, con atencion especial a
bancos. La eleccion es deliberada:

- El experimento que origino el proyecto encontro a KBW, firma especializada en
  financial services, entre sus mejores resultados aparentes.
- Permite probar una hipotesis mas interesante que un ranking general: si los
  especialistas de un sector anticipan mejor sus acciones que firmas
  generalistas.
- Existe un benchmark sectorial observable, empezando por `XLF` para
  financials.
- Un universo acotado facilita auditar fuentes, acciones corporativas y calidad
  de cada observacion antes de escalar.

TargetAudit no intentara competir inicialmente como una pagina de targets
actuales. Su propuesta es mostrar el historial verificable, los fallos y la
utilidad relativa al sector de cada pronostico.

## IPO Watch

El segundo modulo sigue cotizaciones tecnológicas y estrategicas de alto
interes. Su pagina futura del dashboard mostrara:

- Estado confirmado: candidata, filing publico, listada o retirada.
- Fuente primaria y fecha de verificacion.
- Eventos siguientes: enmiendas SEC, pricing, ticker y primer dia de mercado.
- Riesgos publicados y tareas de investigacion.

Al `2026-05-24`, la muestra incluida refleja dos hechos confirmados: SpaceX
presento un `S-1` publico ante la SEC el `2026-05-20`, y Cerebras Systems ya
comenzo a cotizar como `CBRS` en Nasdaq el `2026-05-14`. Anthropic, OpenAI,
Canva, Kraken y Shein aparecen como candidatas para monitorear, no como IPOs
confirmadas por el proyecto.

IPO Watch no genera recomendaciones automaticas de compra, venta ni tamanos
de posicion.

### Descubrimiento Universal De IPOs

Para no depender solo de una lista manual, TargetAudit incluye una cola de
descubrimiento basada en los indices diarios publicos de SEC EDGAR. Busca
formularios como `S-1`, `F-1`, `424B4` y `RW` de cualquier emisor:

```bash
export TARGETAUDIT_SEC_USER_AGENT="TargetAudit tu-correo@ejemplo.com"
PYTHONPATH=src python3 -m targetaudit sec-ipo-discover \
  --date 2026-05-20 \
  --output build/live/sec-ipo-discovery.csv \
  --report build/live/sec-ipo-discovery.md
```

La cola detecta candidatos para revision; no clasifica automaticamente todo
`S-1` como IPO, porque algunos registros corresponden a otras ofertas.

## Global Listings Watch

Una tercera pagina separa los mercados internacionales de la cola SEC de
Estados Unidos. Su primer mapa de fuentes cubre:

- `LSE` / Reino Unido: feed JSON oficial de `New issues` y contraste futuro con prospectos FCA NSM.
- `HKEX` / Hong Kong: documentos de nuevas solicitudes y `PHIP`.
- `ASX` / Australia: pagina oficial de upcoming floats and listings.
- `TSX` / Canada: nuevas companias listadas oficialmente.
- `SGX` / Singapur: catalogo oficial de prospectos IPO.

Hong Kong ya incluye un conector a los JSON oficiales de HKEXnews para
solicitudes activas, activas con `PHIP`, inactivas, listadas y devueltas.
Londres ya lee el componente JSON oficial de `Upcoming issues`; la
confirmacion avanzada mediante prospectos o documentos FCA NSM se mantiene
como siguiente control documental.

Para leer HKEX en vivo:

```bash
PYTHONPATH=src python3 -m targetaudit hkex-monitor \
  --output data/raw/hkex-monitor.csv \
  --report build/live/hkex-monitor.md \
  --html build/live/hkex-monitor.html
```

Para leer LSE en vivo:

```bash
PYTHONPATH=src python3 -m targetaudit lse-upcoming \
  --report build/live/lse-upcoming.md \
  --html build/live/lse-upcoming.html
```

## Estado Del Proyecto

`v0.1` es un motor de investigacion reproducible:

- Importa observaciones de targets desde CSV.
- Exige firma, ticker, fecha, target y fuente para evaluar una observacion.
- Evalua targets alcistas y bajistas con precios diarios ajustados.
- Calcula acierto, dias hasta target, error al vencimiento y retorno frente a
  un benchmark.
- Desglosa resultados entre targets alcistas y bajistas.
- Genera un ranking que muestra el numero de observaciones y aplica una muestra
  minima configurable.
- Incluye datos sinteticos y pruebas automatizadas; no distribuye datos
  comerciales.
- Genera un reporte inicial de `IPO Watch` con estado y fuentes auditables.

Todavia no es un ranking de mercado listo para decisiones de inversion. Para
publicar resultados reales hacen falta observaciones historicas licenciadas o
documentadas una por una y precios ajustados cuya licencia permita su uso.

## Inicio Rapido

Requiere Python 3.9 o superior. No requiere instalar paquetes para ejecutar el
demo.

```bash
make verify
```

La verificacion ejecuta pruebas, construye el demo y genera un paquete
instalable. Escribe:

```text
build/demo/evaluations.csv
build/demo/report.md
build/demo/ipo-watch.md
build/demo/ipo-watch.html
build/demo/sec-ipo-discovery.csv
build/demo/sec-ipo-discovery.md
build/demo/global-listings.md
build/demo/global-listings.html
build/demo/lse-upcoming.md
build/demo/lse-upcoming.html
build/demo/hkex-monitor.csv
build/demo/hkex-monitor.md
build/demo/hkex-monitor.html
build/dist/targetaudit-0.1.0-py3-none-any.whl
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
docs/                   Metodologia, estrategia, dashboard, fuentes y roadmap
.github/workflows/      Integracion continua
```

## Siguientes Versiones

- `v0.2`: conectores para precios publicos/freemium y cache local.
- `v0.2`: monitor SEC/news para hitos verificables de IPO Watch.
- `v0.3`: normalizacion de firmas, acciones corporativas e integrantes
  historicos del universo.
- `v0.4`: API con FastAPI y base DuckDB/PostgreSQL.
- `v0.5`: dashboard web, filtros por sector y paginas de firma/accion.
- `v1.0`: pipeline actualizado periodicamente con una fuente de targets cuya
  licencia permita el producto publico.

Consulta [la metodologia](docs/methodology.md),
[las fuentes evaluadas](docs/data-sources.md) y
[la estrategia de producto](docs/product-strategy.md). El progreso tecnico se
mantiene en [el roadmap](docs/roadmap.md) y la ejecucion continua en
[operations.md](docs/operations.md).

## Aviso

TargetAudit es software de investigacion. No ofrece asesoramiento financiero ni
recomendaciones de compra o venta. Ver [DISCLAIMER.md](DISCLAIMER.md).

## Licencia

El codigo se publica bajo la licencia MIT. Los datos de terceros mantienen sus
propias licencias y no quedan cubiertos por la licencia del codigo.
