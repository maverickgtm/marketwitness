from __future__ import annotations

import csv
import json
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

SEC_COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers_exchange.json"


class SecDataError(ValueError):
    """Raised when SEC reference data is unusable."""


def fetch_company_ticker_map(user_agent: str) -> list[dict[str, str]]:
    if "@" not in user_agent:
        raise SecDataError(
            "SEC requests require a declared user agent including a contact email."
        )
    request = Request(
        SEC_COMPANY_TICKERS_URL,
        headers={"User-Agent": user_agent, "Accept": "application/json"},
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise SecDataError(f"Unable to retrieve SEC company ticker data: {exc}") from exc
    return parse_company_ticker_payload(payload)


def parse_company_ticker_payload(payload: dict[str, object]) -> list[dict[str, str]]:
    fields = payload.get("fields")
    data = payload.get("data")
    if not isinstance(fields, list) or not isinstance(data, list):
        raise SecDataError("Unexpected SEC company ticker payload.")
    expected = {"cik", "name", "ticker", "exchange"}
    if not expected.issubset(set(fields)):
        raise SecDataError("SEC company ticker payload is missing expected fields.")
    rows = []
    for values in data:
        if not isinstance(values, list) or len(values) != len(fields):
            raise SecDataError("Unexpected SEC company ticker row.")
        record = dict(zip(fields, values))
        rows.append(
            {
                "cik": str(record["cik"]).zfill(10),
                "company_name": str(record["name"]),
                "ticker": str(record["ticker"]).upper(),
                "exchange": str(record["exchange"]),
                "source_provider": "sec",
                "source_url": SEC_COMPANY_TICKERS_URL,
            }
        )
    return rows


def write_company_ticker_map(path: str | Path, rows: list[dict[str, str]]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "cik",
        "company_name",
        "ticker",
        "exchange",
        "source_provider",
        "source_url",
    ]
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
