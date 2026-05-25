# Roadmap

TargetAudit inicia con un `Financials Scorecard` para targets de acciones
financieras estadounidenses y un modulo separado `IPO Watch` para hitos
verificables de cotizaciones tecnologicas/estrategicas.

## Milestone 1: Research Engine (`v0.1`)

- [x] Metodologia inicial y esquema auditado.
- [x] Importacion CSV de targets y barras ajustadas.
- [x] Evaluacion direccional, error terminal y comparacion con benchmark.
- [x] Ranking Markdown y datos sinteticos reproducibles.
- [x] Especializacion inicial en U.S. Financials con benchmark `XLF`.
- [x] Desglose de resultados por direccion del target.
- [x] Registro y reporte inicial de IPO Watch con SpaceX/Cerebras verificados.
- [x] Pagina Global Listings Watch con fuentes oficiales identificadas.
- [x] Pruebas unitarias y GitHub Actions.

## Milestone 2: Data Adapters (`v0.2`)

- [x] Registro formal de proveedores y licencias.
- [x] Adaptador SEC para metadatos de emisores/CIK.
- [x] Adaptador de precios freemium con cache y limites visibles.
- [x] Importador para exportaciones autorizadas de targets con manifiesto y auditoria.
- [x] Descubridor SEC para formularios `S-1`, `F-1`, `424B4` y retiros desde
  un indice diario completo.
- [x] Ejecucion diaria persistente SEC con historial y cola enlazada por CIK.
- [x] Triage SEC transparente para coincidencias watchlist, señales SPAC/ETF y prospectos finales.
- [x] Promocion revisada desde SEC IPO Alerts al tablero IPO Watch mediante decisiones documentadas.
- [x] Conector LSE `New issues` mediante componente JSON oficial.
- [x] Conector HKEX/HKEXnews para estados oficiales AP/PHIP.
- [x] Snapshot trazable de LSE `Upcoming issues`.
- [x] Agregar contraste documental FCA NSM para LSE.
- [x] Clasificar metadatos FCA como prospecto, admission document, intention to float u otra revision.
- [x] Conector ASX `Upcoming floats and listings` desde HTML oficial.
- [x] Conector TSX `New Company Listings` como confirmacion de listings.
- [x] Conector SGX `IPO Prospectus` mediante API JSON oficial.
- [x] Monitor JPX `New Listings` para aprobaciones y fechas de listing de Tokio.
- [x] Historial y diff diario de seis monitores globales, incluido JPX, con cola de revision.
- [x] Ingesta de comunicados oficiales para confirmar listings.
- [x] Validacion de splits y cambios de ticker.
- [x] Validacion de barras de precios duplicadas o incoherentes.

## Milestone 3: Rigor Cuantitativo (`v0.3`)

- [x] Intervalos de confianza Wilson 95% para hit rate.
- [x] Ranking por sector y por direccion con minimo muestral por segmento.
- [x] Universo historico punto-en-el-tiempo con membresia y sector auditables.
- [x] Revision de targets encadenados por firma/accion con exclusion auditable.
- [x] Reglas de backtest con salida y costos explicitos.

## Milestone 4: Aplicacion (`v0.4`)

- [x] DuckDB inicial para conservar corridas de evaluacion, hashes de evidencia
  y resultados tipados, con esquema relacional portable a PostgreSQL.
- [x] API FastAPI inicial de solo lectura con endpoints de corridas, ranking
  de firmas, acciones y auditoria de exclusiones.
- [x] Dashboard web inicial `Financials Scorecard` con filtros, ranking,
  detalle por firma/ticker y auditoria de exclusiones sobre la API.
- [x] Linea temporal visual de evidencia por ticker y exportaciones CSV del
  ranking filtrado y las observaciones de una corrida.
- [ ] Serie diaria completa de precios/targets autorizada para graficos
  historicos publicos.
- [x] Pagina de auditoria de fuentes, controles de publicacion y observaciones
  excluidas o pendientes por corrida.
- [x] Pagina `Scorecard Readiness` para separar fixtures, uso interno y
  requisitos productivos, incluido el universo historico punto-en-el-tiempo,
  antes de habilitar rankings publicos.
- [x] Persistir `provider_id` por observacion para enlazar resultados y
  gobernanza de fuentes sin inferencias por URL.
- [x] Pagina `ETF Holdings Activity` con comparador de snapshots, diferencias
  de posiciones, sello de fecha/frecuencia y demo sintetica reproducible.
- [x] Importador local de archivos diarios ARK con normalizacion auditable y
  politica de no redistribucion de holdings reales pendiente de permiso.
- [x] Importador local State Street SPDR/XLF para holdings diarios y demo
  `XLF-DEMO` alineado a Financials.
- [x] Importador local iShares/IYF para un segundo ETF financiero, con demo
  `IYF-DEMO` y bloqueo explicito de descarga automatizada por terminos.
- [ ] Conectores de snapshots diarios oficiales por emisor para la pagina
  `ETF Holdings Activity`, incluyendo autorizacion y permisos de publicacion
  para ARK, SPDR e iShares.
- [x] Respaldo regulatorio ETF mediante SEC `N-PORT` para periodos publicados,
  separado de las descargas diarias del emisor y limitado inicialmente a
  posiciones en acciones.
- [x] Recoleccion SEC `N-PORT` reciente por `CIK`/`seriesId`, con XML
  validado archivado localmente y acceso identificado mediante `User-Agent`.
- [x] Backfill historico de `N-PORT` mediante datasets trimestrales SEC
  extraidos, con snapshots por periodo y revision obligatoria de enmiendas.
- [x] Catalogo y descarga manual controlada de ZIP trimestrales `N-PORT`,
  con extraccion segura y archivos conservados fuera de Git.
- [x] Ejecucion programada que consulta nuevos trimestres `N-PORT`, descarga
  solo releases nuevas y regenera la serie `XLF` cuando hay evidencia local.

## Milestone 5: Operacion Publica (`v1.0`)

- [x] Open Edition ejecutable sin suscripciones de datos, con sandbox
  redistribuible y monitores regulatorios públicos claramente separados.
- [x] Catalogo `bring your own license` para que el usuario compare opciones
  pagadas sin volverlas requisito ni confundirlas con permiso de publicacion.
- [x] Clasificacion de APIs freemium de targets/consenso (Finnhub y FMP) como
  opciones contractuales pendientes de derechos de output publico.
- [ ] Widget atribuido de TradingView para contexto visual de mercado, sin
  usarlo como fuente de datos del scorecard.
- [x] Mapa inicial `RWA Watch` de los 20 CEX lideres por Trust Score y
  Pepperstone, separando emisores, venues y CFD.
- [x] `RWA Watch Sandbox` ejecutable y visible en dashboard con observaciones
  sinteticas, desviacion de precio y bloqueo explicito de datos live.
- [ ] Adaptador real `RWA Watch` para `xStocks / Backed`, solo si se obtiene
  autorizacion escrita de display, retencion y output derivado.
- [x] Revision de venues RWA principales: Bybit y Kraken quedan como
  referencias bloqueadas; Gate y Bitget permanecen pendientes de permisos de
  output publico.
- [ ] Aprobacion contractual de `Ondo Global Markets`, Gate o Bitget para
  activar datos reales en una edicion opcional.
- [ ] Licencia o aportación autorizada opcional para mostrar rankings reales
  de analistas públicamente.
- [ ] Actualizaciones programadas del scorecard real con fuentes opcionales
  publicables.
- [x] Monitoreo de calidad por corrida con bloqueo de entradas/linaje
  incompletos, modo de publicación que exige acciones corporativas y universo
  histórico, y revisión visible de exclusiones anormales.
- [x] Versionado de datasets y metodologia por corrida, con huella estable de
  entradas y comparacion visible en API/dashboard.
- [ ] Informes periodicos reproducibles.
- [x] Informe operativo reproducible de calidad, disponible por CLI, dashboard
  y monitor local recurrente del warehouse live.
- [x] Release Center que combina derechos de fuentes, linaje de targets,
  procedencia de activos y calidad pública en una decisión reproducible.
- [x] Cola de aprobación de proveedores que documenta evidencia y criterio de
  promoción de los candidatos críticos sin autoautorizar publicación.
- [x] Flujo de decisión manual que genera registros promovidos o pendientes
  con evidencia, sin editar la gobernanza base en silencio.
- [x] Preparacion de colaboracion publica en GitHub con politica de seguridad
  y plantillas que exigen derechos y procedencia para fuentes propuestas.
- [x] Barrido internacional inicial de fuentes gratuitas o abiertas en Reino
  Unido, Japon, Australia, Hong Kong, Singapur y China continental.
- [x] Segunda ronda internacional en India, Mexico, Brasil, Argentina,
  Alemania, Suiza, Paises Bajos e Italia, con clasificacion de derechos.
- [x] Deep dive en Tokio, Toronto y Frankfurt para combinar `EDINET`/`JPX`,
  bloquear automatizacion `SEDAR+` y validar cobertura `ESMA`/`BaFin`.
- [x] Revision final de brechas en Corea, Golfo y Sudafrica, incorporando
  `OpenDART`/`KRX` y dejando los mercados sin API confirmada en observacion.
- [x] Revision de Rusia, documentando `Bank of Russia`/`MOEX ISS` como
  `restricted_research_only` por la designacion OFAC de `MOEX`.
- [x] Implementar un monitor regulatorio japones sobre el API oficial
  `EDINET` para filings de oferta con clave gratuita.
- [ ] Integrar filings `EDINET` al historial diario y validar un conector adicional
  de ofertas de Singapur sobre datasets/API de `MAS OPERA`.
- [ ] Implementar collectors de ofertas de Brasil (`CVM Dados Abertos`) y
  prospectos europeos (`ESMA Prospectus III`) con atribucion visible.
- [ ] Implementar collector coreano de securities registration statements
  sobre `OpenDART` y validar confirmacion de mercado `KRX`.
- [ ] Revision legal del producto y de sus disclaimers.
- [ ] Mantener Rusia sin ingesta automatica salvo autorizacion legal
  documentada sobre sanciones y licencia de datos.

## Decisiones Pendientes

1. Si se desea ampliar Open Edition, proveedor o aportación autorizada de
   targets históricos para una primera muestra real.
2. Para esa ampliación opcional, precios ajustados que permitan publicación.
3. Nombre/dominio final y alcance: proyecto de investigacion o producto
   publico con actualizaciones.
