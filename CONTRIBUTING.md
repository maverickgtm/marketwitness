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

## Seguridad Y Privacidad

No incluyas claves API, `.env`, descargas en `data/raw/`, evidencia privada ni
el correo usado en solicitudes SEC. Los problemas de seguridad se reportan de
forma privada siguiendo [SECURITY.md](SECURITY.md).
