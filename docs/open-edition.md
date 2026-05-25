# TargetAudit Open Edition

La edicion principal publicada en GitHub debe poder ejecutarse sin comprar
datos ni contratar APIs comerciales.

## Promesa Del Producto

`Open Edition` incluye tres niveles claramente separados:

| Modo | Datos | Costo De Datos | Uso |
|---|---|---:|---|
| Offline showcase | Fixtures creados por el proyecto | Ninguno | Probar Financials Scorecard, auditoria y dashboard completo |
| Public monitors | SEC EDGAR, SEC N-PORT y FCA NSM bajo sus reglas publicas | Ninguno | Seguir filings IPO y evidencia regulatoria ETF/documental |
| Authorized extension | Archivos aportados por el usuario con derechos documentados | No requerido por TargetAudit | Ejecutar rankings propios sin que el repositorio distribuya datos restringidos |

El repositorio no promete un ranking real de analistas construido con un
dataset comercial. Ese módulo continúa disponible como motor y formato de
investigación, pero la utilidad de la edición pública no depende de Benzinga,
Alpha Vantage, Nasdaq, NYSE ni S&P DJI.

La ruta `/dashboard/extensions` documenta proveedores opcionales que un
usuario podria contratar por cuenta propia. Incluye la expansion individual
Massive / Benzinga publicada a `USD 99/month`, sin presentarla como permiso
para publicar rankings compartidos.

## Capacidades Incluidas

### Financials Scorecard Sandbox

- Funciona completamente offline con datos sintéticos redistribuibles.
- Demuestra evaluación de targets, exclusiones, comparaciones, linaje,
  operaciones de calidad y Release Center.
- Sus resultados nunca se presentan como desempeño real de una firma.

### U.S. IPO Filing Watch

- Consume fuentes públicas SEC EDGAR sin clave de pago.
- Descubre filings potencialmente relacionados con cotizaciones y exige
  revisión documentada antes de promover una empresa.
- Las solicitudes live deben incluir `TARGETAUDIT_SEC_USER_AGENT` con un
  correo de contacto conforme a las reglas SEC.

### ETF Regulatory Holdings

- Consume filings y datasets públicos SEC N-PORT.
- Permite comparar periodos reportados y mantener una evidencia auditable.
- No se etiqueta como información diaria ni en tiempo real.

### Public Document Checks

- Usa consulta documental pública FCA NSM para corroborar documentos de
  emisores seguidos.
- No sustituye monitores de bolsas cuya reutilización requiera revisar
  términos.

## Ejecutar Sin Costos

```bash
python3 -m pip install -e ".[application]"
make verify
export TARGETAUDIT_DATABASE="build/demo/targetaudit.duckdb"
export TARGETAUDIT_SOURCE_REGISTRY="data/samples/source_registry.csv"
export TARGETAUDIT_GENERATED_REPORTS="build/demo"
python3 -m uvicorn targetaudit.api:app --host 127.0.0.1 --port 8000
```

Abrir `http://127.0.0.1:8000/` muestra la portada `Open Edition`.
Desde ella se abren `/dashboard/ipo-watch`, `/dashboard/etf-regulatory` y
`/dashboard/document-checks`, que solo sirven artefactos HTML conocidos
producidos por `make demo`.

Para recolectar datos SEC públicos en vez de utilizar fixtures:

```bash
export TARGETAUDIT_SEC_USER_AGENT="TargetAudit contacto@example.com"
```

No se necesita clave de API ni suscripción de datos para los conectores SEC.

## Extensiones Opcionales

Los expedientes de aprobación de proveedores comerciales se conservan como
arquitectura preparada para quien, en el futuro, decida aportar datos con
derechos suficientes. No son requisito para instalar, demostrar o utilizar
los módulos públicos gratuitos de TargetAudit.

Ver [Extensiones Licenciadas Opcionales](licensed-extensions.md) para precios
visibles, condiciones revisadas y el flujo `bring your own license`.
