# Operacion Continua De Listing Watch

## Open Edition Sin Cuota De Datos

La distribución pública del repositorio prioriza operaciones que no requieren
suscripciones comerciales. `open-edition` genera el manifiesto visible de esa
promesa:

```bash
PYTHONPATH=src python3 -m targetaudit open-edition \
  --registry data/samples/source_registry.csv \
  --report build/live/open-edition.md \
  --html build/live/open-edition.html \
  --as-of YYYY-MM-DD
```

El sandbox de Financials corre con fixtures propios. La operación live sin
cuota utiliza SEC EDGAR para IPO Watch y SEC N-PORT para evidencia periódica
ETF; la SEC requiere un `User-Agent` con contacto, pero no una API key de pago.
Los proveedores comerciales se conservan como extensiones opcionales.
`/dashboard/market-context` carga un widget atribuido de TradingView como
display externo de `XLF`; no genera archivos, no alimenta rankings y requiere
Internet solo para visualizar ese tercero.

## Objetivo

La lista inicial de SpaceX, Cerebras y candidatos conocidos es una semilla.
El monitor continuo debe detectar **cualquier** potencial nueva IPO visible en
fuentes publicas, someterla a revision y luego actualizar el dashboard.
La ruta `/dashboard/ipo` presenta este recorrido y mantiene separada la
evidencia internacional ya implementada.

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
  --report build/live/sec-ipo-discovery.md \
  --html build/live/sec-ipo-discovery.html
```

La entrada universal generada puede inspeccionarse en
`/dashboard/sec-discovery`. Luego, la salida normalizada se convierte en una
cola con historial y enlace por `CIK` al tablero:

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

## Quality Gate De Corridas

Toda ejecucion periodica del scorecard debe evaluar la calidad de las corridas
almacenadas antes de actualizar una vista publica o distribuir un reporte:

```bash
PYTHONPATH=src python3 -m targetaudit operations-quality \
  --database build/live/targetaudit.duckdb \
  --run-id RUN-ID \
  --report build/live/operations-quality.md \
  --html build/live/operations-quality.html \
  --maximum-excluded-rate 0.50 \
  --public-release \
  --require-quality-pass \
  --as-of YYYY-MM-DD
```

El alcance operativo normal marca `blocked` si falta la version metodologica,
la huella de entradas, archivos mínimos (`targets` y `prices`) o linaje
`provider_id`. Con `--public-release`, la corrida candidata también debe
conservar `corporate_actions` y `universe_membership`; así un ranking no puede
liberarse omitiendo las guardas que ya exige `Scorecard Readiness`.
Marca `review_required` si la tasa de exclusiones excede el umbral o la
muestra evaluada no alcanza el mínimo del ranking. `quality_pass` significa
que la corrida pasó verificaciones operativas; no sustituye la revisión de
licencias y permisos en Source Governance.

Con `--run-id` una ejecución automatizada verifica únicamente la corrida que
intenta distribuir. `--require-quality-pass` exige además `--public-release`,
conserva los reportes de
evidencia, pero finaliza con código `2` si la corrida queda `blocked` o
`review_required`, impidiendo que un pipeline publique resultados sin revisión.
La compuerta exige `--run-id`: nunca aprueba por accidente una corrida antigua
solo porque el warehouse contiene resultados previos.

La API sirve el mismo cálculo en
`/api/v1/operations/quality?run_id=RUN-ID&public_release=true` y la página
`/dashboard/operations` permite activar `Public release inputs` para ver el
bloqueo antes de una distribución.

## Decision Combinada De Publicacion

Una liberación del scorecard debe comprobar en el mismo expediente que las
fuentes son publicables y que la corrida candidata utilizó ese linaje:

```bash
PYTHONPATH=src python3 -m targetaudit scorecard-release \
  --registry data/samples/source_registry.csv \
  --database build/live/targetaudit.duckdb \
  --run-id RUN-ID \
  --report build/live/scorecard-release.md \
  --html build/live/scorecard-release.html \
  --maximum-excluded-rate 0.50 \
  --require-release-ready \
  --as-of YYYY-MM-DD
```

El reporte conserva cuatro compuertas separadas: derechos productivos para los
cuatro controles del scorecard, `provider_id` de targets realmente utilizado
por la corrida, procedencia declarada de `prices`, `corporate_actions` y
`universe_membership`, y calidad de publicación con sus cuatro activos. Un bloqueo
devuelve código `2`, por lo que puede detener un despliegue automatizado sin
ocultar la evidencia generada. La misma decisión está disponible en
`/dashboard/release` y `/api/v1/releases/scorecard?run_id=RUN-ID`.

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

Para organizar el trabajo de permisos que puede destrabar el scorecard:

```bash
PYTHONPATH=src python3 -m targetaudit provider-approvals \
  --registry data/samples/source_registry.csv \
  --approvals data/samples/provider_approval_queue.csv \
  --report build/live/provider-approvals.md \
  --html build/live/provider-approvals.html \
  --as-of YYYY-MM-DD
```

La cola inicial conserva siete candidatos y cuatro aprobaciones críticas
abiertas. Una fila aprobada que contradiga `source_registry.csv` hace fallar
el reporte: la evidencia de permiso y la gobernanza deben coincidir antes de
activar una fuente. La vista web está disponible en `/dashboard/approvals`.

Para mostrar alternativas que el usuario podria pagar voluntariamente, sin
activar ingestion ni publicacion:

```bash
PYTHONPATH=src python3 -m targetaudit licensed-extensions \
  --catalog data/samples/licensed_extensions.csv \
  --report build/live/licensed-extensions.md \
  --html build/live/licensed-extensions.html \
  --as-of YYYY-MM-DD
```

La pagina `/dashboard/extensions` presenta el precio publicado y los terminos
revisados. La opcion individual Massive / Benzinga (`USD 99/month`) continua
marcada como uso privado sujeto a licencia; no satisface por si sola el
requisito de output publico de `/dashboard/readiness`.
Finnhub y Financial Modeling Prep aparecen solo como candidatos a contrato:
una clave gratis o de pruebas no cambia el bloqueo de publicacion hasta contar
con derechos escritos de display o redistribucion.

Cuando se reciba o revise evidencia de licencia, aplicarla mediante una
decisión manual a salidas generadas, no editando el registro original:

```bash
PYTHONPATH=src python3 -m targetaudit provider-approval-review \
  --registry data/samples/source_registry.csv \
  --approvals data/samples/provider_approval_queue.csv \
  --decisions data/private/provider_approval_decisions.csv \
  --output-registry build/live/provider-reviewed-source-registry.csv \
  --output-approvals build/live/provider-reviewed-approval-queue.csv \
  --output build/live/provider-approval-review-outcomes.csv \
  --report build/live/provider-approval-review-outcomes.md \
  --html build/live/provider-approval-review-outcomes.html \
  --as-of YYYY-MM-DD
```

`retain_pending` registra evidencia insuficiente sin promover;
`reject_public_output` cierra un expediente para este uso; y
`approve_public_output` solo acepta permiso documentado junto con un conector
verificado como `implemented` o `manual_verified`. Usar después
`build/live/provider-reviewed-source-registry.csv` en `scorecard-readiness` y
`scorecard-release`.

Los cinco reportes generados de la cadena Financials tambien se pueden
recorrer en el dashboard por rutas fijas: `/dashboard/audit/target-import`,
`/dashboard/audit/adjusted-prices`, `/dashboard/audit/corporate-actions`,
`/dashboard/audit/operations-quality` y
`/dashboard/audit/release-decision`. La pagina de decision del demo documenta
el bloqueo; no autoriza publicar rankings reales.
La portada `/dashboard/financials-evidence` los reúne con readiness,
gobernanza, calidad y release para revisar el recorrido completo antes de
interpretar cualquier salida del sandbox.

Para auditar el estado exacto incluido en un bundle, las rutas
`/dashboard/governance-report/open-edition`,
`/dashboard/governance-report/licensed-extensions`,
`/dashboard/governance-report/source-registry`,
`/dashboard/governance-report/provider-approvals`,
`/dashboard/governance-report/approval-review` y
`/dashboard/governance-report/scorecard-readiness` sirven snapshots HTML
generados. Las vistas `/dashboard/governance`, `/dashboard/approvals` y
`/dashboard/readiness` continúan como controles interactivos separados.
El snapshot `open-edition` conserva navegación directa hacia cada capacidad
declarada para revisar el bundle publicado sin volver a la portada dinámica.

## Readiness Del Scorecard Publico

Antes de producir una corrida real se debe revisar si existen fuentes
productivas aprobadas para cada control obligatorio del scorecard financiero:

```bash
PYTHONPATH=src python3 -m targetaudit scorecard-readiness \
  --registry data/samples/source_registry.csv \
  --report build/live/scorecard-readiness.md \
  --html build/live/scorecard-readiness.html \
  --as-of YYYY-MM-DD
```

El reporte diferencia `public_ready`, `internal_only`, `integration_pending`
y `missing_source` para targets, precios, acciones corporativas y membresía
histórica del universo. Los fixtures `synthetic-demo` y `authorized-demo`
prueban la aplicación, pero nunca habilitan publicación real. La API
`/api/v1/readiness/scorecard` y la página `/dashboard/readiness` exponen este
estado antes de correr o distribuir un ranking.

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

En la aplicacion, `/dashboard/etf` es el índice que explica las frecuencias
y límites de esta evidencia. `/dashboard/etf/arkk-demo`, `/dashboard/etf/xlf-demo` y
`/dashboard/etf/iyf-demo` presentan solamente fixtures sinteticos. La
evidencia SEC queda separada en
`/dashboard/etf/nport-recent`, `/dashboard/etf-regulatory`,
`/dashboard/etf/nport-catalog` y `/dashboard/etf/nport-sync`; ninguna de
estas rutas se presenta como actividad diaria o en tiempo real.

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
El bundle probado incluye `/dashboard/etf/arkk-demo`, calculado exclusivamente
desde dos archivos ARK-shaped sinteticos redistribuibles.

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

### Importacion Manual iShares/IYF

`IYF` agrega cobertura de otro ETF concentrado en acciones financieras
estadounidenses. El operador puede descargar el archivo desde la pagina
oficial y normalizarlo localmente:

```bash
PYTHONPATH=src python3 -m targetaudit ishares-holdings-import \
  --snapshot data/raw/etf/IYF_HOLDINGS.csv \
  --fund-symbol IYF \
  --fund-name "iShares U.S. Financials ETF" \
  --captured-on YYYY-MM-DD \
  --output data/raw/etf/iyf-normalized.csv \
  --report build/live/iyf-import.md
```

El importador detecta la fecha declarada del holdings file, procesa
posiciones equity con acciones y peso, y reporta filas no equity omitidas.
La evidencia real se marca `official_snapshot` y no `daily_official`, porque
el sitio publica una captura fechada sin que TargetAudit asuma frecuencia.
No existe automatizacion para iShares: los terminos BlackRock prohíben que un
agente automatico monitorice o copie sus materiales sin permiso. La salida
real queda local y no se publica.

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
export TARGETAUDIT_SEC_USER_AGENT="TargetAudit tu-correo@ejemplo.com"
PYTHONPATH=src python3 -m targetaudit sec-nport-datasets \
  --output build/live/nport-dataset-catalog.csv \
  --report build/live/nport-dataset-catalog.md \
  --html build/live/nport-dataset-catalog.html \
  --download-quarter 2026q1 \
  --storage-dir data/raw/etf/nport/datasets

PYTHONPATH=src python3 -m targetaudit sec-nport-backfill \
  --dataset-dir data/raw/etf/nport/datasets/2025q4/extracted \
  --dataset-dir data/raw/etf/nport/datasets/2026q1/extracted \
  --series-id S000006411 \
  --fund-symbol XLF \
  --captured-on YYYY-MM-DD \
  --data-set-label "SEC N-PORT quarterly extracts" \
  --output-dir data/raw/etf/nport/backfill/xlf \
  --manifest build/live/xlf-nport-backfill.csv \
  --report build/live/xlf-nport-backfill.md
```

`sec-nport-datasets` lee el catalogo oficial y solo descarga el trimestre
solicitado. Conserva el ZIP local en
`data/raw/etf/nport/datasets/YYYYqN/` y extrae cinco tablas necesarias bajo
`extracted/`; la extraccion rechaza rutas inseguras dentro del ZIP. No usar
`--force` salvo cuando se quiera reemplazar deliberadamente una copia local.
La revision en vivo del `2026-05-24` detecto `26` ZIP publicados, desde
`2019q4` hasta `2026q1`; una ejecucion posterior debe tomar el catalogo
actual y no asumir que `2026q1` siga siendo el ultimo trimestre disponible.

`sec-nport-backfill` consume `SUBMISSION.tsv`, `REGISTRANT.tsv`,
`FUND_REPORTED_INFO.tsv`, `FUND_REPORTED_HOLDING.tsv` e `IDENTIFIERS.tsv`.
Cada ZIP se une internamente para evitar asumir que `HOLDING_ID` es global
entre trimestres. Si dos entradas producen el mismo `REPORT_DATE`, la
ejecucion se detiene para revisar la enmienda antes de publicar una serie.

Para una tarea recurrente, inicializar una linea base y luego procesar solo
ZIP trimestrales nuevos:

```bash
export TARGETAUDIT_SEC_USER_AGENT="TargetAudit tu-correo@ejemplo.com"
PYTHONPATH=src python3 -m targetaudit sec-nport-sync \
  --state data/raw/etf/nport/sync-state.csv \
  --storage-dir data/raw/etf/nport/datasets \
  --report build/live/nport-sync.md \
  --html build/live/nport-sync.html \
  --as-of YYYY-MM-DD \
  --series-id S000006411 \
  --fund-symbol XLF \
  --data-set-label "SEC N-PORT synchronized extracts" \
  --output-dir data/raw/etf/nport/backfill/xlf \
  --manifest build/live/xlf-nport-backfill.csv \
  --backfill-report build/live/xlf-nport-backfill.md
```

La primera corrida conserva los releases publicados en
`data/raw/etf/nport/sync-state.csv` como referencia, sin iniciar una descarga
historica masiva. Desde la segunda, un trimestre que aparezca por primera vez
se descarga, valida y extrae; luego la serie solicitada se regenera usando
todos los trimestres disponibles localmente. El estado se reemplaza
atomicamente y rechaza estados desconocidos, para que una interrupcion o
edicion accidental no sea tomada como evidencia ya procesada.

El bundle reproducible sirve estos controles únicamente por las rutas fijas
`/dashboard/etf/nport-catalog` y `/dashboard/etf/nport-sync`. Ambas son
evidencia de disponibilidad y sincronizacion regulatoria trimestral; no
representan compras, ventas ni una cartera diaria.

Para el benchmark financiero inicial, un filing oficial `NPORT-P` de
`SELECT SECTOR SPDR TRUST` confirma `XLF` como serie `S000006411` del
registrante `CIK 0001064641`.

## Historial De Mercados Globales

Los diez feeds internacionales generan CSV normalizados. Después de
obtenerlos, `global-alerts` copia la lectura del día a
`data/raw/global/history/YYYY-MM-DD/`, selecciona la última captura anterior
y genera una bandeja común:

```bash
PYTHONPATH=src python3 -m targetaudit global-alerts \
  --hkex data/raw/global/hkex-monitor-live.csv \
  --lse data/raw/global/lse-upcoming-live.csv \
  --asx data/raw/global/asx-monitor-live.csv \
  --tsx data/raw/global/tsx-monitor-live.csv \
  --jpx data/raw/global/jpx-monitor.csv \
  --edinet data/raw/global/edinet-monitor.csv \
  --cvm data/raw/global/cvm-monitor.csv \
  --esma data/raw/global/esma-monitor.csv \
  --opendart data/raw/global/opendart-monitor.csv \
  --sgx data/raw/global/sgx-monitor-live.csv \
  --history-dir data/raw/global/history \
  --output build/live/global-alerts.csv \
  --report build/live/global-alerts.md \
  --html build/live/global-alerts.html
```

La primera ejecución establece la línea base y no inventa cambios. A partir
de la segunda, la bandeja marca evidencia nueva, modificada o removida del
feed para revisión. En Japón, un documento EDINET permanece como señal
documental y JPX confirma el hito de listing. En Brasil, una oferta CVM
permanece como evidencia regulatoria hasta que una fuente B3 confirme el
listing. En Europa, ESMA conserva evidencia de prospecto o admision para
revision, no primera negociacion. En Corea, un filing OpenDART permanece como
evidencia regulatoria y no como IPO o listing confirmado. Una remoción nunca se promueve
automáticamente a retirada, admisión o cotización completada.

La portada `/dashboard/global-listings` es el índice operativo de estas
salidas; cada HTML generado enlaza de regreso a ella para consultar la regla
de confirmación aplicable a su mercado.

## Confirmacion JPX De Tokio

El monitor JPX adicional lee la pagina oficial `New Listings` y genera
confirmaciones de aprobacion o fecha de listing con evidencia enlazada:

```bash
PYTHONPATH=src python3 -m targetaudit jpx-monitor \
  --output data/raw/global/jpx-monitor.csv \
  --report build/live/jpx-monitor.md \
  --html build/live/jpx-monitor.html
```

Su CSV ya entra en el diff global diario junto con `EDINET`, que aporta una
señal documental anterior sin convertirse en estado de listing. Una
aprobacion JPX no es una instruccion de inversion.

## Filings EDINET De Japon

El API oficial EDINET requiere una clave gratuita emitida por la FSA. La clave
se mantiene fuera de Git y se pasa por variable de entorno:

```bash
export TARGETAUDIT_EDINET_API_KEY="tu-clave-privada"
PYTHONPATH=src python3 -m targetaudit edinet-monitor \
  --filing-date YYYY-MM-DD \
  --output data/raw/global/edinet-monitor.csv \
  --report build/live/edinet-monitor.md \
  --html build/live/edinet-monitor.html \
  --as-of YYYY-MM-DD
```

El collector conserva únicamente los documentos `030`, `040` y `050`
definidos en la especificación oficial EDINET. Su resultado abre revisión de
la oferta y entra en el diff diario mediante `--edinet`; la confirmación de
listing sigue correspondiendo a JPX.

## Ofertas CVM De Brasil

`cvm-monitor` lee el ZIP diario del conjunto oficial `Ofertas Públicas de
Distribuição`, publicado por CVM bajo licencia ODbL, y filtra solamente
ofertas de acciones:

```bash
PYTHONPATH=src python3 -m targetaudit cvm-monitor \
  --since YYYY-MM-DD \
  --output data/raw/global/cvm-monitor.csv \
  --report build/live/cvm-monitor.md \
  --html build/live/cvm-monitor.html \
  --as-of YYYY-MM-DD
```

No requiere clave ni proveedor pagado. El CSV identifica la oferta, el tipo
de acción, el rito y el estado observado. Es evidencia de una oferta pública;
la admisión o negociación en B3 debe verificarse mediante una fuente distinta.

## Prospectos ESMA De Europa

`esma-monitor` consulta el servicio A2A oficial `Prospectus III Securities`,
sin clave, y selecciona únicamente registros `SHRS` de Alemania, Países Bajos
e Italia:

```bash
PYTHONPATH=src python3 -m targetaudit esma-monitor \
  --since YYYY-MM-DD \
  --output data/raw/global/esma-monitor.csv \
  --report build/live/esma-monitor.md \
  --html build/live/esma-monitor.html \
  --as-of YYYY-MM-DD
```

El aviso legal oficial autoriza reproducir información del registro con
atribución y rotulado de transformaciones. TargetAudit muestra esa procedencia
y mantiene los eventos de oferta/admisión como revisión regulatoria; no
declara primera negociación.

## Filings OpenDART De Corea Del Sur

`opendart-monitor` consulta la búsqueda oficial de disclosures de FSS
OpenDART y selecciona únicamente `C001` (equity securities registration) y
`C006` (small equity public offering). El servicio es gratuito en principio,
pero requiere una clave del operador guardada fuera de Git:

```bash
export TARGETAUDIT_OPENDART_API_KEY="tu-clave-privada"
PYTHONPATH=src python3 -m targetaudit opendart-monitor \
  --since YYYY-MM-DD \
  --output data/raw/global/opendart-monitor.csv \
  --report build/live/opendart-monitor.md \
  --html build/live/opendart-monitor.html \
  --as-of YYYY-MM-DD
```

Un resultado inicia revisión regulatoria de oferta de capital; no confirma
IPO, admisión, cotización ni inversión. `KRX OPEN API` no se conecta a la
edición pública: sus términos en inglés revisados el `2026-05-25` limitan el
uso a fines no comerciales y prohíben proporcionar sus datos a terceros.

## Automatizaciones Locales Activas

En la aplicacion Codex se configuraron cuatro ejecuciones recurrentes locales:

- `TargetAudit IPO Watch diario`: consulta el indice SEC, conserva snapshots,
  genera `SEC IPO Alerts` y resume posibles registros, prospectos o retiros
  nuevos, incluyendo coincidencias exactas de `CIK` con la watchlist y triage
  heuristico visible para SPAC/ETF.
- `TargetAudit Global Listings diario`: consulta feeds oficiales o páginas
  estructuradas, el componente JSON oficial LSE `Upcoming issues` y el
  contraste público FCA NSM, además de las tablas oficiales ASX y TSX; resume
  cambios HKEX, emisiones previstas en Londres, coincidencias documentales,
  solicitudes/retiradas australianas, cotizaciones confirmadas en Canada,
  aprobaciones/listings JPX, ofertas de acciones CVM, prospectos europeos ESMA,
  filings coreanos OpenDART y prospectos SGX.
  También preserva snapshots y genera `Global Listings Alerts`.
- `TargetAudit N-PORT trimestral`: consulta el catalogo oficial SEC cada lunes
  a las `21:50` hora de Guatemala, comenzando el `2026-05-25`; establece una
  linea base en su primera corrida y luego descarga solo ZIP nuevos para
  regenerar la serie regulatoria `XLF` cuando existan datos locales validos.
- `TargetAudit Scorecard Quality diario`: comprueba de lunes a viernes el
  readiness de fuentes para el scorecard y el warehouse
  `build/live/targetaudit.duckdb`; genera el reporte operativo si existen
  corridas reales autorizadas y reporta claramente cuando aun no hay una
  corrida live. Nunca sustituye esa ausencia con el demo y exige
  `scorecard-release` antes de distribuir una corrida candidata; esa decisión
  también exige procedencia por activo en la nueva corrida.

Las cuatro tareas tratan evidencia operativa o eventos regulatorios para
investigar, no como instrucciones para tomar posiciones.

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

## Revision MAS OPERA De Singapur

`MAS OPERA` es un repositorio oficial, pero no un conector live de la Open
Edition. La pagina `Public Offers` exige un security code y sus terminos,
actualizados el `2026-04-18`, restringen retrieval automatizado, caching y
deep links sin permiso escrito. El sistema no debe hacer scraping de OPERA ni
archivar sus documentos; para monitor automatico de prospectos de Singapur se
utiliza `SGX IPO Prospectus`.

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

## Reporte Reproducible En GitHub

La Open Edition ya tiene una tarea programada publicable en
`.github/workflows/open-edition-report.yml`. Corre cada lunes a las
`12:17 UTC` y tambien admite ejecucion manual. Su unica entrada son fixtures
redistribuibles del repositorio: ejecuta `make verify`, genera todas las
paginas de `build/demo/`, construye el wheel en `build/dist/` y sube ambos
directorios como artefacto de GitHub Actions conservado por 30 dias.

Este reporte verifica que la aplicacion abierta sigue siendo instalable y
reproducible sin costo de datos. No solicita APIs live, no lee secrets y no
debe interpretarse como una actualizacion del mercado ni como un ranking real
de analistas.

## Despliegue Live Futuro En GitHub

- Entrada: indices diarios SEC, feeds HKEXnews y comunicados oficiales.
- Salida: eventos nuevos, entidades promovidas, retiros y cambios de estado.
- Alertas: nuevas IPOs confirmadas, pricing, primer dia de cotizacion.
- Proteccion SEC: maximo muy inferior a las 10 solicitudes por segundo
  permitidas; normalmente una solicitud diaria de indice y solicitudes
  puntuales de documentos a revisar.

Para habilitar esa fase live en un repositorio GitHub publico,
`TARGETAUDIT_SEC_USER_AGENT` se configurara
como `Actions secret`, nunca escrito en el codigo ni en los reportes.
Antes de abrir contribuciones, habilita `Private vulnerability reporting` en
GitHub para que los reportes descritos en `SECURITY.md` no expongan secretos ni
fallas explotables en issues publicos.

## Limites

- Las presentaciones confidenciales no se pueden descubrir hasta hacerse
  publicas.
- SEC cubre el mercado regulado en Estados Unidos; IPOs en Londres, Hong Kong
  u otras plazas necesitan conectores adicionales.
- Fuentes noticiosas pueden advertir de una operacion, pero no deben confirmar
  estado por si solas.
