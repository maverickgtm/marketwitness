from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, localcontext
from pathlib import Path
from statistics import median

from . import METHODOLOGY_VERSION
from .models import Evaluation

WILSON_Z_95 = Decimal("1.959963984540054")


def write_markdown_report(
    path: str | Path,
    evaluations: list[Evaluation],
    as_of: date,
    minimum_sample: int,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_markdown_report(evaluations, as_of, minimum_sample), encoding="utf-8"
    )


def render_markdown_report(
    evaluations: list[Evaluation],
    as_of: date,
    minimum_sample: int,
) -> str:
    statuses = Counter(item.status for item in evaluations)
    evaluated = [item for item in evaluations if item.status == "evaluated"]
    by_firm: defaultdict[str, list[Evaluation]] = defaultdict(list)
    for item in evaluated:
        by_firm[item.firm].append(item)

    firms = []
    for firm, rows in by_firm.items():
        if len(rows) >= minimum_sample:
            firms.append((_hit_rate(rows), len(rows), firm, rows))
    firms.sort(key=lambda item: (-item[0], -item[1], item[2].lower()))

    lines = [
        "# TargetAudit Report",
        "",
        f"- Methodology version: `{METHODOLOGY_VERSION}`",
        f"- Calculated as of: `{as_of.isoformat()}`",
        f"- Minimum firm sample in ranking: `{minimum_sample}`",
        f"- Input observations: `{len(evaluations)}`",
        f"- Evaluated: `{statuses['evaluated']}`",
        f"- Excluded: `{statuses['excluded']}`",
        f"- Pending: `{statuses['pending']}`",
        "- Hit-rate uncertainty: `95% Wilson score interval`",
        "",
        "## Firm Ranking",
        "",
    ]
    if not firms:
        lines.append("No firm meets the configured minimum sample.")
    else:
        lines.extend(
            [
                "| Firm | N | Target Hit Rate | Hit Rate 95% CI | Mean Terminal Error | Median Days To Hit | Mean Excess Return |",
                "|---|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for _, count, firm, rows in firms:
            lines.append(
                "| {firm} | {count} | {hit} | {confidence} | {error} | {days} | {excess} |".format(
                    firm=firm,
                    count=count,
                    hit=_pct(_hit_rate(rows)),
                    confidence=_format_hit_rate_interval(rows),
                    error=_pct(_mean_present(rows, "terminal_absolute_error_pct")),
                    days=_median_hit_days(rows),
                    excess=_pct(_mean_present(rows, "excess_return_pct")),
                )
            )

    reason_counts = Counter(
        item.reason for item in evaluations if item.status != "evaluated" and item.reason
    )
    lines.extend(["", "## Exclusions And Pending"])
    if not reason_counts:
        lines.extend(["", "No observations were excluded or pending."])
    else:
        lines.extend(["", "| Reason | Rows |", "|---|---:|"])
        for reason, count in sorted(reason_counts.items()):
            lines.append(f"| `{reason}` | {count} |")

    lines.extend(
        [
            "",
            "## Direction Breakdown",
            "",
            "| Direction | N | Target Hit Rate | Hit Rate 95% CI | Mean Terminal Error | Mean Excess Return |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for direction in ("up", "down"):
        rows = [item for item in evaluated if item.direction == direction]
        if rows:
            lines.append(
                "| {direction} | {count} | {hit} | {confidence} | {error} | {excess} |".format(
                    direction=direction,
                    count=len(rows),
                    hit=_pct(_hit_rate(rows)),
                    confidence=_format_hit_rate_interval(rows),
                    error=_pct(_mean_present(rows, "terminal_absolute_error_pct")),
                    excess=_pct(_mean_present(rows, "excess_return_pct")),
                )
            )
    if not evaluated:
        lines.append("| - | 0 | - | - | - | - |")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "A target hit only indicates that an adjusted daily high or low reached the",
            "published target during the evaluation horizon. It is not evidence that an",
            "investor captured that price or outperformed the market.",
            "",
            "The 95% Wilson interval quantifies sampling uncertainty in each observed",
            "hit rate. Wide intervals, especially for small N, should prevent strong",
            "comparisons between firms even when their point estimates differ.",
            "",
        ]
    )
    return "\n".join(lines)


def _hit_rate(rows: list[Evaluation]) -> Decimal:
    hits = sum(1 for row in rows if row.hit)
    return Decimal(hits) / Decimal(len(rows))


def wilson_interval(hits: int, total: int) -> tuple[Decimal, Decimal]:
    if total <= 0 or hits < 0 or hits > total:
        raise ValueError("Wilson interval requires hits between zero and total.")
    with localcontext() as context:
        context.prec = 40
        n = Decimal(total)
        proportion = Decimal(hits) / n
        z_squared = WILSON_Z_95 * WILSON_Z_95
        denominator = Decimal("1") + z_squared / n
        center = (proportion + z_squared / (Decimal("2") * n)) / denominator
        spread = (
            WILSON_Z_95
            * (
                (proportion * (Decimal("1") - proportion) / n)
                + z_squared / (Decimal("4") * n * n)
            ).sqrt()
            / denominator
        )
        return max(Decimal("0"), center - spread), min(Decimal("1"), center + spread)


def _format_hit_rate_interval(rows: list[Evaluation]) -> str:
    hits = sum(1 for row in rows if row.hit)
    low, high = wilson_interval(hits, len(rows))
    return f"{_pct(low)} to {_pct(high)}"


def _mean_present(rows: list[Evaluation], field: str) -> Decimal | None:
    values = [getattr(row, field) for row in rows if getattr(row, field) is not None]
    if not values:
        return None
    return sum(values, Decimal("0")) / Decimal(len(values))


def _median_hit_days(rows: list[Evaluation]) -> str:
    values = [row.days_to_target for row in rows if row.days_to_target is not None]
    if not values:
        return "-"
    return str(int(median(values)))


def _pct(value: Decimal | None) -> str:
    if value is None:
        return "-"
    return f"{value * Decimal('100'):.2f}%"
