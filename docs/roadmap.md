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

- [ ] Registro formal de proveedores y licencias.
- [x] Adaptador SEC para metadatos de emisores/CIK.
- [ ] Adaptador de precios gratuito o freemium con cache y limites.
- [ ] Importador para exportaciones autorizadas de targets.
- [x] Descubridor SEC para formularios `S-1`, `F-1`, `424B4` y retiros desde
  un indice diario completo.
- [ ] Ejecucion diaria persistente y promocion revisada al tablero IPO Watch.
- [x] Conector LSE `New issues` mediante componente JSON oficial.
- [x] Conector HKEX/HKEXnews para estados oficiales AP/PHIP.
- [x] Snapshot trazable de LSE `Upcoming issues`.
- [x] Agregar contraste documental FCA NSM para LSE.
- [ ] Clasificar documentos FCA revisados como prospecto/admission evidence.
- [x] Conector ASX `Upcoming floats and listings` desde HTML oficial.
- [x] Conector TSX `New Company Listings` como confirmacion de listings.
- [x] Conector SGX `IPO Prospectus` mediante API JSON oficial.
- [ ] Ingesta de comunicados oficiales para confirmar listings.
- [ ] Validacion de splits y cambios de ticker.
- [x] Validacion de barras de precios duplicadas o incoherentes.

## Milestone 3: Rigor Cuantitativo (`v0.3`)

- [ ] Intervalos de confianza para hit rate.
- [ ] Ranking por sector y por direccion.
- [ ] Universo historico punto-en-el-tiempo.
- [ ] Revision de targets encadenados por firma/accion.
- [ ] Reglas de backtest con salida y costos explicitos.

## Milestone 4: Aplicacion (`v0.4`)

- [ ] DuckDB para analisis local y migracion preparada a PostgreSQL.
- [ ] API FastAPI con endpoints de rankings, firmas y acciones.
- [ ] Dashboard web con filtros, series de targets y exportaciones.
- [ ] Pagina de auditoria de fuente y observaciones excluidas.

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
