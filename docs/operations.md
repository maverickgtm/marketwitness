# Operacion Continua De Listing Watch

## Objetivo

La lista inicial de SpaceX, Cerebras y candidatos conocidos es una semilla.
El monitor continuo debe detectar **cualquier** potencial nueva IPO visible en
fuentes publicas, someterla a revision y luego actualizar el dashboard.

## Fuente Primaria: SEC EDGAR

La SEC publica indices diarios de todos los filings presentados. TargetAudit
escanea los formularios con interes para IPO Watch:

| Formulario | Uso En La Cola |
|---|---|
| `S-1`, `F-1` | Nueva declaracion de registro que requiere verificar si es IPO |
| `S-1/A`, `F-1/A` | Enmienda a una declaracion detectada |
| `S-1MEF`, `F-1MEF` | Posible ampliacion de valores registrados |
| `424B4` | Prospecto final que puede confirmar terminos de oferta |
| `RW` | Solicitud de retiro que puede cancelar el seguimiento |

Un filing descubierto no entra automaticamente como IPO confirmada. Muchos
formularios de registro pueden representar ofertas secundarias, reventas u
otras operaciones.

## Que Es El User-Agent

La SEC no pide una cuenta ni una clave API para descargar datos publicos.
Solicita que el trafico automatizado se identifique con una organizacion o
proyecto y un correo monitoreado.

Ejemplo:

```text
TargetAudit mario@ejemplo.com
```

El correo debe ser uno que puedas revisar si la SEC necesita contactar al
operador del monitor. Puede ser tu correo normal o, preferiblemente, un correo
dedicado al proyecto, por ejemplo `targetaudit@tudominio.com`.

No pongas ese correo en GitHub. Configuralo localmente o como secret del
repositorio:

```bash
export TARGETAUDIT_SEC_USER_AGENT="TargetAudit tu-correo@ejemplo.com"
```

Para una ejecucion recurrente local tambien puede guardarse en el archivo
ignorado `data/private/sec_user_agent.txt`, con una sola linea:

```text
TargetAudit tu-correo@ejemplo.com
```

El archivo `.env.example` muestra el nombre esperado de la variable, pero no
incluye una credencial real.

## Ejecucion Manual En Vivo

```bash
export TARGETAUDIT_SEC_USER_AGENT="TargetAudit tu-correo@ejemplo.com"
PYTHONPATH=src python3 -m targetaudit sec-ipo-discover \
  --date YYYY-MM-DD \
  --output build/live/sec-ipo-discovery.csv \
  --report build/live/sec-ipo-discovery.md
```

Para el demo y las pruebas se usa un indice local de ejemplo, sin solicitar
datos a SEC:

```bash
make verify
```

## Flujo Continuo Recomendado

1. Cada dia habil de mercado, descargar el indice diario SEC una vez.
2. Extraer formularios potencialmente relacionados con IPO.
3. Guardar la cola y comparar contra ejecuciones anteriores.
4. Revisar nuevos `S-1`/`F-1` para confirmar si describen una IPO.
5. Promover casos confirmados al registro `IPO Watch`.
6. Confirmar ticker, exchange y fecha solo desde prospecto final, exchange o
   comunicado oficial.
7. Publicar el dashboard actualizado con historial de cambios.

## Historial De Mercados Globales

Los cinco conectores internacionales generan CSV normalizados. Después de
obtenerlos, `global-alerts` copia la lectura del día a
`data/raw/global/history/YYYY-MM-DD/`, selecciona la última captura anterior
y genera una bandeja común:

```bash
PYTHONPATH=src python3 -m targetaudit global-alerts \
  --hkex data/raw/global/hkex-monitor-live.csv \
  --lse data/raw/global/lse-upcoming-live.csv \
  --asx data/raw/global/asx-monitor-live.csv \
  --tsx data/raw/global/tsx-monitor-live.csv \
  --sgx data/raw/global/sgx-monitor-live.csv \
  --history-dir data/raw/global/history \
  --output build/live/global-alerts.csv \
  --report build/live/global-alerts.md \
  --html build/live/global-alerts.html
```

La primera ejecución establece la línea base y no inventa cambios. A partir
de la segunda, la bandeja marca evidencia nueva, modificada o removida del
feed para revisión. Una remoción nunca se promueve automáticamente a retirada,
admisión o cotización completada.

## Automatizaciones Locales Activas

En la aplicacion Codex se configuraron dos ejecuciones recurrentes locales en
dias habiles:

- `TargetAudit IPO Watch diario`: consulta el indice SEC, guarda la cola de
  revision y resume posibles registros, prospectos o retiros nuevos.
- `TargetAudit Global Listings diario`: consulta los cinco feeds JSON
  oficiales o páginas estructuradas, el componente JSON oficial LSE `Upcoming issues` y el
  contraste público FCA NSM, además de las tablas oficiales ASX y TSX; resume
  cambios HKEX, emisiones previstas en Londres, coincidencias documentales,
  solicitudes/retiradas australianas, cotizaciones confirmadas en Canadá y
  prospectos SGX. También preserva snapshots y genera `Global Listings Alerts`.

Ambas tareas tratan los eventos como informacion regulatoria para investigar,
no como instrucciones para tomar posiciones.

El contraste FCA NSM distingue entre un emisor sin documento encontrado y
una coincidencia documental que requiere revisión. No promueve
automáticamente una fecha esperada a admisión confirmada, porque el NSM no es
en tiempo real y el tipo de documento debe examinarse.

El monitor ASX conserva como `anticipated` los registros con fecha prevista y
como `withdrawn` los retirados. ASX indica que recibió una solicitud formal,
pero fechas y códigos aún pueden cambiar.

El monitor TSX conserva únicamente el estado `listed`, porque su fuente
publica nuevas compañías ya cotizadas. Debe utilizarse como confirmación
posterior y no como detector anticipado de IPO.

El monitor SGX conserva `prospectus_published`, porque su fuente publica
documentos de prospecto. Es una señal documental para revisión, no una
confirmación automática de trading.

## Despliegue Futuro En GitHub

- Entrada: indices diarios SEC, feeds HKEXnews y comunicados oficiales.
- Salida: eventos nuevos, entidades promovidas, retiros y cambios de estado.
- Alertas: nuevas IPOs confirmadas, pricing, primer dia de cotizacion.
- Proteccion SEC: maximo muy inferior a las 10 solicitudes por segundo
  permitidas; normalmente una solicitud diaria de indice y solicitudes
  puntuales de documentos a revisar.

En un repositorio GitHub publico, `TARGETAUDIT_SEC_USER_AGENT` se configurara
como `Actions secret`, nunca escrito en el codigo ni en los reportes.

## Limites

- Las presentaciones confidenciales no se pueden descubrir hasta hacerse
  publicas.
- SEC cubre el mercado regulado en Estados Unidos; IPOs en Londres, Hong Kong
  u otras plazas necesitan conectores adicionales.
- Fuentes noticiosas pueden advertir de una operacion, pero no deben confirmar
  estado por si solas.
