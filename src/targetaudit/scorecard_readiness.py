from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path
from typing import Any

from .source_registry import SourceProvider, SourceRegistryDataError

NON_PRODUCTION_PROVIDER_IDS = {"synthetic-demo", "authorized-demo"}


@dataclass(frozen=True)
class ScorecardRequirement:
    key: str
    label: str
    data_class: str
    purpose: str


REQUIREMENTS = (
    ScorecardRequirement(
        "analyst_targets",
        "Historical analyst targets",
        "Analyst targets",
        "Core input for firm hit rates and target timelines.",
    ),
    ScorecardRequirement(
        "adjusted_prices",
        "Adjusted price bars",
        "Adjusted price bars",
        "Core input for reached-target and terminal-return evaluation.",
    ),
    ScorecardRequirement(
        "corporate_actions",
        "Corporate action coverage",
        "Corporate actions",
        "Release safeguard for splits and ticker changes in target horizons.",
    ),
    ScorecardRequirement(
        "historical_universe",
        "Point-in-time Financials universe",
        "Historical universe membership",
        "Membership control that prevents survivor-biased historical rankings.",
    ),
)


def build_scorecard_readiness(
    providers: list[SourceProvider], as_of: date
) -> dict[str, Any]:
    if any(provider.reviewed_on > as_of for provider in providers):
        raise SourceRegistryDataError(
            "Source registry includes a provider review after the readiness cutoff."
        )
    requirements = [_assess_requirement(requirement, providers) for requirement in REQUIREMENTS]
    statuses = Counter(item["status"] for item in requirements)
    blockers = [
        item["blocker"]
        for item in requirements
        if item["status"] != "public_ready"
    ]
    return {
        "market_focus": "U.S. Financials",
        "as_of": as_of.isoformat(),
        "public_release_ready": all(
            item["status"] == "public_ready" for item in requirements
        ),
        "internal_research_ready": all(
            item["internal_ready"] for item in requirements
        ),
        "requirement_count": len(requirements),
        "public_ready_count": statuses["public_ready"],
        "internal_only_count": statuses["internal_only"],
        "integration_pending_count": statuses["integration_pending"],
        "missing_source_count": statuses["missing_source"],
        "blockers": blockers,
        "publication_note": (
            "Technical integration is not publication permission. A public Financials "
            "Scorecard remains disabled until every required data control has an "
            "approved production source."
        ),
        "requirements": requirements,
    }


def _assess_requirement(
    requirement: ScorecardRequirement, providers: list[SourceProvider]
) -> dict[str, Any]:
    matching = [
        provider for provider in providers if provider.data_class == requirement.data_class
    ]
    production = [
        provider
        for provider in matching
        if provider.provider_id not in NON_PRODUCTION_PROVIDER_IDS
    ]
    integrated = [
        provider
        for provider in production
        if provider.integration_status in {"implemented", "manual_verified"}
        and provider.deployment_state != "blocked"
    ]
    public = [
        provider for provider in integrated if provider.deployment_state == "usable_with_policy"
    ]
    if public:
        status = "public_ready"
        blocker = ""
    elif integrated:
        status = "internal_only"
        blocker = f"{requirement.label} has integration but not approved public-output rights."
    elif production:
        status = "integration_pending"
        blocker = f"{requirement.label} has candidate sources but no production integration."
    else:
        status = "missing_source"
        blocker = f"{requirement.label} has no production source registered."
    return {
        "key": requirement.key,
        "label": requirement.label,
        "data_class": requirement.data_class,
        "purpose": requirement.purpose,
        "status": status,
        "internal_ready": bool(integrated),
        "providers": [_provider_payload(provider) for provider in matching],
        "production_provider_count": len(production),
        "blocker": blocker,
    }


def _provider_payload(provider: SourceProvider) -> dict[str, Any]:
    return {
        "provider_id": provider.provider_id,
        "provider_name": provider.provider_name,
        "integration_status": provider.integration_status,
        "deployment_state": provider.deployment_state,
        "publication_policy": provider.publication_policy,
        "production_eligible": provider.provider_id not in NON_PRODUCTION_PROVIDER_IDS,
        "official_url": provider.official_url,
        "review_note": provider.review_note,
    }


def render_readiness_report(snapshot: dict[str, Any]) -> str:
    lines = [
        "# Financials Scorecard Readiness",
        "",
        f"- Market focus: `{snapshot['market_focus']}`",
        f"- Reviewed as of: `{snapshot['as_of']}`",
        f"- Public release ready: `{str(snapshot['public_release_ready']).lower()}`",
        f"- Internal production research ready: `{str(snapshot['internal_research_ready']).lower()}`",
        f"- Public-ready controls: `{snapshot['public_ready_count']}` / `{snapshot['requirement_count']}`",
        "",
        snapshot["publication_note"],
        "",
        "## Required Controls",
        "",
        "| Requirement | Status | Production Providers | Blocker |",
        "|---|---|---:|---|",
    ]
    for requirement in snapshot["requirements"]:
        lines.append(
            f"| {requirement['label']} | `{requirement['status']}` | "
            f"{requirement['production_provider_count']} | "
            f"{requirement['blocker'] or 'none'} |"
        )
    lines.extend(["", "## Provider Candidates", ""])
    for requirement in snapshot["requirements"]:
        lines.append(f"### {requirement['label']}")
        if not requirement["providers"]:
            lines.extend(["", "No provider registered.", ""])
            continue
        lines.append("")
        for provider in requirement["providers"]:
            qualifier = "production candidate" if provider["production_eligible"] else "demo only"
            lines.append(
                f"- `{provider['provider_id']}` / {provider['provider_name']}: "
                f"`{provider['deployment_state']}` ({qualifier})"
            )
        lines.append("")
    return "\n".join(lines)


def write_readiness_report(path: str | Path, snapshot: dict[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_readiness_report(snapshot), encoding="utf-8")


def render_readiness_html(snapshot: dict[str, Any]) -> str:
    rows = "".join(
        "<tr>"
        f"<td><strong>{escape(item['label'])}</strong><small>{escape(item['purpose'])}</small></td>"
        f"<td><span class=\"pill {escape(item['status'])}\">{escape(item['status'])}</span></td>"
        f"<td>{item['production_provider_count']}</td>"
        f"<td>{escape(item['blocker'] or 'Ready under approved policy.')}</td>"
        "</tr>"
        for item in snapshot["requirements"]
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TargetAudit | Scorecard Readiness</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;--blue:#62a6ff;--red:#ff7d72;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1160px;margin:auto;padding:30px 28px}}nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}h1{{font-size:clamp(36px,5vw,56px);line-height:1.06;margin:38px 0 14px}}.lead{{color:var(--muted);font-size:17px;max-width:850px}}.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:35px 0}}.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px}}.card p{{margin:0;color:var(--muted)}}.card strong{{font-size:34px;color:var(--mint);display:block}}.blocked-value{{color:var(--red)!important}}.notice{{border-left:3px solid var(--gold);color:var(--muted);padding:15px 18px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{text-transform:uppercase;font-size:12px;color:var(--muted);font-weight:500}}td small{{display:block;color:var(--muted)}}.pill{{display:inline-block;border-radius:999px;padding:5px 9px;font-size:12px}}.public_ready{{color:var(--mint);background:rgba(86,218,172,.12)}}.internal_only{{color:var(--blue);background:rgba(98,166,255,.12)}}.integration_pending,.missing_source{{color:var(--gold);background:rgba(240,188,98,.12)}}.table-wrap{{overflow:hidden;margin-top:18px}}@media(max-width:820px){{.cards{{grid-template-columns:1fr}}.table-wrap{{overflow-x:auto}}table{{min-width:700px}}}}
</style></head><body><header><nav>TargetAudit / Financials / Readiness</nav><h1>Earn the right<br>to publish.</h1>
<p class="lead">Production readiness for a public U.S. Financials scorecard, separated from demo fixtures and internal-only data access.</p>
<p class="meta">Reviewed as of {escape(snapshot['as_of'])}</p>
<section class="cards"><article class="card"><p>Required controls</p><strong>{snapshot['requirement_count']}</strong></article><article class="card"><p>Public ready</p><strong>{snapshot['public_ready_count']}</strong></article><article class="card"><p>Release enabled</p><strong class="{'blocked-value' if not snapshot['public_release_ready'] else ''}">{'Yes' if snapshot['public_release_ready'] else 'No'}</strong></article></section></header>
<main><p class="notice">{escape(snapshot['publication_note'])}</p><h2>Public Release Requirements</h2><div class="table-wrap"><table><thead><tr><th>Control</th><th>Status</th><th>Providers</th><th>Blocking Reason</th></tr></thead><tbody>{rows}</tbody></table></div></main></body></html>"""


def write_readiness_html(path: str | Path, snapshot: dict[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_readiness_html(snapshot), encoding="utf-8")
