from __future__ import annotations

from collections import Counter
from datetime import date
from decimal import Decimal
from html import escape
from pathlib import Path
from typing import Any

from .storage import (
    list_run_summaries,
    read_evaluations,
    read_run_assets,
    read_run_summary,
)

REQUIRED_INPUT_ROLES = {"prices", "targets"}


def build_quality_snapshot(
    database_path: str | Path,
    maximum_excluded_rate: Decimal = Decimal("0.50"),
    run_id: str = "",
) -> dict[str, Any]:
    if maximum_excluded_rate < 0 or maximum_excluded_rate > 1:
        raise ValueError("Maximum excluded rate must be between zero and one.")
    summaries = (
        [read_run_summary(database_path, run_id)]
        if run_id
        else list_run_summaries(database_path)
    )
    runs = [
        _assess_run(
            run,
            read_run_assets(database_path, run["run_id"]),
            read_evaluations(database_path, run["run_id"]),
            maximum_excluded_rate,
        )
        for run in summaries
    ]
    statuses = Counter(run["quality_status"] for run in runs)
    return {
        "selected_run_id": run_id or None,
        "maximum_excluded_rate": float(maximum_excluded_rate),
        "run_count": len(runs),
        "quality_pass_count": statuses["quality_pass"],
        "review_required_count": statuses["review_required"],
        "blocked_count": statuses["blocked"],
        "publication_note": (
            "Operational quality passing does not grant data publication rights; "
            "source-governance approval is still required."
        ),
        "runs": runs,
    }


def _assess_run(
    run: dict[str, Any],
    assets: list[dict[str, Any]],
    evaluations: list[Any],
    maximum_excluded_rate: Decimal,
) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    asset_roles = sorted(asset["asset_role"] for asset in assets)
    missing_roles = sorted(REQUIRED_INPUT_ROLES - set(asset_roles))
    unlinked = sum(not item.provider_id for item in evaluations)
    observations = run["observation_count"]
    excluded_rate = (
        Decimal(run["excluded_count"]) / Decimal(observations)
        if observations
        else Decimal("0")
    )

    if not run["methodology_version"]:
        _finding(findings, "blocked", "methodology_unstamped", "Methodology version is missing.")
    if not run["dataset_fingerprint"]:
        _finding(findings, "blocked", "dataset_unstamped", "Dataset fingerprint is missing.")
    if not run["dataset_label"]:
        _finding(findings, "review", "dataset_label_missing", "Dataset label is missing.")
    if missing_roles:
        _finding(
            findings,
            "blocked",
            "required_input_missing",
            f"Required input assets missing: {', '.join(missing_roles)}.",
        )
    if unlinked:
        _finding(
            findings,
            "blocked",
            "provider_lineage_missing",
            f"{unlinked} observation(s) have no declared provider lineage.",
        )
    if excluded_rate > maximum_excluded_rate:
        _finding(
            findings,
            "review",
            "excluded_rate_high",
            (
                f"Excluded rate {excluded_rate:.2%} exceeds the configured "
                f"{maximum_excluded_rate:.2%} threshold."
            ),
        )
    if run["evaluated_count"] < run["minimum_sample"]:
        _finding(
            findings,
            "review",
            "ranking_sample_not_met",
            "Evaluated observations are below the configured ranking minimum sample.",
        )

    severity = {item["severity"] for item in findings}
    if "blocked" in severity:
        quality_status = "blocked"
    elif "review" in severity:
        quality_status = "review_required"
    else:
        quality_status = "quality_pass"
    return {
        "run_id": run["run_id"],
        "as_of": run["as_of"],
        "methodology_version": run["methodology_version"],
        "dataset_label": run["dataset_label"],
        "dataset_fingerprint": run["dataset_fingerprint"],
        "quality_status": quality_status,
        "observation_count": observations,
        "evaluated_count": run["evaluated_count"],
        "excluded_count": run["excluded_count"],
        "pending_count": run["pending_count"],
        "excluded_rate": float(excluded_rate),
        "unlinked_observation_count": unlinked,
        "asset_roles": asset_roles,
        "findings": findings,
    }


def _finding(
    findings: list[dict[str, str]], severity: str, code: str, message: str
) -> None:
    findings.append({"severity": severity, "code": code, "message": message})


def render_quality_report(snapshot: dict[str, Any], as_of: date) -> str:
    lines = [
        "# Operations Quality Monitor",
        "",
        f"- Generated as of: `{as_of.isoformat()}`",
        f"- Evaluation runs checked: `{snapshot['run_count']}`",
        f"- Quality pass: `{snapshot['quality_pass_count']}`",
        f"- Review required: `{snapshot['review_required_count']}`",
        f"- Blocked: `{snapshot['blocked_count']}`",
        f"- Maximum excluded rate before review: `{snapshot['maximum_excluded_rate']:.2%}`",
        "",
        snapshot["publication_note"],
        "",
        "## Stored Run Quality",
        "",
        "| Run | Dataset | Methodology | Status | Evaluated | Excluded Rate | Findings |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for run in snapshot["runs"]:
        findings = "; ".join(item["code"] for item in run["findings"]) or "none"
        lines.append(
            f"| `{run['run_id']}` | {run['dataset_label'] or 'unstamped'} | "
            f"`{run['methodology_version'] or 'unstamped'}` | "
            f"`{run['quality_status']}` | {run['evaluated_count']} | "
            f"{run['excluded_rate']:.2%} | {findings} |"
        )
    lines.extend(["", "## Review Queue", ""])
    for run in snapshot["runs"]:
        if not run["findings"]:
            continue
        lines.append(f"### {run['run_id']}")
        lines.extend(
            f"- `{finding['severity']}` / `{finding['code']}`: {finding['message']}"
            for finding in run["findings"]
        )
        lines.append("")
    if all(not run["findings"] for run in snapshot["runs"]):
        lines.append("No operational quality findings require review.")
    return "\n".join(lines)


def write_quality_report(path: str | Path, snapshot: dict[str, Any], as_of: date) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_quality_report(snapshot, as_of), encoding="utf-8")


def render_quality_html(snapshot: dict[str, Any], as_of: date) -> str:
    rows = "".join(
        "<tr>"
        f"<td><strong>{escape(run['run_id'])}</strong><small>{escape(run['dataset_label'] or 'unstamped')}</small></td>"
        f"<td><span class=\"pill {escape(run['quality_status'])}\">{escape(run['quality_status'])}</span></td>"
        f"<td>{run['evaluated_count']} / {run['observation_count']}</td>"
        f"<td>{run['excluded_rate']:.2%}</td>"
        f"<td>{escape('; '.join(item['code'] for item in run['findings']) or 'none')}</td>"
        "</tr>"
        for run in snapshot["runs"]
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TargetAudit | Operations Quality</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;--red:#ff7d72;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1160px;margin:auto;padding:30px 28px}}nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}h1{{font-size:clamp(36px,5vw,56px);line-height:1.06;margin:38px 0 14px}}.lead{{color:var(--muted);font-size:17px;max-width:840px}}.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:35px 0}}.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px}}.card p{{margin:0;color:var(--muted)}}.card strong{{font-size:38px;color:var(--mint);display:block}}.notice{{border-left:3px solid var(--gold);color:var(--muted);padding:15px 18px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{text-transform:uppercase;font-size:12px;color:var(--muted);font-weight:500}}td small{{display:block;color:var(--muted)}}.pill{{display:inline-block;border-radius:999px;padding:5px 9px;font-size:12px}}.quality_pass{{color:var(--mint);background:rgba(86,218,172,.12)}}.review_required{{color:var(--gold);background:rgba(240,188,98,.12)}}.blocked{{color:var(--red);background:rgba(255,125,114,.12)}}.table-wrap{{overflow:hidden;margin-top:18px}}@media(max-width:820px){{.cards{{grid-template-columns:repeat(2,1fr)}}.table-wrap{{overflow-x:auto}}table{{min-width:700px}}}}
</style></head><body><header><nav>TargetAudit / Operations / Quality</nav><h1>Ship evidence,<br>not surprises.</h1>
<p class="lead">Quality gates for stored evaluation runs: reproducibility stamps, required inputs, provider lineage and anomalous exclusion rates.</p>
<p class="meta">Generated as of {escape(as_of.isoformat())} / Exclusion review threshold {snapshot['maximum_excluded_rate']:.2%}</p>
<section class="cards"><article class="card"><p>Runs</p><strong>{snapshot['run_count']}</strong></article><article class="card"><p>Pass</p><strong>{snapshot['quality_pass_count']}</strong></article><article class="card"><p>Review</p><strong>{snapshot['review_required_count']}</strong></article><article class="card"><p>Blocked</p><strong>{snapshot['blocked_count']}</strong></article></section></header>
<main><p class="notice">{escape(snapshot['publication_note'])}</p><h2>Stored Run Quality</h2><div class="table-wrap"><table><thead><tr><th>Run</th><th>Status</th><th>Evaluated</th><th>Excluded Rate</th><th>Findings</th></tr></thead><tbody>{rows}</tbody></table></div></main></body></html>"""


def write_quality_html(path: str | Path, snapshot: dict[str, Any], as_of: date) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_quality_html(snapshot, as_of), encoding="utf-8")
