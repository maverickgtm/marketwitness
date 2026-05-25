# TargetAudit

**Auditable market intelligence: analyst targets and upcoming public listings.**

Plataforma abierta para evaluar, con datos verificables, la precision historica y
la utilidad economica de los `price targets` publicados por analistas financieros
en bancos y companias financieras cotizadas en Estados Unidos.

## Open Edition: Funcional Sin Costos De Datos

La edicion principal para GitHub no requiere suscripciones pagadas ni claves
comerciales. Incluye:

- `Financials Scorecard Sandbox` completo con fixtures creados por el proyecto.
- `U.S. IPO Filing Watch` sobre filings públicos SEC EDGAR.
- `ETF Regulatory Holdings` sobre datos públicos SEC N-PORT.
- Verificaciones documentales regulatorias públicas mediante FCA NSM.

Los rankings de analistas con observaciones reales permanecen como extensión
opcional: el usuario puede aportar entradas autorizadas, pero TargetAudit no
obliga a comprar Benzinga, Alpha Vantage, Nasdaq, NYSE ni S&P DJI para que el
repositorio sea ejecutable y útil.

```bash
PYTHONPATH=src python3 -m targetaudit open-edition \
  --registry data/samples/source_registry.csv \
  --report build/demo/open-edition.md \
  --html build/demo/open-edition.html \
  --as-of 2026-05-24
```

Ver [Open Edition](docs/open-edition.md) para el alcance gratuito y sus
límites metodológicos.

Quien decida pagar por datos reales puede revisar
[Extensiones Licenciadas Opcionales](docs/licensed-extensions.md). La opcion
con precio publico encontrada es Massive / Benzinga Analyst Ratings Expansion,
publicada a `USD 99/month` para uso individual. Ese acceso puede servir para
investigacion privada autorizada, pero no concede por si solo permiso para
publicar un ranking real compartido.

Tambien se evaluaron opciones mas economicas: MarketBeat All Access publica
`USD 249/year` o `USD 29/month` y WallStreetZen Premium publica
`USD 19.50/month` facturado anualmente. MarketBeat puede servir para un piloto
privado, pero anuncia exportacion de ratings de hasta seis meses recientes,
insuficiente para el ranking de targets con mas de un ano de antiguedad.
WallStreetZen es referencia de metodologia/rendimiento, no un feed historico
de targets confirmado para el motor.

Finnhub y Financial Modeling Prep ofrecen rutas programaticas potenciales
para consenso o targets, pero sus paginas oficiales no convierten el plan
gratis en permiso de publicacion: Finnhub situa redistribucion en Enterprise
y FMP exige un acuerdo especifico de display/licencia. TradingView puede
anadirse mas adelante como widget gratuito atribuido para contexto visual, no
como fuente de historial de analistas.

Tambien se realizo un barrido internacional en Reino Unido, Japon, Australia,
Hong Kong, Singapur y China continental. No aparecio un historial gratuito
publicable de targets individuales de firmas estadounidenses; si surgieron
rutas prometedoras para ampliar monitores regulatorios: el API oficial
gratuito de documentos de Japon (`EDINET`) ya cuenta con collector de ofertas
autenticado por clave gratuita, y
Singapur (`MAS OPERA`) requiere confirmar un endpoint abierto concreto. Tambien
surgio un laboratorio de precios japoneses
mediante el plan gratis de JPX `J-Quants`, sujeto a confirmar derechos de
output. Ver
[Busqueda Internacional De Datos Gratuitos](docs/international-data-search.md).

La segunda ronda, concluida el `2026-05-25`, reviso India, Mexico, Brasil,
Argentina, Alemania, Suiza, Paises Bajos e Italia. Brasil `CVM Dados Abertos`
ya se implemento para ofertas de acciones bajo ODbL; el registro europeo
`ESMA Prospectus III` ya se implemento para valores clasificados como acciones
en Alemania, Paises Bajos e Italia bajo reproduccion atribuida. `BMV` Mexico no
se conecta porque sus terminos prohiben parsing y reproduccion sin permiso
escrito. Ver
[Busqueda Internacional Gratuita: Ronda 2](docs/international-data-search-round-2.md).

El deep dive de Tokio, Toronto y Frankfurt mejoro las reglas de evidencia:
Japon combinara documentos `EDINET` con confirmacion de listings de
`JPX New Listings`; Toronto conserva el feed `TSX` de cotizaciones completadas
pero no automatiza `SEDAR+` por sus restricciones; Frankfurt queda cubierto
por `ESMA` con `BaFin` como corroboracion nacional. Ver
[Deep Dive: Tokio, Toronto Y Frankfurt](docs/market-deep-dive-tokyo-toronto-frankfurt.md).

La revision final de brechas del `2026-05-25` encontro una nueva ruta
defendible en Corea del Sur: `Korea OpenDART Equity Offering Watch` ya
monitoriza disclosures `C001` y `C006` mediante Open API con clave gratuita.
La revisión de `KRX OPEN API` confirmó que sus datos no deben entregarse a
terceros, por lo que no se publican en el dashboard abierto. Arabia
Saudita, Emiratos y Sudafrica quedaron en observacion por falta de un camino
gratuito reutilizable confirmado. Ver
[Market Gap Review: Corea, Golfo Y Africa](docs/market-gap-review-korea-gulf-africa.md).

La investigacion de `RWA Watch` ya cubre 20 exchanges relevantes y
Pepperstone. `xStocks / Backed` documenta APIs sin autenticacion para
metadatos, precios, documentos legales y proof of reserves, pero sus terminos
revisados no sustentan recoleccion/republicacion automatizada en un producto
publico. Por eso TargetAudit incorpora un `RWA Watch Sandbox` con datos
sinteticos y mantiene xStocks/Backed y el venue Bybit bloqueados hasta
autorizacion escrita; Kraken tambien queda como referencia bloqueada por su
indisponibilidad oficial en Estados Unidos. `Ondo
Global Markets` documenta datos para display en aplicaciones, pero exige
onboarding y API key, asi que permanece como extension autorizada pendiente.
Gate y Bitget quedan como referencias pendientes de derechos de output.
Ver
[RWA Watch: Exchanges Y Fuentes Base](docs/rwa-watch-sources.md). Esta linea
no suministra ratings, price targets ni recomendaciones.

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

La cola de aprobaciones convierte esos bloqueos en expedientes concretos de
trabajo, sin cambiar por sí sola el estado de gobernanza:

```bash
PYTHONPATH=src python3 -m targetaudit provider-approvals \
  --registry data/samples/source_registry.csv \
  --approvals data/samples/provider_approval_queue.csv \
  --report build/live/provider-approvals.md \
  --html build/live/provider-approvals.html \
  --as-of YYYY-MM-DD
```

El expediente opcional sigue siete candidatos: Benzinga, Alpha Vantage,
Nasdaq Daily List, NYSE, S&P DJI, Finnhub y Financial Modeling Prep. Cuatro
son críticos para habilitar targets, precios, acciones corporativas y universo
histórico de un ranking real; ninguno está aprobado para salida pública
todavía, y ninguno es requisito para `Open Edition`.

Una revisión humana documentada genera copias actualizadas del registro y la
cola, manteniendo intactos los archivos base:

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

`approve_public_output` exige un enlace HTTPS de evidencia y una integración
`implemented` o `manual_verified`. Después de promover un proveedor, Readiness
y Release Center deben ejecutarse sobre el registro generado; una aprobación
aislada nunca autoriza publicar una corrida.

La vista de preparación del scorecard traduce esas reglas en requisitos de
publicación para `U.S. Financials`:

```bash
PYTHONPATH=src python3 -m targetaudit scorecard-readiness \
  --registry data/samples/source_registry.csv \
  --report build/live/scorecard-readiness.md \
  --html build/live/scorecard-readiness.html \
  --as-of YYYY-MM-DD
```

El demo prueba el flujo, pero no cuenta como fuente productiva. Mientras no
existan targets históricos, precios ajustados, cobertura de acciones
corporativas y membresía histórica del universo aprobados para salida pública,
el scorecard real permanece deshabilitado.

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

### Evidencia De Precios Ajustados Opcional

Como extensión no requerida por `Open Edition`, TargetAudit incorpora un
adaptador cache-first para `Alpha Vantage Daily
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
- `JPX` / Japon: monitores `JPX New Listings` y `EDINET` con diff diario separado para confirmaciones de Tokio y filings de oferta con clave gratuita.
- `CVM` / Brasil: monitor oficial ODbL de ofertas publicas de acciones y diff diario; requiere evidencia B3 separada para confirmar listing.
- `ESMA` / Union Europea: monitor oficial atribuible de prospectos para acciones en Alemania, Paises Bajos e Italia; no confirma primera negociacion.
- `KRX` / Corea del Sur: monitor `OpenDART` implementado para filings de oferta de capital `C001`/`C006` con clave gratuita; KRX no se republica por sus restricciones a terceros.
- `MOEX` / Rusia: `Bank of Russia` y `MOEX ISS` identificados, solo investigacion restringida por sanciones vigentes.

Hong Kong ya incluye un conector a los JSON oficiales de HKEXnews para
solicitudes activas, activas con `PHIP`, inactivas, listadas y devueltas.
Londres ya lee el componente JSON oficial de `Upcoming issues` y puede
cruzar cada emisor con documentos públicos del FCA NSM. Una coincidencia
queda para revisión: no se convierte automáticamente en admisión confirmada.
Australia ya lee la tabla oficial ASX de solicitudes formales y separa
listados anticipados de retiros publicados.
Canada ya lee `TSX New Company Listings` como comprobación de cotizaciones
completadas; no lo usa para predecir solicitudes futuras ni automatiza
`SEDAR+`, cuyos terminos prohíben scraping y bases de datos públicas.
Singapur ya consulta el catálogo JSON oficial `SGX IPO Prospectus`; registra
documentos publicados para revisión y no confirma automáticamente una
cotización completada.
Japon ya tiene dos capas: `EDINET` filtra securities registration statements,
enmiendas y retiros desde el API oficial, mientras `JPX New Listings` confirma
fechas de aprobacion o listing en Tokio. Ambas capas ya entran al historial
comparativo diario con estados separados para que un filing no se presente
como cotizacion.
Brasil ya cuenta con `CVM Equity Offering Watch`: lee el ZIP diario abierto
de `CVM Dados Abertos`, filtra ofertas de acciones y las incorpora al diff
diario. El registro es evidencia regulatoria, no confirmacion de cotizacion
en B3. La Union Europea ya cuenta con `ESMA Equity Prospectus Watch`: consulta
`Prospectus III Securities`, conserva solamente `SHRS` en Alemania, Paises
Bajos e Italia y marca cada documento para revision sin afirmar trading.
Corea del Sur ya cuenta con `Korea OpenDART Equity Offering Watch`: consulta
filings `C001` y `C006` del API oficial con clave gratuita y los marca para
revisión sin afirmar IPO o listing. `KRX OPEN API` no se integra al output
público porque los términos revisados prohíben proporcionar sus datos a terceros.
Rusia queda visible pero no activada: el Banco de Rusia anuncio un registro
oficial de valores el `2025-09-03` y `MOEX ISS` expone datos tecnicamente
utiles, pero OFAC designo `MOEX`, `NCC` y `NSD` el `2024-06-12`. No se
implementara ingesta ni orientacion de posiciones sin revision legal.

Detalle: [Market Gap Review: Rusia](docs/market-gap-review-russia.md).

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

Para leer aprobaciones y confirmaciones JPX en vivo:

```bash
PYTHONPATH=src python3 -m targetaudit jpx-monitor \
  --output data/raw/global/jpx-monitor.csv \
  --report build/live/jpx-monitor.md \
  --html build/live/jpx-monitor.html
```

Para leer filings de oferta EDINET en vivo se necesita una clave gratuita
emitida por la FSA, guardada fuera de Git:

```bash
export TARGETAUDIT_EDINET_API_KEY="tu-clave-privada"
PYTHONPATH=src python3 -m targetaudit edinet-monitor \
  --filing-date YYYY-MM-DD \
  --output data/raw/global/edinet-monitor.csv \
  --report build/live/edinet-monitor.md \
  --html build/live/edinet-monitor.html \
  --as-of YYYY-MM-DD
```

Para leer ofertas publicas de acciones de Brasil desde el ZIP diario ODbL de
CVM, sin clave:

```bash
PYTHONPATH=src python3 -m targetaudit cvm-monitor \
  --since YYYY-MM-DD \
  --output data/raw/global/cvm-monitor.csv \
  --report build/live/cvm-monitor.md \
  --html build/live/cvm-monitor.html \
  --as-of YYYY-MM-DD
```

El resultado abre revision regulatoria; no confirma admision ni primera
negociacion en B3.

Para leer prospectos europeos asociados a acciones desde ESMA, sin clave:

```bash
PYTHONPATH=src python3 -m targetaudit esma-monitor \
  --since YYYY-MM-DD \
  --output data/raw/global/esma-monitor.csv \
  --report build/live/esma-monitor.md \
  --html build/live/esma-monitor.html \
  --as-of YYYY-MM-DD
```

El monitor usa el registro oficial `Prospectus III Securities` y filtra
`SHRS`; un registro de admision inicial sigue siendo evidencia para revision,
no confirmacion de primera negociacion.

Para leer filings coreanos de oferta de capital desde OpenDART se necesita
una clave gratuita del operador, guardada fuera de Git:

```bash
export TARGETAUDIT_OPENDART_API_KEY="tu-clave-privada"
PYTHONPATH=src python3 -m targetaudit opendart-monitor \
  --since YYYY-MM-DD \
  --output data/raw/global/opendart-monitor.csv \
  --report build/live/opendart-monitor.md \
  --html build/live/opendart-monitor.html \
  --as-of YYYY-MM-DD
```

El monitor consulta únicamente `C001` y `C006`: un resultado abre revisión
regulatoria, no confirma IPO, listing o primera negociación en KRX.

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
  --jpx data/raw/global/jpx-monitor.csv \
  --edinet data/raw/global/edinet-monitor.csv \
  --cvm data/raw/global/cvm-monitor.csv \
  --esma data/raw/global/esma-monitor.csv \
  --opendart data/raw/global/opendart-monitor.csv \
  --sgx data/raw/global/sgx-monitor.csv \
  --history-dir data/raw/global/history \
  --output build/live/global-alerts.csv \
  --report build/live/global-alerts.md \
  --html build/live/global-alerts.html
```

`global-alerts` clasifica diferencias como nuevas, modificadas o removidas
del feed para revisión. EDINET, CVM, ESMA y OpenDART entran como evidencia regulatoria
temprana; JPX confirma hitos japoneses de listing, B3 requerira evidencia
separada para Brasil y ESMA no confirma primera negociacion europea. Una
remoción no confirma retiro, admisión ni inicio de negociación.

## ETF Holdings Activity

La primera pagina ETF ya es ejecutable con snapshots normalizados y una demo
sintetica reproducible. Compara posiciones nuevas, aumentadas, reducidas,
removidas o con variacion de peso, conservando fecha efectiva, frecuencia y
enlace de evidencia.

```bash
PYTHONPATH=src python3 -m targetaudit etf-holdings-activity \
  --previous data/samples/etf-holdings-previous.csv \
  --current data/samples/etf-holdings-current.csv \
  --output build/demo/etf-holdings-activity.csv \
  --report build/demo/etf-holdings-activity.md \
  --html build/demo/etf-holdings-activity.html \
  --as-of 2026-05-24
```

Los datos incluidos son sinteticos: todavia falta habilitar publicacion
abierta de descargas oficiales. Ya existe un importador local de CSV
descargados desde ARK:

```bash
PYTHONPATH=src python3 -m targetaudit ark-holdings-import \
  --snapshot data/raw/etf/ARKK_HOLDINGS.csv \
  --fund-symbol ARKK \
  --fund-name "ARK Innovation ETF" \
  --captured-on YYYY-MM-DD \
  --output data/raw/etf/arkk-normalized.csv \
  --report build/live/arkk-import.md
```

ARK declara actualizacion al cierre de cada dia habil y explica que la fecha
del CSV corresponde al siguiente dia de negociacion. El adaptador conserva
esa fecha como efectiva, pero no redistribuye holdings oficiales en el
repositorio: la publicacion real requiere resolver los terminos de uso.
La automatizacion autorizada de State Street SPDR sigue pendiente; `SEC
N-PORT` ya se procesa como respaldo regulatorio historico, no como fuente en
tiempo real. Un aumento o reduccion se presenta como cambio observado, no
como compra o venta confirmada del gestor.

Para el ETF sectorial que sirve como benchmark del proyecto, tambien existe
un importador local State Street SPDR/XLF:

```bash
PYTHONPATH=src python3 -m targetaudit spdr-holdings-import \
  --snapshot data/raw/etf/XLF_HOLDINGS.csv \
  --fund-symbol XLF \
  --fund-name "State Street Financial Select Sector SPDR ETF" \
  --captured-on YYYY-MM-DD \
  --output data/raw/etf/xlf-normalized.csv \
  --report build/live/xlf-import.md
```

La pagina oficial de `XLF` identifica la descarga completa de holdings como
diaria y muestra acciones mantenidas y peso. La misma pagina restringe
reproduccion sin consentimiento escrito, por lo que el repositorio usa
fixtures sinteticos y mantiene salidas reales solo en almacenamiento local.

Como segundo ETF financiero, el proyecto admite archivos descargados
manualmente de `IYF`, iShares U.S. Financials ETF:

```bash
PYTHONPATH=src python3 -m targetaudit ishares-holdings-import \
  --snapshot data/raw/etf/IYF_HOLDINGS.csv \
  --fund-symbol IYF \
  --fund-name "iShares U.S. Financials ETF" \
  --captured-on YYYY-MM-DD \
  --output data/raw/etf/iyf-normalized.csv \
  --report build/live/iyf-import.md
```

La pagina oficial de iShares describe `IYF` como exposicion a acciones
financieras estadounidenses y publica holdings con acciones y peso. Sus
terminos prohíben a agentes automaticos monitorizar o copiar materiales sin
permiso, por lo que TargetAudit solo implementa importacion manual local y no
programa descargas de iShares.

La capa historica regulatoria tambien esta implementada mediante filings
publicos `SEC NPORT-P` en XML. Para recolectar el filing reciente de una
serie desde EDGAR y conservar una copia local validada:

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

`N-PORT` se muestra por separado como evidencia `regulatory_periodic`: la SEC
indica que los datasets publicos provienen de filings difundidos y se
actualizan trimestralmente. La primera version normaliza solo posiciones
declaradas en acciones y registra los instrumentos omitidos. El colector
consulta la ventana reciente de submissions del registrante por `CIK` y solo
archiva el XML cuyo contenido confirma la `seriesId` solicitada. Para un
archivo ya descargado sigue disponible `sec-nport-import`.
Los identificadores `XLF` anteriores fueron confirmados en un filing
`NPORT-P` oficial de `SELECT SECTOR SPDR TRUST`.

Para reconstruir varios periodos desde ZIP trimestrales SEC extraidos
localmente, se puede repetir `--dataset-dir` por trimestre:

```bash
export TARGETAUDIT_SEC_USER_AGENT="TargetAudit tu-correo@ejemplo.com"
PYTHONPATH=src python3 -m targetaudit sec-nport-datasets \
  --output build/live/nport-dataset-catalog.csv \
  --report build/live/nport-dataset-catalog.md \
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

`sec-nport-datasets` mantiene el ZIP en almacenamiento local y extrae solo
las cinco tablas necesarias para el backfill. El backfill las une por
accession y holding, conserva un snapshot por `REPORT_DATE` y se detiene si
aparecen periodos duplicados que puedan corresponder a enmiendas.

Para monitorear nuevas publicaciones trimestrales sin volver a descargar
periodos ya conocidos:

```bash
PYTHONPATH=src python3 -m targetaudit sec-nport-sync \
  --state data/raw/etf/nport/sync-state.csv \
  --storage-dir data/raw/etf/nport/datasets \
  --report build/live/nport-sync.md \
  --as-of YYYY-MM-DD \
  --series-id S000006411 \
  --fund-symbol XLF \
  --data-set-label "SEC N-PORT synchronized extracts" \
  --output-dir data/raw/etf/nport/backfill/xlf \
  --manifest build/live/xlf-nport-backfill.csv \
  --backfill-report build/live/xlf-nport-backfill.md
```

La primera ejecucion de `sec-nport-sync` registra el catalogo como linea base
y no descarga automaticamente todo el historico. En ejecuciones posteriores,
solo descarga releases que la SEC publique despues de esa linea base; si se
incluye una serie, regenera sus periodos a partir de los trimestres disponibles
localmente.

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
- Excluye targets reemplazados por una revision posterior de la misma firma y
  accion, registrando la cadena sin contarlos como fallos.
- Simula salida al target o al vencimiento con costos configurables y muestra
  retorno neto frente al benchmark en la misma fecha de salida.
- Desglosa resultados entre targets alcistas y bajistas.
- Genera un ranking que muestra el numero de observaciones y aplica una muestra
  minima configurable.
- Incluye datos sinteticos y pruebas automatizadas; no distribuye datos
  comerciales.
- Genera un reporte inicial de `IPO Watch` con estado y fuentes auditables.
- Marca splits y cambios de ticker documentados antes de puntuar targets.
- Publica un registro de gobernanza de proveedores, licencias y uso permitido.
- Genera una pagina `ETF Holdings Activity` para diferencias auditables entre
  snapshots, con una demo sintetica y limites de interpretacion visibles.
- Normaliza descargas locales de holdings ARK al esquema ETF, manteniendo
  bloqueada la redistribucion publica de datos oficiales hasta revisar permiso.
- Normaliza descargas locales SPDR/XLF y usa un fixture `XLF-DEMO` para probar
  actividad ETF alineada con la especializacion en financials.
- Normaliza descargas manuales iShares/IYF y usa un fixture `IYF-DEMO`, dejando
  bloqueada la recoleccion automatica por los terminos oficiales.
- Normaliza filings publicos `SEC NPORT-P` en una salida regulatoria ETF
  separada, los recolecta por `CIK`/`seriesId` desde EDGAR y omite
  instrumentos aun no modelados de forma visible.
- Reconstruye periodos historicos ETF desde datasets trimestrales SEC
  extraidos, con manifiesto de accession y control de enmiendas.
- Cataloga y descarga por trimestre los ZIP SEC `N-PORT`, manteniendo los
  archivos grandes fuera del repositorio publico.
- Sincroniza incrementalmente publicaciones trimestrales `N-PORT`, con estado
  local atomico y regeneracion opcional de una serie ETF.
- Importa exportaciones autorizadas de targets con manifiesto y cola de rechazos.

La edición abierta ya es funcional como sandbox auditado y monitor regulatorio
gratuito. No es un ranking real de mercado listo para decisiones de inversion:
para publicar resultados de analistas reales hacen falta observaciones
autorizadas y precios ajustados cuyo uso público esté permitido.

## Almacen Local De Corridas

Para conservar resultados consultables por la futura API, instala la capacidad
opcional DuckDB y agrega `--database` a `evaluate`:

```bash
python3 -m pip install -e ".[warehouse]"
PYTHONPATH=src python3 -m targetaudit evaluate \
  --targets data/samples/targets.csv \
  --prices data/samples/prices.csv \
  --universe-membership data/samples/historical_universe.csv \
  --prices-provider-id synthetic-demo \
  --universe-provider-id synthetic-demo \
  --output build/demo/evaluations-warehouse.csv \
  --report build/demo/report-warehouse.md \
  --database build/demo/targetaudit.duckdb \
  --run-id demo-financials-2025-01-01 \
  --dataset-label "Synthetic Financials evaluation" \
  --minimum-sample 1 \
  --as-of 2025-01-01
```

La base registra parametros de la corrida, version metodologica, resultados
tipados y hashes SHA-256 de los archivos de entrada y salida. Tambien deriva
una `dataset_fingerprint` estable solo a partir de las entradas, para comparar
corridas sin confundir evidencia con reportes regenerados; la huella también
cambia si varía el proveedor declarado de un activo. Un `run-id` existente se
rechaza para evitar que una evidencia anterior sea reemplazada silenciosamente.
Las corridas destinadas a revisión pública deben declarar
`--prices-provider-id`, `--corporate-actions-provider-id` y
`--universe-provider-id` cuando esos activos existen; `Release Center`
contrasta esos identificadores con las políticas aprobadas del registro.

## API De Lectura

La primera API FastAPI sirve únicamente resultados ya almacenados en DuckDB.
No recolecta datos ni habilita la publicación de fuentes pendientes de licencia.
El registro transversal de gobernanza se consulta desde el CSV validado
configurable mediante `TARGETAUDIT_SOURCE_REGISTRY`.

```bash
python3 -m pip install -e ".[application]"
export TARGETAUDIT_DATABASE="build/demo/targetaudit.duckdb"
export TARGETAUDIT_SOURCE_REGISTRY="data/samples/source_registry.csv"
export TARGETAUDIT_PROVIDER_APPROVALS="data/samples/provider_approval_queue.csv"
export TARGETAUDIT_GENERATED_REPORTS="build/demo"
export TARGETAUDIT_LICENSED_EXTENSIONS="data/samples/licensed_extensions.csv"
python3 -m uvicorn targetaudit.api:app --host 127.0.0.1 --port 8000
```

Al abrir `http://127.0.0.1:8000/` se muestra la portada `Open Edition`, que
distingue capacidades gratuitas y extensiones opcionales. La ruta
`/dashboard/extensions` presenta proveedores que un usuario puede contratar
por su cuenta, sus precios visibles y los derechos que aun bloquean la
publicacion de rankings reales. La ruta
`/dashboard/financials` muestra `Financials Scorecard`, conectado a las
corridas almacenadas. Incluye filtros
de sector, direccion y muestra minima, detalle por firma/ticker y auditoria de
exclusiones. La ficha de ticker incluye una linea temporal de hitos retenidos
(referencia, entrada, target y salida/terminal) y deja visible que no representa
una serie diaria de mercado. El demo almacena corridas separadas para el
scorecard principal, targets revisados y guardas por acciones corporativas.
El panel `Compare Stored Runs` contrasta corridas con su version de metodologia
y huella de entradas; una diferencia de evidencia se muestra antes de comparar
los conteos. La API ofrece el mismo control en `/api/v1/runs/compare`.
La ruta `/dashboard/governance` presenta controles de fuente y observaciones
excluidas o pendientes por corrida. Las nuevas evaluaciones conservan
`provider_id` y enlazan su control de publicacion; resultados historicos sin
ese campo se identifican como `unlinked` en vez de inferirlo por la URL.
La ruta `/dashboard/approvals` presenta el expediente de permisos pendiente
por proveedor y los cuatro controles críticos que aún bloquean el scorecard
público.
La ruta `/dashboard/operations` presenta el monitor de calidad de corridas:
revisa sellos reproducibles, entradas obligatorias, linaje de proveedor y
tasas altas de exclusion. Pasar este monitor no autoriza publicar fuentes que
aun requieran licencia o revision de terminos.
La ruta `/dashboard/readiness` presenta los requisitos del scorecard público
antes de que exista una corrida: separa fixtures del demo, integraciones de
uso interno y fuentes productivas con política de publicación aprobada.

Para una actualización automatizada del scorecard, la corrida candidata se
puede detener antes de publicarla:

```bash
PYTHONPATH=src python3 -m targetaudit operations-quality \
  --database build/live/targetaudit.duckdb \
  --run-id RUN-ID \
  --report build/live/operations-quality.md \
  --html build/live/operations-quality.html \
  --public-release \
  --require-quality-pass \
  --as-of YYYY-MM-DD
```

El informe se escribe aunque la compuerta falle; un estado `blocked` o
`review_required` devuelve código de salida `2` para detener el pipeline.
El modo `--public-release` exige que la corrida conserve `targets`, `prices`,
`corporate_actions` y `universe_membership`; pasarla tampoco reemplaza la
aprobación de fuentes en `Scorecard Readiness`.

Para una decisión final única, `Release Center` combina fuentes, linaje de las
observaciones, procedencia de los activos y calidad de publicación. Una
observación o archivo enlazado a un fixture demo o a un proveedor no aprobado
bloquea la salida aunque existan fuentes candidatas en el registro:

```bash
PYTHONPATH=src python3 -m targetaudit scorecard-release \
  --registry data/samples/source_registry.csv \
  --database build/live/targetaudit.duckdb \
  --run-id RUN-ID \
  --report build/live/scorecard-release.md \
  --html build/live/scorecard-release.html \
  --require-release-ready \
  --as-of YYYY-MM-DD
```

Endpoints iniciales:

| Ruta | Uso |
|---|---|
| `/api/v1/health` | Estado y versión metodológica |
| `/api/v1/open-edition` | Capacidades ejecutables sin suscripciones pagadas y límites declarados |
| `/dashboard/open` | Portada de la edición gratuita de GitHub |
| `/api/v1/extensions/licensed` | Opciones de datos pagados por el usuario, precio visible y restricciones de publicación |
| `/dashboard/extensions` | Página de extensiones opcionales `bring your own license` |
| `/dashboard/ipo-watch` | Reporte generado de vigilancia SEC de filings IPO |
| `/dashboard/etf-regulatory` | Actividad regulatoria ETF basada en periodos N-PORT |
| `/dashboard/document-checks` | Verificaciones documentales regulatorias generadas |
| `/api/v1/runs` | Corridas almacenadas |
| `/api/v1/runs/{run_id}` | Parámetros y hashes de evidencia de una corrida |
| `/api/v1/runs/{run_id}/facets` | Sectores, firmas y tickers para filtros |
| `/api/v1/runs/{run_id}/rankings/firms` | Ranking, con filtros `sector`, `direction` y `minimum_sample` |
| `/api/v1/runs/{run_id}/firms/{firm}` | Observaciones y resumen de una firma |
| `/api/v1/runs/{run_id}/tickers/{ticker}` | Historial evaluado de una acción |
| `/api/v1/runs/{run_id}/tickers/{ticker}/timeline` | Hitos de evidencia retenidos para la visualización |
| `/api/v1/runs/{run_id}/audit/exclusions` | Excluidos y pendientes con motivo |
| `/api/v1/runs/{run_id}/export/evaluations.csv` | Descarga CSV de observaciones de la corrida |
| `/api/v1/runs/{run_id}/export/rankings-firms.csv` | Descarga CSV del ranking con los mismos filtros |
| `/api/v1/governance/sources` | Registro de fuentes y controles de publicacion, filtrable por estado y clase |
| `/dashboard/governance` | Pagina de auditoria de fuentes y observaciones excluidas |
| `/api/v1/governance/approvals` | Cola de permisos, evidencia requerida y controles críticos de activación pública |
| `/dashboard/approvals` | Expedientes de aprobación de proveedores pendientes o resueltos |
| `/api/v1/readiness/scorecard` | Requisitos de fuentes productivas para publicar el Financials Scorecard |
| `/dashboard/readiness` | Pagina de preparación y bloqueos de publicación del scorecard |
| `/api/v1/operations/quality?run_id=RUN-ID&public_release=true` | Monitor operativo o compuerta de publicación de una corrida candidata, con umbral configurable de exclusiones |
| `/dashboard/operations` | Pagina operativa de corridas aprobadas, en revision o bloqueadas |
| `/api/v1/releases/scorecard?run_id=RUN-ID` | Decisión combinada de publicación: fuentes, linaje de observaciones, procedencia de activos y calidad |
| `/dashboard/release` | Release Center para inspeccionar una corrida candidata antes de distribuirla |

La documentación interactiva local queda disponible en `/docs` al iniciar el
servidor. La API omite las rutas locales de los archivos originales y presenta
únicamente sus hashes y tamaños como evidencia reproducible.

## Inicio Rapido

Requiere Python 3.9 o superior. El motor CLI básico puede ejecutarse sin
paquetes externos; la verificación completa instala la capa de aplicación
porque genera DuckDB y prueba la API/dashboard:

```bash
python3 -m pip install -e ".[application]"
make verify
```

La verificacion ejecuta pruebas, construye el demo y genera un paquete
instalable. Escribe:

```text
build/demo/evaluations.csv
build/demo/report.md
build/demo/targetaudit.duckdb
build/demo/authorized-targets.csv
build/demo/authorized-targets-audit.csv
build/demo/authorized-targets-import.md
build/demo/authorized-targets-import.html
build/demo/report-target-revisions.md
build/demo/evaluations-target-revisions.csv
build/demo/source-registry.md
build/demo/source-registry.html
build/demo/open-edition.md
build/demo/open-edition.html
build/demo/licensed-extensions.md
build/demo/licensed-extensions.html
build/demo/provider-approvals.md
build/demo/provider-approvals.html
build/demo/provider-reviewed-source-registry.csv
build/demo/provider-reviewed-approval-queue.csv
build/demo/provider-approval-review-outcomes.csv
build/demo/provider-approval-review-outcomes.md
build/demo/provider-approval-review-outcomes.html
build/demo/scorecard-readiness.md
build/demo/scorecard-readiness.html
build/demo/scorecard-release.md
build/demo/scorecard-release.html
build/demo/alpha-vantage-prices.csv
build/demo/alpha-vantage-prices.md
build/demo/alpha-vantage-prices.html
build/demo/corporate-actions.csv
build/demo/corporate-actions.md
build/demo/corporate-actions.html
build/demo/evaluations-actions-guarded.csv
build/demo/report-actions-guarded.md
build/demo/operations-quality.md
build/demo/operations-quality.html
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
build/demo/jpx-monitor.csv
build/demo/jpx-monitor.md
build/demo/jpx-monitor.html
build/demo/edinet-monitor.csv
build/demo/edinet-monitor.md
build/demo/edinet-monitor.html
build/demo/cvm-monitor.csv
build/demo/cvm-monitor.md
build/demo/cvm-monitor.html
build/demo/esma-monitor.csv
build/demo/esma-monitor.md
build/demo/esma-monitor.html
build/demo/opendart-monitor.csv
build/demo/opendart-monitor.md
build/demo/opendart-monitor.html
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
  --transaction-cost-bps 10 \
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
.github/ISSUE_TEMPLATE/ Formularios para bugs y nuevas fuentes con permisos documentados
SECURITY.md              Reporte privado y manejo de credenciales/datos locales
```

## Siguientes Versiones

- `v0.3`: rigor cuantitativo, incluyendo intervalos, segmentos y control de
  integrantes historicos del universo.
- `v0.4`: base DuckDB y API FastAPI de solo lectura para corridas auditables,
  seguidas por el dashboard web.
- `v0.5`: dashboard web, filtros por sector y paginas de firma/accion.
- `v1.0`: Open Edition publica, reproducible y sin costo de datos; rankings
  reales quedan como extension opcional con entradas autorizadas.

Consulta [la metodologia](docs/methodology.md),
[las fuentes evaluadas](docs/data-sources.md) y
[la estrategia de producto](docs/product-strategy.md), junto con el alcance
[Open Edition](docs/open-edition.md). El progreso tecnico se
mantiene en [el roadmap](docs/roadmap.md) y la ejecucion continua en
[operations.md](docs/operations.md). Para colaborar, consulta
[CONTRIBUTING.md](CONTRIBUTING.md) y la politica de [seguridad](SECURITY.md).
La investigacion de nuevas fuentes internacionales se conserva en
[international-data-search.md](docs/international-data-search.md) y
[international-data-search-round-2.md](docs/international-data-search-round-2.md).
El refinamiento de mercados ya mapeados esta en
[market-deep-dive-tokyo-toronto-frankfurt.md](docs/market-deep-dive-tokyo-toronto-frankfurt.md).
La ultima revision de brechas se conserva en
[market-gap-review-korea-gulf-africa.md](docs/market-gap-review-korea-gulf-africa.md).

## Aviso

TargetAudit es software de investigacion. No ofrece asesoramiento financiero ni
recomendaciones de compra o venta. Ver [DISCLAIMER.md](DISCLAIMER.md).

## Licencia

El codigo se publica bajo la licencia MIT. Los datos de terceros mantienen sus
propias licencias y no quedan cubiertos por la licencia del codigo.
