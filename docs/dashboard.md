# Dashboard Product Outline

TargetAudit tendra dos paginas principales. No comparten score: una evalua
pronosticos ya medibles y la otra sigue eventos de companias que pueden llegar
al mercado.

Con la expansion internacional, el producto pasa a tres paginas principales:

## Pagina 1: Financials Scorecard

Objetivo: auditar `price targets` sobre financials de Estados Unidos.

Componentes:

- Ranking de firmas especialistas frente a generalistas.
- Filtros por banco, subindustria, periodo y direccion del target.
- Comparacion contra `XLF`.
- Tabla de observaciones excluidas y motivo.
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

## Pagina 3: Global Listings Watch

Objetivo: extender la inteligencia de nuevas cotizaciones fuera de Estados
Unidos sin aplicar reglas SEC a jurisdicciones distintas.

### Cobertura Inicial

| Mercado | Fuente Oficial Identificada | Estado De Implementacion |
|---|---|---|
| London Stock Exchange | LSE `New issues` y FCA National Storage Mechanism | Conector prioritario |
| Hong Kong HKEX | HKEX/HKEXnews new listings y documentos `PHIP` | Conector prioritario |
| Australian Securities Exchange | ASX `Upcoming floats and listings` | Planificado |
| Toronto Stock Exchange | TSX `New Company Listings` | Planificado |
| Singapore Exchange | SGX `IPO Prospectus` | Planificado |

### Regla De Evidencia

Cada jurisdiccion conserva sus propias etapas:

- Reino Unido: una aparicion en `New issues` indica una oferta esperada; la
  confirmacion avanzada debe contrastarse con prospecto/admission evidence.
- Hong Kong: un `Application Proof` inicia seguimiento; un `PHIP` indica
  aprobacion en principio, no trading completado.
- Australia: ASX informa que sus upcoming listings tienen solicitud formal
  recibida, pero las fechas de primera cotizacion siguen siendo anticipadas.
- Canada y Singapur: sus fuentes oficiales identificadas sirven inicialmente
  para listings/prospectos publicados y requieren disenar el estado previo
  antes de considerarlos monitores prospectivos.
