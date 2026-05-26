from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path
from typing import Any

CATALOG_COLUMNS = {
    "extension_id",
    "extension_name",
    "data_class",
    "provider",
    "access_model",
    "price_display",
    "price_basis",
    "coverage",
    "status",
    "allowed_mode",
    "public_output_status",
    "official_url",
    "pricing_url",
    "terms_url",
    "reviewed_on",
    "review_note",
}
ACCESS_MODELS = {
    "paid_user_subscription",
    "sales_contact_required",
    "marketplace_subscription",
}
STATUSES = {"available_byol", "quote_required"}
ALLOWED_MODES = {"individual_user_license", "negotiated_license"}
PUBLIC_OUTPUT_STATUSES = {
    "requires_separate_written_rights",
    "requires_negotiated_public_output_rights",
    "approved_public_output",
}


class LicensedExtensionDataError(ValueError):
    """Raised when optional licensed-source metadata is invalid."""


@dataclass(frozen=True)
class LicensedExtension:
    extension_id: str
    extension_name: str
    data_class: str
    provider: str
    access_model: str
    price_display: str
    price_basis: str
    coverage: str
    status: str
    allowed_mode: str
    public_output_status: str
    official_url: str
    pricing_url: str
    terms_url: str
    reviewed_on: date
    review_note: str


def load_licensed_extensions(path: str | Path) -> list[LicensedExtension]:
    with Path(path).open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        missing = sorted(CATALOG_COLUMNS - set(reader.fieldnames or []))
        if missing:
            raise LicensedExtensionDataError(
                f"{path}: missing columns: {', '.join(missing)}"
            )
        extensions: list[LicensedExtension] = []
        seen: set[str] = set()
        for index, row in enumerate(reader, start=2):
            extension_id = row["extension_id"].strip()
            access_model = row["access_model"].strip()
            status = row["status"].strip()
            allowed_mode = row["allowed_mode"].strip()
            public_output = row["public_output_status"].strip()
            if not extension_id or extension_id in seen:
                raise LicensedExtensionDataError(
                    f"{path}: blank or duplicate extension id on row {index}"
                )
            if access_model not in ACCESS_MODELS:
                raise LicensedExtensionDataError(
                    f"{path}: invalid access model on row {index}"
                )
            if status not in STATUSES:
                raise LicensedExtensionDataError(
                    f"{path}: invalid availability status on row {index}"
                )
            if allowed_mode not in ALLOWED_MODES:
                raise LicensedExtensionDataError(
                    f"{path}: invalid allowed mode on row {index}"
                )
            if public_output not in PUBLIC_OUTPUT_STATUSES:
                raise LicensedExtensionDataError(
                    f"{path}: invalid public output status on row {index}"
                )
            content = [
                row["extension_name"].strip(),
                row["data_class"].strip(),
                row["provider"].strip(),
                row["price_display"].strip(),
                row["price_basis"].strip(),
                row["coverage"].strip(),
                row["official_url"].strip(),
                row["pricing_url"].strip(),
                row["terms_url"].strip(),
                row["review_note"].strip(),
            ]
            if not all(content):
                raise LicensedExtensionDataError(
                    f"{path}: missing content on row {index}"
                )
            if any(not url.startswith("https://") for url in content[6:9]):
                raise LicensedExtensionDataError(
                    f"{path}: source links must use HTTPS on row {index}"
                )
            try:
                reviewed_on = date.fromisoformat(row["reviewed_on"].strip())
            except ValueError as exc:
                raise LicensedExtensionDataError(
                    f"{path}: invalid review date on row {index}"
                ) from exc
            seen.add(extension_id)
            extensions.append(
                LicensedExtension(
                    extension_id=extension_id,
                    extension_name=content[0],
                    data_class=content[1],
                    provider=content[2],
                    access_model=access_model,
                    price_display=content[3],
                    price_basis=content[4],
                    coverage=content[5],
                    status=status,
                    allowed_mode=allowed_mode,
                    public_output_status=public_output,
                    official_url=content[6],
                    pricing_url=content[7],
                    terms_url=content[8],
                    reviewed_on=reviewed_on,
                    review_note=content[9],
                )
            )
        return extensions


def build_licensed_extensions_snapshot(
    extensions: list[LicensedExtension], as_of: date
) -> dict[str, Any]:
    if any(extension.reviewed_on > as_of for extension in extensions):
        raise LicensedExtensionDataError(
            "Licensed extension catalog includes a review after the report cutoff."
        )
    statuses = Counter(extension.status for extension in extensions)
    return {
        "market_focus": "U.S. Financials",
        "mode": "bring_your_own_license",
        "as_of": as_of.isoformat(),
        "included_in_open_edition_cost": False,
        "extension_count": len(extensions),
        "listed_price_count": sum(
            extension.price_display != "Quote required" for extension in extensions
        ),
        "individual_option_count": sum(
            extension.allowed_mode == "individual_user_license"
            for extension in extensions
        ),
        "quote_required_count": statuses["quote_required"],
        "public_output_approved_count": sum(
            extension.public_output_status == "approved_public_output"
            for extension in extensions
        ),
        "policy_note": (
            "Open Edition does not require these providers. A user may process data "
            "obtained under their own license only for uses that license permits. "
            "MarketWitness does not bundle restricted rows or publish shared real "
            "rankings without written output rights."
        ),
        "items": [_extension_payload(extension) for extension in extensions],
    }


def _extension_payload(extension: LicensedExtension) -> dict[str, str]:
    return {
        "extension_id": extension.extension_id,
        "extension_name": extension.extension_name,
        "data_class": extension.data_class,
        "provider": extension.provider,
        "access_model": extension.access_model,
        "price_display": extension.price_display,
        "price_basis": extension.price_basis,
        "coverage": extension.coverage,
        "status": extension.status,
        "allowed_mode": extension.allowed_mode,
        "public_output_status": extension.public_output_status,
        "official_url": extension.official_url,
        "pricing_url": extension.pricing_url,
        "terms_url": extension.terms_url,
        "reviewed_on": extension.reviewed_on.isoformat(),
        "review_note": extension.review_note,
    }


def render_licensed_extensions_report(snapshot: dict[str, Any]) -> str:
    lines = [
        "# Licensed Extensions Catalog",
        "",
        f"- Market focus: `{snapshot['market_focus']}`",
        f"- Reviewed as of: `{snapshot['as_of']}`",
        f"- Optional providers tracked: `{snapshot['extension_count']}`",
        f"- Providers with a listed price: `{snapshot['listed_price_count']}`",
        f"- Individual-license options: `{snapshot['individual_option_count']}`",
        f"- Approved for public output: `{snapshot['public_output_approved_count']}`",
        "",
        snapshot["policy_note"],
        "",
        "## Optional Data Paths",
        "",
        "| Provider | Price Visible | Coverage | Mode | Public Output |",
        "|---|---|---|---|---|",
    ]
    for item in snapshot["items"]:
        lines.append(
            f"| {item['extension_name']} | {item['price_display']} | "
            f"{item['coverage']} | `{item['allowed_mode']}` | "
            f"`{item['public_output_status']}` |"
        )
    lines.extend(["", "## Review Notes", ""])
    for item in snapshot["items"]:
        lines.extend(
            [
                f"### {item['extension_name']}",
                "",
                f"- Price basis: {item['price_basis']}",
                f"- Source: [{item['official_url']}]({item['official_url']})",
                f"- Pricing: [{item['pricing_url']}]({item['pricing_url']})",
                f"- Terms: [{item['terms_url']}]({item['terms_url']})",
                f"- Note: {item['review_note']}",
                "",
            ]
        )
    return "\n".join(lines)


def write_licensed_extensions_report(path: str | Path, snapshot: dict[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_licensed_extensions_report(snapshot), encoding="utf-8")


def render_licensed_extensions_html(snapshot: dict[str, Any]) -> str:
    rows = "".join(
        "<tr>"
        f"<td data-label=\"Provider\"><strong>{escape(item['extension_name'])}</strong><small>{escape(item['provider'])}</small></td>"
        f"<td data-label=\"Listed price\">{escape(item['price_display'])}<small>{escape(item['price_basis'])}</small></td>"
        f"<td data-label=\"Coverage\">{escape(item['coverage'])}</td>"
        f"<td data-label=\"Public output\"><span class=\"pill {escape(item['public_output_status'])}\">{escape(item['public_output_status'])}</span></td>"
        f"<td data-label=\"Links\"><a href=\"{escape(item['pricing_url'])}\">Price</a><small><a href=\"{escape(item['terms_url'])}\">Terms</a></small></td>"
        "</tr>"
        for item in snapshot["items"]
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MarketWitness | Licensed Extensions</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;--red:#ff7d72;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1180px;margin:auto;padding:30px 28px}}nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}h1{{font-size:clamp(36px,5vw,56px);line-height:1.06;margin:38px 0 14px}}.lead{{color:var(--muted);font-size:17px;max-width:880px}}.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:34px 0}}.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px}}.card p{{margin:0;color:var(--muted)}}.card strong{{display:block;font-size:35px;color:var(--mint)}}.notice{{border-left:3px solid var(--gold);padding:15px 18px;color:var(--muted)}}.table-wrap{{margin-top:18px;overflow:hidden}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{color:var(--muted);font-size:12px;text-transform:uppercase;font-weight:500}}td small{{display:block;color:var(--muted);max-width:300px}}a{{color:var(--mint);text-decoration:none}}.pill{{display:inline-block;border-radius:999px;padding:5px 9px;font-size:12px}}.requires_separate_written_rights,.requires_negotiated_public_output_rights{{color:var(--gold);background:rgba(240,188,98,.12)}}.approved_public_output{{color:var(--mint);background:rgba(86,218,172,.12)}}@media(max-width:880px){{.cards{{grid-template-columns:1fr}}.table-wrap{{background:transparent;border:0;overflow:visible}}thead{{display:none}}table,tbody,tr,td{{display:block;width:100%}}tr{{background:var(--panel);border:1px solid var(--line);border-radius:14px;margin-bottom:14px;padding:11px 15px}}td{{border:0;padding:9px 0 9px 126px;min-height:40px;position:relative}}td::before{{content:attr(data-label);position:absolute;left:0;top:10px;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.06em}}}}
</style></head><body><header><nav>MarketWitness / Licensed Extensions</nav><h1>Bring your own<br>licensed data.</h1>
<p class="lead">{escape(snapshot['policy_note'])}</p><p class="meta">Reviewed as of {escape(snapshot['as_of'])}</p>
<section class="cards"><article class="card"><p>Optional providers</p><strong>{snapshot['extension_count']}</strong></article><article class="card"><p>Listed prices</p><strong>{snapshot['listed_price_count']}</strong></article><article class="card"><p>Individual paths</p><strong>{snapshot['individual_option_count']}</strong></article><article class="card"><p>Public-output approved</p><strong>{snapshot['public_output_approved_count']}</strong></article></section></header>
<main><p class="notice">A paid individual subscription can support private research only when its terms allow it. It does not enable MarketWitness to publish a shared leaderboard of real analyst results.</p><h2>Optional Providers</h2><div class="table-wrap"><table><thead><tr><th>Provider</th><th>Listed Price</th><th>Coverage</th><th>Public Output</th><th>Official Links</th></tr></thead><tbody>{rows}</tbody></table></div></main></body></html>"""


def write_licensed_extensions_html(path: str | Path, snapshot: dict[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_licensed_extensions_html(snapshot), encoding="utf-8")
