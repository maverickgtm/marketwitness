# Hosted Open Edition Demo

The public MarketWitness demo runs the read-only FastAPI application behind an
HTTPS reverse proxy:

- Public URL: <https://marketwitness-43-157-95-145.nip.io/>
- Application process: `uvicorn` bound to `127.0.0.1:8765`
- Public proxy and TLS: Caddy on ports `80` and `443`
- Demonstration data: generated Open Edition artifacts and the DuckDB demo
  warehouse built from redistributable fixtures

The `nip.io` hostname is a no-cost DNS route that resolves the embedded public
IP address. It is appropriate for an initial public demo; a branded domain can
replace it later without changing the application architecture.

## Published Scope

The hosted demo is an exploration surface for the Open Edition. It shows the
dashboard, read-only API, evidence passports, controlled research workflows
and explicit source-rights boundaries. It does not publish real analyst
rankings, trading recommendations or licensed historical volatility results.

GitHub Actions continue to produce permitted public-source monitor artifacts.
Loading continuously refreshed monitor output into the hosted application is a
separate operational step and must preserve the same provenance and rights
controls.

## VPS Layout

The initial deployment uses:

```text
/home/ubuntu/marketwitness/                   application checkout and venv
/etc/systemd/system/marketwitness-demo.service read-only app service
/etc/caddy/Caddyfile                          HTTPS reverse proxy
```

The tracked reference files are:

- [`deploy/marketwitness-demo.service`](../deploy/marketwitness-demo.service)
- [`deploy/Caddyfile.marketwitness-demo`](../deploy/Caddyfile.marketwitness-demo)

No secret or request-identification email is stored in either deployment file.
Any future live collection on the VPS must place secrets outside the repository
and should not enable a source until its passport permits public output.
