# Contribuir

Gracias por ayudar a que TargetAudit sea verificable y util.

## Reglas Basicas

- No agregues datasets de terceros sin documentar licencia y permiso de
  redistribucion.
- Toda nueva metrica debe documentarse en `docs/methodology.md` e incluir
  pruebas.
- No presentes una firma como "mejor" sin mostrar muestra, periodo y
  benchmark.
- El vertical publico inicial es `U.S. Financials`; propuestas para otros
  sectores deben explicar fuente, universo y benchmark.
- Mantener fuentes originales o identificadores auditables para toda
  observacion real.

## Desarrollo

```bash
make verify
```

Para proponer una fuente de datos, abre un issue indicando cobertura historica,
campos, limites de uso, costo y condiciones de redistribucion. GitHub ofrece
la plantilla `Propuesta de fuente de datos` para registrar esas pruebas de
forma uniforme.

La edicion principal debe conservar al menos una ruta funcional sin gastos:
se prefieren fuentes regulatorias publicas, fixtures redistribuibles y
contribuciones de datos cuyos derechos estén documentados. Un conector
comercial puede añadirse como extensión opcional, no como requisito de uso.

## Evidence Passport Commons

TargetAudit busca contributors globales para ampliar su red de evidencia
oficial. Antes de proponer codigo para una fuente nueva, prepara un
`Evidence Passport` mediante la plantilla `Propuesta de fuente de datos`.
Debe identificar:

- fuente oficial y clase de evidencia;
- terminos, licencia o permiso de output derivado;
- frecuencia o cadencia de actualizacion;
- regla de confirmacion y la afirmacion que la fuente no demuestra;
- costo, clave o requisito de registro.

Los passports aceptados pueden incorporarse al registro publico y a
`/api/v1/commons/passports`. Un conector se implementa despues, cuando su
uso publico es defendible. Esta separacion permite contribuir aun sin pagar
datasets ni desarrollar Python.

Antes de proponer una salida publica o un collector nuevo, revisa
[Politica De Uso Publico Y Derechos De Datos](docs/public-use-policy.md): una
fuente marcada como bloqueada o manual no debe automatizarse desde una
contribucion.

## Seguridad Y Privacidad

No incluyas claves API, `.env`, descargas en `data/raw/`, evidencia privada ni
el correo usado en solicitudes SEC. Los problemas de seguridad se reportan de
forma privada siguiendo [SECURITY.md](SECURITY.md).
