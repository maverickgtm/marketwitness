# GitHub Release Candidate Checklist

## Objetivo Del Candidato

Publicar `TargetAudit Open Edition v0.1.0-rc.1` como proyecto abierto,
reproducible y util sin pagos obligatorios. El candidato demuestra auditoria
de evidencia, monitores regulatorios y un dashboard navegable; no promete
rankings reales de analistas ni recomendaciones de inversion.

## Listo Para El Candidato

- [x] Codigo bajo licencia MIT.
- [x] `DISCLAIMER.md`, politica de uso publico y limites de fuentes visibles.
- [x] `CONTRIBUTING.md`, `SECURITY.md`, plantillas de issues y pull requests.
- [x] Tests automatizados y workflow de GitHub Actions para Python 3.9 y 3.12.
- [x] Bundle Open Edition reproducible y wheel instalable sin datos pagados.
- [x] Dashboard y API de solo lectura con fuentes bloqueadas identificables.
- [x] Registro de 49 fuentes con clasificacion de permisos y evidencia.
- [x] Ruta gratuita oficial para futuros eventos presidenciales mediante
  `White House News RSS` y `Presidential Actions RSS`.

## Antes De Hacer Publico El Repositorio

- [ ] Ejecutar `make verify` desde un clon limpio y conservar el resultado de
  CI verde en el commit candidato.
- [x] Publicar tres capturas seleccionadas en `docs/assets/` y usarlas
  en el `README`: IPO Watch, Global Listings y Policy Signals.
- [ ] Crear el repositorio GitHub con descripcion, topics y enlace correcto
  antes de añadir badges permanentes.
- [ ] Habilitar `Private vulnerability reporting` en la pestana `Security`.
- [ ] Ejecutar una revision final de secretos y confirmar que correos, API
  keys, `data/private/`, `data/raw/` y `build/` no estan versionados.
- [ ] Publicar desde una historia limpia o reescrita: el borrador privado de
  permiso incluyo anteriormente un correo personal en commits locales.
- [ ] Crear tag y notas `v0.1.0-rc.1` unicamente despues de que Actions pase
  desde el repositorio publico.

## No Bloquea La Open Edition

- Un historial real publicable de price targets de firmas como Roth MKM,
  KBW, UBS, Barclays o Citi. Es una extension futura sujeta a licencia.
- Series historicas propias de Cboe/ICE para episodios VIX/VVIX/MOVE.
- Activacion de datos RWA, holdings diarios de emisores o fuentes comerciales.
- Collector automatico de White House RSS. La fuente ya esta aprobada como
  candidata; el collector es una mejora posterior al candidato inicial.

## Bloquea Cualquier Afirmacion De Datos Reales

- Publicar rankings reales de analistas sin derechos de output y evidencia por
  observacion.
- Automatizar Truth Social, fuentes marcadas `restricted_no_collection` o
  enlaces de terceros de White House Wire.
- Presentar estudios de reaccion, volatilidad o listings como consejo de
  inversion o causalidad comprobada.

## Comandos De Verificacion

```bash
python3 -m pip install -e ".[application]"
make verify
```

Para revisar el dashboard construido:

```bash
export TARGETAUDIT_DATABASE="build/demo/targetaudit.duckdb"
export TARGETAUDIT_SOURCE_REGISTRY="data/samples/source_registry.csv"
export TARGETAUDIT_PROVIDER_APPROVALS="data/samples/provider_approval_queue.csv"
export TARGETAUDIT_GENERATED_REPORTS="build/demo"
export TARGETAUDIT_LICENSED_EXTENSIONS="data/samples/licensed_extensions.csv"
python3 -m uvicorn targetaudit.api:app --host 127.0.0.1 --port 8000
```

Abrir `http://127.0.0.1:8000/` y recorrer `/dashboard/ipo`,
`/dashboard/global-listings`, `/dashboard/intelligence`,
`/dashboard/volatility`, `/dashboard/policy-signals` y `/dashboard/policy`.
