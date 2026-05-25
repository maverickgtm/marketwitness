# Dashboard Product Outline

TargetAudit tendra dos paginas principales. No comparten score: una evalua
pronosticos ya medibles y la otra sigue eventos de companias que pueden llegar
al mercado.

Con la expansion internacional y los controles de publicación, el producto
tiene páginas operativas adicionales, incluida la página de actividad
publicada de ETF:

## Pagina: RWA Watch Sandbox

Objetivo: demostrar gratis como se auditarian activos tokenizados sin
recolectar ni republicar un feed cuya licencia no este aprobada.

- La ruta `/dashboard/rwa-watch` presenta observaciones sinteticas creadas por
  TargetAudit, comparando precio de referencia contra precio token/venue.
- Muestra red, venue, modelo emisor, estado de respaldo y desviaciones que
  ameritarian revision.
- Explica que `xStocks / Backed` queda bloqueado para ingestion publica por
  sus terminos revisados, pese a documentar endpoints sin autenticacion.
- No emite posiciones recomendadas ni mezcla el modulo con analyst targets.

## Portada: Open Edition

Objetivo: mostrar desde el primer acceso que la versión GitHub funciona sin
comprar datos comerciales.

- La raíz `/` y `/dashboard/open` consumen `/api/v1/open-edition`.
- Distingue un sandbox offline con fixtures redistribuibles, monitores
  regulatorios públicos sin cuota de datos y extensiones autorizadas
  opcionales.
- Presenta SEC IPO Watch y SEC N-PORT como capacidades gratuitas con límites
  visibles, incluida la identificación `User-Agent` exigida para solicitudes
  SEC live.
- Enlaza reportes generados autorizados mediante `/dashboard/ipo-watch`,
  `/dashboard/etf-regulatory` y `/dashboard/document-checks`; la API no expone
  archivos arbitrarios de la carpeta de construcción.
- El ranking real de analistas permanece como ampliación voluntaria y nunca
  como condición para usar la edición pública.

## Pagina: Licensed Extensions

Objetivo: permitir que el usuario decida si desea contratar datos reales, sin
confundir un precio disponible con derechos de publicacion publica.

- La ruta `/dashboard/extensions` consume `/api/v1/extensions/licensed`.
- Muestra la expansion Massive / Benzinga con el precio publicado
  `USD 99/month`, MarketBeat `USD 249/year` o `USD 29/month`,
  WallStreetZen `USD 19.50/month` facturado anualmente y rutas sujetas a
  cotizacion.
- Identifica a MarketBeat como posible piloto privado de bajo costo, pero
  muestra que sus exportaciones anunciadas de hasta seis meses no bastan para
  evaluar targets vencidos a un ano.
- Identifica a WallStreetZen como benchmark privado de rankings existentes,
  no como feed historico confirmado para ingestion.
- Registra Finnhub y Financial Modeling Prep como rutas programaticas futuras,
  mostrando que los derechos de display o redistribucion requieren acuerdo.
- Mantiene TradingView como posible widget de contexto visual atribuido,
  separado de la ingesta de targets y del ranking.
- Mantiene `xStocks / Backed`, `Ondo` y sus venues fuera de esta pagina:
  pertenecen a un eventual monitor `RWA Watch`, no a las fuentes de price
  targets de analistas.
- Expone enlaces oficiales a producto, precio y terminos.
- Mantiene el contador de proveedores aprobados para output publico en cero
  mientras no exista permiso escrito.
- Permite planificar una importacion local autorizada, pero no recolecta datos
  comprados ni habilita un leaderboard publico.

## API De Aplicacion

La capa inicial FastAPI consulta exclusivamente corridas guardadas en DuckDB.
Expone salud metodologica, inventario/detalle de corridas, ranking de firmas,
ficha de firma, ficha de ticker y auditoria de observaciones excluidas o
pendientes. Las respuestas de evidencia incluyen hashes de artefactos, no
rutas privadas del operador.

Esta API puede alimentar el dashboard web con datos sinteticos o autorizados.
Una base que contenga datos reales no debe exponerse publicamente hasta
resolver los permisos de targets, precios y cualquier fuente redistribuida.

## Aplicacion Financials Scorecard

La ruta web inicial `/dashboard/financials` consume esta API y presenta:

- Tarjetas de observaciones evaluadas, excluidas y pendientes.
- Ranking de firmas con tasa de acierto, intervalo Wilson 95%, mediana de
  dias al target y exceso neto.
- Filtros por corrida, sector, direccion y muestra minima.
- Panel de firma/ticker con enlace de evidencia.
- Linea temporal visual de los hitos retenidos por observacion; no se presenta
  como una serie diaria de precios.
- Exportacion CSV de observaciones y del ranking filtrado.
- Comparacion de corridas almacenadas con version metodologica, huella de
  entradas y diferencias de conteos antes de interpretar resultados.
- Tabla de exclusiones y pendientes por motivo.

El demo genera `build/demo/targetaudit.duckdb` con corridas sinteticas del
scorecard, revisiones y guardas de acciones corporativas para probar ranking y
exclusiones sin publicar datos comerciales.

La API expone `/api/v1/runs/compare?left_run_id=...&right_run_id=...`. Una
comparacion solo se identifica como la misma evidencia y metodologia cuando
coinciden ambos sellos; corridas heredadas sin sello permanecen visibles pero
no se marcan como equivalentes.

## Vista Transversal: Source Governance

Objetivo: hacer visible qué datos pueden alimentar un producto público y qué
fuentes aún requieren términos, licencia o exclusión expresa.

- La ruta web `/dashboard/governance` consume el registro validado y la
  auditoria de exclusiones almacenada por cada corrida.
- Registro de fuentes oficiales, candidatas comerciales y datos sintéticos.
- Estado de integración separado de estado de licencia/publicación.
- Bloqueo visible para fuentes que no deben recolectarse automáticamente.
- Enlace a la referencia oficial usada para cada decisión.
- Filtros por clase de dato y estado operativo, junto a la vista por corrida
  de observaciones excluidas y pendientes.

Las nuevas corridas guardan `provider_id` junto al enlace de evidencia y la
vista muestra el control de publicacion enlazado en cada exclusion o pendiente.
Entradas historicas sin ese linaje permanecen visibles como `unlinked`, sin
inferir una fuente por la URL.

## Vista De Aprobacion: Provider Approvals

Objetivo: convertir fuentes candidatas en una cola revisable de permisos antes
de permitir datos reales en una salida pública.

- La ruta web `/dashboard/approvals` consume
  `/api/v1/governance/approvals`.
- Muestra expedientes de Benzinga, Alpha Vantage, Nasdaq Daily List, NYSE y
  S&P DJI con evidencia requerida y criterio de promoción.
- Marca como críticos los candidatos necesarios para targets, precios,
  acciones corporativas y membresía histórica del universo.
- Un expediente `approved_public_output` solo es válido si el registro de
  fuentes también declara una política compatible con salida pública.
- La cola documenta trabajo pendiente; no aprueba ni conecta una fuente
  automáticamente.
- El comando `provider-approval-review` produce una auditoría HTML y copias
  generadas del registro y la cola después de una decisión humana; estas
  copias son las que deben evaluarse en Readiness.

## Vista De Preparacion: Scorecard Readiness

Objetivo: impedir que un dashboard tecnicamente funcional sea confundido con
un producto listo para publicar resultados reales.

- La ruta web `/dashboard/readiness` consume `/api/v1/readiness/scorecard`.
- Evalua los requisitos productivos de `Analyst targets`, `Adjusted price
  bars`, `Corporate actions` y `Historical universe membership` para el
  enfoque `U.S. Financials`.
- Excluye expresamente los fixtures del demo como fuentes productivas.
- Distingue una integración `internal_only` de una fuente
  `public_ready` con política de publicación aprobada.
- Conserva el scorecard público deshabilitado mientras cualquiera de sus
  controles obligatorios no tenga una fuente apta.

## Vista Operativa: Operations Quality

Objetivo: impedir que una tarea recurrente publique o destaque una corrida
incompleta sin hacer visible el problema.

- La ruta `/dashboard/operations` consume
  `/api/v1/operations/quality?maximum_excluded_rate=...`.
- Valida que cada corrida tenga version metodologica y huella del dataset.
- Exige activos de entrada `targets` y `prices` antes de considerarla completa.
- El control `Public release inputs` exige además activos
  `corporate_actions` y `universe_membership` para una corrida candidata a
  distribución.
- Bloquea resultados con observaciones sin `provider_id` declarado.
- Envia a revision corridas cuya tasa de exclusiones supera el umbral
  operativo o cuya muestra evaluada no alcanza el minimo configurado.
- Un estado `quality_pass` es solo un control tecnico; la autorizacion de
  publicacion permanece bajo `Source Governance`.

## Vista De Publicacion: Release Center

Objetivo: resolver en una sola decisión si una corrida candidata puede
alimentar un scorecard público.

- La ruta `/dashboard/release` consume
  `/api/v1/releases/scorecard?run_id=RUN-ID`.
- Combina `Scorecard Readiness` con `Operations Quality` en alcance
  `public_release`.
- Bloquea una corrida si sus observaciones declaran un `provider_id` que no
  corresponde a un proveedor de targets aprobado para salida pública.
- Exige que activos de precios, acciones corporativas y universo histórico
  declaren también el proveedor aprobado que los originó.
- Mantiene separados los estados de derechos de fuente, linaje de targets,
  procedencia de activos y calidad de evidencia.

## Pagina 1: Financials Scorecard

Objetivo: auditar `price targets` sobre financials de Estados Unidos.

Componentes:

- Ranking de firmas especialistas frente a generalistas.
- Intervalo Wilson 95% junto a cada tasa de acierto para hacer visible la
  incertidumbre de muestras pequenas.
- Rankings separados por sector y por direccion, con umbral de muestra en
  cada segmento.
- Control de universo historico: identifica la composicion aplicada y excluye
  targets que no pertenecian al universo en la fecha publicada.
- Auditoria de revisiones: muestra targets reemplazados por otra nota de la
  misma firma/accion y los retira del score.
- Resultado de estrategia: salida por target o vencimiento, costos declarados
  y retorno neto excedente frente a `XLF` sobre la misma fecha de salida.
- Filtros por banco, subindustria, periodo y direccion del target.
- Comparacion contra `XLF`.
- Tabla de observaciones excluidas y motivo.
- `Corporate Actions Audit`: cola de targets atravesados por splits o cambios
  de ticker, antes de entrar al ranking.
- `Adjusted Price Evidence`: importacion cache-first, formula de ajuste y
  estado de licencia de la fuente de precios.
- `Target Import Audit`: proveedor declarado, permiso de uso, filas aceptadas
  y rechazos antes de que entren al ranking.
- Ficha de cada pronostico con fuente, referencia, entrada y resultado.

## Pagina 2: IPO Watch

Objetivo: seguir eventos verificables de grandes IPOs tecnologicas y
estrategicas, sin convertir rumores en operaciones.

### Panel Superior

Tarjetas:

- `Filed publicly`: companias con prospecto publico verificable.
- `Listed`: IPO ya completada y disponible para seguimiento post-debut.
- `Candidates`: nombres importantes sin filing publico confirmado.
- `Changed this week`: novedades verificadas desde la ultima ejecucion.

### Tabla Principal

Campos:

| Campo | Uso |
|---|---|
| Compania | SpaceX, Cerebras, Anthropic, OpenAI, Canva, Kraken, Shein |
| Tema | Space/AI, AI hardware, foundation models, software, crypto, retail |
| Estado | `candidate_unverified`, `filed_public`, `listed`, `withdrawn` |
| Fecha verificada | Ultimo evento confirmado |
| Ticker/Exchange | Solo cuando este respaldado por fuente primaria |
| Proximo evento | Que documento o anuncio se espera comprobar |
| Riesgos | Riesgos del prospecto o pendientes de investigar |
| Fuente | Enlace auditable |

### Ficha De Compania

- Linea temporal de eventos y documentos.
- Acceso al filing o anuncio primario.
- Resumen de factores de riesgo documentados.
- Checklist de due diligence antes del debut.
- Seguimiento post-IPO: precio de oferta, apertura, 30/90/365 dias, una vez
  que haya datos permitidos.

## Politica De Posiciones

El dashboard no dira `comprar SpaceX` o `vender CBRS` por una noticia. Antes
de evaluar una posible estrategia debe existir:

1. Filing o cotizacion confirmada.
2. Prospecto revisado: riesgos, gobernanza, uso de fondos y lock-ups.
3. Precio de oferta o mercado observable.
4. Benchmark definido para la categoria.
5. Regla de entrada, salida, riesgo y tamano documentada.
6. Aviso claro de que el resultado es investigacion, no asesoria.

En lugar de posiciones, la pagina usa estados de investigacion:

- `Monitor`: candidato sin filing publico.
- `Review Filing`: prospecto publico; revisar antes de cualquier analisis.
- `Observe Listing`: debut confirmado; recolectar historial inicial.
- `Eligible for Study`: historial suficiente para un estudio definido.

## Automatizacion Prevista

- SEC EDGAR: detectar nuevos `S-1`, `S-1/A`, `424B4` y retiros para emisores
  conocidos; requiere un `User-Agent` con contacto real.
- Fuentes corporativas oficiales: comunicados de listing/closing.
- Noticias: solo como alerta de busqueda; nunca elevan estado sin confirmacion
  primaria.
- Historial de cambios: guardar fecha, estado previo, fuente y version del
  reporte.

### Descubrimiento Universal

La pagina no se limita a las siete companias semilla. Una cola interna
`SEC Discovery Queue` examina diariamente formularios publicos potencialmente
relacionados con IPO para cualquier emisor. Los casos nuevos aparecen en un
panel de revision; solo los confirmados pasan al tablero publico.

### Revision Manual De SEC

`SEC IPO Alerts` puede alimentar una copia actualizada de `IPO Watch` solo
despues de una decision documentada. La pantalla `IPO Watch Manual SEC
Reviews` muestra decision, resultado, estado anterior/nuevo y evidencia. El
flujo exige coincidencia exacta de URL de filing y `CIK`; descubrir un filing
no cambia por si solo el estado.

## Pagina 3: Global Listings Watch

Objetivo: extender la inteligencia de nuevas cotizaciones fuera de Estados
Unidos sin aplicar reglas SEC a jurisdicciones distintas.

### Cobertura Inicial

| Mercado | Fuente Oficial Identificada | Estado De Implementacion |
|---|---|---|
| London Stock Exchange | LSE `New issues` JSON y FCA National Storage Mechanism | Feed y clasificación FCA de prospectus/admission/intention implementados; admision requiere revision |
| Hong Kong HKEX | HKEX/HKEXnews AP/PHIP JSON feeds | Feed oficial implementado |
| Australian Securities Exchange | ASX `Upcoming floats and listings` | Feed HTML oficial implementado |
| Toronto Stock Exchange | TSX `New Company Listings` | Feed HTML oficial implementado para listings completados; `SEDAR+` no automatizable sin permiso |
| Singapore Exchange | SGX `IPO Prospectus` | Feed JSON oficial implementado para prospectos publicados |
| Tokio / Japon | FSA `EDINET` Documents API y JPX `New Listings` | Monitor JPX y diff diario implementados; EDINET pendiente para deteccion documental previa |
| Brasil | CVM `Portal Dados Abertos` | Conector prioritario pendiente para ofertas publicas estructuradas |
| Union Europea | ESMA `Prospectus III` | Conector prioritario pendiente para prospectos de Alemania, Paises Bajos e Italia |
| Corea del Sur | FSS `OpenDART` y KRX `OPEN API` | Conector prioritario pendiente para ofertas regulatorias y confirmacion de mercado |
| Rusia | Bank of Russia `Register of Russian Securities` y MOEX `ISS` | Solo investigacion restringida; sin ingesta ni señales por sanciones vigentes |

### Regla De Evidencia

Cada jurisdiccion conserva sus propias etapas:

- Reino Unido: una aparicion en `New issues` indica una oferta esperada; la
  confirmacion avanzada debe contrastarse con prospecto/admission evidence.
- Hong Kong: un `Application Proof` inicia seguimiento; un `PHIP` indica
  aprobacion en principio, no trading completado.
- Australia: ASX informa que sus upcoming listings tienen solicitud formal
  recibida, pero las fechas de primera cotizacion siguen siendo anticipadas.
- Canada: el feed implementado documenta listings completados; `SEDAR+`
  restringe scraping y almacenamiento en bases para el monitor público.
- Singapur: el feed implementado documenta prospectos publicados; cada
  documento debe revisarse antes de afirmar admision o inicio de negociacion.
- Tokio: `JPX New Listings` ya confirma hitos de aprobacion/listing mediante
  pagina y CSV; un futuro collector `EDINET` iniciara revision documental.
- Brasil: un registro de oferta en `CVM` inicia revision; no confirma listado
  o trading en B3.
- Alemania, Paises Bajos e Italia: un prospecto `ESMA` es evidencia
  regulatoria; el output transformado debe declarar fuente y transformacion.
  Para Frankfurt, `BaFin` servira como corroboracion nacional del prospecto.
- Corea del Sur: un securities registration statement de `OpenDART` inicia
  revision; `KRX` solo confirmara mercado tras validar derechos del output.
- Rusia: el registro del Banco de Rusia documenta securities y `MOEX ISS`
  ofrece datos tecnicamente disponibles, pero `MOEX` fue designada por OFAC
  el `2024-06-12`; se excluye automatizacion y orientacion de posiciones.

### Salidas Operativas

- `SEC IPO Alerts`: bandeja de filings SEC nuevos, enlazados por `CIK` a
  empresas ya seguidas en `IPO Watch` cuando existe coincidencia exacta, con
  triage visible para señales SPAC/ETF, prospectos finales y retiros.
- `HKEX Listing Monitor`: pagina y CSV generados desde los cinco feeds JSON
  oficiales, util para detectar cambios de ciclo.
- `LSE Upcoming Issues Monitor`: pagina generada desde el componente JSON
  oficial; los registros se consideran proximos, no admitidos definitivamente.
- `LSE / FCA NSM Corroboration Monitor`: pagina que busca documentos FCA por
  cada emisor próximo y separa señales metadata de prospecto, documento de
  admisión, intención de flotar u otra revisión.
- `ASX Upcoming Floats And Listings Monitor`: pagina que muestra solicitudes
  formales anticipadas y retiros visibles en ASX.
- `TSX New Company Listings Monitor`: pagina de confirmaciones publicadas de
  compañías ya listadas; no funciona como señal prospectiva.
- `JPX New Listings Monitor`: pagina de aprobaciones y fechas de listing
  publicadas para Tokio, con enlace al outline oficial.
- `SGX IPO Prospectus Monitor`: pagina de documentos publicados en el
  catalogo oficial SGX; funciona como señal documental para revision.
- `Issuer Listing Confirmations`: pagina de hitos posteriores documentados
  por comunicados oficiales del emisor, con fecha de evento y de verificacion.
- `ETF Holdings Activity`: pagina de diferencias entre snapshots de posiciones
  con fixtures sinteticos e importadores locales; la automatizacion autorizada
  de fuentes diarias aun esta pendiente.
- `Global Listings Alerts`: bandeja diaria que compara snapshots de los seis
  mercados y marca registros nuevos, modificados o ausentes para revisión.
- La portada `Global Listings Watch` enlaza ambas vistas para navegar entre
  cobertura global, cambios diarios, feed HKEX, feed LSE, contraste FCA, ASX,
  TSX, JPX, SGX, confirmaciones del emisor, actividad ETF y gobernanza de fuentes.

## Pagina 4: ETF Holdings Activity

Objetivo: mostrar cambios publicados en las posiciones de ETF observables,
con la frecuencia real de cada fuente.

- Implementado: comparador de snapshots normalizados, CSV de diferencias,
  reporte Markdown y pagina HTML con fixture sintetico reproducible.
- Implementado: importador local de CSV ARK descargado por el operador,
  conservando fecha efectiva y frecuencia diaria declarada.
- Implementado: importador local State Street SPDR/XLF y fixture
  `XLF-DEMO`, alineado al benchmark Financials.
- Implementado: importador manual iShares/IYF y fixture `IYF-DEMO`; los
  terminos oficiales impiden convertirlo en colector automatico sin permiso.
- Pendiente de conexion/publicacion: automatizacion autorizada y permisos de
  salidas reales de ARK, State Street SPDR e iShares.
- Implementado: importador XML `SEC NPORT-P` y salida regulatoria separada;
  es auditable pero no equivale a datos intradia ni a un feed diario.
- Implementado: colector EDGAR de filings recientes por `CIK`/`seriesId`,
  con archivo local del XML validado y `User-Agent` obligatorio en vivo.
- Implementado: backfill desde datasets trimestrales SEC N-PORT extraidos,
  con snapshots historicos, manifiesto y bloqueo de periodos duplicados.
- Implementado: catalogo y descarga local por trimestre de ZIP SEC N-PORT,
  con extraccion limitada a tablas necesarias y defensa de rutas inseguras.
- Implementado: sincronizacion incremental N-PORT con linea base persistente,
  descarga exclusiva de releases nuevas y regeneracion opcional de una serie.
- Presentacion: posiciones nuevas, aumentadas, reducidas, ausentes o con
  cambio solo de peso, fecha efectiva, frecuencia y enlace de evidencia.
- Regla de lenguaje: una diferencia de holdings se describe como cambio
  observado, no como compra o venta confirmada del gestor sin evidencia
  adicional.
