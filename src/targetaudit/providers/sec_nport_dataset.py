from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from ..etf_holdings import Holding
from .sec_nport import (
    SEC_NPORT_DATASETS_URL,
    SHARE_UNITS,
    SecNportDataError,
    SecNportImport,
)

REQUIRED_TABLES = {
    "SUBMISSION.tsv": {
        "ACCESSION_NUMBER",
        "FILING_DATE",
        "SUB_TYPE",
        "REPORT_DATE",
    },
    "REGISTRANT.tsv": {
        "ACCESSION_NUMBER",
        "REGISTRANT_NAME",
    },
    "FUND_REPORTED_INFO.tsv": {
        "ACCESSION_NUMBER",
        "SERIES_NAME",
        "SERIES_ID",
    },
    "FUND_REPORTED_HOLDING.tsv": {
        "ACCESSION_NUMBER",
        "HOLDING_ID",
        "ISSUER_NAME",
        "ISSUER_CUSIP",
        "BALANCE",
        "UNIT",
        "PERCENTAGE",
    },
    "IDENTIFIERS.tsv": {
        "HOLDING_ID",
        "IDENTIFIER_TICKER",
    },
}
_SYMBOL_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9.:\-]{0,29}$")


@dataclass(frozen=True)
class SecNportDatasetSnapshot:
    accession_number: str
    filing_date: date
    import_result: SecNportImport


@dataclass(frozen=True)
class SecNportDatasetBackfill:
    data_set_label: str
    series_id: str
    fund_symbol: str
    captured_on: date
    source_url: str
    snapshots: tuple[SecNportDatasetSnapshot, ...]


def load_nport_dataset_backfill(
    directory: str | Path | list[str | Path],
    series_id: str,
    fund_symbol: str,
    captured_on: date,
    data_set_label: str,
    source_url: str = SEC_NPORT_DATASETS_URL,
    synthetic_fixture: bool = False,
) -> SecNportDatasetBackfill:
    requested_series = _series_id(series_id)
    symbol = _symbol(fund_symbol)
    if not data_set_label.strip():
        raise SecNportDataError("SEC N-PORT dataset label is required.")
    if not source_url.startswith("https://"):
        raise SecNportDataError("SEC N-PORT dataset source URL must use HTTPS.")
    snapshots: list[SecNportDatasetSnapshot] = []
    for root in _directories(directory):
        snapshots.extend(
            _load_directory_snapshots(
                root,
                requested_series,
                symbol,
                captured_on,
                source_url,
                synthetic_fixture,
            )
        )
    if not snapshots:
        raise SecNportDataError(
            f"SEC N-PORT dataset contains no usable periods for series {requested_series}."
        )
    snapshots.sort(key=lambda snapshot: snapshot.import_result.effective_date)
    effective_dates = [snapshot.import_result.effective_date for snapshot in snapshots]
    if len(set(effective_dates)) != len(effective_dates):
        raise SecNportDataError(
            "SEC N-PORT dataset contains duplicate periods; amendments require review."
        )
    return SecNportDatasetBackfill(
        data_set_label=data_set_label.strip(),
        series_id=requested_series,
        fund_symbol=symbol,
        captured_on=captured_on,
        source_url=source_url,
        snapshots=tuple(snapshots),
    )


def _load_directory_snapshots(
    root: Path,
    requested_series: str,
    symbol: str,
    captured_on: date,
    source_url: str,
    synthetic_fixture: bool,
) -> list[SecNportDatasetSnapshot]:
    tables = {
        filename: _read_table(root / filename, fields)
        for filename, fields in REQUIRED_TABLES.items()
    }
    submissions = _index_accession(tables["SUBMISSION.tsv"], "SUBMISSION.tsv")
    registrants = _index_accession(tables["REGISTRANT.tsv"], "REGISTRANT.tsv")
    funds = _index_accession(tables["FUND_REPORTED_INFO.tsv"], "FUND_REPORTED_INFO.tsv")
    holdings_by_accession = _group_by(
        tables["FUND_REPORTED_HOLDING.tsv"], "ACCESSION_NUMBER"
    )
    identifiers_by_holding = _group_by(tables["IDENTIFIERS.tsv"], "HOLDING_ID")
    snapshots = []
    for accession, fund in funds.items():
        if fund["SERIES_ID"].strip().upper() != requested_series:
            continue
        submission = submissions.get(accession)
        registrant = registrants.get(accession)
        if submission is None or registrant is None:
            raise SecNportDataError(
                f"SEC N-PORT dataset accession {accession} lacks linked metadata."
            )
        if submission["SUB_TYPE"].strip() not in {"NPORT-P", "NPORT-P/A"}:
            continue
        filing_date = _date_field(submission["FILING_DATE"], "FILING_DATE", accession)
        effective_date = _date_field(submission["REPORT_DATE"], "REPORT_DATE", accession)
        if filing_date > captured_on or effective_date > captured_on:
            continue
        raw_holdings = holdings_by_accession.get(accession, [])
        import_result = _make_import(
            accession,
            symbol,
            requested_series,
            fund,
            registrant,
            effective_date,
            captured_on,
            raw_holdings,
            identifiers_by_holding,
            source_url,
            synthetic_fixture,
        )
        snapshots.append(
            SecNportDatasetSnapshot(
                accession_number=accession,
                filing_date=filing_date,
                import_result=import_result,
            )
        )
    return snapshots


def write_backfill_snapshots(
    output_dir: str | Path, backfill: SecNportDatasetBackfill
) -> list[Path]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    outputs = []
    for snapshot in backfill.snapshots:
        output = destination / f"{backfill.fund_symbol.lower()}-{snapshot.import_result.effective_date}.csv"
        with output.open("w", newline="", encoding="utf-8") as target:
            writer = csv.DictWriter(target, fieldnames=list(Holding.__annotations__))
            writer.writeheader()
            for holding in snapshot.import_result.holdings:
                row = dict(holding.__dict__)
                row["effective_date"] = holding.effective_date.isoformat()
                row["captured_on"] = holding.captured_on.isoformat()
                writer.writerow(row)
        outputs.append(output)
    return outputs


def write_backfill_manifest(path: str | Path, backfill: SecNportDatasetBackfill) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(
            target,
            fieldnames=[
                "data_set_label",
                "series_id",
                "fund_symbol",
                "accession_number",
                "filing_date",
                "effective_date",
                "positions_normalized",
                "positions_omitted",
                "source_url",
            ],
        )
        writer.writeheader()
        for snapshot in backfill.snapshots:
            imported = snapshot.import_result
            writer.writerow(
                {
                    "data_set_label": backfill.data_set_label,
                    "series_id": backfill.series_id,
                    "fund_symbol": backfill.fund_symbol,
                    "accession_number": snapshot.accession_number,
                    "filing_date": snapshot.filing_date.isoformat(),
                    "effective_date": imported.effective_date.isoformat(),
                    "positions_normalized": len(imported.holdings),
                    "positions_omitted": imported.omitted_non_share_positions,
                    "source_url": backfill.source_url,
                }
            )


def render_backfill_report(backfill: SecNportDatasetBackfill) -> str:
    lines = [
        "# SEC N-PORT Historical Backfill",
        "",
        f"- Data set: `{backfill.data_set_label}`",
        f"- Fund: `{backfill.fund_symbol}`",
        f"- Series ID: `{backfill.series_id}`",
        "- Source frequency layer: `regulatory_periodic`",
        f"- Captured on: `{backfill.captured_on.isoformat()}`",
        f"- Usable periods normalized: `{len(backfill.snapshots)}`",
        f"- SEC data-set source: <{backfill.source_url}>",
        "",
        "The quarterly SEC data set is filing-derived public regulatory evidence,",
        "not a daily holdings feed. Periods after the capture cutoff are excluded.",
        "If amendments create duplicate reporting periods, the import stops for",
        "manual review instead of choosing a version silently.",
        "",
        "## Periods",
        "",
        "| Report Date | Accession | Filing Date | Share Positions | Omitted |",
        "|---|---|---|---:|---:|",
    ]
    for snapshot in backfill.snapshots:
        imported = snapshot.import_result
        lines.append(
            f"| {imported.effective_date.isoformat()} | "
            f"`{snapshot.accession_number}` | {snapshot.filing_date.isoformat()} | "
            f"{len(imported.holdings)} | {imported.omitted_non_share_positions} |"
        )
    lines.append("")
    return "\n".join(lines)


def write_backfill_report(path: str | Path, backfill: SecNportDatasetBackfill) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_backfill_report(backfill), encoding="utf-8")


def _make_import(
    accession: str,
    fund_symbol: str,
    series_id: str,
    fund: dict[str, str],
    registrant: dict[str, str],
    effective_date: date,
    captured_on: date,
    rows: list[dict[str, str]],
    identifiers_by_holding: dict[str, list[dict[str, str]]],
    source_url: str,
    synthetic_fixture: bool,
) -> SecNportImport:
    issuer = (
        "TargetAudit Synthetic N-PORT Dataset Fixture"
        if synthetic_fixture
        else registrant["REGISTRANT_NAME"].strip()
    )
    holdings = []
    omitted = 0
    identifiers = set()
    for row in rows:
        if row["UNIT"].strip().upper() not in SHARE_UNITS:
            omitted += 1
            continue
        position = _holding_symbol(row, identifiers_by_holding)
        if position.casefold() in identifiers:
            raise SecNportDataError(
                f"SEC N-PORT dataset accession {accession} duplicates position {position}."
            )
        identifiers.add(position.casefold())
        shares = _decimal_field(row["BALANCE"], "BALANCE", accession)
        weight = _decimal_field(row["PERCENTAGE"], "PERCENTAGE", accession)
        if shares < 0 or weight < 0 or weight > 100:
            raise SecNportDataError(
                f"SEC N-PORT dataset accession {accession} has invalid holding amounts."
            )
        holdings.append(
            Holding(
                issuer=issuer,
                fund_symbol=fund_symbol,
                fund_name=fund["SERIES_NAME"].strip(),
                effective_date=effective_date,
                captured_on=captured_on,
                position_ticker=position,
                position_name=row["ISSUER_NAME"].strip(),
                shares=shares,
                weight_pct=weight,
                source_frequency="regulatory_periodic",
                source_url=source_url,
            )
        )
    if not holdings:
        raise SecNportDataError(
            f"SEC N-PORT dataset accession {accession} has no share positions."
        )
    return SecNportImport(
        registrant_name=issuer,
        fund_symbol=fund_symbol,
        fund_name=fund["SERIES_NAME"].strip(),
        series_id=series_id,
        effective_date=effective_date,
        captured_on=captured_on,
        holdings=tuple(holdings),
        reported_investments=len(rows),
        omitted_non_share_positions=omitted,
        source_url=source_url,
        source_mode="synthetic_fixture" if synthetic_fixture else "sec_quarterly_dataset",
    )


def _holding_symbol(
    row: dict[str, str], identifiers_by_holding: dict[str, list[dict[str, str]]]
) -> str:
    holding_id = row["HOLDING_ID"].strip()
    for identifier in identifiers_by_holding.get(holding_id, []):
        ticker = identifier["IDENTIFIER_TICKER"].strip().upper()
        if ticker:
            return _symbol(ticker)
    cusip = row["ISSUER_CUSIP"].strip().upper()
    if cusip:
        return _symbol(f"CUSIP:{cusip}")
    raise SecNportDataError(
        f"SEC N-PORT dataset holding {holding_id} lacks ticker or CUSIP."
    )


def _read_table(path: Path, required: set[str]) -> list[dict[str, str]]:
    try:
        with path.open("r", newline="", encoding="utf-8-sig") as source:
            reader = csv.DictReader(source, delimiter="\t")
            fields = set(reader.fieldnames or [])
            if not required.issubset(fields):
                raise SecNportDataError(
                    f"SEC N-PORT table {path.name} is missing required columns."
                )
            return [dict(row) for row in reader]
    except OSError as exc:
        raise SecNportDataError(f"Unable to read SEC N-PORT table {path}: {exc}") from exc


def _directories(directory: str | Path | list[str | Path]) -> list[Path]:
    entries = directory if isinstance(directory, list) else [directory]
    if not entries:
        raise SecNportDataError("At least one SEC N-PORT dataset directory is required.")
    return [Path(entry) for entry in entries]


def _index_accession(rows: list[dict[str, str]], table: str) -> dict[str, dict[str, str]]:
    indexed = {}
    for row in rows:
        accession = row["ACCESSION_NUMBER"].strip()
        if accession in indexed:
            raise SecNportDataError(f"SEC N-PORT table {table} duplicates accession.")
        indexed[accession] = row
    return indexed


def _group_by(rows: list[dict[str, str]], field: str) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row[field].strip(), []).append(row)
    return grouped


def _series_id(value: str) -> str:
    result = value.strip().upper()
    if not result.startswith("S") or not result[1:].isalnum():
        raise SecNportDataError(f"Invalid SEC series identifier: {value!r}.")
    return result


def _symbol(value: str) -> str:
    result = value.strip().upper()
    if not _SYMBOL_PATTERN.fullmatch(result):
        raise SecNportDataError(f"Invalid N-PORT symbol: {value!r}.")
    return result


def _date_field(value: str, field: str, accession: str) -> date:
    try:
        return date.fromisoformat(value.strip())
    except ValueError as exc:
        raise SecNportDataError(
            f"SEC N-PORT dataset accession {accession} has invalid {field}."
        ) from exc


def _decimal_field(value: str, field: str, accession: str) -> Decimal:
    try:
        result = Decimal(value.replace(",", "").strip())
    except InvalidOperation as exc:
        raise SecNportDataError(
            f"SEC N-PORT dataset accession {accession} has invalid {field}."
        ) from exc
    if not result.is_finite():
        raise SecNportDataError(
            f"SEC N-PORT dataset accession {accession} has invalid {field}."
        )
    return result
