# Policy Signal Impact Lab

Fecha de revision: `2026-05-25`.

## Propuesta

`Policy Signal Impact Lab` estudia si una comunicacion publica verificable
coincide con cambios posteriores en volatilidad o activos relacionados. El
primer caso disenado es `Donald Trump / Truth Social`, con punto de inicio del
segundo mandato el `2025-01-20`.

El nombre de trabajo de la medida es **Policy Signal Impact Trace**. No se
publica aun como un indice cuantitativo porque no existe un historial
autorizado de publicaciones ingerido por TargetAudit.

## Por Que Puede Diferenciar El Proyecto

La intuicion no es completamente nueva:

| Precedente | Lo Que Ya Existe | Diferencia De TargetAudit |
|---|---|---|
| JPMorgan `Volfefe Index` (2019) | Analizo tweets de Donald Trump y volatilidad de tasas, especialmente Treasury 2Y/5Y | TargetAudit plantea trazabilidad publica por evento, ventanas declaradas, activos multiples e interseccion con IPO/listing evidence |
| `Trump & Dump` (sitio revisado en 2026-05-25) | Declara seguimiento de Truth Social y correlacion de mercado con un score de manipulacion | TargetAudit evita etiquetar manipulacion o causalidad sin evidencia reproducible y mantiene un control de derechos visible |

La funcion distintiva no debe ser solamente alertar cuando una publicacion
aparece. Debe permitir inspeccionar exactamente:

1. Que publicacion o documento origino el episodio y bajo que permiso se obtuvo.
2. Que tema se clasifico: tarifas, tasas, energia, empresa, cripto o geopolitica.
3. Que activos y ventanas se midieron.
4. Que datos fueron excluidos, retrasados o no autorizados.
5. Que conclusion es observacional y no una recomendacion.

## Diseno De Medicion

La pagina `/dashboard/policy-signals` y el endpoint
`/api/v1/intelligence/policy-signals` publican el diseno inicial:

| Capa | Lentes Iniciales |
|---|---|
| Equity beta | S&P 500, Nasdaq-100 y ETFs sectoriales |
| Risk temperature | Grafico diario externo `VIXCLS` de FRED |
| Policy transmission | Treasury curve, USD, WTI y Brent |
| Frontier markets | BTC, ETH e IPO/listing candidates monitorizados |

Ventanas propuestas: misma sesion, sesion siguiente, `5`, `20` y `60`
sesiones. Un episodio real necesitara timestamp verificable, referencia
publica, derechos documentados y datos de mercado autorizados para cada
ventana.

## Limite De Truth Social

Truth Social es una fuente relevante, pero no queda habilitada como feed.
Sus terminos oficiales revisados el `2026-05-25` indican que el usuario no
debe:

- acceder al servicio por medios automatizados o no humanos;
- recuperar sistematicamente contenidos para crear una coleccion o base de datos;
- utilizar data mining, robots, scrapers u otras herramientas de extraccion;
- usar el servicio o contenido para fines comerciales sin permiso.

Por eso TargetAudit registra `truth-social-public-content` como
`restricted_no_collection`: no descarga el historial, no reproduce textos de
publicaciones y no ofrece monitoreo en tiempo real mientras no exista permiso
escrito o un proveedor autorizado con derechos suficientes.

## Ruta Gratuita Confirmada: White House RSS

La busqueda confirmo una alternativa mucho mas limpia para iniciar episodios
oficiales sin esperar permiso de Truth Social:

| Feed | Verificacion | Uso En TargetAudit |
|---|---|---|
| `https://www.whitehouse.gov/news/feed/` | RSS oficial activo; declara actualizacion horaria e incluye entradas firmadas `The White House` | Fuente primaria candidata para statements, fact sheets y noticias oficiales |
| `https://www.whitehouse.gov/presidential-actions/feed/` | RSS oficial activo; incluye executive orders, memoranda y proclamations | Fuente primaria candidata para decisiones formales con posible impacto económico |
| `https://www.whitehouse.gov/wire/feed/` | RSS oficial activo, pero enlaza Reuters, Fox, WSJ, YouTube y otros medios | Solo radar de titulo, timestamp y URL externa; no importar cuerpos periodisticos |

La politica de copyright de `whitehouse.gov` indica que los materiales
producidos por el Gobierno no estan protegidos por copyright conforme a ley
federal y que, salvo indicacion distinta, contenido de terceros del sitio se
licencia bajo CC BY 3.0. Aun asi, `White House Wire` se trata de manera
conservadora porque los articulos enlazados viven en dominios de terceros y
conservan sus propias condiciones.

Esto cambia el roadmap: podemos construir primero un monitor oficial de
decisiones y mensajes presidenciales, y dejar Truth Social como una extension
futura sujeta a permiso.

## Grafica VIX Visible

El laboratorio utiliza una imagen alojada por FRED de la serie
`CBOE Volatility Index: VIX [VIXCLS]` desde `2025-01-20`. FRED identifica la
serie como `Copyrighted: Citation Required`; la pagina conserva el enlace y
la atribucion visible. La grafica es contexto externo: TargetAudit no ingiere
observaciones VIX ni calcula resultados con ella en esta entrega.

## Fuentes Consultadas

- Truth Social Terms of Service: <https://help.truthsocial.com/legal/terms-of-service/>
- White House News RSS: <https://www.whitehouse.gov/news/feed/>
- White House Presidential Actions RSS: <https://www.whitehouse.gov/presidential-actions/feed/>
- White House Wire RSS: <https://www.whitehouse.gov/wire/feed/>
- White House copyright policy: <https://www.whitehouse.gov/copyright/>
- FRED `VIXCLS`: <https://fred.stlouisfed.org/series/VIXCLS>
- FRED graph sharing help: <https://fredhelp.stlouisfed.org/category/fred/graphs/share-my-fred-graph/>
- Bloomberg, JPMorgan `Volfefe Index`, 2019-09-09:
  <https://www.bloomberg.com/news/articles/2019-09-09/jpmorgan-creates-volfefe-index-to-track-trump-tweet-impact>
- CNBC, JPMorgan `Volfefe Index`, 2019-09-08:
  <https://www.cnbc.com/2019/09/08/donald-trump-is-tweeting-more-and-its-impacting-the-bond-market.html>
- Trump & Dump: <https://www.trumpanddump.app/>
