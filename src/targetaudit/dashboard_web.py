from __future__ import annotations


def open_edition_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TargetAudit | Open Edition</title>
  <style>
    :root {
      --bg:#071016; --panel:#0f1c24; --panel2:#14242d; --line:#20343d;
      --text:#edf1ef; --muted:#98abb0; --mint:#56daac; --gold:#f0bc62;
      --blue:#62a6ff; --red:#ff7d72;
    }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--bg); color:var(--text); font:15px/1.5 Inter,Arial,sans-serif; }
    header, main { max-width:1240px; margin:auto; padding:30px 28px; }
    nav,.meta { color:var(--muted); text-transform:uppercase; letter-spacing:.08em; font-size:13px; }
    a { color:var(--mint); text-decoration:none; }
    h1 { font-size:clamp(40px,5vw,62px); line-height:1.04; margin:38px 0 14px; }
    h2 { margin:44px 0 16px; font-size:22px; }
    h3 { margin:13px 0 8px; }
    .lead { color:var(--muted); font-size:18px; max-width:930px; }
    .notice { background:var(--panel); border:1px solid var(--line); border-left:3px solid var(--mint);
      border-radius:14px; padding:15px 18px; color:var(--muted); margin:18px 0; }
    .cards { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin:34px 0; }
    .card,.feature,.mode { background:var(--panel); border:1px solid var(--line); border-radius:14px; }
    .card { padding:17px 20px; }
    .card p { color:var(--muted); margin:0; }
    .card strong { display:block; font-size:37px; color:var(--mint); margin-top:4px; }
    .features { display:grid; grid-template-columns:repeat(2,1fr); gap:16px; }
    .feature { padding:18px; }
    .feature strong { color:var(--mint); display:block; margin:8px 0; }
    .feature p,.feature small,.mode small { color:var(--muted); display:block; }
    .pill { display:inline-block; border-radius:999px; padding:4px 9px; font-size:12px; white-space:nowrap; }
    .bundled_offline_demo { color:var(--blue); background:rgba(98,166,255,.12); }
    .public_source_no_key { color:var(--mint); background:rgba(86,218,172,.12); }
    .attributed_external_widget { color:var(--mint); background:rgba(86,218,172,.12); }
    .bring_authorized_data { color:var(--gold); background:rgba(240,188,98,.12); }
    .modes { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }
    .mode { padding:18px; }
    .mode p { color:var(--mint); }
    #error { display:none; border-left-color:var(--red); color:var(--red); }
    @media(max-width:920px) { .cards,.features,.modes { grid-template-columns:1fr; } }
  </style>
</head>
<body>
  <header>
    <nav>TargetAudit / Open Edition / <a href="/dashboard/reports">Report Center</a> / <a href="/dashboard/market-context">Market Context</a> / <a href="/dashboard/policy">Public Use Policy</a> / <a href="/dashboard/extensions">Licensed Extensions</a> / <a href="/dashboard/financials">Financials Sandbox</a> / <a href="/dashboard/release">Release Center</a> / <a href="/dashboard/governance">Governance</a></nav>
    <h1>Market research.<br>No paid data required.</h1>
    <p class="lead" id="promise">Loading the zero-cost product profile...</p>
    <p class="meta" id="reviewed">Loading source controls...</p>
    <section class="cards">
      <article class="card"><p>No-cost capabilities</p><strong id="free">-</strong></article>
      <article class="card"><p>Offline demo</p><strong id="offline">-</strong></article>
      <article class="card"><p>Public-data monitors</p><strong id="public">-</strong></article>
      <article class="card"><p>Optional extensions</p><strong id="optional">-</strong></article>
    </section>
  </header>
  <main>
    <p class="notice">This GitHub edition runs without commercial subscriptions. Real analyst ranking inputs are optional and must arrive with usage rights.</p>
    <p id="error" class="notice"></p>
    <h2>Included Capabilities</h2>
    <section class="features" id="capabilities"></section>
    <h2>Run Modes</h2>
    <section class="modes" id="modes"></section>
  </main>
  <script>
    const $ = (id) => document.getElementById(id);
    function text(value) {
      return String(value == null || value === "" ? "-" : value)
        .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
    }
    async function initialize() {
      try {
        const response = await fetch("/api/v1/open-edition");
        if (!response.ok) throw new Error((await response.json()).detail || "Request failed");
        const data = await response.json();
        $("promise").textContent = data.promise;
        $("reviewed").textContent = `${data.edition} / Reviewed as of ${data.as_of}`;
        $("free").textContent = data.zero_cost_available_count;
        $("offline").textContent = data.offline_ready_count;
        $("public").textContent = data.public_data_ready_count;
        $("optional").textContent = data.optional_extension_count;
        $("capabilities").innerHTML = data.capabilities.map((item) => {
          const route = item.route ? `<a href="${text(item.route)}">Open ${text(item.title)}</a>` : "";
          return `<article class="feature"><span class="pill ${text(item.status)}">${text(item.status)}</span><h3>${text(item.title)}</h3><strong>${text(item.cost)}</strong><p>${text(item.output)}</p><small>${text(item.limitation)}</small>${route}</article>`;
        }).join("");
        $("modes").innerHTML = data.setup_modes.map((mode) => `<article class="mode"><h3>${text(mode.title)}</h3><p>${text(mode.requirement)}</p><small>${text(mode.result)}</small></article>`).join("");
      } catch (error) {
        $("error").style.display = "block";
        $("error").textContent = error.message;
      }
    }
    initialize();
  </script>
</body>
</html>"""


def report_center_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TargetAudit | Report Center</title>
  <style>
    :root {
      --bg:#071016; --panel:#0f1c24; --line:#20343d; --text:#edf1ef;
      --muted:#98abb0; --mint:#56daac; --gold:#f0bc62; --blue:#62a6ff;
    }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--bg); color:var(--text); font:15px/1.5 Inter,Arial,sans-serif; }
    header,main { max-width:1240px; margin:auto; padding:30px 28px; }
    nav,.meta { color:var(--muted); text-transform:uppercase; letter-spacing:.08em; font-size:13px; }
    a { color:var(--mint); text-decoration:none; }
    h1 { font-size:clamp(40px,5vw,62px); line-height:1.04; margin:38px 0 14px; }
    h2 { margin:42px 0 16px; font-size:22px; }
    h3 { margin:12px 0 8px; }
    .lead { color:var(--muted); font-size:18px; max-width:920px; }
    .cards { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin:34px 0; }
    .card,.report,.control,.notice { background:var(--panel); border:1px solid var(--line); border-radius:14px; }
    .card { padding:18px 20px; }
    .card p { color:var(--muted); margin:0; }
    .card strong { color:var(--mint); display:block; font-size:20px; margin-top:5px; }
    .notice { border-left:3px solid var(--gold); padding:15px 18px; color:var(--muted); margin:18px 0; }
    .reports { display:grid; grid-template-columns:repeat(2,1fr); gap:16px; }
    .report,.control { padding:18px; }
    .report p,.report small,.control p { color:var(--muted); display:block; }
    .pill { display:inline-block; border-radius:999px; padding:4px 9px; font-size:12px; }
    .fixture { color:var(--blue); background:rgba(98,166,255,.12); }
    .regulatory { color:var(--mint); background:rgba(86,218,172,.12); }
    .controls { display:grid; grid-template-columns:repeat(auto-fit,minmax(205px,1fr)); gap:16px; }
    @media(max-width:900px) { .cards,.reports,.controls { grid-template-columns:1fr; } }
  </style>
</head>
<body>
  <header>
    <nav><a href="/dashboard/open">Open Edition</a> / Report Center / <a href="/dashboard/policy">Public Use Policy</a> / <a href="/dashboard/financials">Financials Sandbox</a></nav>
    <h1>Reproducible reports.<br>Known routes only.</h1>
    <p class="lead">A reading room for the report pages included in the tested Open Edition bundle. It exposes approved dashboard routes, never arbitrary files from the generated-report directory.</p>
    <p class="meta">Open Edition bundle / Weekly GitHub Actions build / 30-day artifact retention</p>
    <section class="cards">
      <article class="card"><p>Generated report routes</p><strong>27 allowlisted pages</strong></article>
      <article class="card"><p>Bundle schedule</p><strong>Weekly + manual</strong></article>
      <article class="card"><p>Required paid data</p><strong>None</strong></article>
    </section>
  </header>
  <main>
    <p class="notice"><strong>Scope:</strong> the weekly GitHub artifact is generated from redistributable fixtures. These pages demonstrate monitoring and audit workflows; they are not live market alerts, analyst rankings or investment recommendations.</p>
    <h2>Generated Reports</h2>
    <section class="reports">
      <article class="report"><span class="pill fixture">fixture workflow</span><h3>IPO Watch</h3><p>Reviewed IPO-watch example with SEC-shaped discovery and documented decisions.</p><small>Demonstration evidence, not a live SEC scan.</small><a href="/dashboard/ipo-watch">Open report</a></article>
      <article class="report"><span class="pill regulatory">SEC daily intake</span><h3>SEC IPO Discovery Queue</h3><p>Potential registration, prospectus and withdrawal forms found before triage.</p><small>Discovery is universal intake, not a confirmed IPO calendar.</small><a href="/dashboard/sec-discovery">Open report</a></article>
      <article class="report"><span class="pill regulatory">SEC discovery</span><h3>SEC IPO Alerts</h3><p>Public-filing review queue with watchlist matching and visible filing signals.</p><small>New evidence requires review before changing a company state.</small><a href="/dashboard/sec-alerts">Open report</a></article>
      <article class="report"><span class="pill regulatory">manual decision log</span><h3>IPO Review Outcomes</h3><p>Documented review decisions used to generate the current IPO Watch registry.</p><small>A retained audit trail for promotion, rejection or pending review.</small><a href="/dashboard/ipo-reviews">Open report</a></article>
      <article class="report"><span class="pill fixture">synthetic ETF snapshot</span><h3>ARKK Holdings Sandbox</h3><p>Daily-shaped observed differences from normalized ARK-format snapshots.</p><small>Synthetic snapshots only; not ARK trades or redistributed holdings.</small><a href="/dashboard/etf/arkk-demo">Open report</a></article>
      <article class="report"><span class="pill fixture">synthetic ETF snapshot</span><h3>XLF Holdings Sandbox</h3><p>Daily-shaped observed holding differences for the financial-sector benchmark.</p><small>Synthetic snapshots only; not confirmed manager trades.</small><a href="/dashboard/etf/xlf-demo">Open report</a></article>
      <article class="report"><span class="pill fixture">synthetic ETF snapshot</span><h3>IYF Holdings Sandbox</h3><p>A second financial ETF comparison to test multi-fund activity reporting.</p><small>Synthetic snapshots only; no automated iShares collection.</small><a href="/dashboard/etf/iyf-demo">Open report</a></article>
      <article class="report"><span class="pill regulatory">regulatory periodic</span><h3>N-PORT Recent Filing</h3><p>A recent-period comparison from the SEC regulatory evidence workflow.</p><small>Periodic filing evidence, not daily portfolio activity.</small><a href="/dashboard/etf/nport-recent">Open report</a></article>
      <article class="report"><span class="pill regulatory">regulatory periodic</span><h3>ETF Regulatory Holdings</h3><p>N-PORT period comparison for the regulatory ETF evidence layer.</p><small>Periodic filing evidence, not real-time ETF trading.</small><a href="/dashboard/etf-regulatory">Open report</a></article>
      <article class="report"><span class="pill regulatory">SEC quarterly catalog</span><h3>N-PORT Dataset Catalog</h3><p>Published SEC ZIP releases available for controlled historical holdings backfill.</p><small>Official regulatory periods, never daily manager activity.</small><a href="/dashboard/etf/nport-catalog">Open report</a></article>
      <article class="report"><span class="pill regulatory">incremental control</span><h3>N-PORT Sync Status</h3><p>Local-baseline workflow that tracks and downloads only newly observed SEC quarters.</p><small>Download state is operational evidence, not a position signal.</small><a href="/dashboard/etf/nport-sync">Open report</a></article>
      <article class="report"><span class="pill regulatory">document check</span><h3>Public Document Checks</h3><p>Documentary corroboration example for monitored listing candidates.</p><small>A document match does not confirm admission or trading.</small><a href="/dashboard/document-checks">Open report</a></article>
      <article class="report"><span class="pill fixture">synthetic sandbox</span><h3>RWA Watch Sandbox</h3><p>Auditable tokenized-asset observation format using synthetic rows only.</p><small>No live xStocks, venue or issuer feed is collected.</small><a href="/dashboard/rwa-watch">Open report</a></article>
      <article class="report"><span class="pill regulatory">international coverage</span><h3>Global Listings Watch</h3><p>Official signal map and navigation for international listing and filing monitors.</p><small>Jurisdictions retain separate confirmation rules and blocked paths.</small><a href="/dashboard/global-listings">Open report</a></article>
      <article class="report"><span class="pill regulatory">global review queue</span><h3>Global Listings Alerts</h3><p>Differences across listing and regulatory-document monitors in ten international markets.</p><small>Filings open review; exchange evidence is required to confirm listing milestones.</small><a href="/dashboard/global-alerts">Open report</a></article>
      <article class="report"><span class="pill regulatory">primary evidence</span><h3>Issuer Confirmations</h3><p>Official issuer-release milestones reviewed separately from listing-candidate feeds.</p><small>Verified events remain research evidence, not trading instructions.</small><a href="/dashboard/issuer-confirmations">Open report</a></article>
    </section>
    <h2>Financials Audit Evidence</h2>
    <section class="reports">
      <article class="report"><span class="pill fixture">controlled input</span><h3>Target Import Audit</h3><p>Authorized-export ingestion demo with accepted and rejected rows kept visible.</p><small>Internal-only fixture evidence; not a public analyst dataset.</small><a href="/dashboard/audit/target-import">Open report</a></article>
      <article class="report"><span class="pill fixture">price provenance</span><h3>Adjusted Price Evidence</h3><p>Normalized adjusted-price fixture prepared for evaluation with provenance shown.</p><small>Demonstrates the adapter; does not license public scorecard data.</small><a href="/dashboard/audit/adjusted-prices">Open report</a></article>
      <article class="report"><span class="pill regulatory">scoring guard</span><h3>Corporate Actions Audit</h3><p>Splits and ticker-transition evidence checked before comparable scoring.</p><small>Affected observations are guarded rather than silently counted.</small><a href="/dashboard/audit/corporate-actions">Open report</a></article>
      <article class="report"><span class="pill regulatory">quality gate</span><h3>Operations Quality Snapshot</h3><p>Generated check of required inputs, lineage and exclusion review status.</p><small>Passing quality alone never grants data-publication rights.</small><a href="/dashboard/audit/operations-quality">Open report</a></article>
      <article class="report"><span class="pill regulatory">release gate</span><h3>Release Decision Snapshot</h3><p>Generated decision combining source rights, lineage and run quality.</p><small>The included demo remains blocked from public real-data claims.</small><a href="/dashboard/audit/release-decision">Open report</a></article>
    </section>
    <h2>Governance Snapshots</h2>
    <section class="reports">
      <article class="report"><span class="pill fixture">edition manifest</span><h3>Open Edition Snapshot</h3><p>Generated statement of zero-cost capabilities and boundaries for this bundle.</p><small>A dated artifact, separated from the application home page.</small><a href="/dashboard/governance-report/open-edition">Open report</a></article>
      <article class="report"><span class="pill regulatory">optional licenses</span><h3>Licensed Extensions Snapshot</h3><p>Generated catalog of optional paid routes, listed prices and public-output restrictions.</p><small>A priced option is not permission to publish a shared ranking.</small><a href="/dashboard/governance-report/licensed-extensions">Open report</a></article>
      <article class="report"><span class="pill regulatory">source controls</span><h3>Source Registry Snapshot</h3><p>Generated provider registry after documented demonstration decisions are applied.</p><small>Shows permissions and blocked sources as built.</small><a href="/dashboard/governance-report/source-registry">Open report</a></article>
      <article class="report"><span class="pill regulatory">permission queue</span><h3>Provider Approvals Snapshot</h3><p>Generated queue of source permissions still needed for a real scorecard.</p><small>An open item is not authorization.</small><a href="/dashboard/governance-report/provider-approvals">Open report</a></article>
      <article class="report"><span class="pill regulatory">decision audit</span><h3>Approval Review Outcomes</h3><p>Generated outcome log for reviewed provider-permission decisions.</p><small>Preserves the audit trail without modifying base governance silently.</small><a href="/dashboard/governance-report/approval-review">Open report</a></article>
      <article class="report"><span class="pill regulatory">readiness gate</span><h3>Scorecard Readiness Snapshot</h3><p>Generated view of requirements still blocking a public real-data scorecard.</p><small>Fixtures validate workflow; they do not unlock publication.</small><a href="/dashboard/governance-report/scorecard-readiness">Open report</a></article>
    </section>
    <h2>Operational Controls</h2>
    <section class="controls">
      <article class="control"><h3>IPO Watch Center</h3><p>Follow discovery, reviewed status and international listing evidence without blending milestones.</p><a href="/dashboard/ipo">Open IPO workflow</a></article>
      <article class="control"><h3>ETF Evidence Center</h3><p>Separate synthetic comparisons from periodic SEC N-PORT evidence before reading changes.</p><a href="/dashboard/etf">Open ETF evidence</a></article>
      <article class="control"><h3>Financials Evidence Center</h3><p>Trace controlled inputs, scoring guards and release blockers before opening a ranking.</p><a href="/dashboard/financials-evidence">Open financials evidence</a></article>
      <article class="control"><h3>Global Contributors</h3><p>Propose official market connectors or lawful target-data access in five languages.</p><a href="/dashboard/contribute?lang=en">Open contributor gateway</a></article>
      <article class="control"><h3>Public Use Policy</h3><p>See data boundaries, blocked sources and no-recommendation rules.</p><a href="/dashboard/policy">Open policy</a></article>
      <article class="control"><h3>Source Governance</h3><p>Inspect provider states, rights review and excluded observations.</p><a href="/dashboard/governance">Open governance</a></article>
      <article class="control"><h3>Release Center</h3><p>Review why demo evidence cannot become a public real-data scorecard.</p><a href="/dashboard/release">Open release controls</a></article>
    </section>
  </main>
</body>
</html>"""


def financials_evidence_center_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TargetAudit | Financials Evidence Center</title>
  <style>
    :root {
      --bg:#071016; --panel:#0f1c24; --line:#20343d; --text:#edf1ef;
      --muted:#98abb0; --mint:#56daac; --gold:#f0bc62; --blue:#62a6ff;
    }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--bg); color:var(--text); font:15px/1.5 Inter,Arial,sans-serif; }
    header,main { max-width:1220px; margin:auto; padding:30px 28px; }
    nav,.meta { color:var(--muted); text-transform:uppercase; letter-spacing:.08em; font-size:13px; }
    a { color:var(--mint); text-decoration:none; }
    h1 { font-size:clamp(40px,5vw,62px); line-height:1.04; margin:38px 0 14px; }
    h2 { margin:42px 0 16px; font-size:22px; }
    h3 { margin:10px 0 8px; }
    .lead { color:var(--muted); font-size:18px; max-width:920px; }
    .cards { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin:34px 0; }
    .card,.view,.notice { background:var(--panel); border:1px solid var(--line); border-radius:14px; }
    .card { padding:18px 20px; }
    .card p,.view p,.view small { color:var(--muted); margin:0; display:block; }
    .card strong { color:var(--mint); display:block; font-size:27px; margin-top:5px; }
    .blocked { color:var(--gold)!important; }
    .notice { border-left:3px solid var(--gold); padding:15px 18px; color:var(--muted); }
    .views { display:grid; grid-template-columns:repeat(2,1fr); gap:16px; }
    .view { padding:18px; }
    .pill { display:inline-block; border-radius:999px; padding:4px 9px; font-size:12px; }
    .fixture { color:var(--blue); background:rgba(98,166,255,.12); }
    .gate { color:var(--mint); background:rgba(86,218,172,.12); }
    @media(max-width:900px) { .cards,.views { grid-template-columns:1fr; } }
  </style>
</head>
<body>
  <header>
    <nav><a href="/dashboard/open">Open Edition</a> / <a href="/dashboard/reports">Report Center</a> / Financials Evidence Center</nav>
    <h1>Financials evidence.<br>Audit before ranking.</h1>
    <p class="lead">Trace the U.S. Financials sandbox from controlled target input through publication decision, without presenting fixture outcomes as actual analyst performance.</p>
    <section class="cards">
      <article class="card"><p>Generated audit reports</p><strong>5</strong></article>
      <article class="card"><p>Interactive controls</p><strong>6</strong></article>
      <article class="card"><p>Public real-data scorecard</p><strong class="blocked">Blocked</strong></article>
      <article class="card"><p>Required paid data for demo</p><strong>None</strong></article>
    </section>
  </header>
  <main>
    <p class="notice"><strong>Publication boundary:</strong> this demonstration does not publish real analyst track records or a ranking of Roth MKM, UBS, Barclays, Citi or other firms. Authorized target publication rights and approved production-source lineage are still required.</p>
    <h2>Generated Audit Trail</h2>
    <section class="views">
      <article class="view"><span class="pill fixture">1 / controlled input</span><h3>Target Import Audit</h3><p>Review accepted and rejected rows from an authorized-export fixture.</p><small>Internal demonstration evidence.</small><a href="/dashboard/audit/target-import">Open report</a></article>
      <article class="view"><span class="pill fixture">2 / provenance</span><h3>Adjusted Price Evidence</h3><p>Inspect normalized price bounds and the disclosed data-source limitation.</p><small>No public output license is implied.</small><a href="/dashboard/audit/adjusted-prices">Open report</a></article>
      <article class="view"><span class="pill gate">3 / scoring guard</span><h3>Corporate Actions Audit</h3><p>Exclude targets crossed by unresolved splits or ticker transitions.</p><small>Guarded scoring before ranking.</small><a href="/dashboard/audit/corporate-actions">Open report</a></article>
      <article class="view"><span class="pill gate">4 / quality gate</span><h3>Operations Quality Snapshot</h3><p>Verify inputs, lineage, reproducibility and exclusion-review state.</p><small>A pass does not grant publishing rights.</small><a href="/dashboard/audit/operations-quality">Open report</a></article>
      <article class="view"><span class="pill gate">5 / release gate</span><h3>Release Decision Snapshot</h3><p>Combine rights, lineage and quality into a visible release decision.</p><small>The bundled demo remains blocked for real-data claims.</small><a href="/dashboard/audit/release-decision">Open report</a></article>
    </section>
    <h2>Interactive Controls</h2>
    <section class="views">
      <article class="view"><h3>Financials Sandbox</h3><p>Explore scored fixture runs and auditable exclusions.</p><a href="/dashboard/financials">Open scorecard</a></article>
      <article class="view"><h3>Scorecard Readiness</h3><p>Inspect the source requirements for any future public ranking.</p><a href="/dashboard/readiness">Open readiness</a></article>
      <article class="view"><h3>Release Center</h3><p>Evaluate a candidate run against publication controls.</p><a href="/dashboard/release">Open release controls</a></article>
      <article class="view"><h3>Source Governance</h3><p>Read registered source policies and linked evidence status.</p><a href="/dashboard/governance">Open governance</a></article>
      <article class="view"><h3>Provider Approvals</h3><p>Track permissions that cannot be inferred from technical access.</p><a href="/dashboard/approvals">Open approvals</a></article>
      <article class="view"><h3>Operations Quality</h3><p>Review current stored-run checks interactively.</p><a href="/dashboard/operations">Open quality controls</a></article>
    </section>
  </main>
</body>
</html>"""


def ipo_watch_center_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TargetAudit | IPO Watch Center</title>
  <style>
    :root {
      --bg:#071016; --panel:#0f1c24; --line:#20343d; --text:#edf1ef;
      --muted:#98abb0; --mint:#56daac; --gold:#f0bc62; --blue:#62a6ff;
    }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--bg); color:var(--text); font:15px/1.5 Inter,Arial,sans-serif; }
    header,main { max-width:1220px; margin:auto; padding:30px 28px; }
    nav,.meta { color:var(--muted); text-transform:uppercase; letter-spacing:.08em; font-size:13px; }
    a { color:var(--mint); text-decoration:none; }
    h1 { font-size:clamp(40px,5vw,62px); line-height:1.04; margin:38px 0 14px; }
    h2 { margin:42px 0 16px; font-size:22px; }
    h3 { margin:10px 0 8px; }
    .lead { color:var(--muted); font-size:18px; max-width:920px; }
    .cards { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin:34px 0; }
    .card,.stage,.notice { background:var(--panel); border:1px solid var(--line); border-radius:14px; }
    .card { padding:18px 20px; }
    .card p,.stage p,.stage small { color:var(--muted); margin:0; display:block; }
    .card strong { color:var(--mint); display:block; font-size:27px; margin-top:5px; }
    .notice { border-left:3px solid var(--gold); padding:15px 18px; color:var(--muted); }
    .workflow { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; }
    .coverage { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }
    .stage { padding:18px; }
    .pill { display:inline-block; border-radius:999px; padding:4px 9px; font-size:12px; }
    .intake { color:var(--blue); background:rgba(98,166,255,.12); }
    .review { color:var(--gold); background:rgba(240,188,98,.12); }
    .verified { color:var(--mint); background:rgba(86,218,172,.12); }
    @media(max-width:950px) { .cards,.workflow,.coverage { grid-template-columns:1fr; } }
  </style>
</head>
<body>
  <header>
    <nav><a href="/dashboard/open">Open Edition</a> / <a href="/dashboard/reports">Report Center</a> / IPO Watch Center</nav>
    <h1>IPO evidence.<br>Confirm before status.</h1>
    <p class="lead">Navigate potential offerings, reviewed filing evidence and confirmed listing milestones without turning rumors or documents into trading instructions.</p>
    <section class="cards">
      <article class="card"><p>U.S. workflow stages</p><strong>4</strong></article>
      <article class="card"><p>International markets mapped</p><strong>10</strong></article>
      <article class="card"><p>Official global feeds active</p><strong>9</strong></article>
      <article class="card"><p>Required paid data</p><strong>None</strong></article>
    </section>
  </header>
  <main>
    <p class="notice"><strong>Evidence rule:</strong> a discovered filing begins review; it does not confirm an IPO, listing, first trade or position to take. Verified issuer and exchange evidence remains separate from candidate monitoring.</p>
    <h2>U.S. SEC Review Workflow</h2>
    <section class="workflow">
      <article class="stage"><span class="pill intake">1 / intake</span><h3>SEC Discovery Queue</h3><p>Potential registration, prospectus and withdrawal forms from a daily index.</p><small>Not a confirmed IPO calendar.</small><a href="/dashboard/sec-discovery">Open view</a></article>
      <article class="stage"><span class="pill review">2 / triage</span><h3>SEC IPO Alerts</h3><p>New filing evidence prioritized by transparent review signals.</p><small>No automatic status changes.</small><a href="/dashboard/sec-alerts">Open view</a></article>
      <article class="stage"><span class="pill review">3 / decision</span><h3>IPO Review Outcomes</h3><p>Documented human decisions matched back to filing URL and CIK.</p><small>Controlled promotion audit.</small><a href="/dashboard/ipo-reviews">Open view</a></article>
      <article class="stage"><span class="pill verified">4 / registry</span><h3>IPO Watch</h3><p>Candidate, filed, listed and withdrawn milestones with sources.</p><small>Research status board only.</small><a href="/dashboard/ipo-watch">Open view</a></article>
    </section>
    <h2>International Listings Evidence</h2>
    <section class="coverage">
      <article class="stage"><span class="pill verified">source map</span><h3>Global Listings Watch</h3><p>Official signal rules for ten markets, with restricted routes kept explicit.</p><a href="/dashboard/global-listings">Open view</a></article>
      <article class="stage"><span class="pill review">change queue</span><h3>Global Listings Alerts</h3><p>Daily comparison of offering, prospectus and listing-document signals.</p><a href="/dashboard/global-alerts">Open view</a></article>
      <article class="stage"><span class="pill verified">primary evidence</span><h3>Issuer Confirmations</h3><p>Reviewed official issuer milestones such as trading start or offering close.</p><a href="/dashboard/issuer-confirmations">Open view</a></article>
    </section>
  </main>
</body>
</html>"""


def etf_evidence_center_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TargetAudit | ETF Evidence Center</title>
  <style>
    :root {
      --bg:#071016; --panel:#0f1c24; --line:#20343d; --text:#edf1ef;
      --muted:#98abb0; --mint:#56daac; --gold:#f0bc62; --blue:#62a6ff;
    }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--bg); color:var(--text); font:15px/1.5 Inter,Arial,sans-serif; }
    header,main { max-width:1220px; margin:auto; padding:30px 28px; }
    nav,.meta { color:var(--muted); text-transform:uppercase; letter-spacing:.08em; font-size:13px; }
    a { color:var(--mint); text-decoration:none; }
    h1 { font-size:clamp(40px,5vw,62px); line-height:1.04; margin:38px 0 14px; }
    h2 { margin:42px 0 16px; font-size:22px; }
    h3 { margin:10px 0 8px; }
    .lead { color:var(--muted); font-size:18px; max-width:920px; }
    .cards { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin:34px 0; }
    .card,.view,.notice { background:var(--panel); border:1px solid var(--line); border-radius:14px; }
    .card { padding:18px 20px; }
    .card p,.view p,.view small { color:var(--muted); margin:0; display:block; }
    .card strong { color:var(--mint); display:block; font-size:28px; margin-top:5px; }
    .notice { border-left:3px solid var(--gold); padding:15px 18px; color:var(--muted); }
    .views { display:grid; grid-template-columns:repeat(2,1fr); gap:16px; }
    .view { padding:18px; }
    .pill { display:inline-block; border-radius:999px; padding:4px 9px; font-size:12px; }
    .fixture { color:var(--blue); background:rgba(98,166,255,.12); }
    .regulatory { color:var(--mint); background:rgba(86,218,172,.12); }
    @media(max-width:880px) { .cards,.views { grid-template-columns:1fr; } }
  </style>
</head>
<body>
  <header>
    <nav><a href="/dashboard/open">Open Edition</a> / <a href="/dashboard/reports">Report Center</a> / ETF Evidence Center</nav>
    <h1>ETF evidence.<br>Frequency first.</h1>
    <p class="lead">A single entry point for holdings research that keeps synthetic daily-shaped comparisons separate from official periodic SEC N-PORT evidence.</p>
    <section class="cards">
      <article class="card"><p>Synthetic sandboxes</p><strong>3</strong></article>
      <article class="card"><p>Regulatory comparisons</p><strong>2</strong></article>
      <article class="card"><p>N-PORT controls</p><strong>2</strong></article>
      <article class="card"><p>Required paid data</p><strong>None</strong></article>
    </section>
  </header>
  <main>
    <p class="notice"><strong>Reading rule:</strong> observed position differences are not confirmed manager trades. The included sandboxes do not redistribute real issuer holdings, and N-PORT periods are regulatory evidence rather than daily or real-time activity.</p>
    <h2>Synthetic Snapshot Sandboxes</h2>
    <section class="views">
      <article class="view"><span class="pill fixture">daily-shaped fixture</span><h3>ARKK Holdings Sandbox</h3><p>Exercise normalized ARK-format position changes without publishing ARK holdings.</p><small>Project-authored fixtures only.</small><a href="/dashboard/etf/arkk-demo">Open view</a></article>
      <article class="view"><span class="pill fixture">daily-shaped fixture</span><h3>XLF Holdings Sandbox</h3><p>Test the financial-sector benchmark workflow with synthetic snapshots.</p><small>Not confirmed manager trades.</small><a href="/dashboard/etf/xlf-demo">Open view</a></article>
      <article class="view"><span class="pill fixture">daily-shaped fixture</span><h3>IYF Holdings Sandbox</h3><p>Test a second financial ETF without automated iShares collection.</p><small>Project-authored fixtures only.</small><a href="/dashboard/etf/iyf-demo">Open view</a></article>
    </section>
    <h2>SEC N-PORT Evidence</h2>
    <section class="views">
      <article class="view"><span class="pill regulatory">regulatory periodic</span><h3>N-PORT Recent Filing</h3><p>Compare a recent filing period through the regulatory workflow.</p><small>Periodic evidence, not daily activity.</small><a href="/dashboard/etf/nport-recent">Open view</a></article>
      <article class="view"><span class="pill regulatory">regulatory periodic</span><h3>ETF Regulatory Holdings</h3><p>Read historical N-PORT position comparisons in their own layer.</p><small>Does not claim real-time trading.</small><a href="/dashboard/etf-regulatory">Open view</a></article>
      <article class="view"><span class="pill regulatory">official catalog</span><h3>N-PORT Dataset Catalog</h3><p>Inspect published SEC ZIP releases available for historical backfill.</p><small>Official public source; quarterly cadence.</small><a href="/dashboard/etf/nport-catalog">Open view</a></article>
      <article class="view"><span class="pill regulatory">sync control</span><h3>N-PORT Sync Status</h3><p>Track newly observed SEC quarters and controlled local downloads.</p><small>Operational state, not a signal.</small><a href="/dashboard/etf/nport-sync">Open view</a></article>
    </section>
  </main>
</body>
</html>"""


_GLOBAL_CONTRIBUTOR_COPY = {
    "en": {
        "page_title": "Global Contributor Gateway",
        "language_label": "Languages",
        "languages_card": "Languages",
        "monitors_card": "Global monitors mapped",
        "paid_card": "Required paid data",
        "real_card": "Real target sources activated",
        "none": "None",
        "evidence_rule": "Evidence rule",
        "heading": "Bring your market.<br>Bring the evidence.",
        "lead": "Help TargetAudit cover official listings evidence or find lawful historical analyst-target data without asking open-source users to buy a dataset.",
        "boundary": "A public page, API endpoint or GitHub repository is not publication permission. A proposal must identify the official source, access terms and the output we may legally display.",
        "reports": "Current analytical reports remain in English so generated artifacts and tests stay reproducible. This is the first localized contributor surface.",
        "paths": "Contribution paths",
        "connector": "Official listings connector",
        "connector_body": "Propose an exchange or regulator feed for filings, approvals, listings or withdrawals.",
        "targets": "Historical target source",
        "targets_body": "Find dated target prices with firm attribution and explicit public-output rights.",
        "permission": "Permission evidence",
        "permission_body": "Provide a written license or terms page allowing collection, retention and derived public display.",
        "required": "Required evidence",
        "items": [
            "Official product or regulator URL",
            "Terms, license or open-data notice URL",
            "Fields, history and update frequency",
            "Cost and key or registration requirements",
            "Rule for storage, redistribution and derived output",
        ],
        "not_accept": "Not accepted as activation evidence",
        "not_accept_body": "Screenshots, scraped pages, unofficial wrappers and free sign-up access alone cannot unlock a real public ranking.",
        "github": "Use the GitHub Data Source Proposal issue template after launch. TargetAudit will review the source before any connector is enabled.",
    },
    "ja": {
        "page_title": "グローバル貢献者ゲートウェイ",
        "language_label": "言語",
        "languages_card": "対応言語",
        "monitors_card": "対象市場モニター",
        "paid_card": "必要な有料データ",
        "real_card": "有効化済み実データ",
        "none": "なし",
        "evidence_rule": "証拠のルール",
        "heading": "市場の知識を。<br>根拠とともに。",
        "lead": "オープンソース利用者に有料データ購入を求めず、公式の上場証拠や合法的に利用できる過去の目標株価データを探す活動に参加できます。",
        "boundary": "公開ページ、API、GitHub リポジトリが存在するだけでは公開許可になりません。公式ソース、利用規約、公開可能な出力を明示してください。",
        "reports": "生成レポートとテストの再現性を保つため、現在の分析レポートは英語のままです。このページが最初の多言語コントリビューター画面です。",
        "paths": "貢献できる内容",
        "connector": "公式上場コネクター",
        "connector_body": "届出、承認、新規上場、取消しを示す取引所または規制当局のフィードを提案してください。",
        "targets": "過去の目標株価ソース",
        "targets_body": "日付と証券会社名があり、公開出力の権利が明示された目標株価データを探します。",
        "permission": "許諾の証拠",
        "permission_body": "収集、保存、派生結果の公開表示を認める規約または書面許可を提示してください。",
        "required": "必要な証拠",
        "items": ["公式製品または規制当局の URL", "利用規約、ライセンス、オープンデータ通知の URL", "項目、履歴期間、更新頻度", "費用とキーまたは登録要件", "保存、再配布、派生出力のルール"],
        "not_accept": "有効化の根拠にならないもの",
        "not_accept_body": "スクリーンショット、スクレイピング、非公式ラッパー、無料登録だけでは公開ランキングを有効化できません。",
        "github": "公開後は GitHub の Data Source Proposal テンプレートを使用してください。コネクターを有効化する前にソースを審査します。",
    },
    "pt-BR": {
        "page_title": "Portal Global de Colaboradores",
        "language_label": "Idiomas",
        "languages_card": "Idiomas",
        "monitors_card": "Monitores globais mapeados",
        "paid_card": "Dados pagos obrigatórios",
        "real_card": "Fontes reais ativadas",
        "none": "Nenhum",
        "evidence_rule": "Regra de evidência",
        "heading": "Traga seu mercado.<br>Traga a evidência.",
        "lead": "Ajude o TargetAudit a cobrir listagens oficiais ou encontrar histórico legal de preços-alvo sem obrigar usuários open source a comprar dados.",
        "boundary": "Uma página pública, API ou repositório GitHub não representa permissão de publicação. A proposta deve indicar fonte oficial, termos de acesso e o output que podemos exibir legalmente.",
        "reports": "Os relatórios analíticos atuais permanecem em inglês para manter artefatos e testes reproduzíveis. Esta é a primeira superfície localizada para colaboradores.",
        "paths": "Formas de colaborar",
        "connector": "Conector oficial de listagens",
        "connector_body": "Proponha um feed de bolsa ou regulador para ofertas, aprovações, listagens ou cancelamentos.",
        "targets": "Fonte histórica de preço-alvo",
        "targets_body": "Encontre preços-alvo datados, com instituição atribuída e direitos expressos para output público.",
        "permission": "Evidência de permissão",
        "permission_body": "Forneça licença ou termos escritos que permitam coleta, retenção e exibição pública derivada.",
        "required": "Evidência obrigatória",
        "items": ["URL oficial do produto ou regulador", "URL de termos, licença ou aviso de dados abertos", "Campos, histórico e frequência de atualização", "Custo e exigência de chave ou cadastro", "Regra para armazenamento, redistribuição e output derivado"],
        "not_accept": "Não basta para ativar",
        "not_accept_body": "Capturas de tela, scraping, wrappers não oficiais e apenas acesso gratuito não liberam um ranking público real.",
        "github": "Depois do lançamento, use o template GitHub Data Source Proposal. O TargetAudit revisará a fonte antes de ativar qualquer conector.",
    },
    "zh-Hant": {
        "page_title": "全球貢獻者入口",
        "language_label": "語言",
        "languages_card": "支援語言",
        "monitors_card": "已盤點全球監測器",
        "paid_card": "必要付費資料",
        "real_card": "已啟用真實目標價來源",
        "none": "無",
        "evidence_rule": "證據規則",
        "heading": "帶來你的市場，<br>也帶來證據。",
        "lead": "協助 TargetAudit 納入官方上市證據，或尋找可合法使用的歷史分析師目標價資料，而不要求開源使用者購買資料。",
        "boundary": "公開網頁、API 或 GitHub 儲存庫的存在，不等同公開發布許可。提案必須說明官方來源、使用條款及可合法展示的輸出。",
        "reports": "為維持產出檔案與測試的可重現性，目前分析報告保留英文。這是第一個多語言貢獻者介面。",
        "paths": "貢獻途徑",
        "connector": "官方上市連接器",
        "connector_body": "提出交易所或監管機構針對申請、核准、上市或撤回的資料來源。",
        "targets": "歷史目標價來源",
        "targets_body": "尋找含日期、機構歸屬及明確公共輸出權利的目標價資料。",
        "permission": "授權證據",
        "permission_body": "提供允許收集、保存及公開展示衍生結果的書面授權或條款頁面。",
        "required": "必要證據",
        "items": ["官方產品或監管機構網址", "條款、授權或開放資料聲明網址", "欄位、歷史範圍及更新頻率", "費用與金鑰或註冊要求", "儲存、再發布及衍生輸出的規則"],
        "not_accept": "不能作為啟用依據",
        "not_accept_body": "截圖、爬取頁面、非官方包裝器或僅有免費註冊，都不足以啟用真實公開排名。",
        "github": "發布後請使用 GitHub Data Source Proposal issue 範本。TargetAudit 會在啟用任何連接器前審查來源。",
    },
    "ko": {
        "page_title": "글로벌 기여자 게이트웨이",
        "language_label": "언어",
        "languages_card": "지원 언어",
        "monitors_card": "검토한 글로벌 모니터",
        "paid_card": "필수 유료 데이터",
        "real_card": "활성화된 실제 목표주가 출처",
        "none": "없음",
        "evidence_rule": "근거 규칙",
        "heading": "시장을 제안하고,<br>근거를 함께 제출하세요.",
        "lead": "오픈 소스 사용자가 유료 데이터를 구매하지 않아도 공식 상장 근거 또는 합법적으로 사용할 수 있는 과거 애널리스트 목표주가 자료를 찾는 데 참여할 수 있습니다.",
        "boundary": "공개 웹페이지, API 또는 GitHub 저장소가 있다는 사실만으로 공개 게시 권한이 생기지 않습니다. 공식 출처, 이용 조건, 합법적으로 표시할 수 있는 결과를 제시해야 합니다.",
        "reports": "생성 산출물과 테스트의 재현성을 유지하기 위해 현재 분석 보고서는 영어로 유지됩니다. 이 페이지가 첫 다국어 기여자 화면입니다.",
        "paths": "기여 방법",
        "connector": "공식 상장 커넥터",
        "connector_body": "공시, 승인, 신규 상장 또는 철회를 보여 주는 거래소나 규제기관 피드를 제안하세요.",
        "targets": "과거 목표주가 출처",
        "targets_body": "날짜와 증권사 귀속 정보가 있으며 공개 결과 권한이 명시된 목표주가 자료를 찾습니다.",
        "permission": "허가 근거",
        "permission_body": "수집, 보관, 파생 결과의 공개 표시를 허용하는 서면 허가나 약관을 제출하세요.",
        "required": "필수 근거",
        "items": ["공식 제품 또는 규제기관 URL", "약관, 라이선스 또는 공개데이터 고지 URL", "필드, 과거 범위 및 갱신 주기", "비용과 키 또는 등록 요건", "저장, 재배포 및 파생 출력 규칙"],
        "not_accept": "활성화 근거로 인정되지 않는 것",
        "not_accept_body": "스크린샷, 스크래핑 페이지, 비공식 래퍼, 무료 가입만으로는 실제 공개 순위를 활성화할 수 없습니다.",
        "github": "출시 후 GitHub Data Source Proposal 이슈 템플릿을 사용하세요. TargetAudit은 커넥터를 활성화하기 전에 출처를 검토합니다.",
    },
}


def global_contributors_html(locale: str = "en") -> str:
    language = locale if locale in _GLOBAL_CONTRIBUTOR_COPY else "en"
    copy = _GLOBAL_CONTRIBUTOR_COPY[language]
    language_links = " / ".join(
        f'<a href="/dashboard/contribute?lang={code}">{label}</a>'
        for code, label in (
            ("en", "English"),
            ("ja", "日本語"),
            ("pt-BR", "Português (Brasil)"),
            ("zh-Hant", "繁體中文"),
            ("ko", "한국어"),
        )
    )
    evidence_items = "".join(f"<li>{item}</li>" for item in copy["items"])
    return f"""<!doctype html>
<html lang="{language}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TargetAudit | {copy["page_title"]}</title>
  <style>
    :root {{
      --bg:#071016; --panel:#0f1c24; --line:#20343d; --text:#edf1ef;
      --muted:#98abb0; --mint:#56daac; --gold:#f0bc62; --blue:#62a6ff;
    }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--bg); color:var(--text); font:15px/1.6 Inter,Arial,sans-serif; }}
    header,main {{ max-width:1160px; margin:auto; padding:30px 28px; }}
    nav,.meta {{ color:var(--muted); font-size:13px; }}
    nav:first-of-type {{ text-transform:uppercase; letter-spacing:.08em; }}
    a {{ color:var(--mint); text-decoration:none; }}
    h1 {{ font-size:clamp(38px,5vw,60px); line-height:1.08; margin:38px 0 14px; }}
    h2 {{ margin:42px 0 16px; font-size:22px; }}
    h3 {{ margin:10px 0 8px; }}
    .lead {{ color:var(--muted); font-size:18px; max-width:930px; }}
    .languages {{ margin-top:18px; background:var(--panel); border:1px solid var(--line); border-radius:999px; padding:10px 17px; display:inline-block; }}
    .cards {{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin:34px 0; }}
    .card,.path,.notice,.checklist {{ background:var(--panel); border:1px solid var(--line); border-radius:14px; }}
    .card {{ padding:18px 20px; }} .card p,.path p {{ color:var(--muted); margin:0; }}
    .card strong {{ display:block; color:var(--mint); font-size:29px; margin-top:5px; }}
    .notice {{ border-left:3px solid var(--gold); padding:15px 18px; color:var(--muted); margin:16px 0; }}
    .paths {{ display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }}
    .path {{ padding:18px; }} .pill {{ display:inline-block; color:var(--blue); background:rgba(98,166,255,.12); border-radius:999px; padding:4px 9px; font-size:12px; }}
    .two-col {{ display:grid; grid-template-columns:1.15fr .85fr; gap:16px; }}
    .checklist {{ padding:18px 22px; }} .checklist ul {{ margin:10px 0 0; padding-left:21px; color:var(--muted); }}
    .github {{ margin-top:28px; color:var(--mint); font-weight:600; }}
    @media(max-width:900px) {{ .cards,.paths,.two-col {{ grid-template-columns:1fr; }} .languages {{ border-radius:14px; }} }}
  </style>
</head>
<body>
  <header>
    <nav><a href="/dashboard/open">Open Edition</a> / <a href="/dashboard/reports">Report Center</a> / <a href="/dashboard/global-listings">Global Listings Watch</a> / {copy["page_title"]}</nav>
    <div class="languages" aria-label="{copy["language_label"]}">{language_links}</div>
    <h1>{copy["heading"]}</h1>
    <p class="lead">{copy["lead"]}</p>
    <section class="cards">
      <article class="card"><p>{copy["languages_card"]}</p><strong>5</strong></article>
      <article class="card"><p>{copy["monitors_card"]}</p><strong>10</strong></article>
      <article class="card"><p>{copy["paid_card"]}</p><strong>{copy["none"]}</strong></article>
      <article class="card"><p>{copy["real_card"]}</p><strong>0</strong></article>
    </section>
  </header>
  <main>
    <p class="notice"><strong>{copy["evidence_rule"]}:</strong> {copy["boundary"]}</p>
    <p class="notice">{copy["reports"]}</p>
    <h2>{copy["paths"]}</h2>
    <section class="paths">
      <article class="path"><span class="pill">LISTINGS</span><h3>{copy["connector"]}</h3><p>{copy["connector_body"]}</p></article>
      <article class="path"><span class="pill">TARGETS</span><h3>{copy["targets"]}</h3><p>{copy["targets_body"]}</p></article>
      <article class="path"><span class="pill">RIGHTS</span><h3>{copy["permission"]}</h3><p>{copy["permission_body"]}</p></article>
    </section>
    <h2>{copy["required"]}</h2>
    <section class="two-col">
      <article class="checklist"><ul>{evidence_items}</ul></article>
      <article class="checklist"><h3>{copy["not_accept"]}</h3><p>{copy["not_accept_body"]}</p></article>
    </section>
    <p class="github">{copy["github"]}</p>
  </main>
</body>
</html>"""


def licensed_extensions_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TargetAudit | Licensed Extensions</title>
  <style>
    :root {
      --bg:#071016; --panel:#0f1c24; --panel2:#14242d; --line:#20343d;
      --text:#edf1ef; --muted:#98abb0; --mint:#56daac; --gold:#f0bc62; --red:#ff7d72;
    }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--bg); color:var(--text); font:15px/1.5 Inter,Arial,sans-serif; }
    header, main { max-width:1220px; margin:auto; padding:30px 28px; }
    nav,.meta { color:var(--muted); text-transform:uppercase; letter-spacing:.08em; font-size:13px; }
    a { color:var(--mint); text-decoration:none; }
    h1 { font-size:clamp(39px,5vw,60px); line-height:1.04; margin:38px 0 14px; }
    h2 { margin:43px 0 16px; font-size:22px; }
    .lead { color:var(--muted); font-size:18px; max-width:920px; }
    .notice { background:var(--panel); border:1px solid var(--line); border-left:3px solid var(--gold);
      border-radius:14px; padding:15px 18px; color:var(--muted); margin:18px 0; }
    .cards { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin:34px 0; }
    .card,.table-wrap,.detail { background:var(--panel); border:1px solid var(--line); border-radius:14px; }
    .card { padding:18px 20px; }
    .card p { margin:0; color:var(--muted); }
    .card strong { display:block; font-size:36px; color:var(--mint); }
    .layout { display:grid; grid-template-columns:minmax(620px,1fr) 370px; gap:18px; }
    .table-wrap { overflow:hidden; }
    table { width:100%; border-collapse:collapse; }
    th,td { padding:14px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }
    th { color:var(--muted); text-transform:uppercase; font-size:12px; font-weight:500; }
    td small { display:block; color:var(--muted); }
    tr[data-extension] { cursor:pointer; }
    tr[data-extension]:hover { background:var(--panel2); }
    .pill { display:inline-block; border-radius:999px; padding:4px 9px; font-size:12px; white-space:nowrap; }
    .available_byol { color:var(--mint); background:rgba(86,218,172,.12); }
    .quote_required,.requires_separate_written_rights,.requires_negotiated_public_output_rights {
      color:var(--gold); background:rgba(240,188,98,.12);
    }
    .detail { padding:18px; min-height:355px; }
    .detail p { color:var(--muted); }
    .fact { background:var(--panel2); border-radius:9px; padding:11px; margin:10px 0; }
    .fact small { display:block; color:var(--muted); text-transform:uppercase; letter-spacing:.05em; margin-bottom:4px; }
    #error { display:none; border-left-color:var(--red); color:var(--red); }
    @media(max-width:980px) {
      .cards,.layout { grid-template-columns:1fr; }
      .table-wrap { background:transparent; border:0; overflow:visible; }
      thead { display:none; }
      table,tbody,tr,td { display:block; width:100%; }
      tr { background:var(--panel); border:1px solid var(--line); border-radius:14px; margin-bottom:14px; padding:11px 15px; }
      td { border:0; padding:9px 0 9px 126px; min-height:40px; position:relative; }
      td::before { content:attr(data-label); position:absolute; left:0; top:10px; color:var(--muted); font-size:11px; text-transform:uppercase; letter-spacing:.06em; }
    }
  </style>
</head>
<body>
  <header>
    <nav><a href="/dashboard/open">Open Edition</a> / Licensed Extensions / <a href="/dashboard/approvals">Provider Approvals</a> / <a href="/dashboard/readiness">Readiness</a></nav>
    <h1>Bring your own<br>licensed data.</h1>
    <p class="lead">Optional paid sources for users who choose private, licensed analyst-target research. Open Edition remains useful at no data cost.</p>
    <p class="meta" id="reviewed">Loading licensed-source research...</p>
    <section class="cards">
      <article class="card"><p>Optional providers</p><strong id="tracked">-</strong></article>
      <article class="card"><p>Listed prices</p><strong id="listed">-</strong></article>
      <article class="card"><p>Individual paths</p><strong id="individual">-</strong></article>
      <article class="card"><p>Public-output approved</p><strong id="public">-</strong></article>
    </section>
  </header>
  <main>
    <p class="notice" id="policy">Loading licensing boundary...</p>
    <p class="notice">The displayed <strong>USD 99/month</strong> Massive price is for its individual Benzinga Analyst Ratings expansion. Confirm any required base Stocks plan at checkout. Individual terms do not enable a shared public ranking.</p>
    <p class="notice"><strong>MarketBeat All Access</strong> is a cheaper private-pilot candidate at <strong>USD 249/year or USD 29/month</strong>, but its advertised ratings export covers only up to six recent months. That is not enough for the one-year target audit unless separate historical access is licensed.</p>
    <p class="notice"><strong>Freemium API warning:</strong> Finnhub advertises Recommendation Trends and Price Target coverage, and FMP documents target-consensus endpoints. Their reviewed pages require negotiated redistribution or data-display rights before TargetAudit can publish data or derived rankings.</p>
    <p id="error" class="notice"></p>
    <h2>Optional Providers</h2>
    <section class="layout">
      <div class="table-wrap">
        <table>
          <thead><tr><th>Provider</th><th>Listed Price</th><th>Availability</th><th>Output Rights</th></tr></thead>
          <tbody id="extensions"><tr><td colspan="4">Loading candidates...</td></tr></tbody>
        </table>
      </div>
      <aside class="detail" id="detail">
        <h3>License Review</h3>
        <p>Select an option to inspect official price, terms and permitted TargetAudit use.</p>
      </aside>
    </section>
  </main>
  <script>
    const $ = (id) => document.getElementById(id);
    let extensions = [];
    function text(value) {
      return String(value == null || value === "" ? "-" : value)
        .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
    }
    function href(value) {
      try {
        const parsed = new URL(value);
        return parsed.protocol === "https:" ? text(value) : "#";
      } catch (_) { return "#"; }
    }
    async function initialize() {
      try {
        const response = await fetch("/api/v1/extensions/licensed");
        if (!response.ok) throw new Error((await response.json()).detail || "Request failed");
        const data = await response.json();
        extensions = data.items;
        $("reviewed").textContent = `${data.market_focus} / reviewed as of ${data.as_of}`;
        $("tracked").textContent = data.extension_count;
        $("listed").textContent = data.listed_price_count;
        $("individual").textContent = data.individual_option_count;
        $("public").textContent = data.public_output_approved_count;
        $("policy").textContent = data.policy_note;
        $("extensions").innerHTML = extensions.map((item) => `<tr data-extension="${text(item.extension_id)}"><td data-label="Provider"><strong>${text(item.extension_name)}</strong><small>${text(item.provider)}</small></td><td data-label="Listed price">${text(item.price_display)}<small>${text(item.price_basis)}</small></td><td data-label="Availability"><span class="pill ${text(item.status)}">${text(item.status)}</span></td><td data-label="Output rights"><span class="pill ${text(item.public_output_status)}">${text(item.public_output_status)}</span></td></tr>`).join("");
        document.querySelectorAll("tr[data-extension]").forEach((row) => row.addEventListener("click", () => showExtension(row.dataset.extension)));
        if (extensions.length) showExtension(extensions[0].extension_id);
      } catch (error) {
        $("error").style.display = "block";
        $("error").textContent = error.message;
      }
    }
    function showExtension(extensionId) {
      const item = extensions.find((candidate) => candidate.extension_id === extensionId);
      $("detail").innerHTML = `<h3>${text(item.extension_name)}</h3><p>${text(item.coverage)}</p><div class="fact"><small>Listed price</small>${text(item.price_display)}<br>${text(item.price_basis)}</div><div class="fact"><small>Allowed integration mode</small>${text(item.allowed_mode)}</div><div class="fact"><small>Public output status</small>${text(item.public_output_status)}</div><p>${text(item.review_note)}</p><p><a href="${href(item.official_url)}" target="_blank" rel="noopener">Product</a> / <a href="${href(item.pricing_url)}" target="_blank" rel="noopener">Pricing</a> / <a href="${href(item.terms_url)}" target="_blank" rel="noopener">Terms</a></p>`;
    }
    initialize();
  </script>
</body>
</html>"""


def market_context_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TargetAudit | Market Context</title>
  <style>
    :root {
      --bg:#071016; --panel:#0f1c24; --line:#20343d; --text:#edf1ef;
      --muted:#98abb0; --mint:#56daac; --gold:#f0bc62; --blue:#62a6ff;
    }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--bg); color:var(--text); font:15px/1.5 Inter,Arial,sans-serif; }
    header,main { max-width:1240px; margin:auto; padding:30px 28px; }
    nav,.meta { color:var(--muted); text-transform:uppercase; letter-spacing:.08em; font-size:13px; }
    a { color:var(--mint); text-decoration:none; }
    h1 { font-size:clamp(38px,5vw,60px); line-height:1.04; margin:38px 0 14px; }
    h2 { font-size:22px; margin:40px 0 16px; }
    .lead { color:var(--muted); font-size:18px; max-width:930px; }
    .cards { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin:34px 0; }
    .card,.notice,.chart-shell { background:var(--panel); border:1px solid var(--line); border-radius:14px; }
    .card { padding:17px 20px; }
    .card p { color:var(--muted); margin:0; }
    .card strong { display:block; color:var(--mint); margin-top:5px; font-size:16px; }
    .notice { border-left:3px solid var(--gold); color:var(--muted); padding:15px 18px; margin:18px 0; }
    .chart-shell { padding:18px; height:min(680px, calc(100vh - 230px)); min-height:520px; }
    .tradingview-widget-container { height:100%; width:100%; }
    .tradingview-widget-container__widget { height:calc(100% - 32px); width:100%; }
    .tradingview-widget-copyright { font-size:13px; line-height:32px; color:var(--muted); text-align:left; }
    .tradingview-widget-copyright .blue-text { color:var(--blue); }
    @media(max-width:900px) { .cards { grid-template-columns:1fr 1fr; } .chart-shell { height:560px; } }
    @media(max-width:570px) { .cards { grid-template-columns:1fr; } }
  </style>
</head>
<body>
  <header>
    <nav><a href="/dashboard/open">Open Edition</a> / Market Context / <a href="/dashboard/policy">Public Use Policy</a> / <a href="/dashboard/financials">Financials Sandbox</a></nav>
    <h1>Sector context.<br>Separate from scoring.</h1>
    <p class="lead">A visual chart for the Financials benchmark, embedded from TradingView with attribution intact. TargetAudit does not collect, normalize or export widget data.</p>
    <p class="meta">External attributed display / default symbol: AMEX:XLF</p>
    <section class="cards">
      <article class="card"><p>Role</p><strong>Context only</strong></article>
      <article class="card"><p>Data collection</p><strong>None</strong></article>
      <article class="card"><p>Scorecard input</p><strong>Never</strong></article>
      <article class="card"><p>Attribution</p><strong>TradingView visible</strong></article>
    </section>
  </header>
  <main>
    <p class="notice">This third-party chart is for visual context only. It is not investment advice, a TargetAudit data source, a verified real-time record or evidence for analyst ranking results.</p>
    <h2>XLF Visual Context</h2>
    <section class="chart-shell">
      <!-- TradingView Widget BEGIN -->
      <div class="tradingview-widget-container">
        <div class="tradingview-widget-container__widget"></div>
        <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/symbols/AMEX-XLF/" rel="noopener nofollow" target="_blank"><span class="blue-text">XLF chart</span></a><span class="trademark"> by TradingView</span></div>
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
        {
          "autosize": true,
          "symbol": "AMEX:XLF",
          "interval": "D",
          "timezone": "Etc/UTC",
          "theme": "dark",
          "style": "1",
          "locale": "en",
          "allow_symbol_change": true,
          "calendar": false,
          "support_host": "https://www.tradingview.com"
        }
        </script>
      </div>
      <!-- TradingView Widget END -->
    </section>
  </main>
</body>
</html>"""


def public_use_policy_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TargetAudit | Public Use Policy</title>
  <style>
    :root {
      --bg:#071016; --panel:#0f1c24; --panel2:#14242d; --line:#20343d;
      --text:#edf1ef; --muted:#98abb0; --mint:#56daac; --gold:#f0bc62;
      --blue:#62a6ff; --red:#ff7d72;
    }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--bg); color:var(--text); font:15px/1.5 Inter,Arial,sans-serif; }
    header,main { max-width:1240px; margin:auto; padding:30px 28px; }
    nav,.meta { color:var(--muted); text-transform:uppercase; letter-spacing:.08em; font-size:13px; }
    a { color:var(--mint); text-decoration:none; }
    h1 { font-size:clamp(38px,5vw,60px); line-height:1.04; margin:38px 0 14px; }
    h2 { margin:42px 0 16px; font-size:22px; }
    h3 { margin:0 0 10px; font-size:17px; }
    .lead { color:var(--muted); font-size:18px; max-width:940px; }
    .notice { background:var(--panel); border:1px solid var(--line); border-left:3px solid var(--gold);
      border-radius:14px; padding:15px 18px; color:var(--muted); margin:18px 0; }
    .cards { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin:34px 0; }
    .card,.layer,.panel,.blocked { background:var(--panel); border:1px solid var(--line); border-radius:14px; }
    .card { padding:17px 20px; }
    .card p { color:var(--muted); margin:0; }
    .card strong { display:block; font-size:35px; color:var(--mint); margin-top:4px; }
    .layers { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }
    .layer { padding:18px; }
    .layer p,.panel li,.blocked p { color:var(--muted); }
    .pill { display:inline-block; border-radius:999px; padding:5px 9px; font-size:12px; margin-bottom:12px; }
    .redistributable_demo { color:var(--blue); background:rgba(98,166,255,.12); }
    .evidence_only { color:var(--mint); background:rgba(86,218,172,.12); }
    .permission_required { color:var(--gold); background:rgba(240,188,98,.12); }
    .external_display_only { color:var(--blue); background:rgba(98,166,255,.12); }
    .layout { display:grid; grid-template-columns:1fr 1fr; gap:18px; }
    .panel { padding:18px; }
    .panel ul { margin:0; padding-left:20px; }
    .panel li { margin:10px 0; }
    .blocked-list { display:grid; grid-template-columns:repeat(2,1fr); gap:14px; }
    .blocked { padding:16px; }
    .blocked small { display:block; color:var(--muted); margin:5px 0 11px; }
    .blocked strong { color:var(--red); }
    #error { display:none; border-left-color:var(--red); color:var(--red); }
    @media(max-width:960px) { .cards,.layers,.layout,.blocked-list { grid-template-columns:1fr; } }
  </style>
</head>
<body>
  <header>
    <nav><a href="/dashboard/open">Open Edition</a> / Public Use Policy / <a href="/dashboard/governance">Source Governance</a> / <a href="/dashboard/release">Release Center</a></nav>
    <h1>Research evidence.<br>Not investment advice.</h1>
    <p class="lead" id="summary">Loading public-use boundaries...</p>
    <p class="meta" id="reviewed">Loading policy status...</p>
    <section class="cards">
      <article class="card"><p>Tracked sources</p><strong id="tracked">-</strong></article>
      <article class="card"><p>Blocked sources</p><strong id="blocked-count">-</strong></article>
      <article class="card"><p>Reviews pending</p><strong id="review-count">-</strong></article>
      <article class="card"><p>Manual only</p><strong id="manual-count">-</strong></article>
    </section>
  </header>
  <main>
    <p class="notice"><strong>Important:</strong> This page is an internal product safeguard pending external legal review. It is not legal, tax or investment advice.</p>
    <p id="error" class="notice"></p>
    <h2>Data Layers</h2>
    <section class="layers" id="layers"></section>
    <h2>Publication Controls</h2>
    <section class="layout">
      <article class="panel"><h3>Before public output</h3><ul id="rules"></ul></article>
      <article class="panel"><h3>Operator responsibilities</h3><ul id="responsibilities"></ul></article>
    </section>
    <h2>Blocked From Automated Collection</h2>
    <section class="blocked-list" id="blocked-sources"></section>
  </main>
  <script>
    const $ = (id) => document.getElementById(id);
    function text(value) {
      return String(value == null || value === "" ? "-" : value)
        .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
    }
    function href(value) {
      try {
        const parsed = new URL(value);
        return parsed.protocol === "https:" ? text(value) : "#";
      } catch (_) { return "#"; }
    }
    async function initialize() {
      try {
        const response = await fetch("/api/v1/policy/public-use");
        if (!response.ok) throw new Error((await response.json()).detail || "Request failed");
        const data = await response.json();
        $("summary").textContent = data.summary;
        $("reviewed").textContent = `Policy ${data.policy_version} / ${data.review_status} / sources reviewed as of ${data.as_of}`;
        $("tracked").textContent = data.tracked_source_count;
        $("blocked-count").textContent = data.blocked_source_count;
        $("review-count").textContent = data.review_required_count;
        $("manual-count").textContent = data.manual_only_count;
        $("layers").innerHTML = data.data_layers.map((item) => `<article class="layer"><span class="pill ${text(item.status)}">${text(item.status)}</span><h3>${text(item.title)}</h3><p>${text(item.description)}</p></article>`).join("");
        $("rules").innerHTML = data.publication_rules.map((item) => `<li>${text(item)}</li>`).join("");
        $("responsibilities").innerHTML = data.operator_responsibilities.map((item) => `<li>${text(item)}</li>`).join("");
        $("blocked-sources").innerHTML = data.blocked_sources.map((item) => `<article class="blocked"><strong>${text(item.provider_name)}</strong><small>${text(item.data_class)}</small><p>${text(item.restriction)}</p><a href="${href(item.reference_url)}" target="_blank" rel="noopener">Terms / reference</a></article>`).join("");
      } catch (error) {
        $("error").style.display = "block";
        $("error").textContent = error.message;
      }
    }
    initialize();
  </script>
</body>
</html>"""


def financials_scorecard_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TargetAudit | Financials Scorecard</title>
  <style>
    :root {
      --bg:#071016; --panel:#0f1c24; --panel2:#14242d; --line:#20343d;
      --text:#edf1ef; --muted:#98abb0; --mint:#56daac; --gold:#f0bc62;
      --blue:#62a6ff; --red:#ff7d72;
    }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--bg); color:var(--text); font:15px/1.5 Inter,Arial,sans-serif; }
    header, main { max-width:1240px; margin:auto; padding:30px 28px; }
    nav,.meta { color:var(--muted); text-transform:uppercase; letter-spacing:.08em; font-size:13px; }
    h1 { font-size:clamp(38px,5vw,58px); line-height:1.05; margin:38px 0 14px; }
    h2 { margin:44px 0 16px; font-size:22px; }
    h3 { margin:0 0 12px; font-size:16px; }
    .lead { color:var(--muted); font-size:17px; max-width:780px; }
    .notice { background:var(--panel); border:1px solid var(--line); border-left:3px solid var(--gold);
      border-radius:14px; padding:15px 18px; color:var(--muted); margin:18px 0; }
    .cards { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin:34px 0; }
    .card,.filters,.table-wrap,.side-panel,.empty,.compare { background:var(--panel); border:1px solid var(--line); border-radius:14px; }
    .card { padding:17px 20px; }
    .card p { color:var(--muted); margin:0; }
    .card strong { display:block; font-size:35px; color:var(--mint); margin-top:4px; }
    .card small { color:var(--muted); }
    .filters { padding:17px; display:grid; grid-template-columns:2fr 1.2fr 1.1fr .8fr auto; gap:12px; align-items:end; }
    label { display:block; color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.06em; margin-bottom:6px; }
    select,input { width:100%; height:43px; background:var(--panel2); color:var(--text); border:1px solid var(--line); border-radius:9px; padding:0 11px; }
    button { height:43px; border:0; border-radius:9px; color:#061117; background:var(--mint); padding:0 20px; font-weight:600; cursor:pointer; }
    .actions { display:flex; flex-wrap:wrap; gap:12px; align-items:center; margin:15px 0 32px; color:var(--muted); }
    .action-link { background:var(--panel2); border:1px solid var(--line); border-radius:9px; padding:10px 14px; font-size:14px; }
    .compare { padding:18px; margin:0 0 34px; }
    .compare-controls { display:grid; grid-template-columns:1fr 1fr auto; gap:12px; align-items:end; }
    .compare-result { margin-top:15px; padding:13px; background:var(--panel2); border-radius:9px; color:var(--muted); }
    .compare-result strong { color:var(--mint); }
    .layout { display:grid; grid-template-columns:minmax(580px,1fr) 355px; gap:18px; }
    .table-wrap { overflow:hidden; }
    table { width:100%; border-collapse:collapse; }
    th,td { padding:14px 14px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }
    th { color:var(--muted); text-transform:uppercase; font-size:12px; font-weight:500; }
    td small { color:var(--muted); display:block; }
    tr[data-firm], tr[data-ticker] { cursor:pointer; }
    tr[data-firm]:hover, tr[data-ticker]:hover { background:var(--panel2); }
    .rate { color:var(--mint); font-weight:600; }
    .negative { color:var(--red); }
    .pill { display:inline-block; font-size:12px; padding:4px 9px; border-radius:999px; background:rgba(98,166,255,.12); color:var(--blue); }
    .pill.excluded { color:var(--gold); background:rgba(240,188,98,.12); }
    .side-panel { padding:18px; min-height:340px; }
    .side-panel p { color:var(--muted); }
    .summary { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin:14px 0; }
    .metric { background:var(--panel2); border-radius:9px; padding:10px; }
    .metric small { display:block; color:var(--muted); }
    .metric strong { font-size:19px; }
    .timeline { margin-top:18px; }
    .timeline p { font-size:13px; }
    .chart { margin:12px 0; padding:10px; background:var(--panel2); border-radius:9px; overflow:hidden; }
    .chart h4 { font-size:13px; margin:0 0 7px; color:var(--text); font-weight:500; }
    .chart svg { display:block; width:100%; height:auto; }
    .chart-events { display:grid; gap:5px; margin-top:8px; color:var(--muted); font-size:11px; }
    .chart-events strong { color:var(--text); font-weight:500; }
    .chart-note { color:var(--gold); }
    a { color:var(--mint); text-decoration:none; }
    .audit-grid { display:grid; grid-template-columns:300px 1fr; gap:18px; }
    .reasons { padding:18px; }
    .reason { display:flex; justify-content:space-between; border-bottom:1px solid var(--line); padding:10px 0; color:var(--muted); }
    .reason strong { color:var(--gold); }
    .empty { color:var(--muted); padding:26px; text-align:center; }
    #error { display:none; border-left-color:var(--red); color:var(--red); }
    @media(max-width:980px) {
      .cards { grid-template-columns:repeat(2,1fr); }
      .filters,.compare-controls,.layout,.audit-grid { grid-template-columns:1fr; }
      .table-wrap { overflow-x:auto; }
      table { min-width:680px; }
    }
  </style>
</head>
<body>
  <header>
    <nav><a href="/dashboard/open">Open Edition</a> / U.S. Financials / <a href="/dashboard/financials-evidence">Evidence Center</a> / Scorecard / <a href="/dashboard/release">Release Center</a> / <a href="/dashboard/readiness">Scorecard Readiness</a> / <a href="/dashboard/approvals">Provider Approvals</a> / <a href="/dashboard/governance">Source Governance</a> / <a href="/dashboard/operations">Operations Quality</a></nav>
    <h1>Price targets,<br>measured in daylight.</h1>
    <p class="lead">Auditable analyst-target research with visible sample size, uncertainty, benchmark context and exclusions. A hit is evidence of a reached target, not investment advice.</p>
    <p class="meta" id="run-meta">Loading latest stored research run...</p>
    <section class="cards">
      <article class="card"><p>Evaluated</p><strong id="evaluated">-</strong><small>Eligible observations</small></article>
      <article class="card"><p>Excluded</p><strong id="excluded">-</strong><small>Removed with reason</small></article>
      <article class="card"><p>Pending</p><strong id="pending">-</strong><small>Not yet mature</small></article>
      <article class="card"><p>Methodology</p><strong id="methodology">-</strong><small>Versioned scoring rules</small></article>
    </section>
  </header>
  <main>
    <p class="notice">Research dashboard only. Results shown here do not recommend buying, selling or sizing a position. Real public rankings remain dependent on approved data rights.</p>
    <p id="error" class="notice"></p>
    <section class="filters" aria-label="Scorecard filters">
      <div><label for="run">Research run</label><select id="run"></select></div>
      <div><label for="sector">Sector</label><select id="sector"><option value="">All sectors</option></select></div>
      <div><label for="direction">Direction</label><select id="direction"><option value="">Up and down</option><option value="up">Up targets</option><option value="down">Down targets</option></select></div>
      <div><label for="sample">Minimum N</label><input id="sample" type="number" min="1" value="1"></div>
      <button id="apply">Apply</button>
    </section>
    <section class="actions" aria-label="Downloads">
      <span>Download auditable results:</span>
      <a id="export-ranking" class="action-link" href="#">Export filtered ranking CSV</a>
      <a id="export-evaluations" class="action-link" href="#">Export observations CSV</a>
    </section>
    <h2>Compare Stored Runs</h2>
    <section class="compare" aria-label="Run comparison">
      <div class="compare-controls">
        <div><label for="compare-left">Baseline run</label><select id="compare-left"></select></div>
        <div><label for="compare-right">Comparison run</label><select id="compare-right"></select></div>
        <button id="compare">Compare</button>
      </div>
      <div id="compare-result" class="compare-result">Choose two stored runs to check whether evidence and methodology are comparable.</div>
    </section>
    <h2>Firm Ranking</h2>
    <section class="layout">
      <div class="table-wrap">
        <table>
          <thead><tr><th>Firm</th><th>N</th><th>Hit rate</th><th>95% CI</th><th>Median hit</th><th>Net excess</th></tr></thead>
          <tbody id="ranking"><tr><td colspan="6">Loading ranking...</td></tr></tbody>
        </table>
      </div>
      <aside id="detail" class="side-panel">
        <h3>Firm Detail</h3>
        <p>Select a firm to inspect its evaluated and excluded observations.</p>
      </aside>
    </section>
    <h2>Exclusions And Pending</h2>
    <section class="audit-grid">
      <div id="reasons" class="side-panel reasons"><p>Loading audit...</p></div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Observation</th><th>Firm</th><th>Ticker</th><th>Status</th><th>Reason</th><th>Evidence</th></tr></thead>
          <tbody id="audit"><tr><td colspan="6">Loading exclusions...</td></tr></tbody>
        </table>
      </div>
    </section>
  </main>
  <script>
    const $ = (id) => document.getElementById(id);
    const base = "/api/v1";
    let currentRun = "";

    function text(value) {
      return String(value == null || value === "" ? "-" : value)
        .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
    }
    function pct(value) { return value == null ? "-" : (value * 100).toFixed(2) + "%"; }
    function evidenceHref(value) {
      try {
        const parsed = new URL(value);
        return parsed.protocol === "https:" || parsed.protocol === "http:" ? text(value) : "#";
      } catch (_) { return "#"; }
    }
    function signedPct(value) {
      if (value == null) return "-";
      const rendered = pct(value);
      return value < 0 ? `<span class="negative">${rendered}</span>` : rendered;
    }
    async function json(url) {
      const response = await fetch(url);
      if (!response.ok) throw new Error((await response.json()).detail || "Request failed");
      return response.json();
    }
    function fail(message) {
      $("error").style.display = "block";
      $("error").textContent = message;
    }
    async function initialize() {
      try {
        const runs = await json(`${base}/runs`);
        if (!runs.length) { fail("No stored evaluation runs are available yet."); return; }
        const options = runs.map((run) => `<option value="${text(run.run_id)}">${text(run.run_id)} / ${text(run.as_of)}</option>`).join("");
        $("run").innerHTML = options;
        $("compare-left").innerHTML = options;
        $("compare-right").innerHTML = options;
        const preferred = runs.find((run) => run.run_id === "demo-financials-2025-01-01");
        currentRun = preferred ? preferred.run_id : runs[0].run_id;
        $("run").value = currentRun;
        $("compare-left").value = currentRun;
        $("compare-right").value = (runs.find((run) => run.run_id !== currentRun) || runs[0]).run_id;
        await loadRun();
        await compareRuns();
      } catch (error) { fail(error.message); }
    }
    async function loadRun() {
      currentRun = $("run").value || currentRun;
      const [run, facets] = await Promise.all([
        json(`${base}/runs/${encodeURIComponent(currentRun)}`),
        json(`${base}/runs/${encodeURIComponent(currentRun)}/facets`)
      ]);
      const method = run.methodology_version || "legacy / unstamped";
      const evidence = run.dataset_fingerprint ? run.dataset_fingerprint.slice(0, 12) : "legacy / unstamped";
      $("run-meta").textContent = `Calculated as of ${run.as_of} / Universe ${run.universe_id || "not supplied"} / Methodology ${method} / Evidence ${evidence} / Costs ${run.transaction_cost_bps_per_side} bps per side`;
      $("evaluated").textContent = run.evaluated_count;
      $("excluded").textContent = run.excluded_count;
      $("pending").textContent = run.pending_count;
      $("methodology").textContent = facets.methodology_version || "legacy";
      $("sample").value = run.minimum_sample;
      $("sector").innerHTML = '<option value="">All sectors</option>' + facets.sectors.map((sector) => `<option value="${text(sector)}">${text(sector)}</option>`).join("");
      await refresh();
    }
    async function refresh() {
      $("error").style.display = "none";
      const params = new URLSearchParams({minimum_sample: $("sample").value || "1"});
      if ($("sector").value) params.set("sector", $("sector").value);
      if ($("direction").value) params.set("direction", $("direction").value);
      $("export-ranking").href = `${base}/runs/${encodeURIComponent(currentRun)}/export/rankings-firms.csv?${params}`;
      $("export-evaluations").href = `${base}/runs/${encodeURIComponent(currentRun)}/export/evaluations.csv`;
      try {
        const [result, audit] = await Promise.all([
          json(`${base}/runs/${encodeURIComponent(currentRun)}/rankings/firms?${params}`),
          json(`${base}/runs/${encodeURIComponent(currentRun)}/audit/exclusions`)
        ]);
        renderRanking(result.ranking);
        resetDetail();
        renderAudit(audit);
      } catch (error) { fail(error.message); }
    }
    async function compareRuns() {
      try {
        const params = new URLSearchParams({
          left_run_id: $("compare-left").value,
          right_run_id: $("compare-right").value
        });
        const result = await json(`${base}/runs/compare?${params}`);
        const descriptions = {
          same_evidence_and_methodology: "Comparable: same evidence and methodology.",
          same_methodology_different_dataset: "Same methodology, different evidence dataset.",
          methodology_changed: "Methodology changed: compare results with caution."
        };
        const left = result.left, right = result.right, delta = result.deltas;
        $("compare-result").innerHTML = `<strong>${text(descriptions[result.comparability])}</strong> ${text(left.dataset_label || left.run_id)} to ${text(right.dataset_label || right.run_id)} / Method ${text(left.methodology_version || "unstamped")} to ${text(right.methodology_version || "unstamped")} / Evaluated delta ${delta.evaluated_count >= 0 ? "+" : ""}${delta.evaluated_count} / Excluded delta ${delta.excluded_count >= 0 ? "+" : ""}${delta.excluded_count}.`;
      } catch (error) { fail(error.message); }
    }
    function resetDetail() {
      $("detail").innerHTML = '<h3>Firm Detail</h3><p>Select a firm from the current ranking to inspect its evaluated and excluded observations.</p>';
    }
    function renderRanking(rows) {
      if (!rows.length) {
        $("ranking").innerHTML = '<tr><td colspan="6">No firm meets these filters and minimum sample.</td></tr>';
        return;
      }
      $("ranking").innerHTML = rows.map((row) => `<tr data-firm="${text(row.firm)}"><td><strong>${text(row.firm)}</strong></td><td>${row.observations}</td><td class="rate">${pct(row.hit_rate)}</td><td>${pct(row.hit_rate_ci_95_low)} to ${pct(row.hit_rate_ci_95_high)}</td><td>${text(row.median_days_to_hit)}</td><td>${signedPct(row.mean_net_strategy_excess_return_pct)}</td></tr>`).join("");
      document.querySelectorAll("tr[data-firm]").forEach((row) => row.addEventListener("click", () => showFirm(row.dataset.firm)));
    }
    async function showFirm(firm) {
      try {
        const data = await json(`${base}/runs/${encodeURIComponent(currentRun)}/firms/${encodeURIComponent(firm)}`);
        const summary = data.summary;
        const observations = data.observations.map((row) => `<tr data-ticker="${text(row.ticker)}"><td>${text(row.ticker)}<small>${text(row.observation_id)}</small></td><td><span class="pill ${row.status === "excluded" ? "excluded" : ""}">${text(row.status)}</span></td><td>${row.hit === null ? "-" : row.hit ? "Hit" : "Miss"}</td></tr>`).join("");
        $("detail").innerHTML = `<h3>${text(firm)}</h3>${summary ? `<section class="summary"><div class="metric"><small>Hit rate</small><strong>${pct(summary.hit_rate)}</strong></div><div class="metric"><small>Evaluated</small><strong>${summary.observations}</strong></div><div class="metric"><small>95% CI</small><strong>${pct(summary.hit_rate_ci_95_low)}</strong></div><div class="metric"><small>Net excess</small><strong>${signedPct(summary.mean_net_strategy_excess_return_pct)}</strong></div></section>` : "<p>No evaluated observations.</p>"}<table><thead><tr><th>Ticker</th><th>Status</th><th>Outcome</th></tr></thead><tbody>${observations}</tbody></table><p>Select a ticker row to review its observation evidence.</p>`;
        document.querySelectorAll("tr[data-ticker]").forEach((row) => row.addEventListener("click", () => showTicker(row.dataset.ticker)));
      } catch (error) { fail(error.message); }
    }
    async function showTicker(ticker) {
      try {
        const [data, timeline] = await Promise.all([
          json(`${base}/runs/${encodeURIComponent(currentRun)}/tickers/${encodeURIComponent(ticker)}`),
          json(`${base}/runs/${encodeURIComponent(currentRun)}/tickers/${encodeURIComponent(ticker)}/timeline`)
        ]);
        const rows = data.observations.map((row) => `<article class="metric"><small>${text(row.firm)} / ${text(row.published_date)}</small><strong>${text(row.status)}${row.hit === true ? " / hit" : row.hit === false ? " / miss" : ""}</strong><small>Target: ${text(row.price_target)} / Reason: ${text(row.reason)}</small><a href="${evidenceHref(row.source_url)}" target="_blank" rel="noopener">Evidence source</a></article>`).join("");
        $("detail").innerHTML = `<h3>${text(ticker)} Evidence</h3><p>${data.observations.length} observation(s) retained in this run.</p><section class="summary">${rows}</section><section class="timeline"><h3>Evaluation Evidence Timeline</h3>${renderTimeline(timeline)}</section>`;
      } catch (error) { fail(error.message); }
    }
    function renderTimeline(data) {
      const charts = data.observations.map((observation) => {
        const points = observation.points
          .filter((point) => Number.isFinite(Number(point.value)))
          .slice()
          .sort((left, right) => left.date.localeCompare(right.date));
        if (!points.length) {
          return `<article class="chart"><h4>${text(observation.firm)} / ${text(observation.observation_id)}</h4><p class="chart-note">No price milestones retained because this observation was not scored.</p></article>`;
        }
        const target = Number(observation.price_target);
        const values = points.map((point) => Number(point.value));
        if (Number.isFinite(target)) values.push(target);
        const lower = Math.min(...values);
        const upper = Math.max(...values);
        const spread = Math.max(upper - lower, Math.max(upper * .04, 1));
        const floor = lower - spread * .2;
        const ceiling = upper + spread * .2;
        const width = 315, height = 150, left = 46, right = 24, top = 13, bottom = 18;
        const plotWidth = width - left - right, plotHeight = height - top - bottom;
        const times = points.map((point) => Date.parse(`${point.date}T00:00:00Z`));
        const minimumTime = Math.min(...times), maximumTime = Math.max(...times);
        const elapsed = Math.max(maximumTime - minimumTime, 1);
        const x = (index) => left + (points.length === 1 ? plotWidth / 2 : plotWidth * (times[index] - minimumTime) / elapsed);
        const y = (value) => top + (ceiling - value) * plotHeight / (ceiling - floor);
        const polyline = points.map((point, index) => `${x(index).toFixed(1)},${y(Number(point.value)).toFixed(1)}`).join(" ");
        const targetLine = Number.isFinite(target) ? `<line x1="${left}" y1="${y(target).toFixed(1)}" x2="${width - right}" y2="${y(target).toFixed(1)}" stroke="#f0bc62" stroke-dasharray="4 4"/><text x="${left}" y="${(y(target) - 5).toFixed(1)}" fill="#f0bc62" font-size="10">target ${text(observation.price_target)}</text>` : "";
        const marks = points.map((point, index) => {
          const color = point.kind === "hit" ? "#f0bc62" : point.kind === "exit" ? "#62a6ff" : "#56daac";
          return `<circle cx="${x(index).toFixed(1)}" cy="${y(Number(point.value)).toFixed(1)}" r="4" fill="${color}"/>`;
        }).join("");
        const events = points.map((point) => `<span><strong>${text(point.date)}</strong> / ${text(point.label)}: ${text(point.value)}</span>`).join("");
        return `<article class="chart"><h4>${text(observation.firm)} / ${text(observation.observation_id)}</h4><svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Retained evaluation milestones for ${text(observation.observation_id)}"><line x1="${left}" y1="${top}" x2="${left}" y2="${height - bottom}" stroke="#20343d"/><line x1="${left}" y1="${height - bottom}" x2="${width - right}" y2="${height - bottom}" stroke="#20343d"/>${targetLine}<polyline points="${polyline}" fill="none" stroke="#56daac" stroke-width="2"/>${marks}</svg><div class="chart-events">${events}</div></article>`;
      }).join("");
      return `<p class="chart-note">${text(data.limitation)}</p>${charts}`;
    }
    function renderAudit(data) {
      const entries = Object.entries(data.counts_by_reason);
      $("reasons").innerHTML = `<h3>Reason Counts</h3>` + (entries.length ? entries.map(([reason,count]) => `<div class="reason"><span>${text(reason)}</span><strong>${count}</strong></div>`).join("") : "<p>No excluded or pending observations.</p>");
      $("audit").innerHTML = data.observations.length ? data.observations.map((row) => `<tr><td>${text(row.observation_id)}</td><td>${text(row.firm)}</td><td>${text(row.ticker)}</td><td><span class="pill excluded">${text(row.status)}</span></td><td>${text(row.reason)}</td><td><a href="${evidenceHref(row.source_url)}" target="_blank" rel="noopener">Source</a></td></tr>`).join("") : '<tr><td colspan="6">No excluded or pending observations.</td></tr>';
    }
    $("run").addEventListener("change", loadRun);
    $("apply").addEventListener("click", refresh);
    $("compare").addEventListener("click", compareRuns);
    initialize();
  </script>
</body>
</html>"""


def source_governance_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TargetAudit | Source Governance</title>
  <style>
    :root {
      --bg:#071016; --panel:#0f1c24; --panel2:#14242d; --line:#20343d;
      --text:#edf1ef; --muted:#98abb0; --mint:#56daac; --gold:#f0bc62;
      --blue:#62a6ff; --red:#ff7d72;
    }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--bg); color:var(--text); font:15px/1.5 Inter,Arial,sans-serif; }
    header,main { max-width:1240px; margin:auto; padding:30px 28px; }
    nav,.meta { color:var(--muted); text-transform:uppercase; letter-spacing:.08em; font-size:13px; }
    a { color:var(--mint); text-decoration:none; }
    h1 { font-size:clamp(38px,5vw,58px); line-height:1.05; margin:38px 0 14px; }
    h2 { margin:42px 0 16px; font-size:22px; }
    h3 { margin:0 0 12px; font-size:16px; }
    .lead { color:var(--muted); font-size:17px; max-width:850px; }
    .notice { background:var(--panel); border:1px solid var(--line); border-left:3px solid var(--gold);
      border-radius:14px; padding:15px 18px; color:var(--muted); margin:18px 0; }
    .cards { display:grid; grid-template-columns:repeat(5,1fr); gap:16px; margin:34px 0; }
    .card,.filters,.table-wrap,.detail { background:var(--panel); border:1px solid var(--line); border-radius:14px; }
    .card { padding:17px 20px; }
    .card p { color:var(--muted); margin:0; }
    .card strong { display:block; font-size:35px; color:var(--mint); margin-top:4px; }
    .card small { color:var(--muted); }
    .filters { padding:17px; display:grid; grid-template-columns:1.7fr 1.5fr auto; gap:12px; align-items:end; margin-bottom:18px; }
    label { display:block; color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.06em; margin-bottom:6px; }
    select { width:100%; height:43px; background:var(--panel2); color:var(--text); border:1px solid var(--line); border-radius:9px; padding:0 11px; }
    button { height:43px; border:0; border-radius:9px; color:#061117; background:var(--mint); padding:0 20px; font-weight:600; cursor:pointer; }
    .sources-layout { display:grid; grid-template-columns:minmax(680px,1fr) 335px; gap:18px; }
    .table-wrap { overflow:hidden; }
    table { width:100%; border-collapse:collapse; }
    th,td { padding:14px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }
    th { color:var(--muted); text-transform:uppercase; font-size:12px; font-weight:500; }
    td small { display:block; color:var(--muted); }
    tr[data-source] { cursor:pointer; }
    tr[data-source]:hover { background:var(--panel2); }
    .pill { display:inline-block; border-radius:999px; padding:4px 9px; font-size:12px; white-space:nowrap; }
    .usable_with_policy { color:var(--mint); background:rgba(86,218,172,.12); }
    .review_required,.manual_only { color:var(--gold); background:rgba(240,188,98,.12); }
    .license_required { color:var(--blue); background:rgba(98,166,255,.12); }
    .blocked { color:var(--red); background:rgba(255,125,114,.12); }
    .detail { padding:18px; min-height:300px; }
    .detail p { color:var(--muted); }
    .fact { background:var(--panel2); border-radius:9px; padding:10px; margin:9px 0; }
    .fact small { display:block; color:var(--muted); }
    .fact strong { font-size:14px; font-weight:500; word-break:break-word; }
    .audit-header { display:flex; align-items:end; justify-content:space-between; gap:16px; margin-top:38px; }
    .audit-header h2 { margin:0; }
    .audit-header select { width:360px; }
    #error { display:none; border-left-color:var(--red); color:var(--red); }
    @media(max-width:1000px) {
      .cards { grid-template-columns:repeat(2,1fr); }
      .filters,.sources-layout { grid-template-columns:1fr; }
      .audit-header { display:block; }
      .audit-header select { width:100%; margin-top:12px; }
      .table-wrap { overflow-x:auto; }
      table { min-width:700px; }
    }
  </style>
</head>
<body>
  <header>
    <nav><a href="/dashboard/open">Open Edition</a> / Governance / Sources / <a href="/dashboard/policy">Public Use Policy</a> / <a href="/dashboard/financials-evidence">Financials Evidence</a> / <a href="/dashboard/financials">Financials Scorecard</a> / <a href="/dashboard/release">Release Center</a> / <a href="/dashboard/readiness">Scorecard Readiness</a> / <a href="/dashboard/approvals">Provider Approvals</a> / <a href="/dashboard/operations">Operations Quality</a></nav>
    <h1>Open code.<br>Controlled data.</h1>
    <p class="lead">Publication rights are part of the evidence. This page separates sources already usable under documented policy from data that still requires terms, licensing or manual controls.</p>
    <p class="meta" id="reviewed">Loading source registry...</p>
    <section class="cards">
      <article class="card"><p>Providers</p><strong id="providers">-</strong><small>Tracked sources</small></article>
      <article class="card"><p>Implemented</p><strong id="implemented">-</strong><small>Technical adapters</small></article>
      <article class="card"><p>Reviews Open</p><strong id="open">-</strong><small>Terms or license</small></article>
      <article class="card"><p>Manual Only</p><strong id="manual">-</strong><small>No automated collection</small></article>
      <article class="card"><p>Blocked</p><strong id="blocked">-</strong><small>No collection</small></article>
    </section>
  </header>
  <main>
    <p class="notice">A public URL is not permission to republish data. Provider controls below govern collection and publication; newer run exclusions retain provider lineage while historical unlinked rows stay visibly unresolved.</p>
    <p id="error" class="notice"></p>
    <h2>Source Controls</h2>
    <section class="filters" aria-label="Source control filters">
      <div><label for="state">Deployment state</label><select id="state"><option value="">All states</option></select></div>
      <div><label for="data-class">Data class</label><select id="data-class"><option value="">All data classes</option></select></div>
      <button id="apply">Apply</button>
    </section>
    <section class="sources-layout">
      <div class="table-wrap">
        <table>
          <thead><tr><th>Provider</th><th>Integration</th><th>Deployment</th><th>Publication Policy</th></tr></thead>
          <tbody id="sources"><tr><td colspan="4">Loading providers...</td></tr></tbody>
        </table>
      </div>
      <aside id="source-detail" class="detail">
        <h3>Source Detail</h3>
        <p>Select a provider to inspect its review note and evidence references.</p>
      </aside>
    </section>
    <section class="audit-header">
      <div><h2>Run Exclusions And Pending</h2><p class="lead">Observations removed before ranking, with their retained source URL and exclusion reason.</p></div>
      <div><label for="run">Research run</label><select id="run"></select></div>
    </section>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Observation</th><th>Firm / Ticker</th><th>Status</th><th>Reason</th><th>Provider Control</th><th>Evidence</th></tr></thead>
        <tbody id="exclusions"><tr><td colspan="6">Loading exclusions...</td></tr></tbody>
      </table>
    </div>
  </main>
  <script>
    const $ = (id) => document.getElementById(id);
    const base = "/api/v1";
    let sourceById = {};
    function text(value) {
      return String(value == null || value === "" ? "-" : value)
        .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
    }
    function href(value) {
      try {
        const parsed = new URL(value);
        return parsed.protocol === "https:" || parsed.protocol === "http:" ? text(value) : "#";
      } catch (_) { return "#"; }
    }
    async function json(url) {
      const response = await fetch(url);
      if (!response.ok) throw new Error((await response.json()).detail || "Request failed");
      return response.json();
    }
    function fail(message) {
      $("error").style.display = "block";
      $("error").textContent = message;
    }
    async function initialize() {
      try {
        const [sources, runs] = await Promise.all([json(`${base}/governance/sources`), json(`${base}/runs`)]);
        sourceById = Object.fromEntries(sources.sources.map((source) => [source.provider_id, source]));
        $("reviewed").textContent = `Source registry reviewed as of ${sources.reviewed_as_of}`;
        $("providers").textContent = sources.provider_count;
        $("implemented").textContent = sources.implemented_count;
        $("open").textContent = sources.open_review_count;
        $("manual").textContent = sources.manual_only_count;
        $("blocked").textContent = sources.blocked_count;
        $("state").innerHTML += sources.deployment_states.map((state) => `<option value="${text(state)}">${text(state)}</option>`).join("");
        $("data-class").innerHTML += sources.data_classes.map((dataClass) => `<option value="${text(dataClass)}">${text(dataClass)}</option>`).join("");
        $("run").innerHTML = runs.map((run) => `<option value="${text(run.run_id)}">${text(run.run_id)} / ${text(run.as_of)}</option>`).join("");
        const excludedRun = runs.find((run) => run.excluded_count > 0);
        if (excludedRun) $("run").value = excludedRun.run_id;
        renderSources(sources.sources);
        await loadExclusions();
      } catch (error) { fail(error.message); }
    }
    async function filterSources() {
      const params = new URLSearchParams();
      if ($("state").value) params.set("deployment_state", $("state").value);
      if ($("data-class").value) params.set("data_class", $("data-class").value);
      try {
        const data = await json(`${base}/governance/sources?${params}`);
        renderSources(data.sources);
        resetSourceDetail();
      } catch (error) { fail(error.message); }
    }
    function renderSources(rows) {
      if (!rows.length) {
        $("sources").innerHTML = '<tr><td colspan="4">No source matches these controls.</td></tr>';
        return;
      }
      $("sources").innerHTML = rows.map((row) => `<tr data-source="${text(row.provider_id)}"><td><strong>${text(row.provider_name)}</strong><small>${text(row.data_class)}</small></td><td>${text(row.integration_status)}<small>${text(row.access_model)}</small></td><td><span class="pill ${text(row.deployment_state)}">${text(row.deployment_state)}</span></td><td><small>${text(row.publication_policy)}</small></td></tr>`).join("");
      document.querySelectorAll("tr[data-source]").forEach((row) => {
        const source = rows.find((item) => item.provider_id === row.dataset.source);
        row.addEventListener("click", () => showSource(source));
      });
    }
    function resetSourceDetail() {
      $("source-detail").innerHTML = '<h3>Source Detail</h3><p>Select a provider to inspect its review note and evidence references.</p>';
    }
    function showSource(source) {
      $("source-detail").innerHTML = `<h3>${text(source.provider_name)}</h3><span class="pill ${text(source.deployment_state)}">${text(source.deployment_state)}</span><div class="fact"><small>License status</small><strong>${text(source.license_status)}</strong></div><div class="fact"><small>Publication policy</small><strong>${text(source.publication_policy)}</strong></div><div class="fact"><small>Reviewed</small><strong>${text(source.reviewed_on)}</strong></div><p>${text(source.review_note)}</p><p><a href="${href(source.official_url)}" target="_blank" rel="noopener">Official source</a><br><a href="${href(source.reference_url)}" target="_blank" rel="noopener">Terms / reference</a></p>`;
    }
    async function loadExclusions() {
      if (!$("run").value) {
        $("exclusions").innerHTML = '<tr><td colspan="6">No evaluation runs stored.</td></tr>';
        return;
      }
      try {
        const audit = await json(`${base}/runs/${encodeURIComponent($("run").value)}/audit/exclusions`);
        $("exclusions").innerHTML = audit.observations.length ? audit.observations.map((row) => {
          const provider = sourceById[row.provider_id];
          const control = provider ? `<strong>${text(provider.provider_name)}</strong><small><span class="pill ${text(provider.deployment_state)}">${text(provider.deployment_state)}</span></small>` : `<span class="pill review_required">unlinked</span><small>${text(row.provider_id || "missing provider_id")}</small>`;
          return `<tr><td>${text(row.observation_id)}</td><td><strong>${text(row.firm)}</strong><small>${text(row.ticker)}</small></td><td><span class="pill review_required">${text(row.status)}</span></td><td>${text(row.reason)}</td><td>${control}</td><td><a href="${href(row.source_url)}" target="_blank" rel="noopener">Source</a></td></tr>`;
        }).join("") : '<tr><td colspan="6">No excluded or pending observations in this run.</td></tr>';
      } catch (error) { fail(error.message); }
    }
    $("apply").addEventListener("click", filterSources);
    $("run").addEventListener("change", loadExclusions);
    initialize();
  </script>
</body>
</html>"""


def operations_quality_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TargetAudit | Operations Quality</title>
  <style>
    :root {
      --bg:#071016; --panel:#0f1c24; --panel2:#14242d; --line:#20343d;
      --text:#edf1ef; --muted:#98abb0; --mint:#56daac; --gold:#f0bc62;
      --red:#ff7d72;
    }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--bg); color:var(--text); font:15px/1.5 Inter,Arial,sans-serif; }
    header,main { max-width:1240px; margin:auto; padding:30px 28px; }
    nav,.meta { color:var(--muted); text-transform:uppercase; letter-spacing:.08em; font-size:13px; }
    a { color:var(--mint); text-decoration:none; }
    h1 { font-size:clamp(38px,5vw,58px); line-height:1.05; margin:38px 0 14px; }
    h2 { margin:42px 0 16px; font-size:22px; }
    h3 { margin:0 0 12px; font-size:16px; }
    .lead { color:var(--muted); font-size:17px; max-width:860px; }
    .notice { background:var(--panel); border:1px solid var(--line); border-left:3px solid var(--gold);
      border-radius:14px; padding:15px 18px; color:var(--muted); margin:18px 0; }
    .cards { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin:34px 0; }
    .card,.controls,.table-wrap,.detail { background:var(--panel); border:1px solid var(--line); border-radius:14px; }
    .card { padding:17px 20px; }
    .card p { color:var(--muted); margin:0; }
    .card strong { display:block; font-size:35px; color:var(--mint); margin-top:4px; }
    .card small { color:var(--muted); }
    .controls { padding:17px; display:grid; grid-template-columns:260px 260px auto; gap:12px; align-items:end; margin-bottom:18px; }
    label { display:block; color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.06em; margin-bottom:6px; }
    input { width:100%; height:43px; background:var(--panel2); color:var(--text); border:1px solid var(--line); border-radius:9px; padding:0 11px; }
    .toggle { height:43px; display:flex; align-items:center; gap:10px; margin:0; padding:0 12px; background:var(--panel2); border:1px solid var(--line); border-radius:9px; color:var(--text); }
    .toggle input { width:auto; height:auto; padding:0; margin:0; }
    button { height:43px; border:0; border-radius:9px; color:#061117; background:var(--mint); padding:0 20px; font-weight:600; cursor:pointer; }
    .layout { display:grid; grid-template-columns:minmax(680px,1fr) 335px; gap:18px; }
    .table-wrap { overflow:hidden; }
    table { width:100%; border-collapse:collapse; }
    th,td { padding:14px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }
    th { color:var(--muted); text-transform:uppercase; font-size:12px; font-weight:500; }
    td small { display:block; color:var(--muted); }
    tr[data-run] { cursor:pointer; }
    tr[data-run]:hover { background:var(--panel2); }
    .pill { display:inline-block; border-radius:999px; padding:4px 9px; font-size:12px; white-space:nowrap; }
    .quality_pass { color:var(--mint); background:rgba(86,218,172,.12); }
    .review_required { color:var(--gold); background:rgba(240,188,98,.12); }
    .blocked { color:var(--red); background:rgba(255,125,114,.12); }
    .detail { padding:18px; min-height:280px; }
    .detail p { color:var(--muted); }
    .finding { padding:10px; margin:9px 0; border-radius:9px; background:var(--panel2); }
    .finding strong { display:block; font-size:12px; color:var(--gold); }
    #error { display:none; border-left-color:var(--red); color:var(--red); }
    @media(max-width:1000px) {
      .cards { grid-template-columns:repeat(2,1fr); }
      .controls,.layout { grid-template-columns:1fr; }
      .table-wrap { overflow-x:auto; }
      table { min-width:720px; }
    }
  </style>
</head>
<body>
  <header>
    <nav><a href="/dashboard/open">Open Edition</a> / Operations / Quality / <a href="/dashboard/financials-evidence">Financials Evidence</a> / <a href="/dashboard/financials">Financials Scorecard</a> / <a href="/dashboard/release">Release Center</a> / <a href="/dashboard/readiness">Scorecard Readiness</a> / <a href="/dashboard/approvals">Provider Approvals</a> / <a href="/dashboard/governance">Source Governance</a></nav>
    <h1>Ship evidence,<br>not surprises.</h1>
    <p class="lead">Operational quality gates for stored evaluation runs: reproducibility stamps, required inputs, provider lineage and anomalous exclusion rates.</p>
    <p class="meta" id="scope">Refreshable quality view over stored evaluation runs</p>
    <section class="cards">
      <article class="card"><p>Runs</p><strong id="runs">-</strong><small>Stored evaluations</small></article>
      <article class="card"><p>Quality Pass</p><strong id="pass">-</strong><small>Still subject to licensing</small></article>
      <article class="card"><p>Review</p><strong id="review">-</strong><small>Needs operator attention</small></article>
      <article class="card"><p>Blocked</p><strong id="blocked">-</strong><small>Do not release</small></article>
    </section>
  </header>
  <main>
    <p class="notice" id="publication-note">Operational quality passing does not grant data publication rights; source-governance approval is still required.</p>
    <p id="error" class="notice"></p>
    <h2>Run Quality Monitor</h2>
    <section class="controls" aria-label="Quality controls">
      <div><label for="threshold">Maximum excluded rate</label><input id="threshold" type="number" min="0" max="1" step="0.05" value="0.50"></div>
      <label class="toggle"><input id="public-release" type="checkbox"> Public release inputs</label>
      <button id="apply">Apply Quality Gate</button>
    </section>
    <section class="layout">
      <div class="table-wrap">
        <table>
          <thead><tr><th>Run</th><th>Status</th><th>Evaluated</th><th>Excluded</th><th>Unlinked</th></tr></thead>
          <tbody id="quality"><tr><td colspan="5">Loading quality monitor...</td></tr></tbody>
        </table>
      </div>
      <aside id="detail" class="detail">
        <h3>Quality Findings</h3>
        <p>Select a run to inspect why it passed, requires review or is blocked.</p>
      </aside>
    </section>
  </main>
  <script>
    const $ = (id) => document.getElementById(id);
    const base = "/api/v1";
    let currentRows = [];
    function text(value) {
      return String(value == null || value === "" ? "-" : value)
        .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
    }
    function pct(value) { return (Number(value) * 100).toFixed(2) + "%"; }
    async function json(url) {
      const response = await fetch(url);
      if (!response.ok) throw new Error((await response.json()).detail || "Request failed");
      return response.json();
    }
    function fail(message) {
      $("error").style.display = "block";
      $("error").textContent = message;
    }
    async function refresh() {
      $("error").style.display = "none";
      try {
        const threshold = $("threshold").value || "0.50";
        const release = $("public-release").checked ? "&public_release=true" : "";
        const data = await json(`${base}/operations/quality?maximum_excluded_rate=${encodeURIComponent(threshold)}${release}`);
        currentRows = data.runs;
        $("runs").textContent = data.run_count;
        $("pass").textContent = data.quality_pass_count;
        $("review").textContent = data.review_required_count;
        $("blocked").textContent = data.blocked_count;
        $("publication-note").textContent = data.publication_note;
        $("scope").textContent = `Scope ${data.quality_scope} / Required inputs: ${data.required_input_roles.join(", ")}`;
        renderRows(data.runs);
      } catch (error) { fail(error.message); }
    }
    function renderRows(rows) {
      if (!rows.length) {
        $("quality").innerHTML = '<tr><td colspan="5">No stored evaluation runs are available.</td></tr>';
        return;
      }
      $("quality").innerHTML = rows.map((row) => `<tr data-run="${text(row.run_id)}"><td><strong>${text(row.run_id)}</strong><small>${text(row.dataset_label || "unstamped")}</small></td><td><span class="pill ${text(row.quality_status)}">${text(row.quality_status)}</span></td><td>${row.evaluated_count} / ${row.observation_count}</td><td>${pct(row.excluded_rate)}</td><td>${row.unlinked_observation_count}</td></tr>`).join("");
      document.querySelectorAll("tr[data-run]").forEach((row) => row.addEventListener("click", () => showRun(row.dataset.run)));
      showRun(rows[0].run_id);
    }
    function showRun(runId) {
      const run = currentRows.find((item) => item.run_id === runId);
      const findings = run.findings.length ? run.findings.map((finding) => `<div class="finding"><strong>${text(finding.severity)} / ${text(finding.code)}</strong>${text(finding.message)}</div>`).join("") : "<p>No operational quality findings in this run.</p>";
      $("detail").innerHTML = `<h3>${text(run.run_id)}</h3><p>Methodology ${text(run.methodology_version || "unstamped")} / Evidence ${text(run.dataset_fingerprint ? run.dataset_fingerprint.slice(0, 12) : "unstamped")}</p>${findings}`;
    }
    $("apply").addEventListener("click", refresh);
    refresh();
  </script>
</body>
</html>"""


def scorecard_readiness_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TargetAudit | Scorecard Readiness</title>
  <style>
    :root {
      --bg:#071016; --panel:#0f1c24; --panel2:#14242d; --line:#20343d;
      --text:#edf1ef; --muted:#98abb0; --mint:#56daac; --gold:#f0bc62;
      --blue:#62a6ff; --red:#ff7d72;
    }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--bg); color:var(--text); font:15px/1.5 Inter,Arial,sans-serif; }
    header,main { max-width:1240px; margin:auto; padding:30px 28px; }
    nav,.meta { color:var(--muted); text-transform:uppercase; letter-spacing:.08em; font-size:13px; }
    a { color:var(--mint); text-decoration:none; }
    h1 { font-size:clamp(38px,5vw,58px); line-height:1.05; margin:38px 0 14px; }
    h2 { margin:42px 0 16px; font-size:22px; }
    h3 { margin:0 0 12px; font-size:16px; }
    .lead { color:var(--muted); font-size:17px; max-width:880px; }
    .notice { background:var(--panel); border:1px solid var(--line); border-left:3px solid var(--gold);
      border-radius:14px; padding:15px 18px; color:var(--muted); margin:18px 0; }
    .cards { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin:34px 0; }
    .card,.table-wrap,.detail { background:var(--panel); border:1px solid var(--line); border-radius:14px; }
    .card { padding:17px 20px; }
    .card p { color:var(--muted); margin:0; }
    .card strong { display:block; font-size:35px; color:var(--mint); margin-top:4px; }
    .card strong.no { color:var(--red); }
    .card small { color:var(--muted); }
    .layout { display:grid; grid-template-columns:minmax(650px,1fr) 370px; gap:18px; }
    .table-wrap { overflow:hidden; }
    table { width:100%; border-collapse:collapse; }
    th,td { padding:14px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }
    th { color:var(--muted); text-transform:uppercase; font-size:12px; font-weight:500; }
    td small { display:block; color:var(--muted); }
    tr[data-control] { cursor:pointer; }
    tr[data-control]:hover { background:var(--panel2); }
    .pill { display:inline-block; border-radius:999px; padding:4px 9px; font-size:12px; white-space:nowrap; }
    .public_ready { color:var(--mint); background:rgba(86,218,172,.12); }
    .internal_only { color:var(--blue); background:rgba(98,166,255,.12); }
    .integration_pending,.missing_source { color:var(--gold); background:rgba(240,188,98,.12); }
    .usable_with_policy { color:var(--mint); }
    .license_required,.review_required { color:var(--gold); }
    .detail { padding:18px; min-height:320px; }
    .detail p { color:var(--muted); }
    .provider { background:var(--panel2); border-radius:9px; padding:10px; margin:9px 0; }
    .provider small { display:block; color:var(--muted); }
    #error { display:none; border-left-color:var(--red); color:var(--red); }
    @media(max-width:1000px) {
      .cards { grid-template-columns:repeat(2,1fr); }
      .layout { grid-template-columns:1fr; }
      .table-wrap { overflow-x:auto; }
      table { min-width:650px; }
    }
  </style>
</head>
<body>
  <header>
    <nav><a href="/dashboard/open">Open Edition</a> / U.S. Financials / Readiness / <a href="/dashboard/financials-evidence">Evidence Center</a> / <a href="/dashboard/financials">Financials Scorecard</a> / <a href="/dashboard/release">Release Center</a> / <a href="/dashboard/approvals">Provider Approvals</a> / <a href="/dashboard/governance">Source Governance</a> / <a href="/dashboard/operations">Operations Quality</a></nav>
    <h1>Earn the right<br>to publish.</h1>
    <p class="lead">Readiness for a real public Financials scorecard. Demo fixtures can test the system; only approved production sources can enable release.</p>
    <p class="meta" id="reviewed">Loading readiness controls...</p>
    <section class="cards">
      <article class="card"><p>Required controls</p><strong id="requirements">-</strong><small>Targets, prices, events, universe</small></article>
      <article class="card"><p>Public ready</p><strong id="public-ready">-</strong><small>Approved controls</small></article>
      <article class="card"><p>Internal only</p><strong id="internal-only">-</strong><small>Not publishable</small></article>
      <article class="card"><p>Release enabled</p><strong id="release" class="no">-</strong><small>Public scorecard</small></article>
    </section>
  </header>
  <main>
    <p class="notice" id="publication-note">Loading publication control...</p>
    <p id="error" class="notice"></p>
    <h2>Release Requirements</h2>
    <section class="layout">
      <div class="table-wrap">
        <table>
          <thead><tr><th>Control</th><th>Status</th><th>Production Sources</th><th>Blocking Reason</th></tr></thead>
          <tbody id="controls"><tr><td colspan="4">Loading requirements...</td></tr></tbody>
        </table>
      </div>
      <aside id="detail" class="detail">
        <h3>Provider Candidates</h3>
        <p>Select a control to inspect candidates, policy state and whether it belongs only to the demo.</p>
      </aside>
    </section>
  </main>
  <script>
    const $ = (id) => document.getElementById(id);
    let controls = [];
    function text(value) {
      return String(value == null || value === "" ? "-" : value)
        .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
    }
    function href(value) {
      try {
        const parsed = new URL(value);
        return parsed.protocol === "https:" || parsed.protocol === "http:" ? text(value) : "#";
      } catch (_) { return "#"; }
    }
    async function json(url) {
      const response = await fetch(url);
      if (!response.ok) throw new Error((await response.json()).detail || "Request failed");
      return response.json();
    }
    function fail(message) {
      $("error").style.display = "block";
      $("error").textContent = message;
    }
    async function initialize() {
      try {
        const data = await json("/api/v1/readiness/scorecard");
        controls = data.requirements;
        $("reviewed").textContent = `${data.market_focus} / source controls reviewed as of ${data.as_of}`;
        $("requirements").textContent = data.requirement_count;
        $("public-ready").textContent = data.public_ready_count;
        $("internal-only").textContent = data.internal_only_count;
        $("release").textContent = data.public_release_ready ? "Yes" : "No";
        $("release").className = data.public_release_ready ? "" : "no";
        $("publication-note").textContent = data.publication_note;
        $("controls").innerHTML = controls.map((item) => `<tr data-control="${text(item.key)}"><td><strong>${text(item.label)}</strong><small>${text(item.purpose)}</small></td><td><span class="pill ${text(item.status)}">${text(item.status)}</span></td><td>${item.production_provider_count}</td><td>${text(item.blocker || "Ready under approved policy.")}</td></tr>`).join("");
        document.querySelectorAll("tr[data-control]").forEach((row) => row.addEventListener("click", () => showControl(row.dataset.control)));
        showControl(controls[0].key);
      } catch (error) { fail(error.message); }
    }
    function showControl(key) {
      const item = controls.find((control) => control.key === key);
      const providers = item.providers.length ? item.providers.map((provider) => `<div class="provider"><strong>${text(provider.provider_name)}</strong><small>${text(provider.provider_id)} / <span class="${text(provider.deployment_state)}">${text(provider.deployment_state)}</span> / ${provider.production_eligible ? "production candidate" : "demo only"}</small><p>${text(provider.review_note)}</p><a href="${href(provider.official_url)}" target="_blank" rel="noopener">Source</a></div>`).join("") : "<p>No provider is registered for this control.</p>";
      $("detail").innerHTML = `<h3>${text(item.label)}</h3><p>${text(item.blocker || "Approved source is available under documented policy.")}</p>${providers}`;
    }
    initialize();
  </script>
</body>
</html>"""


def release_center_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TargetAudit | Release Center</title>
  <style>
    :root {
      --bg:#071016; --panel:#0f1c24; --panel2:#14242d; --line:#20343d;
      --text:#edf1ef; --muted:#98abb0; --mint:#56daac; --gold:#f0bc62;
      --blue:#62a6ff; --red:#ff7d72;
    }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--bg); color:var(--text); font:15px/1.5 Inter,Arial,sans-serif; }
    header,main { max-width:1240px; margin:auto; padding:30px 28px; }
    nav,.meta { color:var(--muted); text-transform:uppercase; letter-spacing:.08em; font-size:13px; }
    a { color:var(--mint); text-decoration:none; }
    h1 { font-size:clamp(38px,5vw,58px); line-height:1.05; margin:38px 0 14px; }
    h2 { margin:40px 0 16px; font-size:22px; }
    .lead { color:var(--muted); font-size:17px; max-width:890px; }
    .notice { background:var(--panel); border:1px solid var(--line); border-left:3px solid var(--gold);
      border-radius:14px; padding:15px 18px; color:var(--muted); margin:18px 0; }
    .cards { display:grid; grid-template-columns:repeat(5,1fr); gap:16px; margin:34px 0; }
    .card,.controls,.panel,.table-wrap { background:var(--panel); border:1px solid var(--line); border-radius:14px; }
    .card { padding:17px 20px; }
    .card p { color:var(--muted); margin:0; }
    .card strong { display:block; font-size:31px; color:var(--mint); margin-top:4px; text-transform:uppercase; }
    .card strong.blocked { color:var(--red); }
    .controls { padding:17px; display:grid; grid-template-columns:2fr 1fr auto; gap:12px; align-items:end; }
    label { display:block; color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.06em; margin-bottom:6px; }
    select,input { width:100%; height:43px; background:var(--panel2); color:var(--text); border:1px solid var(--line); border-radius:9px; padding:0 11px; }
    button { height:43px; border:0; border-radius:9px; color:#061117; background:var(--mint); padding:0 20px; font-weight:600; cursor:pointer; }
    .layout { display:grid; grid-template-columns:minmax(620px,1fr) 370px; gap:18px; }
    .table-wrap { overflow:hidden; }
    table { width:100%; border-collapse:collapse; }
    th,td { padding:14px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }
    th { color:var(--muted); text-transform:uppercase; font-size:12px; font-weight:500; }
    td small { display:block; color:var(--muted); }
    .pill { display:inline-block; border-radius:999px; padding:4px 9px; font-size:12px; white-space:nowrap; }
    .public_ready { color:var(--mint); background:rgba(86,218,172,.12); }
    .internal_only { color:var(--blue); background:rgba(98,166,255,.12); }
    .integration_pending,.missing_source { color:var(--gold); background:rgba(240,188,98,.12); }
    .panel { padding:18px; min-height:300px; }
    .panel p,.panel li { color:var(--muted); }
    .panel ul { padding-left:18px; }
    .evidence { background:var(--panel2); border-radius:9px; padding:10px; margin-top:15px; }
    .evidence small { display:block; color:var(--muted); }
    #error { display:none; border-left-color:var(--red); color:var(--red); }
    @media(max-width:1000px) {
      .cards,.controls,.layout { grid-template-columns:1fr; }
      .table-wrap { overflow-x:auto; }
      table { min-width:640px; }
    }
  </style>
</head>
<body>
  <header>
    <nav><a href="/dashboard/open">Open Edition</a> / U.S. Financials / Release Center / <a href="/dashboard/financials-evidence">Evidence Center</a> / <a href="/dashboard/financials">Scorecard</a> / <a href="/dashboard/readiness">Readiness</a> / <a href="/dashboard/approvals">Provider Approvals</a> / <a href="/dashboard/operations">Operations Quality</a> / <a href="/dashboard/governance">Governance</a></nav>
    <h1>Release only<br>what is defensible.</h1>
    <p class="lead">One publication decision for one candidate run. Approved source rights and complete run evidence must both pass before a real scorecard can be released.</p>
    <p class="meta" id="reviewed">Select a candidate run to review...</p>
    <section class="cards">
      <article class="card"><p>Release decision</p><strong id="release" class="blocked">-</strong></article>
      <article class="card"><p>Source rights</p><strong id="source" class="blocked">-</strong></article>
      <article class="card"><p>Target lineage</p><strong id="lineage" class="blocked">-</strong></article>
      <article class="card"><p>Asset lineage</p><strong id="asset-lineage" class="blocked">-</strong></article>
      <article class="card"><p>Run quality</p><strong id="quality" class="blocked">-</strong></article>
    </section>
  </header>
  <main>
    <p class="notice" id="publication-note">A release decision needs a stored candidate run.</p>
    <p id="error" class="notice"></p>
    <section class="controls" aria-label="Release decision controls">
      <div><label for="run">Candidate run</label><select id="run"></select></div>
      <div><label for="threshold">Maximum excluded rate</label><input id="threshold" type="number" min="0" max="1" step="0.05" value="0.50"></div>
      <button id="apply">Evaluate Release</button>
    </section>
    <section class="layout">
      <div>
        <h2>Required Source Controls</h2>
        <div class="table-wrap">
          <table><thead><tr><th>Control</th><th>Status</th><th>Blocking Reason</th></tr></thead>
            <tbody id="controls"><tr><td colspan="3">Loading candidate decision...</td></tr></tbody>
          </table>
        </div>
      </div>
      <aside class="panel">
        <h2>Decision Blockers</h2>
        <ul id="blockers"><li>Select a candidate run.</li></ul>
        <div id="evidence" class="evidence"><small>Candidate evidence</small>-</div>
      </aside>
    </section>
  </main>
  <script>
    const $ = (id) => document.getElementById(id);
    function text(value) {
      return String(value == null || value === "" ? "-" : value)
        .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
    }
    async function json(url) {
      const response = await fetch(url);
      if (!response.ok) throw new Error((await response.json()).detail || "Request failed");
      return response.json();
    }
    function fail(message) {
      $("error").style.display = "block";
      $("error").textContent = message;
    }
    function state(id, value, passed) {
      $(id).textContent = value;
      $(id).className = passed ? "" : "blocked";
    }
    async function refresh() {
      $("error").style.display = "none";
      const runId = $("run").value;
      if (!runId) return;
      try {
        const threshold = $("threshold").value || "0.50";
        const data = await json(`/api/v1/releases/scorecard?run_id=${encodeURIComponent(runId)}&maximum_excluded_rate=${encodeURIComponent(threshold)}`);
        state("release", data.release_status, data.release_ready);
        state("source", data.source_gate_status, data.source_gate_status === "pass");
        state("lineage", data.lineage_gate_status, data.lineage_gate_status === "pass");
        state("asset-lineage", data.asset_lineage_gate_status, data.asset_lineage_gate_status === "pass");
        state("quality", data.quality_gate_status, data.quality_gate_status === "pass");
        $("reviewed").textContent = `${data.market_focus} / Candidate ${data.run_id} / Reviewed as of ${data.as_of}`;
        $("publication-note").textContent = data.publication_note;
        $("blockers").innerHTML = data.blockers.length ? data.blockers.map((item) => `<li>${text(item)}</li>`).join("") : "<li>No release blockers remain.</li>";
        $("controls").innerHTML = data.readiness.requirements.map((item) => `<tr><td><strong>${text(item.label)}</strong></td><td><span class="pill ${text(item.status)}">${text(item.status)}</span></td><td>${text(item.blocker || "Ready under approved policy.")}</td></tr>`).join("");
        const run = data.candidate_run;
        const assets = data.asset_lineage.map((item) => `${item.role}: ${item.provider_id || "unlinked"} / ${item.status}`).join("<br>");
        $("evidence").innerHTML = `<small>Candidate evidence</small><strong>${text(run.dataset_label)}</strong><p>Methodology ${text(run.methodology_version)} / Assets: ${text(run.asset_roles.join(", "))}</p><p>Target lineage: ${text(data.candidate_provider_ids.join(", "))}</p><p>${assets}</p><p>Evaluated ${run.evaluated_count} / Excluded ${(run.excluded_rate * 100).toFixed(2)}%</p>`;
      } catch (error) { fail(error.message); }
    }
    async function initialize() {
      try {
        const runs = await json("/api/v1/runs");
        $("run").innerHTML = runs.map((run) => `<option value="${text(run.run_id)}">${text(run.run_id)} / ${text(run.dataset_label)}</option>`).join("");
        await refresh();
      } catch (error) { fail(error.message); }
    }
    $("apply").addEventListener("click", refresh);
    $("run").addEventListener("change", refresh);
    initialize();
  </script>
</body>
</html>"""


def provider_approvals_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TargetAudit | Provider Approvals</title>
  <style>
    :root {
      --bg:#071016; --panel:#0f1c24; --panel2:#14242d; --line:#20343d;
      --text:#edf1ef; --muted:#98abb0; --mint:#56daac; --gold:#f0bc62;
      --blue:#62a6ff; --red:#ff7d72;
    }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--bg); color:var(--text); font:15px/1.5 Inter,Arial,sans-serif; }
    header,main { max-width:1240px; margin:auto; padding:30px 28px; }
    nav,.meta { color:var(--muted); text-transform:uppercase; letter-spacing:.08em; font-size:13px; }
    a { color:var(--mint); text-decoration:none; }
    h1 { font-size:clamp(38px,5vw,58px); line-height:1.05; margin:38px 0 14px; }
    h2 { margin:42px 0 16px; font-size:22px; }
    h3 { margin:0 0 12px; font-size:16px; }
    .lead { color:var(--muted); font-size:17px; max-width:900px; }
    .notice { background:var(--panel); border:1px solid var(--line); border-left:3px solid var(--gold);
      border-radius:14px; padding:15px 18px; color:var(--muted); margin:18px 0; }
    .cards { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin:34px 0; }
    .card,.table-wrap,.detail { background:var(--panel); border:1px solid var(--line); border-radius:14px; }
    .card { padding:17px 20px; }
    .card p { color:var(--muted); margin:0; }
    .card strong { display:block; font-size:35px; color:var(--mint); margin-top:4px; }
    .card strong.no { color:var(--red); }
    .card small { color:var(--muted); }
    .controls-table { margin-bottom:32px; overflow:hidden; }
    .layout { display:grid; grid-template-columns:minmax(650px,1fr) 390px; gap:18px; }
    .table-wrap { overflow:hidden; }
    table { width:100%; border-collapse:collapse; }
    th,td { padding:14px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }
    th { color:var(--muted); text-transform:uppercase; font-size:12px; font-weight:500; }
    td small { display:block; color:var(--muted); }
    tr[data-provider] { cursor:pointer; }
    tr[data-provider]:hover { background:var(--panel2); }
    .pill { display:inline-block; border-radius:999px; padding:4px 9px; font-size:12px; white-space:nowrap; }
    .critical,.rejected_public_output { color:var(--red); background:rgba(255,125,114,.12); }
    .high,.pending_terms_review,.pending_license_quote,.pending_written_permission,.pending_approval,.missing_queue_record {
      color:var(--gold); background:rgba(240,188,98,.12);
    }
    .normal { color:var(--blue); background:rgba(98,166,255,.12); }
    .approved,.approved_public_output { color:var(--mint); background:rgba(86,218,172,.12); }
    .detail { padding:18px; min-height:355px; }
    .detail p { color:var(--muted); }
    .fact { background:var(--panel2); border-radius:9px; padding:11px; margin:10px 0; }
    .fact small { display:block; color:var(--muted); text-transform:uppercase; letter-spacing:.05em; margin-bottom:4px; }
    #error { display:none; border-left-color:var(--red); color:var(--red); }
    @media(max-width:1000px) {
      .cards,.layout { grid-template-columns:1fr; }
      .table-wrap { overflow-x:auto; }
      table { min-width:650px; }
    }
  </style>
</head>
<body>
  <header>
    <nav><a href="/dashboard/open">Open Edition</a> / Governance / Provider Approvals / <a href="/dashboard/financials-evidence">Financials Evidence</a> / <a href="/dashboard/financials">Financials Scorecard</a> / <a href="/dashboard/release">Release Center</a> / <a href="/dashboard/readiness">Readiness</a> / <a href="/dashboard/governance">Sources</a></nav>
    <h1>Permission before<br>production data.</h1>
    <p class="lead">A documented review queue for providers that could unlock the public U.S. Financials scorecard. Technical access never stands in for publishing rights.</p>
    <p class="meta" id="reviewed">Loading approval work queue...</p>
    <section class="cards">
      <article class="card"><p>Tracked</p><strong id="tracked">-</strong><small>Provider dossiers</small></article>
      <article class="card"><p>Critical open</p><strong id="critical">-</strong><small>Required controls blocked</small></article>
      <article class="card"><p>Approved</p><strong id="approved">-</strong><small>Public output permission</small></article>
      <article class="card"><p>Activation ready</p><strong id="activation" class="no">-</strong><small>All controls licensed</small></article>
    </section>
  </header>
  <main>
    <p class="notice" id="publication-note">Loading publication control...</p>
    <p id="error" class="notice"></p>
    <h2>Scorecard Controls</h2>
    <div class="table-wrap controls-table">
      <table>
        <thead><tr><th>Required Control</th><th>Status</th><th>Candidates</th><th>Blocker</th></tr></thead>
        <tbody id="controls"><tr><td colspan="4">Loading required controls...</td></tr></tbody>
      </table>
    </div>
    <h2>Approval Work Queue</h2>
    <section class="layout">
      <div class="table-wrap">
        <table>
          <thead><tr><th>Priority</th><th>Provider</th><th>Approval Status</th><th>Evidence Needed</th></tr></thead>
          <tbody id="queue"><tr><td colspan="4">Loading provider dossiers...</td></tr></tbody>
        </table>
      </div>
      <aside id="detail" class="detail">
        <h3>Provider Dossier</h3>
        <p>Select a provider to inspect its requested use and the evidence required for promotion.</p>
      </aside>
    </section>
  </main>
  <script>
    const $ = (id) => document.getElementById(id);
    let providers = [];
    function text(value) {
      return String(value == null || value === "" ? "-" : value)
        .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
    }
    function href(value) {
      try {
        const parsed = new URL(value);
        return parsed.protocol === "https:" ? text(value) : "#";
      } catch (_) { return "#"; }
    }
    async function json(url) {
      const response = await fetch(url);
      if (!response.ok) throw new Error((await response.json()).detail || "Request failed");
      return response.json();
    }
    function fail(message) {
      $("error").style.display = "block";
      $("error").textContent = message;
    }
    async function initialize() {
      try {
        const data = await json("/api/v1/governance/approvals");
        providers = data.items;
        $("reviewed").textContent = `${data.market_focus} / approval review as of ${data.as_of}`;
        $("tracked").textContent = data.queue_count;
        $("critical").textContent = data.critical_open_count;
        $("approved").textContent = data.approved_count;
        $("activation").textContent = data.public_activation_ready ? "Yes" : "No";
        $("activation").className = data.public_activation_ready ? "" : "no";
        $("publication-note").textContent = data.publication_note;
        $("controls").innerHTML = data.controls.map((control) => `<tr><td><strong>${text(control.label)}</strong><small>${text(control.data_class)}</small></td><td><span class="pill ${text(control.status)}">${text(control.status)}</span></td><td>${control.candidate_count}</td><td>${text(control.blocker || "Approved public provider recorded.")}</td></tr>`).join("");
        $("queue").innerHTML = providers.map((provider) => `<tr data-provider="${text(provider.provider_id)}"><td><span class="pill ${text(provider.priority)}">${text(provider.priority)}</span></td><td><strong>${text(provider.provider_name)}</strong><small>${text(provider.data_class)}</small></td><td><span class="pill ${text(provider.approval_status)}">${text(provider.approval_status)}</span></td><td>${text(provider.required_evidence)}</td></tr>`).join("");
        document.querySelectorAll("tr[data-provider]").forEach((row) => row.addEventListener("click", () => showProvider(row.dataset.provider)));
        showProvider(providers[0].provider_id);
      } catch (error) { fail(error.message); }
    }
    function showProvider(providerId) {
      const provider = providers.find((item) => item.provider_id === providerId);
      $("detail").innerHTML = `<h3>${text(provider.provider_name)}</h3><p>${text(provider.provider_id)} / ${text(provider.data_class)} / source state <span class="pill ${text(provider.deployment_state)}">${text(provider.deployment_state)}</span></p><div class="fact"><small>Requested use</small>${text(provider.requested_use)}</div><div class="fact"><small>Required evidence</small>${text(provider.required_evidence)}</div><div class="fact"><small>Promotion criteria</small>${text(provider.promotion_criteria)}</div><p>${text(provider.review_note)}</p><a href="${href(provider.evidence_url)}" target="_blank" rel="noopener">Review evidence source</a>`;
    }
    initialize();
  </script>
</body>
</html>"""
