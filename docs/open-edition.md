# TargetAudit Open Edition

La edicion principal publicada en GitHub debe poder ejecutarse sin comprar
datos ni contratar APIs comerciales.

## Promesa Del Producto

`Open Edition` incluye tres niveles claramente separados:

| Modo | Datos | Costo De Datos | Uso |
|---|---|---:|---|
| Offline showcase | Fixtures creados por el proyecto | Ninguno | Probar Financials Scorecard, RWA Watch Sandbox, auditoria y dashboard completo |
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
Tambien registra MarketBeat como piloto privado potencial de bajo costo y
WallStreetZen como referencia metodologica; ninguno habilita un ranking
publico real ni es requisito de esta edicion.
Finnhub y Financial Modeling Prep quedan registrados como futuras rutas
programaticas, pero sus planes gratuitos no conceden por si solos derechos de
mostrar o redistribuir datos en un producto publico.

La ruta `/dashboard/policy` presenta la politica de uso publico: explica que
los monitores son evidencia para investigacion y no recomendaciones de
inversion, muestra las fuentes bloqueadas desde el registro validado y declara
que la revision legal externa continua pendiente.

La ruta `/dashboard/market-context` integra el widget oficial atribuido de
TradingView para contexto visual de `XLF`. El componente carga directamente
desde TradingView; TargetAudit no almacena, exporta ni usa esos datos en el
ranking, y el widget no reemplaza una licencia de historial de targets.

La investigacion inicial de `RWA Watch` mapea 20 exchanges centralizados y
Pepperstone. Los terminos revisados bloquean la recoleccion/republicacion
publica automatizada de `xStocks / Backed`, aunque existan endpoints visibles;
`Ondo Global Markets` documenta APIs para display pero requiere onboarding,
API key y revision de derechos de output. La Open Edition incluye en su lugar
un sandbox sintetico que no realiza llamadas reales. Ninguna de estas fuentes
alimenta analyst targets. Ver
[RWA Watch: Exchanges Y Fuentes Base](rwa-watch-sources.md).
Bybit tambien permanece como referencia bloqueada: su producto xStocks tiene
restricciones jurisdiccionales incompatibles con tratarlo como feed publico
global del repositorio.
Kraken queda en la misma categoria porque sus divulgaciones xStocks excluyen
Estados Unidos. Gate y Bitget solo se conservan como referencias pendientes de
permiso explicito de output publico.

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
- Las vistas `/dashboard/etf/nport-recent` y `/dashboard/etf-regulatory`
  permanecen separadas de los sandboxes sintéticos `ARKK-DEMO`, `XLF-DEMO`
  e `IYF-DEMO`.
- Las vistas `/dashboard/etf/nport-catalog` y `/dashboard/etf/nport-sync`
  muestran el catálogo trimestral y su control incremental, no operaciones
  diarias del ETF.

### Public Document Checks

- Usa consulta documental pública FCA NSM para corroborar documentos de
  emisores seguidos.
- No sustituye monitores de bolsas cuya reutilización requiera revisar
  términos.

### RWA Watch Sandbox

- Compara precios sinteticos de referencia y de token/venue en una pagina
  separada del scorecard.
- Marca desviaciones para revision metodologica, nunca como senal de compra o
  venta.
- No recolecta datos de xStocks, Ondo o exchanges mientras sus derechos de
  output publico no esten documentados.

### Market Context

- Incrusta el widget oficial gratuito de TradingView con atribucion visible.
- Muestra `XLF` como contexto visual del benchmark sectorial.
- No convierte contenido del widget en dataset, evidencia o input del
  scorecard.

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
Desde ella se abre `/dashboard/reports`, un indice de
`/dashboard/ipo-watch`, `/dashboard/sec-discovery`, `/dashboard/sec-alerts`, `/dashboard/ipo-reviews`,
`/dashboard/etf/arkk-demo`, `/dashboard/etf/xlf-demo`, `/dashboard/etf/iyf-demo`,
`/dashboard/etf/nport-recent`, `/dashboard/etf-regulatory`,
`/dashboard/etf/nport-catalog`, `/dashboard/etf/nport-sync`,
`/dashboard/document-checks`, `/dashboard/rwa-watch`,
`/dashboard/global-listings`, `/dashboard/global-alerts` y
`/dashboard/issuer-confirmations`, ademas del paquete fijo
`/dashboard/audit/{report}` para evidencia Financials del demo; estas rutas
solo sirven artefactos HTML conocidos producidos por `make demo`. El paquete
`/dashboard/governance-report/{snapshot}` expone exclusivamente los snapshots
generados de manifiesto, extensiones licenciadas, fuentes, permisos,
revisiones y readiness, separado
de las pantallas interactivas. La portada global abre exclusivamente
los diez monitores internacionales incluidos en la lista permitida
`/dashboard/global/{monitor}`, no un explorador de archivos generados.
La portada tambien enlaza `/dashboard/policy`, que debe revisarse antes de
habilitar datos live o publicar resultados.
Tambien enlaza `/dashboard/market-context`, cuya carga de TradingView requiere
conexion a Internet pero no suscripcion de datos de TargetAudit.

## Reporte Periodico En GitHub

El workflow `.github/workflows/open-edition-report.yml` genera una copia
probada de la Open Edition cada lunes a las `12:17 UTC` y tambien puede
ejecutarse manualmente desde GitHub Actions. Ejecuta `make verify` y conserva,
durante 30 dias, un artefacto descargable con:

- las paginas, CSV y base DuckDB demostrativa de `build/demo/`;
- el wheel instalable producido en `build/dist/`.

La ejecucion no necesita secrets, claves API ni suscripciones porque procesa
exclusivamente fixtures redistribuibles incluidos en el repositorio. No
consulta filings live, no incluye holdings reales de emisores y no publica un
ranking real de analistas. El bundle puede recorrerse en la aplicacion desde
`/dashboard/reports`, que enlaza solo rutas permitidas y no expone el
directorio generado como explorador de archivos.

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
Ver [Politica De Uso Publico Y Derechos De Datos](public-use-policy.md) para
los limites visibles de interpretacion, recoleccion y output.
