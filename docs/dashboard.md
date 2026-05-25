# Dashboard Product Outline

TargetAudit tendra dos paginas principales. No comparten score: una evalua
pronosticos ya medibles y la otra sigue eventos de companias que pueden llegar
al mercado.

Con la expansion internacional, el producto tiene cuatro paginas activas,
incluida la pagina de actividad publicada de ETF:

## Vista Transversal: Source Governance

Objetivo: hacer visible qué datos pueden alimentar un producto público y qué
fuentes aún requieren términos, licencia o exclusión expresa.

- Registro de fuentes oficiales, candidatas comerciales y datos sintéticos.
- Estado de integración separado de estado de licencia/publicación.
- Bloqueo visible para fuentes que no deben recolectarse automáticamente.
- Enlace a la referencia oficial usada para cada decisión.

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
| Toronto Stock Exchange | TSX `New Company Listings` | Feed HTML oficial implementado para listings completados |
| Singapore Exchange | SGX `IPO Prospectus` | Feed JSON oficial implementado para prospectos publicados |

### Regla De Evidencia

Cada jurisdiccion conserva sus propias etapas:

- Reino Unido: una aparicion en `New issues` indica una oferta esperada; la
  confirmacion avanzada debe contrastarse con prospecto/admission evidence.
- Hong Kong: un `Application Proof` inicia seguimiento; un `PHIP` indica
  aprobacion en principio, no trading completado.
- Australia: ASX informa que sus upcoming listings tienen solicitud formal
  recibida, pero las fechas de primera cotizacion siguen siendo anticipadas.
- Canada: el feed implementado documenta listings completados y requiere una
  fuente adicional para alertas prospectivas.
- Singapur: el feed implementado documenta prospectos publicados; cada
  documento debe revisarse antes de afirmar admision o inicio de negociacion.

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
- `SGX IPO Prospectus Monitor`: pagina de documentos publicados en el
  catalogo oficial SGX; funciona como señal documental para revision.
- `Issuer Listing Confirmations`: pagina de hitos posteriores documentados
  por comunicados oficiales del emisor, con fecha de evento y de verificacion.
- `ETF Holdings Activity`: pagina de diferencias entre snapshots de posiciones
  con fixtures sinteticos e importadores locales; la automatizacion autorizada
  de fuentes diarias aun esta pendiente.
- `Global Listings Alerts`: bandeja diaria que compara snapshots de los cinco
  mercados y marca registros nuevos, modificados o ausentes para revisión.
- La portada `Global Listings Watch` enlaza ambas vistas para navegar entre
  cobertura global, cambios diarios, feed HKEX, feed LSE, contraste FCA, ASX,
  TSX, SGX, confirmaciones del emisor, actividad ETF y gobernanza de fuentes.

## Pagina 4: ETF Holdings Activity

Objetivo: mostrar cambios publicados en las posiciones de ETF observables,
con la frecuencia real de cada fuente.

- Implementado: comparador de snapshots normalizados, CSV de diferencias,
  reporte Markdown y pagina HTML con fixture sintetico reproducible.
- Implementado: importador local de CSV ARK descargado por el operador,
  conservando fecha efectiva y frecuencia diaria declarada.
- Implementado: importador local State Street SPDR/XLF y fixture
  `XLF-DEMO`, alineado al benchmark Financials.
- Pendiente de conexion/publicacion: automatizacion autorizada y permisos de
  salidas reales de ARK y State Street SPDR.
- Implementado: importador XML `SEC NPORT-P` y salida regulatoria separada;
  es auditable pero no equivale a datos intradia ni a un feed diario.
- Implementado: colector EDGAR de filings recientes por `CIK`/`seriesId`,
  con archivo local del XML validado y `User-Agent` obligatorio en vivo.
- Implementado: backfill desde datasets trimestrales SEC N-PORT extraidos,
  con snapshots historicos, manifiesto y bloqueo de periodos duplicados.
- Presentacion: posiciones nuevas, aumentadas, reducidas, ausentes o con
  cambio solo de peso, fecha efectiva, frecuencia y enlace de evidencia.
- Regla de lenguaje: una diferencia de holdings se describe como cambio
  observado, no como compra o venta confirmada del gestor sin evidencia
  adicional.
