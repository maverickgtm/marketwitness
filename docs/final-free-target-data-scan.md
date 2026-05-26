# Final No-Cost Scan For Historical Target Data

Review date: `2026-05-25`.

## Objective And Result

Before public launch, MarketWitness performed a final international search for a
no-cost source of historical price targets, individualized by analyst or firm,
with rights sufficient to publish derived rankings.

The search covered United States providers and local paths in Japan, South
Korea, Hong Kong, Singapore, Brazil, India, the United Kingdom, and Germany.
GitHub repositories were treated as technical clues only: code that queries a
third-party site does not grant rights to the underlying data.

No free dataset was found that can lawfully be activated to publish real
rankings for Roth MKM, KBW, UBS, Citi, Barclays, or other firms.

## Candidates Reviewed

| Source | Relevant Coverage | Visible Cost | MarketWitness Decision |
|---|---|---:|---|
| AnalystCentral | Advertised CSV of Wall Street ratings and targets, 10 years, 8,500+ stocks and indices | Free for members | `permission_candidate`: request written permission; do not download or publish under current terms |
| Intrinio / Zacks Target Prices | U.S. target consensus, 20+ years, API/CSV/S3/Snowflake | Quote; history involves payment | Licensed extension, not Open Edition; individual-firm rows not confirmed |
| QUICK Data Factory | Japanese company ratings and targets with history since January 2003 | Monthly contract | Strong licensed Japanese candidate, not free |
| FnGuide / FnSpace | Korean research and consensus series | Paid published plans | Not free; license limits third-party exposure |
| Webull OpenAPI | High, low, average, and median U.S. stock targets | Requires `x-app-key`; cost/rights unconfirmed | Current consensus only; no demonstrated individual history or public-output rights |
| SGinvestors | Visible SGX target changes or consensus | Public page | Manual reference; no API or republication license found |
| FMP | Structured consensus and historical ratings | Free testing; display/redistribution by agreement | Contractual extension, not free public data |
| GitHub wrappers for TipRanks/Yahoo | Technical access to pages/endpoints | Free code | Excluded; code transfers no data rights |

## Permission Path

The only still-plausible no-cost route for the initial ranking is narrowly
scoped written authorization from `AnalystCentral`. It would need to permit
receipt of dated target rows, local reproducible processing, attributed
aggregate public output, any shareable illustrative fixture, and either
GitHub Actions execution or a private-only real-data workflow.

Until such authorization exists, MarketWitness keeps the importer and release
gate ready but does not activate the source.

## Launch Consequence

The Open Edition remains useful: its evaluation engine and audits run, the
dashboard exposes what is missing for real data, IPO and global regulatory
monitors use public evidence, and the multilingual contributor gateway helps
discover lawful official connectors.

The public promise remains: **MarketWitness audits evidence and exposes when a
conclusion cannot yet be published.**

## Sources Reviewed

- AnalystCentral offering: <https://analystcentral.com/about-us/>
- AnalystCentral terms: <https://analystcentral.com/terms-of-service>
- Intrinio Target Prices: <https://intrinio.com/products/target-prices>
- QUICK Data Factory: <https://corporate.quick.co.jp/data-factory/product/data054/>
- QUICK APIs: <https://corporate.quick.co.jp/en/apis/>
- FnGuide plans: <https://www.fnguide.com/Payment/Purchase>
- Webull Analyst Target Price API: <https://developer.webull.com/apis/docs/reference/get-analyst-target-price>
- Financial Modeling Prep targets: <https://site.financialmodelingprep.com/datasets/analyst-estimates-targets>
- SGinvestors targets: <https://sginvestors.io/analysts/target-price/latest>
