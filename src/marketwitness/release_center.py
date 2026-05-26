from __future__ import annotations

from datetime import date
from decimal import Decimal
from html import escape
from pathlib import Path
from typing import Any

from .operations_quality import build_quality_snapshot
from .scorecard_readiness import NON_PRODUCTION_PROVIDER_IDS, build_scorecard_readiness
from .source_registry import SourceProvider
from .storage import read_evaluations, read_run_assets

PUBLIC_ASSET_CONTROLS = {
    "prices": ("Adjusted price bars", "Adjusted price bars"),
    "corporate_actions": ("Corporate action coverage", "Corporate actions"),
    "universe_membership": (
        "Point-in-time Financials universe",
        "Historical universe membership",
    ),
}


def build_release_decision(
    providers: list[SourceProvider],
    database_path: str | Path,
    run_id: str,
    as_of: date,
    maximum_excluded_rate: Decimal = Decimal("0.50"),
) -> dict[str, Any]:
    readiness = build_scorecard_readiness(providers, as_of)
    quality = build_quality_snapshot(
        database_path, maximum_excluded_rate, run_id, public_release=True
    )
    candidate = quality["runs"][0]
    source_ready = readiness["public_release_ready"]
    run_ready = candidate["quality_status"] == "quality_pass"
    evaluations = read_evaluations(database_path, run_id)
    candidate_provider_ids = sorted(
        {evaluation.provider_id for evaluation in evaluations if evaluation.provider_id}
    )
    has_unlinked_observations = any(not evaluation.provider_id for evaluation in evaluations)
    approved_target_provider_ids = {
        provider.provider_id
        for provider in providers
        if provider.data_class == "Analyst targets"
        and provider.provider_id not in NON_PRODUCTION_PROVIDER_IDS
        and provider.integration_status in {"implemented", "manual_verified"}
        and provider.deployment_state == "usable_with_policy"
    }
    unapproved_provider_ids = sorted(
        set(candidate_provider_ids) - approved_target_provider_ids
    )
    lineage_ready = (
        bool(candidate_provider_ids)
        and not unapproved_provider_ids
        and not has_unlinked_observations
    )
    assets_by_role = {
        item["asset_role"]: item for item in read_run_assets(database_path, run_id)
    }
    asset_lineage = [
        _assess_asset_lineage(role, label, data_class, assets_by_role, providers)
        for role, (label, data_class) in PUBLIC_ASSET_CONTROLS.items()
    ]
    asset_lineage_ready = all(item["status"] == "pass" for item in asset_lineage)
    blockers = list(readiness["blockers"])
    blockers.extend(
        finding["message"]
        for finding in candidate["findings"]
        if finding["severity"] in {"blocked", "review"}
    )
    if unapproved_provider_ids:
        blockers.append(
            "Candidate observations use provider lineage not approved for public "
            f"analyst-target output: {', '.join(unapproved_provider_ids)}."
        )
    elif not candidate_provider_ids and not has_unlinked_observations:
        blockers.append("Candidate observations contain no approved analyst-target lineage.")
    blockers.extend(
        item["blocker"] for item in asset_lineage if item["status"] != "pass"
    )
    release_ready = source_ready and run_ready and lineage_ready and asset_lineage_ready
    return {
        "market_focus": readiness["market_focus"],
        "as_of": as_of.isoformat(),
        "run_id": run_id,
        "release_status": "ready" if release_ready else "blocked",
        "release_ready": release_ready,
        "source_gate_status": "pass" if source_ready else "blocked",
        "lineage_gate_status": "pass" if lineage_ready else "blocked",
        "asset_lineage_gate_status": "pass" if asset_lineage_ready else "blocked",
        "quality_gate_status": (
            "pass" if run_ready else candidate["quality_status"]
        ),
        "candidate_provider_ids": candidate_provider_ids,
        "unapproved_provider_ids": unapproved_provider_ids,
        "asset_lineage": asset_lineage,
        "blockers": blockers,
        "publication_note": (
            "A public scorecard release requires approved source rights and a "
            "quality-passing candidate run. This decision is an audit control, "
            "not investment advice."
        ),
        "readiness": readiness,
        "quality": quality,
        "candidate_run": candidate,
    }


def _assess_asset_lineage(
    role: str,
    label: str,
    data_class: str,
    assets_by_role: dict[str, dict[str, Any]],
    providers: list[SourceProvider],
) -> dict[str, str]:
    asset = assets_by_role.get(role)
    provider_id = asset["provider_id"] if asset else ""
    approved_provider_ids = {
        provider.provider_id
        for provider in providers
        if provider.data_class == data_class
        and provider.provider_id not in NON_PRODUCTION_PROVIDER_IDS
        and provider.integration_status in {"implemented", "manual_verified"}
        and provider.deployment_state == "usable_with_policy"
    }
    if not asset:
        blocker = f"{label} asset is missing from the candidate run."
    elif not provider_id:
        blocker = f"{label} asset has no declared provider lineage."
    elif provider_id not in approved_provider_ids:
        blocker = (
            f"{label} asset uses provider not approved for public output: "
            f"{provider_id}."
        )
    else:
        blocker = ""
    return {
        "role": role,
        "label": label,
        "provider_id": provider_id,
        "status": "pass" if not blocker else "blocked",
        "blocker": blocker,
    }


def render_release_report(snapshot: dict[str, Any]) -> str:
    candidate = snapshot["candidate_run"]
    lines = [
        "# Financials Scorecard Release Decision",
        "",
        f"- Market focus: `{snapshot['market_focus']}`",
        f"- Candidate run: `{snapshot['run_id']}`",
        f"- Reviewed as of: `{snapshot['as_of']}`",
        f"- Release status: `{snapshot['release_status']}`",
        f"- Source gate: `{snapshot['source_gate_status']}`",
        f"- Provider lineage gate: `{snapshot['lineage_gate_status']}`",
        f"- Asset lineage gate: `{snapshot['asset_lineage_gate_status']}`",
        f"- Run quality gate: `{snapshot['quality_gate_status']}`",
        "",
        snapshot["publication_note"],
        "",
        "## Decision Blockers",
        "",
    ]
    if snapshot["blockers"]:
        lines.extend(f"- {blocker}" for blocker in snapshot["blockers"])
    else:
        lines.append("No release blockers remain under the registered policies and evidence.")
    lines.extend(
        [
            "",
            "## Candidate Evidence",
            "",
            f"- Methodology: `{candidate['methodology_version']}`",
            f"- Dataset fingerprint: `{candidate['dataset_fingerprint']}`",
            f"- Required assets present: `{', '.join(candidate['asset_roles'])}`",
            f"- Candidate provider lineage: `{', '.join(snapshot['candidate_provider_ids'])}`",
            f"- Evaluated observations: `{candidate['evaluated_count']}`",
            f"- Excluded rate: `{candidate['excluded_rate']:.2%}`",
            "",
            "## Asset Lineage",
            "",
            "| Asset | Provider | Status | Blocking Reason |",
            "|---|---|---|---|",
        ]
    )
    for item in snapshot["asset_lineage"]:
        lines.append(
            f"| {item['label']} | `{item['provider_id'] or 'unlinked'}` | "
            f"`{item['status']}` | {item['blocker'] or 'none'} |"
        )
    lines.extend(
        [
            "",
            "## Required Source Controls",
            "",
            "| Requirement | Status | Blocking Reason |",
            "|---|---|---|",
        ]
    )
    for requirement in snapshot["readiness"]["requirements"]:
        lines.append(
            f"| {requirement['label']} | `{requirement['status']}` | "
            f"{requirement['blocker'] or 'none'} |"
        )
    return "\n".join(lines)


def write_release_report(path: str | Path, snapshot: dict[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_release_report(snapshot), encoding="utf-8")


def render_release_html(snapshot: dict[str, Any]) -> str:
    blocker_rows = "".join(
        f"<li>{escape(blocker)}</li>" for blocker in snapshot["blockers"]
    ) or "<li>No release blockers remain under the registered policies and evidence.</li>"
    controls = "".join(
        "<tr>"
        f"<td><strong>{escape(item['label'])}</strong></td>"
        f"<td><span class=\"pill {escape(item['status'])}\">{escape(item['status'])}</span></td>"
        f"<td>{escape(item['blocker'] or 'Ready under approved policy.')}</td>"
        "</tr>"
        for item in snapshot["readiness"]["requirements"]
    )
    asset_items = "".join(
        f"<li>{escape(item['label'])}: {escape(item['provider_id'] or 'unlinked')} / "
        f"{escape(item['status'])}</li>"
        for item in snapshot["asset_lineage"]
    )
    state_class = "ready" if snapshot["release_ready"] else "blocked"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MarketWitness | Release Center</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;--blue:#62a6ff;--red:#ff7d72;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1160px;margin:auto;padding:30px 28px}}nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}a{{color:var(--mint);text-decoration:none}}h1{{font-size:clamp(36px,5vw,56px);line-height:1.06;margin:38px 0 14px}}.lead{{color:var(--muted);font-size:17px;max-width:850px}}.cards{{display:grid;grid-template-columns:repeat(5,1fr);gap:16px;margin:35px 0}}.card,.notice,.panel,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px}}.card p{{margin:0;color:var(--muted)}}.card strong{{font-size:31px;color:var(--mint);display:block}}.blocked{{color:var(--red)!important}}.notice{{border-left:3px solid var(--gold);color:var(--muted);padding:15px 18px}}.panel{{padding:18px 22px;margin:20px 0}}ul{{margin:8px 0 0;padding-left:20px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{text-transform:uppercase;font-size:12px;color:var(--muted);font-weight:500}}.pill{{display:inline-block;border-radius:999px;padding:5px 9px;font-size:12px}}.public_ready{{color:var(--mint);background:rgba(86,218,172,.12)}}.internal_only{{color:var(--blue);background:rgba(98,166,255,.12)}}.integration_pending,.missing_source{{color:var(--gold);background:rgba(240,188,98,.12)}}.table-wrap{{overflow:hidden;margin-top:18px}}@media(max-width:920px){{.cards{{grid-template-columns:repeat(2,1fr)}}}}
</style></head><body><header><nav><a href="/dashboard/reports">Report Center</a> / <a href="/dashboard/financials-evidence">Financials Evidence Center</a> / Release Decision</nav><h1>Release only<br>what is defensible.</h1>
<p class="lead">A single publication decision combining source rights with candidate-run evidence quality.</p>
<p class="meta">Candidate {escape(snapshot['run_id'])} / Reviewed as of {escape(snapshot['as_of'])}</p>
<section class="cards"><article class="card"><p>Release status</p><strong class="{state_class}">{escape(snapshot['release_status'])}</strong></article><article class="card"><p>Source gate</p><strong class="{'blocked' if snapshot['source_gate_status'] != 'pass' else ''}">{escape(snapshot['source_gate_status'])}</strong></article><article class="card"><p>Target lineage</p><strong class="{'blocked' if snapshot['lineage_gate_status'] != 'pass' else ''}">{escape(snapshot['lineage_gate_status'])}</strong></article><article class="card"><p>Asset lineage</p><strong class="{'blocked' if snapshot['asset_lineage_gate_status'] != 'pass' else ''}">{escape(snapshot['asset_lineage_gate_status'])}</strong></article><article class="card"><p>Run quality</p><strong class="{'blocked' if snapshot['quality_gate_status'] != 'pass' else ''}">{escape(snapshot['quality_gate_status'])}</strong></article></section></header>
<main><p class="notice">{escape(snapshot['publication_note'])}</p><section class="panel"><h2>Decision Blockers</h2><ul>{blocker_rows}</ul><h2>Asset Lineage</h2><ul>{asset_items}</ul></section><h2>Required Source Controls</h2><div class="table-wrap"><table><thead><tr><th>Control</th><th>Status</th><th>Blocking Reason</th></tr></thead><tbody>{controls}</tbody></table></div></main></body></html>"""


def write_release_html(path: str | Path, snapshot: dict[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_release_html(snapshot), encoding="utf-8")
