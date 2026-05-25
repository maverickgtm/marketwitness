from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from html import escape
from pathlib import Path

RWA_COLUMNS = {
    "token_symbol",
    "reference_symbol",
    "reference_name",
    "issuer_model",
    "network",
    "venue",
    "observed_on",
    "backing_status",
    "reference_price",
    "token_price",
    "source_layer",
    "source_url",
}
SYNTHETIC_LAYER = "synthetic_demo"


class RwaWatchDataError(ValueError):
    """Raised when a tokenized-asset observation is not safe to display."""


@dataclass(frozen=True)
class RwaObservation:
    token_symbol: str
    reference_symbol: str
    reference_name: str
    issuer_model: str
    network: str
    venue: str
    observed_on: date
    backing_status: str
    reference_price: Decimal
    token_price: Decimal
    source_layer: str
    source_url: str

    @property
    def deviation_pct(self) -> Decimal:
        return ((self.token_price - self.reference_price) / self.reference_price) * Decimal("100")

    @property
    def deviation_state(self) -> str:
        if self.deviation_pct >= Decimal("1"):
            return "premium_over_1pct"
        if self.deviation_pct <= Decimal("-1"):
            return "discount_over_1pct"
        return "tracks_reference"


def load_rwa_observations(path: str | Path, as_of: date) -> list[RwaObservation]:
    try:
        with Path(path).open(newline="", encoding="utf-8") as source:
            reader = csv.DictReader(source)
            missing = sorted(RWA_COLUMNS - set(reader.fieldnames or []))
            if missing:
                raise RwaWatchDataError(
                    f"{path}: missing columns: {', '.join(missing)}"
                )
            observations = [
                _parse_observation(path, row, index, as_of)
                for index, row in enumerate(reader, start=2)
            ]
    except OSError as exc:
        raise RwaWatchDataError(f"Unable to read RWA Watch snapshot {path}: {exc}") from exc
    if not observations:
        raise RwaWatchDataError(f"{path}: snapshot contains no token observations")
    identities: set[tuple[str, str, str]] = set()
    for item in observations:
        identity = (item.token_symbol.casefold(), item.network.casefold(), item.venue.casefold())
        if identity in identities:
            raise RwaWatchDataError(
                f"{path}: duplicate token, network and venue observation for {item.token_symbol}"
            )
        identities.add(identity)
    return sorted(observations, key=lambda item: (-abs(item.deviation_pct), item.token_symbol))


def build_rwa_snapshot(observations: list[RwaObservation], as_of: date) -> dict[str, object]:
    if not observations:
        raise RwaWatchDataError("RWA Watch requires at least one observation")
    if any(item.observed_on > as_of for item in observations):
        raise RwaWatchDataError("RWA Watch observation exceeds report cutoff")
    if any(item.source_layer != SYNTHETIC_LAYER for item in observations):
        raise RwaWatchDataError(
            "RWA Watch Sandbox only accepts project-authored synthetic_demo observations"
        )
    states = Counter(item.deviation_state for item in observations)
    networks = sorted({item.network for item in observations})
    venues = sorted({item.venue for item in observations})
    maximum = max(observations, key=lambda item: abs(item.deviation_pct))
    return {
        "as_of": as_of,
        "observations": observations,
        "observation_count": len(observations),
        "network_count": len(networks),
        "venue_count": len(venues),
        "near_reference_count": states["tracks_reference"],
        "flagged_count": states["premium_over_1pct"] + states["discount_over_1pct"],
        "maximum_deviation": maximum,
        "network_names": networks,
        "venue_names": venues,
    }


def render_rwa_report(snapshot: dict[str, object]) -> str:
    observations = snapshot["observations"]
    maximum = snapshot["maximum_deviation"]
    assert isinstance(observations, list)
    assert isinstance(maximum, RwaObservation)
    lines = [
        "# RWA Watch Sandbox",
        "",
        f"- Report cutoff: `{snapshot['as_of'].isoformat()}`",
        f"- Synthetic observations: `{snapshot['observation_count']}`",
        f"- Demonstrated networks: `{snapshot['network_count']}`",
        f"- Demonstrated venues: `{snapshot['venue_count']}`",
        f"- Deviations requiring review: `{snapshot['flagged_count']}`",
        "",
        "This report contains project-authored synthetic data only. It demonstrates",
        "how tokenized-equity reference and venue prices could be audited after",
        "written display and retention rights are obtained. It is not live market",
        "data, ownership evidence or investment advice.",
        "",
        "## Synthetic Venue Observations",
        "",
        "| Token | Reference | Model | Network / Venue | Reference Price | Token Price | Deviation | State |",
        "|---|---|---|---|---:|---:|---:|---|",
    ]
    for item in observations:
        assert isinstance(item, RwaObservation)
        lines.append(
            f"| `{item.token_symbol}` | `{item.reference_symbol}` - {item.reference_name} | "
            f"{item.issuer_model} / {item.backing_status} | {item.network} / {item.venue} | "
            f"{_money(item.reference_price)} | {_money(item.token_price)} | "
            f"{_signed_percent(item.deviation_pct)} | `{item.deviation_state}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"The largest synthetic deviation is `{maximum.token_symbol}` at "
            f"`{_signed_percent(maximum.deviation_pct)}`. In a future licensed or "
            "authorized connector, a flagged deviation would require source, "
            "timestamp, liquidity and instrument-structure review before any conclusion.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_rwa_report(path: str | Path, snapshot: dict[str, object]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_rwa_report(snapshot), encoding="utf-8")


def render_rwa_html(snapshot: dict[str, object]) -> str:
    observations = snapshot["observations"]
    assert isinstance(observations, list)
    rows = "".join(
        "<tr>"
        f'<td><strong>{escape(item.token_symbol)}</strong><small>{escape(item.reference_symbol)} - {escape(item.reference_name)}</small></td>'
        f"<td>{escape(item.issuer_model)}<small>{escape(item.backing_status)}</small></td>"
        f"<td>{escape(item.network)}<small>{escape(item.venue)}</small></td>"
        f"<td>{escape(_money(item.reference_price))}</td>"
        f"<td>{escape(_money(item.token_price))}</td>"
        f'<td class="{escape(item.deviation_state)}">{escape(_signed_percent(item.deviation_pct))}</td>'
        f'<td><span class="badge {escape(item.deviation_state)}">{escape(item.deviation_state)}</span></td>'
        "</tr>"
        for item in observations
        if isinstance(item, RwaObservation)
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TargetAudit | RWA Watch Sandbox</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;--blue:#62a6ff;--red:#ff7d72;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1200px;margin:auto;padding:30px 28px}}nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}a{{color:var(--mint);text-decoration:none}}h1{{font-size:clamp(38px,5vw,58px);line-height:1.05;margin:38px 0 14px}}h2{{margin-top:42px}}.lead{{color:var(--muted);font-size:17px;max-width:900px}}.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:35px 0}}.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px}}.card p{{margin:0;color:var(--muted)}}.card strong{{font-size:38px;color:var(--mint);display:block}}.notice{{padding:15px 18px;border-left:3px solid var(--gold);color:var(--muted)}}.table-wrap{{overflow:hidden;margin-top:16px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{text-transform:uppercase;font-size:12px;color:var(--muted);font-weight:500}}td small{{display:block;color:var(--muted)}}.badge{{display:inline-block;border-radius:999px;padding:5px 9px;font-size:12px;white-space:nowrap}}.tracks_reference{{color:var(--mint);background:rgba(86,218,172,.12)}}.premium_over_1pct,.discount_over_1pct{{color:var(--gold);background:rgba(240,188,98,.12)}}td.tracks_reference,td.premium_over_1pct,td.discount_over_1pct{{background:transparent;font-weight:600}}@media(max-width:860px){{.cards{{grid-template-columns:repeat(2,1fr)}}.table-wrap{{overflow-x:auto}}table{{min-width:940px}}}}
</style></head><body><header><nav><a href="/dashboard/open">Open Edition</a> / RWA Watch / Sandbox</nav>
<h1>Tokenized assets.<br>Audited boundaries.</h1>
<p class="lead">A no-cost demonstration of issuer-first monitoring: compare a reference price with a token venue price while retaining structure, venue and policy limits.</p>
<p class="meta">Synthetic demonstration / report cutoff {snapshot['as_of'].isoformat()}</p>
<section class="cards"><article class="card"><p>Observations</p><strong>{snapshot['observation_count']}</strong></article><article class="card"><p>Networks</p><strong>{snapshot['network_count']}</strong></article><article class="card"><p>Venues</p><strong>{snapshot['venue_count']}</strong></article><article class="card"><p>Review flags</p><strong>{snapshot['flagged_count']}</strong></article></section></header>
<main><p class="notice"><strong>Synthetic data only.</strong> No xStocks, Ondo or exchange market data is collected here. Official xStocks/Backed terms reviewed on 2026-05-24 do not establish public automated republication rights; live ingestion remains blocked pending written authorization.</p>
<h2>Synthetic Venue Observations</h2><div class="table-wrap"><table><thead><tr><th>Token / Reference</th><th>Issuer Model</th><th>Network / Venue</th><th>Reference</th><th>Token</th><th>Deviation</th><th>State</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="meta">A deviation flag is research triage only, never a trading signal or position recommendation.</p></main></body></html>"""


def write_rwa_html(path: str | Path, snapshot: dict[str, object]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_rwa_html(snapshot), encoding="utf-8")


def _parse_observation(
    path: str | Path, row: dict[str, str], index: int, as_of: date
) -> RwaObservation:
    required = [row.get(column, "").strip() for column in RWA_COLUMNS]
    if not all(required):
        raise RwaWatchDataError(f"{path}: incomplete RWA observation row {index}")
    try:
        observed_on = date.fromisoformat(row["observed_on"].strip())
        reference_price = Decimal(row["reference_price"].strip())
        token_price = Decimal(row["token_price"].strip())
    except (ValueError, InvalidOperation) as exc:
        raise RwaWatchDataError(f"{path}: invalid price or date on row {index}") from exc
    if observed_on > as_of:
        raise RwaWatchDataError(f"{path}: observation exceeds evidence cutoff on row {index}")
    if (
        not reference_price.is_finite()
        or not token_price.is_finite()
        or reference_price <= 0
        or token_price < 0
    ):
        raise RwaWatchDataError(f"{path}: invalid price on row {index}")
    if row["source_layer"].strip() != SYNTHETIC_LAYER:
        raise RwaWatchDataError(
            f"{path}: RWA Watch Sandbox rejects non-synthetic data on row {index}"
        )
    source_url = row["source_url"].strip()
    if not source_url.startswith("https://"):
        raise RwaWatchDataError(f"{path}: non-HTTPS source URL on row {index}")
    return RwaObservation(
        token_symbol=row["token_symbol"].strip(),
        reference_symbol=row["reference_symbol"].strip(),
        reference_name=row["reference_name"].strip(),
        issuer_model=row["issuer_model"].strip(),
        network=row["network"].strip(),
        venue=row["venue"].strip(),
        observed_on=observed_on,
        backing_status=row["backing_status"].strip(),
        reference_price=reference_price,
        token_price=token_price,
        source_layer=SYNTHETIC_LAYER,
        source_url=source_url,
    )


def _money(value: Decimal) -> str:
    return f"USD {value:,.2f}"


def _signed_percent(value: Decimal) -> str:
    return f"{value:+.2f}%"
