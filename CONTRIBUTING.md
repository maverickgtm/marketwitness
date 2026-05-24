# Contribuir

Gracias por ayudar a que TargetAudit sea verificable y util.

## Reglas Basicas

- No agregues datasets de terceros sin documentar licencia y permiso de
  redistribucion.
- Toda nueva metrica debe documentarse en `docs/methodology.md` e incluir
  pruebas.
- No presentes una firma como "mejor" sin mostrar muestra, periodo y
  benchmark.
- Mantener fuentes originales o identificadores auditables para toda
  observacion real.

## Desarrollo

```bash
make test
make demo
```

Para proponer una fuente de datos, abre un issue indicando cobertura historica,
campos, limites de uso, costo y condiciones de redistribucion.
