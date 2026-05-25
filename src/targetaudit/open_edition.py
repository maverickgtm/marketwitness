from __future__ import annotations

from collections import Counter
from datetime import date
from html import escape
from pathlib import Path
from typing import Any

from .source_registry import SourceProvider, SourceRegistryDataError


CAPABILITIES = (
    {
        "key": "financials_sandbox",
        "title": "Financials Scorecard Sandbox",
        "status": "bundled_offline_demo",
        "cost": "No cost",
        "provider_ids": ("synthetic-demo",),
        "output": "Financials ranking, exclusions and methodology audit",
        "route": "/dashboard/financials",
        "limitation": "Project-authored fixtures demonstrate the engine; they are not market rankings.",
    },
    {
        "key": "ipo_watch_us",
        "title": "U.S. IPO Filing Watch",
        "status": "public_source_no_key",
        "cost": "No data fee",
        "provider_ids": ("sec-edgar", "sec-company-map"),
        "output": "SEC filing discovery, review queue and watchlist promotion audit",
        "route": "/dashboard/ipo-watch",
        "limitation": "Live collection needs a contact User-Agent and manual filing review.",
    },
    {
        "key": "etf_regulatory_activity",
        "title": "ETF Regulatory Holdings",
        "status": "public_source_no_key",
        "cost": "No data fee",
        "provider_ids": ("sec-nport",),
        "output": "Periodic N-PORT holdings snapshots and change reports",
        "route": "/dashboard/etf-regulatory",
        "limitation": "Regulatory filings are periodic evidence, not real-time ETF trading activity.",
    },
    {
        "key": "regulated_document_checks",
        "title": "Public Document Checks",
        "status": "public_source_no_key",
        "cost": "No data fee",
        "provider_ids": ("fca-nsm",),
        "output": "Regulatory document corroboration for monitored listing candidates",
        "route": "/dashboard/document-checks",
        "limitation": "Document confirmation does not predict or recommend an IPO position.",
    },
    {
        "key": "real_analyst_rankings",
        "title": "Real Analyst Rankings",
        "status": "bring_authorized_data",
        "cost": "Optional only",
        "provider_ids": (),
        "output": "Rankings from user-supplied observations with documented usage rights",
        "route": "/dashboard/extensions",
        "limitation": "Optional paid paths are cataloged, but no licensed target dataset is bundled or required.",
    },
)


def build_open_edition_snapshot(
    providers: list[SourceProvider], as_of: date
) -> dict[str, Any]:
    if any(provider.reviewed_on > as_of for provider in providers):
        raise SourceRegistryDataError(
            "Source registry includes a provider review after the Open Edition cutoff."
        )
    providers_by_id = {provider.provider_id: provider for provider in providers}
    capabilities = [_capability_payload(item, providers_by_id) for item in CAPABILITIES]
    counts = Counter(item["status"] for item in capabilities)
    return {
        "edition": "Open Edition",
        "as_of": as_of.isoformat(),
        "promise": (
            "Runs from GitHub without paid market-data subscriptions: bundled reproducible "
            "research examples plus public regulatory-data monitors. Paid or separately "
            "authorized targets are optional extensions, never a requirement."
        ),
        "zero_cost_available_count": (
            counts["bundled_offline_demo"] + counts["public_source_no_key"]
        ),
        "offline_ready_count": counts["bundled_offline_demo"],
        "public_data_ready_count": counts["public_source_no_key"],
        "optional_extension_count": counts["bring_authorized_data"],
        "capabilities": capabilities,
        "setup_modes": [
            {
                "title": "Offline showcase",
                "requirement": "`make demo`",
                "result": "All generated demo pages, no network request and no API key.",
            },
            {
                "title": "Free public monitors",
                "requirement": "Contact email in `TARGETAUDIT_SEC_USER_AGENT`",
                "result": "SEC IPO and N-PORT collectors under fair-access rules, with no data fee.",
            },
            {
                "title": "Optional scorecard expansion",
                "requirement": "Your own authorized target and price inputs",
                "result": "Run the audit engine without committing restricted third-party datasets.",
            },
        ],
    }


def _capability_payload(
    definition: dict[str, Any], providers_by_id: dict[str, SourceProvider]
) -> dict[str, Any]:
    sources = []
    for provider_id in definition["provider_ids"]:
        provider = providers_by_id.get(provider_id)
        if provider is None:
            raise SourceRegistryDataError(
                f"Open Edition requires registered source: {provider_id}."
            )
        if definition["status"] == "public_source_no_key" and (
            provider.deployment_state != "usable_with_policy"
            or provider.integration_status not in {"implemented", "manual_verified"}
        ):
            raise SourceRegistryDataError(
                f"Open Edition public capability uses an unavailable source: {provider_id}."
            )
        sources.append(
            {
                "provider_id": provider.provider_id,
                "provider_name": provider.provider_name,
                "official_url": provider.official_url,
            }
        )
    return {
        **definition,
        "provider_ids": list(definition["provider_ids"]),
        "sources": sources,
    }


def render_open_edition_report(snapshot: dict[str, Any]) -> str:
    lines = [
        "# TargetAudit Open Edition",
        "",
        f"- Reviewed as of: `{snapshot['as_of']}`",
        f"- Available without paid data subscriptions: `{snapshot['zero_cost_available_count']}`",
        f"- Offline-ready capabilities: `{snapshot['offline_ready_count']}`",
        f"- Free public-data capabilities: `{snapshot['public_data_ready_count']}`",
        f"- Optional authorized-data extensions: `{snapshot['optional_extension_count']}`",
        "",
        snapshot["promise"],
        "",
        "## Included Capabilities",
        "",
        "| Capability | Availability | Cost | Output | Limitation |",
        "|---|---|---|---|---|",
    ]
    for item in snapshot["capabilities"]:
        lines.append(
            f"| {item['title']} | `{item['status']}` | {item['cost']} | "
            f"{item['output']} | {item['limitation']} |"
        )
    lines.extend(["", "## Run Modes", ""])
    for mode in snapshot["setup_modes"]:
        lines.extend(
            [
                f"### {mode['title']}",
                "",
                f"- Requirement: {mode['requirement']}",
                f"- Result: {mode['result']}",
                "",
            ]
        )
    return "\n".join(lines)


def write_open_edition_report(path: str | Path, snapshot: dict[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_open_edition_report(snapshot), encoding="utf-8")


def render_open_edition_html(snapshot: dict[str, Any]) -> str:
    capability_cards = "".join(
        "<article class=\"feature\">"
        f"<span class=\"pill {escape(item['status'])}\">{escape(item['status'])}</span>"
        f"<h3>{escape(item['title'])}</h3><strong>{escape(item['cost'])}</strong>"
        f"<p>{escape(item['output'])}</p><small>{escape(item['limitation'])}</small>"
        "</article>"
        for item in snapshot["capabilities"]
    )
    modes = "".join(
        "<article class=\"mode\">"
        f"<h3>{escape(mode['title'])}</h3>"
        f"<p>{escape(mode['requirement'])}</p><small>{escape(mode['result'])}</small>"
        "</article>"
        for mode in snapshot["setup_modes"]
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TargetAudit | Open Edition</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;--blue:#62a6ff;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1180px;margin:auto;padding:30px 28px}}nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}h1{{font-size:clamp(38px,5vw,60px);line-height:1.04;margin:38px 0 15px}}h2{{margin:44px 0 18px}}h3{{margin:12px 0 8px}}.lead{{color:var(--muted);font-size:18px;max-width:920px}}.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:34px 0}}.card,.feature,.mode,.notice{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px}}.card p{{margin:0;color:var(--muted)}}.card strong{{font-size:38px;color:var(--mint);display:block}}.notice{{padding:15px 18px;border-left:3px solid var(--mint);color:var(--muted)}}.features{{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}}.feature{{padding:18px}}.feature strong{{display:block;color:var(--mint);margin:8px 0}}.feature p,.feature small,.mode small{{color:var(--muted);display:block}}.pill{{display:inline-block;border-radius:999px;padding:5px 9px;font-size:12px}}.bundled_offline_demo{{color:var(--blue);background:rgba(98,166,255,.12)}}.public_source_no_key{{color:var(--mint);background:rgba(86,218,172,.12)}}.bring_authorized_data{{color:var(--gold);background:rgba(240,188,98,.12)}}.modes{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}.mode{{padding:18px}}.mode p{{color:var(--mint)}}@media(max-width:900px){{.cards,.features,.modes{{grid-template-columns:1fr}}}}
</style></head><body><header><nav>TargetAudit / Open Edition</nav><h1>Market research.<br>No paid data required.</h1>
<p class="lead">{escape(snapshot['promise'])}</p><p class="meta">Reviewed as of {escape(snapshot['as_of'])}</p>
<section class="cards"><article class="card"><p>No-cost capabilities</p><strong>{snapshot['zero_cost_available_count']}</strong></article><article class="card"><p>Offline demo</p><strong>{snapshot['offline_ready_count']}</strong></article><article class="card"><p>Public-data monitors</p><strong>{snapshot['public_data_ready_count']}</strong></article><article class="card"><p>Optional extensions</p><strong>{snapshot['optional_extension_count']}</strong></article></section></header>
<main><p class="notice">The GitHub product works without commercial subscriptions. Real analyst ranking inputs remain optional and must be supplied with usage rights.</p><h2>Included Capabilities</h2><section class="features">{capability_cards}</section><h2>Run Modes</h2><section class="modes">{modes}</section></main></body></html>"""


def write_open_edition_html(path: str | Path, snapshot: dict[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_open_edition_html(snapshot), encoding="utf-8")
