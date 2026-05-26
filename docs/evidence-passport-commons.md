# Evidence Passport Commons

Revision: `2026-05-25`

## Propuesta Diferenciadora

`Evidence Passport Commons` es una red abierta de fichas verificables para
fuentes de inteligencia de mercado. En lugar de comenzar por una senal de
compra, un score o una grafica, TargetAudit comienza por la pregunta que
permite confiar en cualquier resultado:

> De donde salio esta evidencia, que derecho permite mostrarla, con que
> cadencia cambia y que afirmacion no puede sostener por si sola?

No afirmamos que ningun proyecto mundial tenga controles de procedencia.
Nuestra decision de producto es convertir esos controles en una superficie
publica, contribuible y consultable por API.

## Que Es Un Passport

Cada `Evidence Passport` conserva cuatro bloques minimos:

| Bloque | Pregunta que responde | Ejemplo |
|---|---|---|
| Identidad | Que fuente oficial y clase de evidencia es? | SEC N-PORT / ETF regulatory holdings |
| Derechos | Se puede recolectar, conservar o publicar output derivado? | `source_link_and_derived_output` |
| Cadencia | Es filing, snapshot periodico o feed continuo? | Trimestral regulatorio, no actividad diaria |
| Limite de afirmacion | Que no demuestra esa fuente? | Un prospectus no confirma primera cotizacion |

La version `0.1` usa el registro de gobernanza ya auditado por TargetAudit y
publica origen, derechos, estado y nota de revision. La incorporacion
estructurada de cadencia y limites especificos es una mision abierta para
contributors; no se declara completa para los registros heredados.
La API de lectura expone el contrato:

```text
GET /api/v1/commons/passports
```

La interfaz publica se encuentra en:

```text
/dashboard/commons
```

## Por Que Puede Interesar En GitHub

Una persona no necesita comprar datos para contribuir. Puede aportar el
passport de una fuente oficial de su mercado, documentar sus terminos y
proponer la regla de confirmacion adecuada antes de escribir un conector.

Esto abre tareas concretas para contributors de Japon, Reino Unido, Brasil,
Hong Kong, Singapur, Corea y nuevos mercados:

1. localizar la fuente oficial y su pagina de terminos;
2. documentar campos, frecuencia y costo de acceso;
3. declarar que output puede publicarse;
4. definir el limite de afirmacion de la evidencia;
5. implementar el conector solo despues de aprobar el passport.

## Diferencia Frente A Productos De Mercado

`OpenBB` ofrece una plataforma financiera amplia; `Stocknear` ofrece una
experiencia visual con muchas senales; `AnaChart` ofrece el historial y
desempeno de targets de analistas. TargetAudit no debe fingir superar esas
ofertas en amplitud o datasets licenciados.

El Commons ocupa otro lugar: una infraestructura abierta para verificar si un
dato puede usarse y que significa antes de convertirlo en una pantalla,
alerta, score o integracion de terceros.

## Modelo Gratuito Y Monetizacion

El registro y su API deben permanecer abiertos. Si el proyecto logra adopcion,
los servicios que podrian cobrarse sin cerrar el Commons son:

- monitoreo alojado y alertas continuas sobre passports aprobados;
- workspace privado con fuentes que el cliente ya tenga licenciadas;
- soporte para instituciones que deban documentar linaje y derechos;
- implementacion patrocinada de conectores oficiales;
- recompensas a contributors por passports o conectores prioritarios.

Los contributors voluntarios no reciben automaticamente una participacion
economica. Si aparecen ingresos, TargetAudit debera publicar reglas separadas
para recompensas, contratos o patrocinio antes de comprometer pagos.

## Regla De Confianza

Un passport aprobado no convierte evidencia en recomendacion financiera.
Autoriza una forma documentada de leer y, cuando los derechos lo permiten,
mostrar hechos derivados de una fuente.
