# Operacion Continua De Listing Watch

## Objetivo

La lista inicial de SpaceX, Cerebras y candidatos conocidos es una semilla.
El monitor continuo debe detectar **cualquier** potencial nueva IPO visible en
fuentes publicas, someterla a revision y luego actualizar el dashboard.

## Fuente Primaria: SEC EDGAR

La SEC publica indices diarios de todos los filings presentados. TargetAudit
escanea los formularios con interes para IPO Watch:

| Formulario | Uso En La Cola |
|---|---|
| `S-1`, `F-1` | Nueva declaracion de registro que requiere verificar si es IPO |
| `S-1/A`, `F-1/A` | Enmienda a una declaracion detectada |
| `S-1MEF`, `F-1MEF` | Posible ampliacion de valores registrados |
| `424B4` | Prospecto final que puede confirmar terminos de oferta |
| `RW` | Solicitud de retiro que puede cancelar el seguimiento |

Un filing descubierto no entra automaticamente como IPO confirmada. Muchos
formularios de registro pueden representar ofertas secundarias, reventas u
otras operaciones.

## Que Es El User-Agent

La SEC no pide una cuenta ni una clave API para descargar datos publicos.
Solicita que el trafico automatizado se identifique con una organizacion o
proyecto y un correo monitoreado.

Ejemplo:

```text
TargetAudit mario@ejemplo.com
```

El correo debe ser uno que puedas revisar si la SEC necesita contactar al
operador del monitor. Puede ser tu correo normal o, preferiblemente, un correo
dedicado al proyecto, por ejemplo `targetaudit@tudominio.com`.

No pongas ese correo en GitHub. Configuralo localmente o como secret del
repositorio:

```bash
export TARGETAUDIT_SEC_USER_AGENT="TargetAudit tu-correo@ejemplo.com"
```

Para una ejecucion recurrente local tambien puede guardarse en el archivo
ignorado `data/private/sec_user_agent.txt`, con una sola linea:

```text
TargetAudit tu-correo@ejemplo.com
```

El archivo `.env.example` muestra el nombre esperado de la variable, pero no
incluye una credencial real.

## Ejecucion Manual En Vivo

```bash
export TARGETAUDIT_SEC_USER_AGENT="TargetAudit tu-correo@ejemplo.com"
PYTHONPATH=src python3 -m targetaudit sec-ipo-discover \
  --date YYYY-MM-DD \
  --output build/live/sec-ipo-discovery.csv \
  --report build/live/sec-ipo-discovery.md
```

Luego, la salida normalizada se convierte en una cola con historial y enlace
por `CIK` al tablero:

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

Una coincidencia de `CIK` significa que el documento pertenece a una empresa
seguida; aún exige leer el filing antes de modificar su estado.

`SEC IPO Alerts` prioriza revisión con indicadores observables: `CIK`
coincidente, formulario `RW` o `424B4`, y señales de nombre como
`Acquisition Corp/Co` o `ETF`. Estas últimas solo reducen trabajo manual:
no confirman que un emisor sea una SPAC, un fondo ni una IPO operativa.

Una vez leido un filing, la revision humana puede generar una copia actualizada
del tablero sin editar el registro base ni aceptar promociones implícitas:

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

Cada decision exige nota de revision, URL del filing y `CIK` idénticos a una
alerta SEC. `confirm_filed_public` solo acepta formularios compatibles y
`confirm_withdrawn` exige `RW`; las otras decisiones conservan el estado.

Para el demo y las pruebas se usa un indice local de ejemplo, sin solicitar
datos a SEC:

```bash
make verify
```

## Registro De Fuentes Y Licencias

Antes de habilitar un nuevo proveedor o mostrar resultados reales, generar la
vista de gobernanza:

```bash
PYTHONPATH=src python3 -m targetaudit source-registry \
  --registry data/samples/source_registry.csv \
  --report build/live/source-registry.md \
  --html build/live/source-registry.html \
  --as-of YYYY-MM-DD
```

El registro separa `integration_status` de `license_status`: una integración
puede funcionar técnicamente y permanecer bloqueada para un producto público
hasta revisar términos de uso o licencia. `restricted_no_collection` impide
registrar accidentalmente una fuente como conector implementado.

## Precios Ajustados Alpha Vantage

Para importar un simbolo con clave privada:

```bash
export TARGETAUDIT_ALPHA_VANTAGE_API_KEY="tu-clave-privada"
PYTHONPATH=src python3 -m targetaudit alpha-vantage-prices \
  --ticker JPM \
  --output data/raw/prices/jpm.csv \
  --report build/live/jpm-prices.md \
  --html build/live/jpm-prices.html \
  --as-of YYYY-MM-DD
```

La clave tambien puede almacenarse localmente en el archivo ignorado
`data/private/alpha_vantage_api_key.txt`. El comando usa primero
`data/raw/prices/alpha-vantage/<TICKER>-daily-adjusted.json`; solo consume una
solicitud si no hay cache o se indica `--refresh`.

Alpha Vantage declara 25 solicitudes diarias como limite estandar y marca el
endpoint ajustado diario como premium. Esta operacion requiere acceso
autorizado al endpoint y sus salidas de datos reales no se habilitan para
publicacion hasta revisar licencia y terminos.

## Importacion Autorizada De Targets

Una fuente comercial o exportacion entregada legalmente debe ingresar mediante
un manifiesto conservado junto al archivo original, ambos fuera de Git:

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

El comando requiere una referencia HTTPS de licencia/autorizacion y
`authorized_for_internal_research: true`. Cada fila necesita ticker, emisor,
firma, fecha, target positivo y URL HTTPS de evidencia; de lo contrario queda
en la auditoria como rechazada. Aunque el manifiesto declare salida publica,
el despliegue real debe esperar revision contractual.

## Auditoria De Acciones Corporativas

Antes de publicar un ranking de targets reales se debe cruzar la muestra
contra splits y cambios de símbolo documentados:

```bash
PYTHONPATH=src python3 -m targetaudit corporate-actions-check \
  --targets data/samples/targets.csv \
  --actions data/samples/corporate_actions.csv \
  --output build/live/corporate-actions.csv \
  --report build/live/corporate-actions.md \
  --html build/live/corporate-actions.html \
  --as-of YYYY-MM-DD

PYTHONPATH=src python3 -m targetaudit evaluate \
  --targets data/samples/targets.csv \
  --prices data/samples/prices.csv \
  --corporate-actions data/samples/corporate_actions.csv \
  --universe-membership data/samples/historical_universe.csv \
  --output build/live/evaluations.csv \
  --report build/live/report.md \
  --transaction-cost-bps 10 \
  --as-of YYYY-MM-DD
```

La muestra incluida contiene acciones sintéticas para comprobar que la
protección funciona. En producción, el registro debe cargarse desde
comunicados del emisor, filings o avisos de bolsa revisados. Nasdaq Daily List
y NYSE Corporate Actions son candidatos oficiales; deben evaluarse términos,
licencia y cobertura antes de automatizar su uso.

## Universo Historico Del Scorecard

Para evitar seleccionar hoy solo las companias que sobrevivieron o permanecen
en el sector, una ejecucion publicable debe suministrar membresia historica:

```bash
PYTHONPATH=src python3 -m targetaudit evaluate \
  --targets data/samples/targets.csv \
  --prices data/samples/prices.csv \
  --universe-membership data/samples/historical_universe.csv \
  --output build/live/evaluations.csv \
  --report build/live/report.md \
  --transaction-cost-bps 10 \
  --as-of YYYY-MM-DD
```

El archivo debe representar un unico universo, con ventanas no solapadas y
fuente verificable por ticker. Los targets fuera de membresia quedan
excluidos; los incluidos adoptan el sector registrado para la fecha del
pronostico. El fixture es sintetico: la publicacion real exige una fuente
licenciada o oficialmente redistribuible de composiciones historicas.

## Revisiones De Price Targets

El evaluador detecta automáticamente cadenas por `firm` y `ticker`. Cuando
existe un target valido posterior publicado antes de vencer el anterior, la
observacion anterior queda excluida como `superseded_by_later_target`; el
reporte y CSV conservan qué target la reemplazo y en qué fecha.

El demo específico puede regenerarse con:

```bash
PYTHONPATH=src python3 -m targetaudit evaluate \
  --targets data/samples/targets_revisions.csv \
  --prices data/samples/prices_revisions.csv \
  --universe-membership data/samples/historical_universe.csv \
  --output build/demo/evaluations-target-revisions.csv \
  --report build/demo/report-target-revisions.md \
  --minimum-sample 1 \
  --transaction-cost-bps 10 \
  --as-of 2025-01-01
```

Esta politica es conservadora: un target sustituido no cuenta ni como acierto
ni como fallo. Si una futura fuente identifica explícitamente el tipo de
revision, se podran modelar intervalos activos hasta la sustitucion.

## Backtest Con Costos

`evaluate` produce ademas un resultado neto ejecutable bajo una regla
declarada: compra/venta al primer cierre elegible, salida limite exactamente
al target si la barra posterior lo alcanza y, en caso contrario, salida al
cierre del vencimiento. El parametro `--transaction-cost-bps` expresa el costo
por lado; el valor demostrativo es `10`, equivalente a `20 bps` ida y vuelta.

El reporte muestra retorno neto medio y exceso neto contra el benchmark usando
la misma fecha de salida cuando existe una barra compatible. Esta simulacion
no incluye deslizamiento, costo de prestamo para cortos, impuestos ni reglas
de asignacion de capital.

## Flujo Continuo Recomendado

1. Cada dia habil de mercado, descargar el indice diario SEC una vez.
2. Extraer formularios potencialmente relacionados con IPO.
3. Guardar la cola y comparar contra ejecuciones anteriores.
4. Revisar nuevos `S-1`/`F-1` para confirmar si describen una IPO.
5. Promover casos confirmados al registro `IPO Watch`.
6. Confirmar ticker, exchange y fecha solo desde prospecto final, exchange o
   comunicado oficial.
7. Publicar el dashboard actualizado con historial de cambios.

## ETF Holdings Activity

La pagina independiente de holdings se genera a partir de dos snapshots
normalizados. El demo incluido usa evidencia sintetica:

```bash
PYTHONPATH=src python3 -m targetaudit etf-holdings-activity \
  --previous data/samples/etf-holdings-previous.csv \
  --current data/samples/etf-holdings-current.csv \
  --output build/demo/etf-holdings-activity.csv \
  --report build/demo/etf-holdings-activity.md \
  --html build/demo/etf-holdings-activity.html \
  --as-of 2026-05-24
```

Para una ejecucion real, cada snapshot debe provenir de una descarga oficial
revisada, conservar su URL, fecha efectiva, fecha de captura y frecuencia
publicada. La verificacion regulatoria `SEC N-PORT` ya puede importarse en
una capa separada; es auditable pero llega con retraso.

Una diferencia entre dos snapshots se reportara como cambio de posicion
publicada. No se etiquetara automaticamente como compra o venta: puede estar
afectada por creaciones/redenciones del fondo, derivados o acciones
corporativas.

### Importacion Local ARK

ARK publica materiales descargables y declara una actualizacion diaria de
holdings al cierre de cada dia habil. El comando normaliza un archivo CSV
descargado por el operador sin incorporarlo a Git:

```bash
PYTHONPATH=src python3 -m targetaudit ark-holdings-import \
  --snapshot data/raw/etf/ARKK_HOLDINGS.csv \
  --fund-symbol ARKK \
  --fund-name "ARK Innovation ETF" \
  --captured-on YYYY-MM-DD \
  --output data/raw/etf/arkk-normalized.csv \
  --report build/live/arkk-import.md
```

Para producir actividad deben importarse dos capturas oficiales separadas y
pasar sus CSV normalizados a `etf-holdings-activity`. Los archivos oficiales
y sus derivados reales permanecen locales mientras la politica de
redistribucion no este autorizada.

### Importacion Local SPDR/XLF

State Street publica `XLF`, el benchmark sectorial inicial de TargetAudit, y
su pagina identifica la descarga completa de holdings como diaria. Para
normalizar un archivo descargado localmente:

```bash
PYTHONPATH=src python3 -m targetaudit spdr-holdings-import \
  --snapshot data/raw/etf/XLF_HOLDINGS.csv \
  --fund-symbol XLF \
  --fund-name "State Street Financial Select Sector SPDR ETF" \
  --captured-on YYYY-MM-DD \
  --output data/raw/etf/xlf-normalized.csv \
  --report build/live/xlf-import.md
```

La pagina oficial tambien advierte que holdings y sectores cambian, no son
recomendaciones de inversion y el contenido no puede reproducirse sin
consentimiento escrito. Por ello las descargas y diferencias reales quedan
fuera de Git hasta contar con autorizacion aplicable. Al procesar la primera
descarga autorizada se deben confirmar los encabezados locales frente al
contrato documentado; el importador se detiene si faltan campos requeridos.

### Evidencia Regulatoria SEC N-PORT

Para consultar submissions recientes del registrante en EDGAR, confirmar la
serie dentro del XML y archivarlo localmente:

```bash
export TARGETAUDIT_SEC_USER_AGENT="TargetAudit tu-correo@ejemplo.com"
PYTHONPATH=src python3 -m targetaudit sec-nport-collect \
  --cik 0001064641 \
  --series-id S000006411 \
  --fund-symbol XLF \
  --captured-on YYYY-MM-DD \
  --archive-dir data/raw/etf/nport/history \
  --output data/raw/etf/nport/xlf-normalized.csv \
  --report build/live/xlf-nport-import.md
```

Esta salida usa la capa `regulatory_periodic`. No puede compararse con
snapshots `daily_official` de ARK o SPDR; solo con otro periodo N-PORT del
mismo fondo. El parser inicial incluye posiciones en acciones y registra las
posiciones no modeladas que omite. Al descargar desde SEC se mantienen los
requisitos de `User-Agent` y acceso justo ya documentados para EDGAR.

El colector usa `data.sec.gov/submissions/CIK##########.json`, que la SEC
describe como historial reciente del filer, y descarga documentos `NPORT-P`
candidatos hasta que el XML confirma la `seriesId`. Conserva el XML validado
debajo de `--archive-dir/YYYY-MM-DD/SERIES-ID/`. Para procesar un XML ya
descargado o hacer un backfill manual:

Cuando EDGAR expone el documento primario bajo una ruta de presentacion
`xslFormNPORT-P_X01/primary_doc.xml`, el colector usa el XML crudo
`primary_doc.xml` del mismo accession; la vista XSL responde HTML y no se
archiva como evidencia estructurada.

```bash
PYTHONPATH=src python3 -m targetaudit sec-nport-import \
  --snapshot data/raw/etf/nport/primary_doc.xml \
  --fund-symbol XLF \
  --captured-on YYYY-MM-DD \
  --source-url https://www.sec.gov/Archives/edgar/data/.../primary_doc.xml \
  --output data/raw/etf/nport/xlf-normalized.csv \
  --report build/live/xlf-nport-import.md
```

Para periodos anteriores a la ventana reciente, descargar los ZIP
trimestrales desde la pagina de datasets SEC, extraerlos fuera de Git y pasar
cada directorio al backfill:

```bash
PYTHONPATH=src python3 -m targetaudit sec-nport-backfill \
  --dataset-dir data/raw/etf/nport/2025q4 \
  --dataset-dir data/raw/etf/nport/2026q1 \
  --series-id S000006411 \
  --fund-symbol XLF \
  --captured-on YYYY-MM-DD \
  --data-set-label "SEC N-PORT quarterly extracts" \
  --output-dir data/raw/etf/nport/backfill/xlf \
  --manifest build/live/xlf-nport-backfill.csv \
  --report build/live/xlf-nport-backfill.md
```

`sec-nport-backfill` consume `SUBMISSION.tsv`, `REGISTRANT.tsv`,
`FUND_REPORTED_INFO.tsv`, `FUND_REPORTED_HOLDING.tsv` e `IDENTIFIERS.tsv`.
Cada ZIP se une internamente para evitar asumir que `HOLDING_ID` es global
entre trimestres. Si dos entradas producen el mismo `REPORT_DATE`, la
ejecucion se detiene para revisar la enmienda antes de publicar una serie.

Para el benchmark financiero inicial, un filing oficial `NPORT-P` de
`SELECT SECTOR SPDR TRUST` confirma `XLF` como serie `S000006411` del
registrante `CIK 0001064641`.

## Historial De Mercados Globales

Los cinco conectores internacionales generan CSV normalizados. Después de
obtenerlos, `global-alerts` copia la lectura del día a
`data/raw/global/history/YYYY-MM-DD/`, selecciona la última captura anterior
y genera una bandeja común:

```bash
PYTHONPATH=src python3 -m targetaudit global-alerts \
  --hkex data/raw/global/hkex-monitor-live.csv \
  --lse data/raw/global/lse-upcoming-live.csv \
  --asx data/raw/global/asx-monitor-live.csv \
  --tsx data/raw/global/tsx-monitor-live.csv \
  --sgx data/raw/global/sgx-monitor-live.csv \
  --history-dir data/raw/global/history \
  --output build/live/global-alerts.csv \
  --report build/live/global-alerts.md \
  --html build/live/global-alerts.html
```

La primera ejecución establece la línea base y no inventa cambios. A partir
de la segunda, la bandeja marca evidencia nueva, modificada o removida del
feed para revisión. Una remoción nunca se promueve automáticamente a retirada,
admisión o cotización completada.

## Automatizaciones Locales Activas

En la aplicacion Codex se configuraron dos ejecuciones recurrentes locales en
dias habiles:

- `TargetAudit IPO Watch diario`: consulta el indice SEC, conserva snapshots,
  genera `SEC IPO Alerts` y resume posibles registros, prospectos o retiros
  nuevos, incluyendo coincidencias exactas de `CIK` con la watchlist y triage
  heuristico visible para SPAC/ETF.
- `TargetAudit Global Listings diario`: consulta los cinco feeds JSON
  oficiales o páginas estructuradas, el componente JSON oficial LSE `Upcoming issues` y el
  contraste público FCA NSM, además de las tablas oficiales ASX y TSX; resume
  cambios HKEX, emisiones previstas en Londres, coincidencias documentales,
  solicitudes/retiradas australianas, cotizaciones confirmadas en Canadá y
  prospectos SGX. También preserva snapshots y genera `Global Listings Alerts`.

Ambas tareas tratan los eventos como informacion regulatoria para investigar,
no como instrucciones para tomar posiciones.

El contraste FCA NSM distingue entre un emisor sin documento encontrado y
una coincidencia documental que requiere revisión. No promueve
automáticamente una fecha esperada a admisión confirmada, porque el NSM no es
en tiempo real y el tipo de documento debe examinarse. Su salida también
clasifica metadatos visibles en `prospectus_document_signal`,
`admission_document_signal`, `intention_to_float_notice` u
`other_document_review`, de modo que una intención de flotar no se confunda
con evidencia documental más avanzada.

El monitor ASX conserva como `anticipated` los registros con fecha prevista y
como `withdrawn` los retirados. ASX indica que recibió una solicitud formal,
pero fechas y códigos aún pueden cambiar.

El monitor TSX conserva únicamente el estado `listed`, porque su fuente
publica nuevas compañías ya cotizadas. Debe utilizarse como confirmación
posterior y no como detector anticipado de IPO.

El monitor SGX conserva `prospectus_published`, porque su fuente publica
documentos de prospecto. Es una señal documental para revisión, no una
confirmación automática de trading.

## Confirmaciones Oficiales Del Emisor

Los comunicados revisados manualmente se normalizan en un registro separado:

```bash
PYTHONPATH=src python3 -m targetaudit issuer-confirmations \
  --registry data/samples/issuer_listing_confirmations.csv \
  --report build/live/issuer-confirmations.md \
  --html build/live/issuer-confirmations.html \
  --as-of YYYY-MM-DD
```

Esta salida conserva un evento por fila y exige fuente HTTPS, mercado,
ticker, fecha de evento y fecha de verificacion. No rastrea titulares
generales ni promueve rumores: confirma solamente el hito que declara el
comunicado oficial revisado.

## Despliegue Futuro En GitHub

- Entrada: indices diarios SEC, feeds HKEXnews y comunicados oficiales.
- Salida: eventos nuevos, entidades promovidas, retiros y cambios de estado.
- Alertas: nuevas IPOs confirmadas, pricing, primer dia de cotizacion.
- Proteccion SEC: maximo muy inferior a las 10 solicitudes por segundo
  permitidas; normalmente una solicitud diaria de indice y solicitudes
  puntuales de documentos a revisar.

En un repositorio GitHub publico, `TARGETAUDIT_SEC_USER_AGENT` se configurara
como `Actions secret`, nunca escrito en el codigo ni en los reportes.

## Limites

- Las presentaciones confidenciales no se pueden descubrir hasta hacerse
  publicas.
- SEC cubre el mercado regulado en Estados Unidos; IPOs en Londres, Hong Kong
  u otras plazas necesitan conectores adicionales.
- Fuentes noticiosas pueden advertir de una operacion, pero no deben confirmar
  estado por si solas.
