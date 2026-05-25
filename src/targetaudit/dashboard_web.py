from __future__ import annotations


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
    .card,.filters,.table-wrap,.side-panel,.empty { background:var(--panel); border:1px solid var(--line); border-radius:14px; }
    .card { padding:17px 20px; }
    .card p { color:var(--muted); margin:0; }
    .card strong { display:block; font-size:35px; color:var(--mint); margin-top:4px; }
    .card small { color:var(--muted); }
    .filters { padding:17px; display:grid; grid-template-columns:2fr 1.2fr 1.1fr .8fr auto; gap:12px; align-items:end; }
    label { display:block; color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.06em; margin-bottom:6px; }
    select,input { width:100%; height:43px; background:var(--panel2); color:var(--text); border:1px solid var(--line); border-radius:9px; padding:0 11px; }
    button { height:43px; border:0; border-radius:9px; color:#061117; background:var(--mint); padding:0 20px; font-weight:600; cursor:pointer; }
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
    a { color:var(--mint); text-decoration:none; }
    .audit-grid { display:grid; grid-template-columns:300px 1fr; gap:18px; }
    .reasons { padding:18px; }
    .reason { display:flex; justify-content:space-between; border-bottom:1px solid var(--line); padding:10px 0; color:var(--muted); }
    .reason strong { color:var(--gold); }
    .empty { color:var(--muted); padding:26px; text-align:center; }
    #error { display:none; border-left-color:var(--red); color:var(--red); }
    @media(max-width:980px) {
      .cards { grid-template-columns:repeat(2,1fr); }
      .filters,.layout,.audit-grid { grid-template-columns:1fr; }
      .table-wrap { overflow-x:auto; }
      table { min-width:680px; }
    }
  </style>
</head>
<body>
  <header>
    <nav>TargetAudit / U.S. Financials / Scorecard</nav>
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
        $("run").innerHTML = runs.map((run) => `<option value="${text(run.run_id)}">${text(run.run_id)} / ${text(run.as_of)}</option>`).join("");
        const preferred = runs.find((run) => run.run_id === "demo-financials-2025-01-01");
        currentRun = preferred ? preferred.run_id : runs[0].run_id;
        $("run").value = currentRun;
        await loadRun();
      } catch (error) { fail(error.message); }
    }
    async function loadRun() {
      currentRun = $("run").value || currentRun;
      const [run, facets] = await Promise.all([
        json(`${base}/runs/${encodeURIComponent(currentRun)}`),
        json(`${base}/runs/${encodeURIComponent(currentRun)}/facets`)
      ]);
      $("run-meta").textContent = `Calculated as of ${run.as_of} / Universe ${run.universe_id || "not supplied"} / Costs ${run.transaction_cost_bps_per_side} bps per side`;
      $("evaluated").textContent = run.evaluated_count;
      $("excluded").textContent = run.excluded_count;
      $("pending").textContent = run.pending_count;
      $("methodology").textContent = facets.methodology_version;
      $("sample").value = run.minimum_sample;
      $("sector").innerHTML = '<option value="">All sectors</option>' + facets.sectors.map((sector) => `<option value="${text(sector)}">${text(sector)}</option>`).join("");
      await refresh();
    }
    async function refresh() {
      $("error").style.display = "none";
      const params = new URLSearchParams({minimum_sample: $("sample").value || "1"});
      if ($("sector").value) params.set("sector", $("sector").value);
      if ($("direction").value) params.set("direction", $("direction").value);
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
        const data = await json(`${base}/runs/${encodeURIComponent(currentRun)}/tickers/${encodeURIComponent(ticker)}`);
        const rows = data.observations.map((row) => `<article class="metric"><small>${text(row.firm)} / ${text(row.published_date)}</small><strong>${text(row.status)}${row.hit === true ? " / hit" : row.hit === false ? " / miss" : ""}</strong><small>Target: ${text(row.price_target)} / Reason: ${text(row.reason)}</small><a href="${evidenceHref(row.source_url)}" target="_blank" rel="noopener">Evidence source</a></article>`).join("");
        $("detail").innerHTML = `<h3>${text(ticker)} Evidence</h3><p>${data.observations.length} observation(s) retained in this run.</p><section class="summary">${rows}</section>`;
      } catch (error) { fail(error.message); }
    }
    function renderAudit(data) {
      const entries = Object.entries(data.counts_by_reason);
      $("reasons").innerHTML = `<h3>Reason Counts</h3>` + (entries.length ? entries.map(([reason,count]) => `<div class="reason"><span>${text(reason)}</span><strong>${count}</strong></div>`).join("") : "<p>No excluded or pending observations.</p>");
      $("audit").innerHTML = data.observations.length ? data.observations.map((row) => `<tr><td>${text(row.observation_id)}</td><td>${text(row.firm)}</td><td>${text(row.ticker)}</td><td><span class="pill excluded">${text(row.status)}</span></td><td>${text(row.reason)}</td><td><a href="${evidenceHref(row.source_url)}" target="_blank" rel="noopener">Source</a></td></tr>`).join("") : '<tr><td colspan="6">No excluded or pending observations.</td></tr>';
    }
    $("run").addEventListener("change", loadRun);
    $("apply").addEventListener("click", refresh);
    initialize();
  </script>
</body>
</html>"""
