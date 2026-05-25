# Seguridad

## Alcance

TargetAudit procesa archivos de evidencia, realiza solicitudes opcionales a
fuentes publicas y expone una API/dashboard local de solo lectura. Reporta de
forma privada problemas que puedan permitir:

- ejecucion de codigo o escritura de archivos al importar evidencia;
- fuga de credenciales, datos en `data/private/` o contactos de `User-Agent`;
- elusion de controles de licencias, procedencia o bloqueo de publicacion;
- solicitudes inesperadas a destinos externos desde un conector.

## Como Reportar

Usa un reporte privado de vulnerabilidad en la pestana `Security` del
repositorio GitHub. No publiques en un issue claves, datos privados ni una
prueba de concepto explotable. El mantenedor debe habilitar `Private
vulnerability reporting` al publicar el repositorio.

Incluye version o commit, componente afectado, impacto, pasos minimos de
reproduccion y una correccion sugerida si existe.

## Datos Y Credenciales

No subas claves API, archivos descargados de proveedores, datasets sin permiso
de redistribucion ni correos personales usados para identificar solicitudes
SEC. El proyecto reserva `data/private/`, `data/raw/`, `.env` y `build/` para
uso local.

