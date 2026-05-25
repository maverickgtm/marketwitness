# Deep Dive: Tokio, Toronto Y Frankfurt

Revision: `2026-05-25`.

Esta revision profundiza tres mercados ya presentes en `Global Listings
Watch`. El objetivo es mejorar reglas de confirmacion y no duplicar conectores
cuando la fuente regional existente ya es la mejor ruta.

## Decision Ejecutiva

| Mercado | Hallazgo Oficial | Decision TargetAudit |
|---|---|---|
| Tokio | `JPX New Listings` publica fecha de listing, fecha de aprobacion, emisor, codigo, segmento y datos de oferta; `EDINET` aporta documentos regulatorios previos | Monitor JPX implementado; mantener prioritario hasta sumar flujo documental `EDINET` y diff diario |
| Toronto | `TSX New Company Listings` ya confirma nuevas cotizaciones; `SEDAR+` muestra filings pero prohibe scraping, automatizacion y construir bases sin permiso | Mantener el feed TSX activo para listings completados y bloquear expansion prospectiva automatizada basada en SEDAR+ |
| Frankfurt | BaFin publica prospectos aprobados y remite al registro `ESMA`; ESMA ya ofrece la ruta A2A atribuible para Alemania | Mantener Frankfurt dentro del conector regional `ESMA`, con BaFin como corroboracion documental, sin crear conector duplicado |

## Tokio

### Senales Gratuitas Utiles

La pagina oficial `JPX New Listings` muestra compañías nuevas de Tokyo Stock
Exchange y contiene datos que sirven para confirmar el ciclo de una IPO:

- fecha de listing y fecha de aprobacion;
- nombre de emisor y codigo;
- segmento de mercado;
- rango indicado y precio de oferta cuando aparecen publicados;
- acciones ofrecidas y distribucion secundaria cuando corresponda.

La combinacion correcta para el producto es:

1. `EDINET`: detectar un securities registration statement u otro documento
   regulatorio de oferta.
2. `JPX New Listings`: confirmar aprobacion de listing o fecha de listing en
   Tokyo Stock Exchange.

Esto mejora IPO Watch internacional sin confundir un filing con negociacion
iniciada.

Implementado el `2026-05-25`: `jpx-monitor` procesa la tabla JPX, distingue
`approved_pending_listing` de `listed` segun la fecha publicada y enlaza el
outline oficial. La etapa `EDINET` permanece pendiente.

### Ruta Que No Entra En Open Edition

`TDnet API` seria valioso para disclosures de compañías japonesas y declara
que la información adquirida puede redistribuirse a terceros. Sin embargo,
JPX publica una tarifa base de `JPY 70,000` mensuales, mas cargo variable por
documentos recuperados. Por eso no debe formar parte de una edición gratuita.

## Toronto

`TSX New Company Listings` continúa siendo una fuente oficial útil para
confirmar compañías ya listadas. El sitio muestra fecha, emisor y símbolo, por
lo que el monitor existente se mantiene.

La vía natural para prospectos previos seria `SEDAR+`, pero sus términos de
uso, actualizados el `2023-04-28`, establecen restricciones incompatibles con
la edición pública automatizada:

- no permite scraping ni medios automatizados para reproducir múltiples
  piezas de información pública;
- no permite construir una base de datos con esa información;
- limita la reproducción a extractos o copias no alteradas en usos acotados,
  sin crear un producto o servicio basado en su comercialización.

Decision: no desarrollar un collector SEDAR+ para TargetAudit público sin
permiso escrito de la autoridad operadora. Toronto queda cubierto únicamente
como confirmacion posterior mediante el feed TSX ya implementado.

## Frankfurt

BaFin indica que, en Alemania, los valores no pueden en principio ofrecerse
públicamente ni admitirse a negociación en un mercado organizado sin un
prospecto aprobado. Su base publica permite consultar prospectos aprobados,
suplementos y documentos asociados, y la propia BaFin remite al registro
`ESMA Prospectus Register`.

Como `ESMA Prospectus III` ya quedó seleccionado para Alemania, Países Bajos e
Italia, no conviene crear otro conector Frankfurt que duplique prospectos.
El diseño previsto es:

- `ESMA`: ingesta regional atribuida de metadata de prospectos alemanes;
- `BaFin`: corroboracion documental de casos alemanes cuando se requiera;
- evidencia posterior del mercado/bolsa: confirmacion de admision o primer
  trading, separada del prospecto.

## Efecto En El Producto

| Capacidad | Antes | Despues De Esta Revision |
|---|---|---|
| Tokio IPO Watch | `EDINET` pendiente para documentos | Confirmacion `JPX New Listings` implementada; deteccion `EDINET` pendiente |
| Toronto Watch | Feed TSX de listings completados | Igual, con bloqueo documentado de `SEDAR+` automatizado |
| Frankfurt Watch | Cubierto regionalmente por `ESMA` | Igual, con `BaFin` definido como corroboracion nacional |
| Rankings de analistas | Sin dataset gratuito publicable | Sin cambio; ninguna de estas fuentes aporta price targets individuales reutilizables |

## Fuentes Oficiales Revisadas

- JPX New Listings: <https://www.jpx.co.jp/english/listing/stocks/new/index.html>
- JPX New Listings / Transfers / Delistings: <https://www.jpx.co.jp/english/listing/stocks/index.html>
- JPX TDnet API Service: <https://www.jpx.co.jp/english/markets/paid-info-listing/tdnet/02.html>
- FSA EDINET Documents API: <https://disclosure2.edinet-fsa.go.jp/guide/static/disclosure/WZEK0090.html>
- TSX New Company Listings: <https://www.tsx.com/en/news/new-company-listings>
- SEDAR+ Terms of Use: <https://sedarplus.ca/onlinehelp/terms-of-use/>
- BaFin securities prospectuses: <https://www.bafin.de/DE/Aufsicht/Prospekte/Wertpapiere/prospektewertpapiere_node.html>
- BaFin deposited securities prospectuses: <https://www.bafin.de/DE/PublikationenDaten/Datenbanken/Prospektdatenbanken/Wertpapiere/wertpapiere_node.html>
- Deutsche Boerse Cash Market segments: <https://www.deutsche-boerse-cash-market.com/scale_e/>
- ESMA Prospectus III A2A help: <https://registers.esma.europa.eu/publication/helpApp>
