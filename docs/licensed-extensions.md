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
| MarketBeat All Access | Mas de un millon de recomendaciones; ratings y cambios de target; export CSV anunciado para hasta seis meses recientes | `USD 249/year` o `USD 29/month` | Buen piloto privado de bajo costo, insuficiente por si solo para targets con mas de un ano |
| WallStreetZen Premium | Rendimiento seguido para mas de 4,000 analistas y recomendaciones de top analysts | `USD 19.50/month` facturado anualmente | Benchmark privado de ranking/metodologia; no se confirmo feed estructurado de targets |
| Benzinga Analyst Ratings API directo | Acciones USA; historial anunciado desde 2013; firma, analista y targets anterior/actual | Cotizacion requerida | Ruta negociada si incluye derechos de output publico |
| AnaChart Price Targets and Ratings Feed | Price targets, ratings, consenso y feeds de accuracy historicos | Cotizacion requerida | Alternativa futura sujeta a precio y derechos escritos |
| GuruFocus Data License | La FAQ oficial identifica estimates provenientes de Refinitiv y Morningstar | Cotizacion requerida para redistribuir | Pendiente confirmar targets individuales historicos y permiso escrito |

La pagina de precios de Massive muestra el complemento Benzinga Analyst
Ratings por `USD 99/month`. Antes de pagar, el usuario debe confirmar en la
contratacion si el complemento exige ademas un plan base de Stocks y cuales
son los derechos aplicables a su cuenta.

MarketBeat es interesante para probar el importador con datos aportados por
un usuario: tiene precio bastante menor y exportacion CSV. Sin embargo, su
FAQ describe exportaciones de ratings recientes de hasta seis meses, mientras
la metodologia central necesita observaciones con horizonte ya vencido de mas
de un ano. Serviria para pruebas de cobertura o para preparar el pipeline,
pero no para publicar el ranking completo prometido.

WallStreetZen ya calcula rankings de rendimiento de analistas y sus terminos
permiten usar datos exportados en investigacion interna, sin redistribuirlos.
Es una excelente referencia para comparar nuestro metodo; no se registra como
feed confirmado de `price targets` historicos porque sus paginas oficiales
revisadas no lo demuestran.

GuruFocus merece quedar en observacion: su documentacion oficial confirma
datos de estimates provenientes de Refinitiv y Morningstar, pero no confirma
todavia el conjunto de filas historicas individuales que necesita TargetAudit.
Ademas, exige licencia comercial para redistribucion.

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

## Referencias Visuales No Integrables Actualmente

| Fuente | Valor Para Investigar Manualmente | Motivo Para No Conectarla |
|---|---|---|
| Yahoo Finance | Consulta visual de recomendaciones y price targets; Yahoo identifica datos de recomendaciones/targets provistos por S&P Global Market Intelligence y upgrades/downgrades por Benzinga | Yahoo indica que la informacion de Finance no debe redistribuirse; no usar librerias no oficiales ni scraping para el producto |
| Investing.com | Consulta manual de ratings visibles en su interfaz | Sus terminos prohiben usar, almacenar, reproducir, mostrar, transmitir o distribuir los datos sin permiso escrito |

El catalogo versionado vive en `data/samples/licensed_extensions.csv` y se
muestra mediante `/dashboard/extensions` y `/api/v1/extensions/licensed`.

## Fuentes Oficiales Revisadas

- Massive Benzinga Analyst Ratings: <https://massive.com/docs/rest/stocks/benzinga/analyst-ratings>
- Massive pricing: <https://massive.com/pricing>
- Massive individual market-data terms: <https://massive.com/legal/market_data_terms_individual>
- Benzinga Analyst Ratings API: <https://www.benzinga.com/apis/analyst-ratings-api/>
- AnaChart datasets and data feeds: <https://anachart.com/datasets-data-feeds>
- MarketBeat All Access pricing: <https://www.marketbeat.com/subscribe/all-access/>
- MarketBeat FAQ: <https://www.marketbeat.com/faq/>
- MarketBeat terms: <https://www.marketbeat.com/terms/>
- WallStreetZen plans: <https://www.wallstreetzen.com/plans>
- WallStreetZen terms: <https://www.wallstreetzen.com/terms-of-service>
- GuruFocus FAQ: <https://www.gurufocus.com/faq>
- GuruFocus term of use: <https://www.gurufocus.com/term-of-use>
- Yahoo Finance providers: <https://help.yahoo.com/kb/SLN2310.html>
- Investing.com terms: <https://www.investing.com/about-us/terms-and-conditions>
