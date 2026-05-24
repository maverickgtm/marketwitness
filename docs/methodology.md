# Metodologia v0.3

## Vertical Inicial

`v0.3` prepara el analisis para `U.S. Financials`, comenzando por bancos y
otras companias financieras con targets verificables. Para el piloto real, el
benchmark sectorial preferido es `XLF`. El motor sigue siendo general para
permitir pruebas y futuros verticales, pero ningun ranking multisectorial se
presentara como resultado principal de la primera investigacion.

## Preguntas De Investigacion

TargetAudit separa tres preguntas que no deben confundirse:

1. **Target Hit Rate:** ?el precio objetivo fue alcanzado durante su horizonte?
2. **Forecast Accuracy:** ?que tan cerca estuvo el target del precio al final
   del horizonte?
3. **Signal Value:** ?la direccion implicita del target obtuvo mejor retorno
   que el benchmark durante el mismo periodo?

Una alta tasa de targets alcanzados no demuestra por si sola que una firma
produzca una estrategia rentable.

## Unidad De Observacion

Una observacion es un target individual publicado por una firma para un
instrumento en una fecha determinada. Es evaluable solo si contiene:

- Identificador unico de observacion.
- Ticker e identificacion de la compania disponible.
- Firma que emitio el target.
- Fecha de publicacion.
- Precio objetivo positivo.
- URL o referencia verificable de la fuente.
- Serie diaria de precios ajustados suficiente para evaluar el horizonte.

El analista individual y el rating son opcionales porque algunas fuentes no
los publican, pero se conservan cuando estan disponibles.

## Ingreso De Targets Reales

Los targets provenientes de un proveedor externo solo se normalizan mediante
una exportacion autorizada acompanada por un manifiesto de uso. El manifiesto
debe identificar proveedor, fecha, referencia de licencia y permiso declarado
para investigacion interna. Este control demuestra el origen operativo del
archivo, no derechos de publicacion; el ranking real permanece bloqueado
hasta aprobar esos derechos.

Una fila del export se rechaza antes de evaluar cuando carece de identificador,
ticker, emisor, firma, fecha ISO, target positivo o URL HTTPS de evidencia, o
cuando duplica un identificador ya importado.

## Acciones Corporativas

Una barra de precio ajustada no basta para asumir que un target nominal
publicado antes de un split continúa en la misma base por accion. Tampoco un
cambio de ticker demuestra que dos series locales tengan continuidad completa.

Cuando se proporciona un registro auditado de acciones corporativas, cualquier
target cuyo horizonte cruce un `stock_split`, `reverse_split` o
`ticker_change` se excluye como `corporate_action_review_required`. Esta
version detecta la incompatibilidad; no reescala targets ni encadena símbolos
automáticamente. Un futuro procedimiento de normalización deberá conservar
fuente, factor utilizado y serie ajustada resultante.

## Convenciones Temporales

- Horizonte por defecto: `365` dias calendario desde la publicacion.
- Referencia: ultimo cierre ajustado disponible en o antes de la fecha de
  publicacion, con una antiguedad maxima de 7 dias calendario. La direccion
  alcista o bajista del target se deriva contra esta referencia.
- Entrada: primer cierre ajustado disponible **posterior** a la fecha de
  publicacion. Esto evita asumir que era posible operar antes de conocer una
  nota publicada durante el dia.
- Si no existe precio de entrada dentro de los 7 dias calendario siguientes a
  la publicacion, la observacion se excluye como `delayed_entry_price`.
- Evaluacion del acierto: comienza en la siguiente barra disponible despues
  del cierre de entrada; un maximo o minimo intradia del propio dia de entrada
  no puede contarse retroactivamente.
- Si la entrada ya atraveso el target definido contra la referencia, la
  observacion se excluye como `target_crossed_before_entry`; no era una senal
  ejecutable bajo esta regla.
- Vencimiento: ultimo precio disponible en o antes de la fecha de expiracion.
- Ventana completa: el precio terminal debe estar como maximo a 7 dias
  calendario del vencimiento esperado.
- Observaciones que aun no vencieron a la fecha de calculo se marcan
  `pending`, no se consideran fallos.

## Direccion Del Target

La direccion se deriva comparando el target con el precio de referencia:

- `up`: target mayor al precio de referencia.
- `down`: target menor al precio de referencia.
- `flat`: target igual al precio de referencia; se excluye del scoring direccional
  en esta version.

## Definicion De Acierto

- Target `up`: acierto si, despues de la entrada, el maximo ajustado diario
  alcanza o supera el target dentro del horizonte.
- Target `down`: acierto si, despues de la entrada, el minimo ajustado diario
  alcanza o cae por debajo del target dentro del horizonte.
- `days_to_target`: dias calendario entre la fecha de entrada y la primera
  fecha de acierto.

El reporte presenta este indicador como `target hit`, no como ganancia
realizada.

## Metricas v0.3

Para cada observacion evaluada:

- `hit`: target alcanzado o no.
- `terminal_price`: cierre ajustado al vencimiento.
- `terminal_absolute_error_pct`: `abs(target - terminal_price) / target`.
- `directional_return_pct`: retorno de una posicion larga para targets `up` y
  retorno corto simple para targets `down`, mantenida hasta vencimiento.
- `benchmark_directional_return_pct`: misma direccion aplicada al benchmark.
- `excess_return_pct`: retorno direccional menos retorno direccional del
  benchmark.

Para cada firma:

- Cantidad de observaciones evaluadas.
- Tasa de acierto.
- Intervalo de confianza Wilson del 95% para la tasa de acierto.
- Error absoluto medio al vencimiento.
- Mediana de dias hasta target para aciertos.
- Retorno excesivo promedio.

Para cada segmento de firma por sector y por direccion:

- Las mismas metricas de firma, con `N` e intervalo Wilson calculados dentro
  del segmento.
- Aplicacion independiente del minimo muestral configurado.

## Incertidumbre De La Tasa De Acierto

El reporte muestra un intervalo Wilson del 95% para cada `target hit rate` de
firma y de direccion. Se utiliza Wilson en lugar de una aproximacion normal
simple porque permanece informativo con muestras pequenas y tasas cercanas a
`0%` o `100%`.

Para `x` aciertos en `n` observaciones y `z = 1.959963984540054`, el intervalo
es:

```text
centro = (p + z^2/(2n)) / (1 + z^2/n)
margen = z * sqrt(p(1-p)/n + z^2/(4n^2)) / (1 + z^2/n)
intervalo = [centro - margen, centro + margen]
```

donde `p = x / n`. Este intervalo cuantifica incertidumbre muestral bajo una
lectura binomial de los aciertos observados. No corrige sesgos de fuente,
seleccion de universo, targets repetidos o dependencia entre observaciones.

## Rankings

El ranking publico de produccion debera exigir al menos 50 observaciones
evaluables por firma. El CLI permite bajar el limite solo para desarrollo y
demostraciones, y el reporte informa claramente el umbral utilizado.
El orden actual conserva la tasa observada y el tamano de muestra, mientras el
intervalo impide presentar diferencias pequenas o muestras reducidas como
conclusiones fuertes.

El reporte conserva un ranking general y agrega rankings de firmas por sector
y por direccion (`up`/`down`). Una firma solo aparece en un segmento si ese
segmento cumple por si mismo el minimo muestral; la muestra global no habilita
un subgrupo pequeno.

En fases futuras se agregaran:

- Ajuste adicional por volatilidad dentro de cada sector.
- Manejo de targets revisados como posiciones activas.
- Costos de transaccion y reglas de salida ejecutables.
- Universo punto-en-el-tiempo para eliminar sesgo de supervivencia.

## Exclusiones

Una observacion se excluye, con motivo registrado, cuando:

- Falta un campo obligatorio o la fuente.
- El target no es positivo.
- No existe un precio de entrada posterior a la publicacion.
- No existe un precio de referencia cercano a la fecha de publicacion.
- El primer precio util o el primer precio del benchmark aparece con mas de 7
  dias de retraso.
- El target ya fue atravesado al momento de la entrada ejecutable.
- La ventana del benchmark no coincide con las fechas de entrada y vencimiento
  de la accion evaluada.
- No hay ventana de precios completa.
- El target es igual al precio de referencia.
- No se encuentra benchmark suficiente cuando este fue especificado.
- Existe un split o cambio de ticker documentado dentro del horizonte y no se
  ha normalizado de forma auditada.

## Reproducibilidad

Cada reporte debe registrar:

- Version de metodologia.
- Fecha `as_of` del calculo.
- Archivos o proveedor de datos usados.
- Filas excluidas y motivo.
- Parametros modificados, como la muestra minima.
