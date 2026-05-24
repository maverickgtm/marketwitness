from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from html import escape
from pathlib import Path

from .models import TargetObservation

ACTION_TYPES = {"stock_split", "reverse_split", "ticker_change"}
EVIDENCE_LEVELS = {
    "synthetic_demo",
    "exchange_notice",
    "issuer_official_release",
    "regulatory_filing",
}
CORPORATE_ACTION_COLUMNS = {
    "action_id",
    "company_name",
    "prior_ticker",
    "current_ticker",
    "action_type",
    "effective_date",
    "split_ratio_new",
    "split_ratio_old",
    "evidence_level",
    "source_title",
    "source_url",
    "verified_on",
    "review_note",
}


class CorporateActionDataError(ValueError):
    """Raised when a corporate-action record cannot support an audit."""


@dataclass(frozen=True)
class CorporateAction:
    action_id: str
    company_name: str
    prior_ticker: str
    current_ticker: str
    action_type: str
    effective_date: date
    split_ratio_new: Decimal | None
    split_ratio_old: Decimal | None
    evidence_level: str
    source_title: str
    source_url: str
    verified_on: date
    review_note: str

    @property
    def adjustment_detail(self) -> str:
        if self.action_type == "ticker_change":
            return f"{self.prior_ticker} -> {self.current_ticker}"
        return f"{self.split_ratio_new}:{self.split_ratio_old}"


@dataclass(frozen=True)
class AffectedObservation:
    observation_id: str
    company_name: str
    target_ticker: str
    published_date: date
    expiry_date: date
    action: CorporateAction
    review_action: str


def load_corporate_actions(path: str | Path) -> list[CorporateAction]:
    with Path(path).open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        missing = sorted(CORPORATE_ACTION_COLUMNS - set(reader.fieldnames or []))
        if missing:
            raise CorporateActionDataError(
                f"{path}: missing columns: {', '.join(missing)}"
            )
        actions: list[CorporateAction] = []
        seen_ids: set[str] = set()
        for index, row in enumerate(reader, start=2):
            action_id = row["action_id"].strip()
            action_type = row["action_type"].strip()
            evidence_level = row["evidence_level"].strip()
            if not action_id or action_id in seen_ids:
                raise CorporateActionDataError(
                    f"{path}: blank or duplicate action id on row {index}"
                )
            if action_type not in ACTION_TYPES:
                raise CorporateActionDataError(f"{path}: invalid action type on row {index}")
            if evidence_level not in EVIDENCE_LEVELS:
                raise CorporateActionDataError(
                    f"{path}: invalid evidence level on row {index}"
                )
            try:
                effective_date = date.fromisoformat(row["effective_date"].strip())
                verified_on = date.fromisoformat(row["verified_on"].strip())
            except ValueError as exc:
                raise CorporateActionDataError(f"{path}: invalid date on row {index}") from exc
            required = [
                row["company_name"].strip(),
                row["prior_ticker"].strip(),
                row["current_ticker"].strip(),
                row["source_title"].strip(),
                row["source_url"].strip(),
                row["review_note"].strip(),
            ]
            if not all(required):
                raise CorporateActionDataError(f"{path}: missing evidence on row {index}")
            if not row["source_url"].strip().startswith("https://"):
                raise CorporateActionDataError(f"{path}: non-HTTPS source on row {index}")
            if verified_on < effective_date:
                raise CorporateActionDataError(
                    f"{path}: verification precedes action on row {index}"
                )
            new_ratio = _optional_ratio(row["split_ratio_new"], path, index)
            old_ratio = _optional_ratio(row["split_ratio_old"], path, index)
            if action_type in {"stock_split", "reverse_split"}:
                if new_ratio is None or old_ratio is None or new_ratio == old_ratio:
                    raise CorporateActionDataError(
                        f"{path}: split requires a non-flat ratio on row {index}"
                    )
            elif new_ratio is not None or old_ratio is not None:
                raise CorporateActionDataError(
                    f"{path}: ticker change cannot specify a split ratio on row {index}"
                )
            seen_ids.add(action_id)
            actions.append(
                CorporateAction(
                    action_id=action_id,
                    company_name=row["company_name"].strip(),
                    prior_ticker=row["prior_ticker"].strip().upper(),
                    current_ticker=row["current_ticker"].strip().upper(),
                    action_type=action_type,
                    effective_date=effective_date,
                    split_ratio_new=new_ratio,
                    split_ratio_old=old_ratio,
                    evidence_level=evidence_level,
                    source_title=row["source_title"].strip(),
                    source_url=row["source_url"].strip(),
                    verified_on=verified_on,
                    review_note=row["review_note"].strip(),
                )
            )
        return actions


def find_affected_observations(
    observations: list[TargetObservation], actions: list[CorporateAction], as_of: date
) -> list[AffectedObservation]:
    _validate_as_of(actions, as_of)
    affected: list[AffectedObservation] = []
    for observation in observations:
        if observation.published_date is None or observation.horizon_days is None:
            continue
        expiry = observation.published_date + timedelta(days=observation.horizon_days)
        for action in actions:
            if (
                observation.ticker == action.prior_ticker
                and observation.published_date < action.effective_date <= expiry
            ):
                affected.append(
                    AffectedObservation(
                        observation_id=observation.observation_id,
                        company_name=observation.company_name,
                        target_ticker=observation.ticker,
                        published_date=observation.published_date,
                        expiry_date=expiry,
                        action=action,
                        review_action=_review_action(action),
                    )
                )
    return affected


def has_action_in_observation_window(
    observation: TargetObservation, actions: list[CorporateAction], as_of: date
) -> bool:
    return bool(find_affected_observations([observation], actions, as_of))


def write_affected_observations_csv(
    path: str | Path, affected: list[AffectedObservation]
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "observation_id",
        "company_name",
        "target_ticker",
        "published_date",
        "expiry_date",
        "action_id",
        "action_type",
        "effective_date",
        "adjustment_detail",
        "evidence_level",
        "source_url",
        "review_action",
    ]
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fields)
        writer.writeheader()
        for item in affected:
            writer.writerow(
                {
                    "observation_id": item.observation_id,
                    "company_name": item.company_name,
                    "target_ticker": item.target_ticker,
                    "published_date": item.published_date.isoformat(),
                    "expiry_date": item.expiry_date.isoformat(),
                    "action_id": item.action.action_id,
                    "action_type": item.action.action_type,
                    "effective_date": item.action.effective_date.isoformat(),
                    "adjustment_detail": item.action.adjustment_detail,
                    "evidence_level": item.action.evidence_level,
                    "source_url": item.action.source_url,
                    "review_action": item.review_action,
                }
            )


def render_corporate_actions_report(
    actions: list[CorporateAction],
    affected: list[AffectedObservation],
    as_of: date,
) -> str:
    _validate_as_of(actions, as_of)
    counts = Counter(action.action_type for action in actions)
    lines = [
        "# Corporate Actions Audit",
        "",
        f"- Verified as of: `{as_of.isoformat()}`",
        f"- Documented actions: `{len(actions)}`",
        f"- Stock splits: `{counts['stock_split']}`",
        f"- Reverse splits: `{counts['reverse_split']}`",
        f"- Ticker changes: `{counts['ticker_change']}`",
        f"- Target observations requiring review: `{len(affected)}`",
        "",
        "An affected target must not enter the scored ranking until its nominal",
        "target and price history are proven comparable across the corporate action.",
        "This audit flags work; it does not silently adjust a target.",
        "",
        "## Affected Targets",
        "",
        "| Target | Company | Window | Action | Effective | Detail | Required Review |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in affected:
        lines.append(
            f"| {item.observation_id} | {item.company_name} | "
            f"{item.published_date.isoformat()} to {item.expiry_date.isoformat()} | "
            f"`{item.action.action_type}` | {item.action.effective_date.isoformat()} | "
            f"{item.action.adjustment_detail} | {item.review_action} |"
        )
    lines.extend(["", "## Evidence Registry", ""])
    for action in sorted(actions, key=lambda item: item.effective_date, reverse=True):
        lines.extend(
            [
                f"### {action.company_name} - {action.action_type}",
                "",
                f"- Effective date: {action.effective_date.isoformat()}",
                f"- Detail: {action.adjustment_detail}",
                f"- Evidence level: `{action.evidence_level}`",
                f"- Source: [{action.source_title}]({action.source_url})",
                f"- Note: {action.review_note}",
                "",
            ]
        )
    return "\n".join(lines)


def write_corporate_actions_report(
    path: str | Path,
    actions: list[CorporateAction],
    affected: list[AffectedObservation],
    as_of: date,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_corporate_actions_report(actions, affected, as_of), encoding="utf-8"
    )


def render_corporate_actions_html(
    actions: list[CorporateAction],
    affected: list[AffectedObservation],
    as_of: date,
) -> str:
    _validate_as_of(actions, as_of)
    counts = Counter(action.action_type for action in actions)
    rows = "".join(
        "<tr>"
        f'<td data-label="Target"><strong>{escape(item.observation_id)}</strong><small>{escape(item.company_name)}</small></td>'
        f'<td data-label="Target window">{escape(item.published_date.isoformat())}<small>to {escape(item.expiry_date.isoformat())}</small></td>'
        f'<td data-label="Action"><span class="badge {escape(item.action.action_type)}">{escape(item.action.action_type)}</span><small>{escape(item.action.adjustment_detail)}</small></td>'
        f'<td data-label="Effective">{escape(item.action.effective_date.isoformat())}</td>'
        f'<td data-label="Review">{escape(item.review_action)}<small><a href="{escape(item.action.source_url)}">Evidence</a></small></td>'
        "</tr>"
        for item in affected
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TargetAudit | Corporate Actions Audit</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;--blue:#62a6ff;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1180px;margin:auto;padding:30px 28px}}
nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}h1{{font-size:clamp(34px,5vw,54px);line-height:1.06;margin:38px 0 14px}}.lead{{color:var(--muted);font-size:17px;max-width:820px}}.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:35px 0}}.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px}}.card p{{margin:0;color:var(--muted)}}.card strong{{font-size:38px;color:var(--mint);display:block}}.notice{{border-left:3px solid var(--gold);color:var(--muted);padding:15px 18px}}h2{{margin-top:42px}}.table-wrap{{overflow:hidden;margin-top:16px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{text-transform:uppercase;font-size:12px;color:var(--muted);font-weight:500}}td small{{display:block;color:var(--muted)}}a{{color:var(--mint);text-decoration:none}}.badge{{border-radius:999px;padding:5px 9px;font-size:12px;white-space:nowrap}}.stock_split{{color:var(--gold);background:rgba(240,188,98,.12)}}.reverse_split{{color:var(--blue);background:rgba(98,166,255,.12)}}.ticker_change{{color:var(--mint);background:rgba(86,218,172,.12)}}
@media(max-width:820px){{.cards{{grid-template-columns:repeat(2,1fr)}}.table-wrap{{background:transparent;border:0;overflow:visible}}thead{{display:none}}table,tbody,tr,td{{display:block;width:100%}}tr{{background:var(--panel);border:1px solid var(--line);border-radius:14px;margin-bottom:14px;padding:10px 15px}}td{{border:0;padding:9px 0 9px 116px;min-height:39px;position:relative}}td::before{{content:attr(data-label);position:absolute;left:0;top:10px;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.06em}}}}
</style></head><body><header><nav>TargetAudit / Financials Scorecard / Corporate Actions</nav>
<h1>Comparable targets.<br>Corporate action audit.</h1><p class="lead">Splits and ticker transitions that cross an analyst target horizon must be resolved before scoring.</p>
<p class="meta">Verified as of {escape(as_of.isoformat())}</p><section class="cards"><article class="card"><p>Actions</p><strong>{len(actions)}</strong></article><article class="card"><p>Affected targets</p><strong>{len(affected)}</strong></article><article class="card"><p>Splits</p><strong>{counts['stock_split'] + counts['reverse_split']}</strong></article><article class="card"><p>Ticker changes</p><strong>{counts['ticker_change']}</strong></article></section></header>
<main><p class="notice">Affected observations are excluded from scored evaluation when this registry is supplied. TargetAudit flags the conflict; it does not invent a split-adjusted target or assume symbol continuity.</p>
<h2>Review queue</h2><div class="table-wrap"><table><thead><tr><th>Target</th><th>Window</th><th>Action</th><th>Effective</th><th>Required review</th></tr></thead><tbody>{rows}</tbody></table></div></main></body></html>"""


def write_corporate_actions_html(
    path: str | Path,
    actions: list[CorporateAction],
    affected: list[AffectedObservation],
    as_of: date,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_corporate_actions_html(actions, affected, as_of), encoding="utf-8"
    )


def _optional_ratio(raw: str, path: str | Path, index: int) -> Decimal | None:
    if not raw.strip():
        return None
    try:
        value = Decimal(raw.strip())
    except InvalidOperation as exc:
        raise CorporateActionDataError(f"{path}: invalid split ratio on row {index}") from exc
    if not value.is_finite() or value <= 0:
        raise CorporateActionDataError(f"{path}: invalid split ratio on row {index}")
    return value


def _review_action(action: CorporateAction) -> str:
    if action.action_type == "ticker_change":
        return "Confirm price-series continuity across old and new ticker before scoring."
    return "Normalize the historical target to the split basis of adjusted prices before scoring."


def _validate_as_of(actions: list[CorporateAction], as_of: date) -> None:
    if any(action.effective_date > as_of or action.verified_on > as_of for action in actions):
        raise CorporateActionDataError(
            "Corporate-action registry includes evidence after the report cutoff."
        )
