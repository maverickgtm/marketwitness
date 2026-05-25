# Politica De Uso Publico Y Derechos De Datos

Version de politica: `2026-05-25`.

## Alcance

TargetAudit es una herramienta de investigacion auditable. Sus reportes,
rankings demostrativos, monitores de filings, diferencias de holdings y
observaciones de activos tokenizados no constituyen recomendacion de comprar,
vender o mantener ningun valor.

Esta politica es un control interno de producto para la edicion GitHub. No es
asesoria legal, fiscal o de inversion y no sustituye una revision legal
externa antes de operar un servicio publico con datos reales.

La aplicacion publica esta politica en `/dashboard/policy` y expone el estado
estructurado en `/api/v1/policy/public-use`. Los conteos y proveedores
bloqueados se derivan de `data/samples/source_registry.csv`.

## Capas De Datos

| Capa | Que Puede Mostrarse | Limite |
|---|---|---|
| Sandbox creado por el proyecto | Fixtures y resultados reproducibles de demostracion | No son hallazgos reales de mercado ni resultados de firmas reales |
| Monitores regulatorios publicos | Filings, prospectos, confirmaciones documentales y holdings reportados bajo la politica registrada | Un documento o filing no es una recomendacion, una cotizacion completada ni una senal en tiempo real |
| Extensiones autorizadas | Analisis local sobre archivos aportados por un usuario con derechos documentados | No activa publicacion de rankings reales sin permiso de output publico para todos los insumos |

## Reglas De Publicacion

1. No publicar rankings reales de analistas mientras targets, precios,
   acciones corporativas y universo historico no tengan derechos documentados
   para output publico.
2. No describir prospectos, filings u ofertas registradas como primera
   negociacion confirmada o como oportunidad de inversion sin evidencia
   separada y lenguaje no recomendatorio.
3. No automatizar, almacenar ni republicar fuentes marcadas `blocked` o
   `manual_only` en `Source Governance`.
4. No incluir claves API, descargas de proveedores, correos de identificacion
   para solicitudes ni archivos privados en el repositorio.

## Fuentes Restringidas Visibles

El dashboard debe hacer visibles, no ocultar, las decisiones negativas. Al
`2026-05-25`, esto incluye:

- `MAS OPERA Public Offers`: referencia oficial manual de Singapur; su
  busqueda exige security code y sus terminos restringen recoleccion
  automatizada, caching y deep links sin permiso.
- `TipRanks`: referencia conceptual de rankings, sin extraccion automatica.
- `xStocks / Backed`, `Bybit xStocks` y `Kraken xStocks`: referencias de
  activos tokenizados excluidas de recoleccion publica bajo la revision
  registrada.

El registro de fuentes, y no esta lista narrativa, es la fuente operativa de
verdad para futuras actualizaciones.

## Responsabilidad Del Operador

- Revisar terminos aplicables y requisitos regulatorios antes de habilitar un
  collector live.
- Mantener la identificacion requerida por SEC y respetar sus reglas de
  acceso justo cuando se hagan consultas en vivo.
- Obtener revision legal externa si el proyecto se despliega publicamente con
  datos reales, publicidad, suscripciones o senales destinadas a terceros.

## Relacion Con Otros Controles

- `Source Governance` define si una fuente es utilizable, pendiente, manual o
  bloqueada.
- `Scorecard Readiness` impide habilitar rankings reales sin insumos
  productivos autorizados.
- `Release Center` decide si una corrida concreta tiene fuentes, linaje y
  calidad suficientes para publicacion.
- `Operations Quality` valida integridad tecnica, pero nunca concede derechos
  de datos por si solo.
