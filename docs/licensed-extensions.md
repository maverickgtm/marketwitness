# Extensiones Licenciadas Opcionales

Revision: `2026-05-24`.

TargetAudit Open Edition funciona sin comprar datos. Esta pagina registra
alternativas para el usuario que decida financiar su propia investigacion con
`price targets` historicos reales. No activa proveedores ni concede derechos
de publicacion.

## Precio Publico Encontrado

| Opcion | Datos Relevantes | Precio Visible | Uso En TargetAudit |
|---|---|---:|---|
| Massive / Benzinga Analyst Ratings Expansion | Ratings y price targets de acciones USA; documentacion indica historial desde `2011-12-08` | `USD 99/month` para la expansion individual | Candidato `bring your own license` para investigacion privada autorizada |
| Benzinga Analyst Ratings API directo | Acciones USA; historial anunciado desde 2013; firma, analista y targets anterior/actual | Cotizacion requerida | Ruta negociada si incluye derechos de output publico |
| AnaChart Price Targets and Ratings Feed | Price targets, ratings, consenso y feeds de accuracy historicos | Cotizacion requerida | Alternativa futura sujeta a precio y derechos escritos |

La pagina de precios de Massive muestra el complemento Benzinga Analyst
Ratings por `USD 99/month`. Antes de pagar, el usuario debe confirmar en la
contratacion si el complemento exige ademas un plan base de Stocks y cuales
son los derechos aplicables a su cuenta.

## Limite De La Licencia Individual

Los terminos de mercado individual de Massive permiten un uso personal y no
comercial del dato. No permiten convertir esa suscripcion en un dataset
incluido en GitHub ni en un ranking publico distribuido a terceros sin
consentimiento escrito adicional.

Por lo tanto:

- TargetAudit puede aceptar una exportacion local que el usuario este
  autorizado a procesar para su propia investigacion.
- El repositorio no incluye filas reales adquiridas, tokens ni claves.
- Un ranking real publico de Roth MKM, KBW, UBS, Barclays o Citi continua
  bloqueado hasta obtener derechos escritos para ese output.

## Flujo Del Usuario Que Decide Pagar

1. El usuario contrata directamente con el proveedor y revisa sus terminos.
2. Conserva sus credenciales y exportaciones fuera de Git.
3. Usa `targets-import` con un manifiesto local que identifica proveedor,
   evidencia contractual y uso autorizado.
4. Ejecuta el scorecard para investigacion interna.
5. Solo publica resultados reales cuando una licencia o permiso escrito cubra
   expresamente la salida derivada y los demas controles de Readiness.

El catalogo versionado vive en `data/samples/licensed_extensions.csv` y se
muestra mediante `/dashboard/extensions` y `/api/v1/extensions/licensed`.

## Fuentes Oficiales Revisadas

- Massive Benzinga Analyst Ratings: <https://massive.com/docs/rest/stocks/benzinga/analyst-ratings>
- Massive pricing: <https://massive.com/pricing>
- Massive individual market-data terms: <https://massive.com/legal/market_data_terms_individual>
- Benzinga Analyst Ratings API: <https://www.benzinga.com/apis/analyst-ratings-api/>
- AnaChart datasets and data feeds: <https://anachart.com/datasets-data-feeds>
