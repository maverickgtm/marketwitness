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
- [x] Historial y diff diario de los cinco monitores globales con cola de revision.
- [x] Ingesta de comunicados oficiales para confirmar listings.
- [x] Validacion de splits y cambios de ticker.
- [x] Validacion de barras de precios duplicadas o incoherentes.

## Milestone 3: Rigor Cuantitativo (`v0.3`)

- [x] Intervalos de confianza Wilson 95% para hit rate.
- [x] Ranking por sector y por direccion con minimo muestral por segmento.
- [x] Universo historico punto-en-el-tiempo con membresia y sector auditables.
- [ ] Revision de targets encadenados por firma/accion.
- [ ] Reglas de backtest con salida y costos explicitos.

## Milestone 4: Aplicacion (`v0.4`)

- [ ] DuckDB para analisis local y migracion preparada a PostgreSQL.
- [ ] API FastAPI con endpoints de rankings, firmas y acciones.
- [ ] Dashboard web con filtros, series de targets y exportaciones.
- [ ] Pagina de auditoria de fuente y observaciones excluidas.
- [ ] Pagina `ETF Holdings Activity` con snapshots diarios oficiales por emisor,
  diferencias de posiciones y sello claro de fecha/frecuencia.
- [ ] Respaldo regulatorio ETF mediante SEC `N-PORT` para periodos publicados,
  separado de las descargas diarias del emisor.

## Milestone 5: Operacion Publica (`v1.0`)

- [ ] Licencia de datos apta para mostrar resultados publicamente.
- [ ] Actualizaciones programadas y monitoreo de calidad.
- [ ] Versionado de datasets y metodologia.
- [ ] Informes periodicos reproducibles.
- [ ] Revision legal del producto y de sus disclaimers.

## Decisiones Pendientes

1. Proveedor legal de targets historicos para la primera muestra real.
2. Proveedor de precios ajustados que permita publicacion del dashboard.
3. Nombre/dominio final y alcance: proyecto de investigacion o producto
   publico con actualizaciones.
