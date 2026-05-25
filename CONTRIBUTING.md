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
campos, limites de uso, costo y condiciones de redistribucion.

La edicion principal debe conservar al menos una ruta funcional sin gastos:
se prefieren fuentes regulatorias publicas, fixtures redistribuibles y
contribuciones de datos cuyos derechos estén documentados. Un conector
comercial puede añadirse como extensión opcional, no como requisito de uso.
