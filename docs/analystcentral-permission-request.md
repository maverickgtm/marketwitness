# Solicitud De Permiso: AnalystCentral

## Proposito

`AnalystCentral` es el unico candidato gratuito localizado en el barrido final
que anuncia historial de ratings y price targets estadounidenses con la
profundidad aproximada que necesita TargetAudit. Sus terminos actuales no
permiten integrarlo ni producir rankings publicos sin consentimiento escrito.

Este borrador permite solicitar una autorizacion limitada, transparente y sin
presuponer que sera concedida.

## Mensaje Sugerido

Subject: Permission request for attributed, derived research using AnalystCentral data

Hello AnalystCentral team,

I am building TargetAudit, an open-source research project that tests whether
historical analyst price targets were reached under a documented one-year
methodology. The public project is intentionally designed not to scrape or
republish third-party data without permission.

Your site describes a free historical analyst ratings and price-target dataset
covering Wall Street securities. I read your Terms of Service and understand
that personal access does not authorize data mining, republication or derived
public outputs without your prior written consent.

Would you consider granting a limited permission for TargetAudit to:

1. receive or download an agreed historical sample containing dated analyst
   ratings and price targets;
2. process the sample locally using an open, documented evaluation method;
3. publish attributed aggregate results only, such as sample size, hit rate,
   confidence interval and methodology notes, without redistributing your raw
   dataset; and
4. include an attribution and link to AnalystCentral in every public result?

If GitHub Actions processing or a small illustrative fixture is not acceptable,
we can keep the raw-data workflow private and publish only code plus synthetic
demonstration data. We would enable any real-data output only after receiving
written terms that state what collection, retention and derived display are
permitted.

Please let us know whether this use is possible, any attribution requirements,
coverage limits, prohibited outputs or commercial terms that would apply.

Thank you,

Mario Antillon
TargetAudit project
[correo monitoreado del proyecto, completar solo al enviar]

La copia versionada del borrador omite deliberadamente el correo real. Agrega
el contacto fuera del repositorio al momento de enviar la solicitud.

## Evidencia A Conservar Si Responden

- Correo completo o documento de permiso con fecha y remitente identificable.
- Campos, periodo y simbolos autorizados.
- Si se permite almacenamiento local y por cuanto tiempo.
- Si se permiten outputs agregados publicos y atribucion exigida.
- Si se permite ejecutar procesamiento automatizado.
- Si se permite compartir una muestra o solamente resultados derivados.

## Regla De Activacion

No se incorporara una fila real de AnalystCentral al dashboard publico hasta
que la autorizacion escrita sea revisada y registrada en la cola de
aprobaciones de proveedores de TargetAudit.
