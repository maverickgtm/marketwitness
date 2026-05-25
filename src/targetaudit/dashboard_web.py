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
    <nav>TargetAudit / U.S. Financials / Scorecard / <a href="/dashboard/readiness">Scorecard Readiness</a> / <a href="/dashboard/governance">Source Governance</a> / <a href="/dashboard/operations">Operations Quality</a></nav>
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
    <nav>TargetAudit / Governance / Sources / <a href="/dashboard/financials">Financials Scorecard</a> / <a href="/dashboard/readiness">Scorecard Readiness</a> / <a href="/dashboard/operations">Operations Quality</a></nav>
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
    <nav>TargetAudit / Operations / Quality / <a href="/dashboard/financials">Financials Scorecard</a> / <a href="/dashboard/readiness">Scorecard Readiness</a> / <a href="/dashboard/governance">Source Governance</a></nav>
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
    <nav>TargetAudit / U.S. Financials / Readiness / <a href="/dashboard/financials">Financials Scorecard</a> / <a href="/dashboard/governance">Source Governance</a> / <a href="/dashboard/operations">Operations Quality</a></nav>
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
