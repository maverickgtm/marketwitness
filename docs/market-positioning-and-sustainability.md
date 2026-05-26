# Posicionamiento Y Sostenibilidad Publica

Revision: `2026-05-25`

## Respuesta Honesta

TargetAudit puede interesar como proyecto publico, pero no debe presentarse
como "otro terminal de bolsa" ni prometer que derrotara a plataformas con
datasets licenciados. En investigacion financiera abierta existen productos
mas grandes, y en ranking de analistas ya existen competidores directos.

La oportunidad real es mas estrecha y mas creible:

> TargetAudit es una plataforma abierta para auditar senales financieras con
> trazabilidad de fuente, derechos de publicacion y reglas de verificacion
> visibles, comenzando por IPOs/listings globales y evidencia regulatoria ETF.

La propuesta concreta para diferenciar el lanzamiento es `Evidence Passport
Commons`: un registro visual y una API publica donde cada fuente muestra
origen y derechos revisados, y donde contributors pueden proponer la capa
faltante de cadencia y limite de afirmacion. En la revision realizada no se
encontro que `OpenBB`, `Stocknear` o `AnaChart` presentaran este protocolo de
contribucion y derechos como su producto central; esto no prueba inexistencia
absoluta de propuestas semejantes.

El ranking real de targets sigue siendo un modulo importante, pero debe
activarse solo cuando el proyecto obtenga datos utilizables con permiso.

## Con Quien Competimos

| Proyecto / producto | Que ya resuelve | Impacto para TargetAudit |
|---|---|---|
| `OpenBB` | Plataforma financiera abierta para analistas, quants y agentes; su repositorio oficial mostraba aproximadamente `68.1k` estrellas al revisar el `2026-05-25`. Ofrece Workspace gratuito para individuos y una capa Pro/enterprise por cotizacion. | No es realista competir como plataforma general de datos. Conviene diferenciarse por auditoria de evidencia, reglas de publicacion y monitores verificables. |
| `Stocknear` | Plataforma open source visual con acciones, ETFs, IPOs y datos de Wall Street; su repositorio `frontend` mostraba `29` estrellas, mientras la pagina comercial declara `10,000+` inversores. Ofrece plan gratuito, `Plus` anunciado a `USD 10/month` y `Pro` a `USD 30/month`, con descuentos anuales visibles al revisar. | Es el competidor de interfaz y producto mas cercano, y muestra que usuarios de producto y estrellas de GitHub no son la misma metrica. TargetAudit necesita una identidad metodologica fuerte, no solo UI bonita. |
| `AnaChart` | Producto centrado directamente en precision de analistas: declara `964K` targets/ratings, `5,617` acciones y `4,074` analistas; cobra `USD 45/month` o `USD 399/year` por acceso avanzado. | Confirma que la idea original tiene demanda, pero tambien que el dataset historico es la barrera competitiva central. |
| `sec-edgar` y herramientas EDGAR abiertas | Descarga y procesamiento de filings SEC; `sec-edgar` mostraba aproximadamente `1.4k` estrellas al revisar el `2026-05-25`. | Son complementarios o competencia parcial del colector, no del producto completo. TargetAudit debe ofrecer flujo de decision y dashboard, no solo descarga. |

## Lo Que Puede Gustar En GitHub

El publico de GitHub puede encontrar valor si el lanzamiento ensena algo
instalable y verificable desde el primer minuto:

1. una demo visual premium que corre sin suscripciones;
2. monitores regulatorios y de listings con fuente primaria y reglas claras;
3. una metodologia que no oculta exclusiones ni llama "operacion" a una
   diferencia de holdings;
4. conectores internacionales que permiten contribuciones concretas;
5. documentacion transparente sobre que datos faltan y por que no se publican.
6. un `Evidence Passport Commons` ampliable sin pedir al contributor que
   compre datos o escriba un conector antes de validar derechos.

Lo que probablemente no atraera por si solo es una gran promesa futura de
ranking de analistas sin un dataset real ya autorizado.

## Modelo Gratuito Y Opciones De Ingreso

Lanzar el codigo gratis no impide obtener ingresos despues. Tampoco los
garantiza. La via mas razonable es mantener la `Open Edition` genuinamente
gratis y cobrar solo por comodidad, operacion o datos que el usuario decida
licenciar.

| Camino | Puede convivir con Open Edition | Condicion previa |
|---|---|---|
| GitHub Sponsors | Si; apoyo voluntario al proyecto | Usuarios reales, actividad y confianza; no debe asumirse como ingreso estable inicial. |
| Hosted alerts / cloud monitor | Si; el repositorio sigue siendo autocontenible | Demanda por alertas continuas, costos de hosting medidos y limites legales de cada fuente. |
| Equipo privado / compliance workspace | Si; empresas pagan por control de acceso, historial y soporte | Seguridad, autenticacion, retencion y acuerdos de servicio. |
| Bring-your-own-license analytics | Si; usuario aporta sus derechos y datos | Flujo robusto para importacion privada y prohibicion de republicar outputs no autorizados. |
| Conectores o reportes patrocinados | Si, con transparencia | Patrocinio declarado y reglas que no alteren resultados. |

No debe monetizarse mediante recomendaciones de compra/venta, venta de una
aparente "senal ganadora" ni rankings publicos armados con datos sin derechos.

## Plan De Validacion Antes De Cobrar

1. Lanzar Open Edition con capturas, demo reproducible y documentacion clara.
2. Medir interes real: estrellas, instalaciones, issues utiles, conectores
   propuestos y personas que pidan alertas alojadas.
3. Intentar permiso escrito para el primer dataset de targets historicos.
4. Publicar conectores oficiales adicionales aportados por la comunidad.
5. Solo despues evaluar un servicio alojado o una capa privada de datos
   autorizados.

## Decision Recomendada

Si: conviene lanzar gratis cuando la experiencia visual sea consistente en los
modulos principales y la instalacion limpia este probada.

No: no conviene venderlo inicialmente como sustituto de OpenBB, Stocknear o
AnaChart. El mensaje correcto es que TargetAudit convierte evidencia publica
dispersa en investigacion rastreable, internacional y legalmente consciente.

## Fuentes Consultadas

- OpenBB, repositorio y licencia: <https://github.com/OpenBB-finance/OpenBB>
- OpenBB, precios de Workspace: <https://openbb.co/pricing>
- Stocknear, frontend open source: <https://github.com/stocknear/frontend>
- Stocknear, planes del producto: <https://www.stocknear.com/pricing>
- AnaChart, producto y cobertura: <https://anachart.com/>
- AnaChart, planes: <https://anachart.com/register/>
- `sec-edgar`, repositorio: <https://github.com/sec-edgar/sec-edgar>
- SEC EDGAR, acceso publico oficial: <https://www.sec.gov/search-filings>
- GitHub Sponsors, documentacion: <https://docs.github.com/en/sponsors/receiving-sponsorships-through-github-sponsors/about-github-sponsors-for-open-source-contributors>
