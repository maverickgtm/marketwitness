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

### Gobernanza De Fuentes

Antes de conectar datos reales, TargetAudit registra qué proveedores están
implementados, cuáles requieren revisar términos o licencia y qué política de
publicación corresponde a cada uno:

```bash
PYTHONPATH=src python3 -m targetaudit source-registry \
  --registry data/samples/source_registry.csv \
  --report build/live/source-registry.md \
  --html build/live/source-registry.html \
  --as-of YYYY-MM-DD
```

Una URL pública no equivale a permiso de redistribución. En la muestra inicial,
SEC/FCA se mantienen como evidencia pública con reglas documentadas; los
conectores de bolsas internacionales quedan pendientes de revisión de términos;
Benzinga y Nasdaq Daily List requieren resolver licencia antes de alimentar
resultados públicos; TipRanks no se adopta para recolección automatizada.

### Auditoria De Acciones Corporativas

Los splits y cambios de ticker pueden volver incomparable un target nominal
contra precios ajustados. TargetAudit incluye una cola de auditoria que
identifica targets cuyo horizonte atraviesa una accion corporativa documentada:

```bash
PYTHONPATH=src python3 -m targetaudit corporate-actions-check \
  --targets data/samples/targets.csv \
  --actions data/samples/corporate_actions.csv \
  --output build/live/corporate-actions.csv \
  --report build/live/corporate-actions.md \
  --html build/live/corporate-actions.html \
  --as-of YYYY-MM-DD
```

Al ejecutar `evaluate` con `--corporate-actions`, los casos afectados se
excluyen como `corporate_action_review_required`. El sistema no inventa un
target reajustado ni asume continuidad entre tickers: esas decisiones exigen
evidencia revisada. El demo usa eventos sintéticos exclusivamente para probar
este bloqueo.

### Evidencia De Precios Ajustados

TargetAudit incorpora un adaptador cache-first para `Alpha Vantage Daily
Adjusted`. El endpoint entrega `high` y `low` operados junto con
`adjusted close`; el adaptador deriva maximos y minimos ajustados usando el
factor diario `adjusted_close / raw_close`, necesario para auditar si un
target se alcanzo intradia.

```bash
export TARGETAUDIT_ALPHA_VANTAGE_API_KEY="tu-clave-privada"
PYTHONPATH=src python3 -m targetaudit alpha-vantage-prices \
  --ticker JPM \
  --output data/raw/prices/jpm.csv \
  --report build/live/jpm-prices.md \
  --html build/live/jpm-prices.html \
  --as-of YYYY-MM-DD
```

Las respuestas se almacenan por simbolo en `data/raw/prices/alpha-vantage/`;
un nuevo pedido solo ocurre con un simbolo sin cache o con `--refresh`. Al
`2026-05-24`, Alpha Vantage publica un limite estandar de 25 solicitudes por
dia y marca `TIME_SERIES_DAILY_ADJUSTED` como funcion premium. La integracion
queda disponible para evaluacion interna autorizada, no para alimentar aun un
ranking publico real.

### Importacion Autorizada De Targets

Los `price targets` reales no se obtendran mediante scraping. TargetAudit
incluye un importador para exportaciones suministradas con autorizacion o
licencia documentada. Un manifiesto JSON declara proveedor, mapeo de columnas,
referencia de licencia y alcance de uso; las filas incompletas se rechazan en
una auditoria separada antes de ejecutar el scorecard.

```bash
PYTHONPATH=src python3 -m targetaudit targets-import \
  --export data/private/targets/proveedor-export.csv \
  --manifest data/private/targets/proveedor-manifest.json \
  --output data/raw/targets/normalized-targets.csv \
  --audit build/live/targets-import-audit.csv \
  --report build/live/targets-import.md \
  --html build/live/targets-import.html \
  --as-of YYYY-MM-DD
```

El manifiesto habilita el procesamiento solo cuando declara permiso para
investigacion interna. Una declaracion no demuestra derechos de
redistribucion: la publicacion del dataset o del ranking real sigue requiriendo
revision contractual.

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

Para archivar cada cola SEC, evitar avisos duplicados y resaltar filings de
empresas ya seguidas por `IPO Watch` mediante `CIK`:

```bash
PYTHONPATH=src python3 -m targetaudit sec-ipo-alerts \
  --discovery data/raw/sec-ipo-discovery-YYYY-MM-DD.csv \
  --watchlist data/samples/ipo_watch.csv \
  --history-dir data/raw/sec/history \
  --output build/live/sec-alerts.csv \
  --report build/live/sec-alerts.md \
  --html build/live/sec-alerts.html \
  --as-of YYYY-MM-DD
```

Esta cola enruta evidencia para revisión; no promueve automáticamente el
estado de una empresa. También ordena casos mediante señales explícitas:
coincidencia exacta de `CIK`, nombres que contienen `Acquisition Corp/Co`,
nombres que contienen `ETF`, formularios `424B4` y solicitudes `RW`. Las
señales de nombre son heurísticas para revisión, no hechos confirmados.

Despues de leer un filing, una decision manual documentada puede producir una
copia revisada del tablero:

```bash
PYTHONPATH=src python3 -m targetaudit ipo-watch-review \
  --alerts build/live/sec-alerts.csv \
  --registry data/samples/ipo_watch.csv \
  --decisions data/private/sec-review-decisions.csv \
  --output-registry build/live/ipo-watch-reviewed.csv \
  --output build/live/sec-review-outcomes.csv \
  --report build/live/sec-review-outcomes.md \
  --html build/live/sec-review-outcomes.html \
  --as-of YYYY-MM-DD
```

El comando exige que el filing y el `CIK` coincidan con una alerta; una señal
automatica nunca actualiza por si sola `IPO Watch`.

## Global Listings Watch

Una tercera pagina separa los mercados internacionales de la cola SEC de
Estados Unidos. Su primer mapa de fuentes cubre:

- `LSE` / Reino Unido: feed JSON oficial de `New issues` y contraste documental con FCA NSM.
- `HKEX` / Hong Kong: documentos de nuevas solicitudes y `PHIP`.
- `ASX` / Australia: monitor HTML oficial de upcoming floats and listings.
- `TSX` / Canada: monitor HTML oficial de nuevas companias ya listadas.
- `SGX` / Singapur: catalogo oficial de prospectos IPO.

Hong Kong ya incluye un conector a los JSON oficiales de HKEXnews para
solicitudes activas, activas con `PHIP`, inactivas, listadas y devueltas.
Londres ya lee el componente JSON oficial de `Upcoming issues` y puede
cruzar cada emisor con documentos públicos del FCA NSM. Una coincidencia
queda para revisión: no se convierte automáticamente en admisión confirmada.
Australia ya lee la tabla oficial ASX de solicitudes formales y separa
listados anticipados de retiros publicados.
Canada ya lee `TSX New Company Listings` como comprobación de cotizaciones
completadas; no lo usa para predecir solicitudes futuras.
Singapur ya consulta el catálogo JSON oficial `SGX IPO Prospectus`; registra
documentos publicados para revisión y no confirma automáticamente una
cotización completada.

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
  --output data/raw/global/lse-upcoming.csv \
  --report build/live/lse-upcoming.md \
  --html build/live/lse-upcoming.html
```

Para contrastar las próximas emisiones LSE con FCA NSM:

```bash
PYTHONPATH=src python3 -m targetaudit lse-fca-check \
  --output data/raw/global/lse-fca-check.csv \
  --report build/live/lse-fca-check.md \
  --html build/live/lse-fca-check.html
```

El chequeo FCA clasifica el campo de tipo publicado para cada documento como señal de
`prospectus`, `admission document`, `intention to float` u otra revisión. Una
clasificación no confirma admisión completada ni inicio de negociación.

Para leer ASX en vivo:

```bash
PYTHONPATH=src python3 -m targetaudit asx-monitor \
  --output data/raw/global/asx-monitor.csv \
  --report build/live/asx-monitor.md \
  --html build/live/asx-monitor.html
```

Para leer confirmaciones TSX en vivo:

```bash
PYTHONPATH=src python3 -m targetaudit tsx-monitor \
  --output data/raw/global/tsx-monitor.csv \
  --report build/live/tsx-monitor.md \
  --html build/live/tsx-monitor.html
```

Para leer prospectos SGX en vivo:

```bash
PYTHONPATH=src python3 -m targetaudit sgx-monitor \
  --output data/raw/global/sgx-monitor.csv \
  --report build/live/sgx-monitor.md \
  --html build/live/sgx-monitor.html
```

Para generar confirmaciones de hitos a partir de comunicados oficiales del emisor revisados:

```bash
PYTHONPATH=src python3 -m targetaudit issuer-confirmations \
  --registry data/samples/issuer_listing_confirmations.csv \
  --report build/live/issuer-confirmations.md \
  --html build/live/issuer-confirmations.html \
  --as-of YYYY-MM-DD
```

La primera evidencia incluida es el comunicado oficial de Cerebras que declara
inicio de trading de `CBRS` el `2026-05-14` y cierre de su oferta el
`2026-05-15`. El registro confirma esos hitos solamente; no recomienda una
posición ni incorpora noticias no verificadas.

Para comparar la lectura global del dia contra la captura anterior y conservar
historial:

```bash
PYTHONPATH=src python3 -m targetaudit global-alerts \
  --hkex data/raw/global/hkex-monitor.csv \
  --lse data/raw/global/lse-upcoming.csv \
  --asx data/raw/global/asx-monitor.csv \
  --tsx data/raw/global/tsx-monitor.csv \
  --sgx data/raw/global/sgx-monitor.csv \
  --history-dir data/raw/global/history \
  --output build/live/global-alerts.csv \
  --report build/live/global-alerts.md \
  --html build/live/global-alerts.html
```

`global-alerts` clasifica diferencias como nuevas, modificadas o removidas
del feed para revisión. Una remoción no confirma retiro, admisión ni inicio de
negociación.

## ETF Holdings Activity En Cola

Queda planificada una pagina separada para observar cambios publicados en
holdings de ETF. La capa mas cercana al mercado usara archivos diarios
oficiales por emisor, inicialmente candidatos como ARK y State Street SPDR;
`SEC N-PORT` servira como respaldo regulatorio historico, no como fuente en
tiempo real. Un aumento o reduccion de holdings se mostrara como cambio
observado, no como compra o venta confirmada del gestor.

## Estado Del Proyecto

El repositorio contiene un motor de investigacion reproducible con adaptadores
auditados en desarrollo:

- Importa observaciones de targets desde CSV.
- Exige firma, ticker, fecha, target y fuente para evaluar una observacion.
- Evalua targets alcistas y bajistas con precios diarios ajustados.
- Calcula acierto, dias hasta target, error al vencimiento y retorno frente a
  un benchmark.
- Muestra intervalo Wilson 95% del hit rate para no ocultar incertidumbre de
  muestras pequenas.
- Compara firmas en rankings separados por sector y por direccion, aplicando
  el minimo muestral dentro de cada segmento.
- Filtra observaciones contra un universo historico opcional y usa el sector
  vigente en la fecha del target para evitar clasificacion retrospectiva.
- Desglosa resultados entre targets alcistas y bajistas.
- Genera un ranking que muestra el numero de observaciones y aplica una muestra
  minima configurable.
- Incluye datos sinteticos y pruebas automatizadas; no distribuye datos
  comerciales.
- Genera un reporte inicial de `IPO Watch` con estado y fuentes auditables.
- Marca splits y cambios de ticker documentados antes de puntuar targets.
- Publica un registro de gobernanza de proveedores, licencias y uso permitido.
- Importa exportaciones autorizadas de targets con manifiesto y cola de rechazos.

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
build/demo/authorized-targets.csv
build/demo/authorized-targets-audit.csv
build/demo/authorized-targets-import.md
build/demo/authorized-targets-import.html
build/demo/source-registry.md
build/demo/source-registry.html
build/demo/alpha-vantage-prices.csv
build/demo/alpha-vantage-prices.md
build/demo/alpha-vantage-prices.html
build/demo/corporate-actions.csv
build/demo/corporate-actions.md
build/demo/corporate-actions.html
build/demo/evaluations-actions-guarded.csv
build/demo/report-actions-guarded.md
build/demo/ipo-watch.md
build/demo/ipo-watch.html
build/demo/sec-ipo-discovery.csv
build/demo/sec-ipo-discovery.md
build/demo/sec-alerts.csv
build/demo/sec-alerts.md
build/demo/sec-alerts.html
build/demo/ipo-watch-reviewed.csv
build/demo/sec-review-outcomes.csv
build/demo/sec-review-outcomes.md
build/demo/sec-review-outcomes.html
build/demo/global-listings.md
build/demo/global-listings.html
build/demo/issuer-confirmations.md
build/demo/issuer-confirmations.html
build/demo/lse-upcoming.md
build/demo/lse-upcoming.html
build/demo/lse-upcoming.csv
build/demo/lse-fca-check.md
build/demo/lse-fca-check.html
build/demo/lse-fca-check.csv
build/demo/hkex-monitor.csv
build/demo/hkex-monitor.md
build/demo/hkex-monitor.html
build/demo/asx-monitor.csv
build/demo/asx-monitor.md
build/demo/asx-monitor.html
build/demo/tsx-monitor.csv
build/demo/tsx-monitor.md
build/demo/tsx-monitor.html
build/demo/sgx-monitor.csv
build/demo/sgx-monitor.md
build/demo/sgx-monitor.html
build/demo/global-alerts.csv
build/demo/global-alerts.md
build/demo/global-alerts.html
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
  --corporate-actions data/samples/corporate_actions.csv \
  --universe-membership data/samples/historical_universe.csv \
  --output build/demo/evaluations-actions-guarded.csv \
  --report build/demo/report-actions-guarded.md \
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

- `v0.3`: rigor cuantitativo, incluyendo intervalos, segmentos y control de
  integrantes historicos del universo.
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
