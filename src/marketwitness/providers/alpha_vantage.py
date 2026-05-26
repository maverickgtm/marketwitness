from __future__ import annotations

import csv
import json
import os
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from html import escape
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from ..models import PriceBar

ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"
DOCUMENTATION_URL = "https://www.alphavantage.co/documentation/"
PREMIUM_URL = "https://www.alphavantage.co/premium/"
LOCAL_API_KEY_PATH = Path("data/private/alpha_vantage_api_key.txt")
DEFAULT_CACHE_DIR = Path("data/raw/prices/alpha-vantage")
PROVIDER_NAME = "alpha_vantage_daily_adjusted_scaled"
_SYMBOL_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9.\-]{0,19}$")


class AlphaVantageDataError(ValueError):
    """Raised when Alpha Vantage price evidence cannot be normalized safely."""


@dataclass(frozen=True)
class AlphaVantageImport:
    ticker: str
    bars: tuple[PriceBar, ...]
    last_refreshed: str
    source_mode: str
    cache_path: str = ""


def configured_api_key(api_key: str | None = None) -> str:
    candidate = (api_key or os.environ.get("MARKETWITNESS_ALPHA_VANTAGE_API_KEY", "")).strip()
    if not candidate and LOCAL_API_KEY_PATH.exists():
        candidate = LOCAL_API_KEY_PATH.read_text(encoding="utf-8").strip()
    if not candidate:
        raise AlphaVantageDataError(
            "Alpha Vantage live requests require MARKETWITNESS_ALPHA_VANTAGE_API_KEY "
            "or data/private/alpha_vantage_api_key.txt."
        )
    return candidate


def load_alpha_vantage_snapshot(path: str | Path, ticker: str) -> AlphaVantageImport:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AlphaVantageDataError(f"Unable to read Alpha Vantage snapshot {path}.") from exc
    return parse_adjusted_daily_payload(payload, ticker, "snapshot")


def fetch_adjusted_daily(
    ticker: str,
    api_key: str | None = None,
    cache_dir: str | Path = DEFAULT_CACHE_DIR,
    refresh: bool = False,
) -> AlphaVantageImport:
    symbol = _symbol(ticker)
    cache_path = Path(cache_dir) / f"{symbol}-daily-adjusted.json"
    if cache_path.exists() and not refresh:
        try:
            payload = json.loads(cache_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise AlphaVantageDataError(f"Unable to read cached prices for {symbol}.") from exc
        return parse_adjusted_daily_payload(payload, symbol, "cache", str(cache_path))

    key = configured_api_key(api_key)
    query = urlencode(
        {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "outputsize": "full",
            "apikey": key,
        }
    )
    request = Request(
        f"{ALPHA_VANTAGE_URL}?{query}",
        headers={"User-Agent": "MarketWitness/0.1 market-research-adapter", "Accept": "application/json"},
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise AlphaVantageDataError(f"Unable to retrieve adjusted prices for {symbol}.") from exc
    imported = parse_adjusted_daily_payload(payload, symbol, "live", str(cache_path))
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return imported


def parse_adjusted_daily_payload(
    payload: object, ticker: str, source_mode: str, cache_path: str = ""
) -> AlphaVantageImport:
    symbol = _symbol(ticker)
    if not isinstance(payload, dict):
        raise AlphaVantageDataError("Alpha Vantage response is not a JSON object.")
    message = payload.get("Error Message") or payload.get("Note") or payload.get("Information")
    if message:
        raise AlphaVantageDataError(f"Alpha Vantage did not return adjusted daily bars: {message}")
    metadata = payload.get("Meta Data")
    series = payload.get("Time Series (Daily)")
    if not isinstance(metadata, dict) or not isinstance(series, dict) or not series:
        raise AlphaVantageDataError(
            "Alpha Vantage response is missing TIME_SERIES_DAILY_ADJUSTED bars."
        )
    returned_symbol = str(metadata.get("2. Symbol", symbol)).strip().upper()
    if returned_symbol and returned_symbol != symbol:
        raise AlphaVantageDataError(
            f"Alpha Vantage returned {returned_symbol} while {symbol} was requested."
        )
    bars: list[PriceBar] = []
    for raw_date, values in series.items():
        if not isinstance(values, dict):
            raise AlphaVantageDataError(f"Alpha Vantage bar {raw_date} is malformed.")
        try:
            bar_date = date.fromisoformat(str(raw_date))
            raw_high = Decimal(str(values["2. high"]))
            raw_low = Decimal(str(values["3. low"]))
            raw_close = Decimal(str(values["4. close"]))
            adjusted_close = Decimal(str(values["5. adjusted close"]))
            factor = adjusted_close / raw_close
            adjusted_high = raw_high * factor
            adjusted_low = raw_low * factor
        except (KeyError, InvalidOperation, ValueError, ZeroDivisionError) as exc:
            raise AlphaVantageDataError(
                f"Alpha Vantage adjusted bar {raw_date} is incomplete or invalid."
            ) from exc
        numbers = (raw_high, raw_low, raw_close, adjusted_close, factor)
        if (
            not all(number.is_finite() and number > 0 for number in numbers)
            or raw_low > raw_close
            or raw_close > raw_high
            or adjusted_low > adjusted_close
            or adjusted_close > adjusted_high
        ):
            raise AlphaVantageDataError(f"Alpha Vantage adjusted bar {raw_date} is inconsistent.")
        bars.append(
            PriceBar(
                ticker=symbol,
                date=bar_date,
                adjusted_high=adjusted_high,
                adjusted_low=adjusted_low,
                adjusted_close=adjusted_close,
                source_provider=PROVIDER_NAME,
            )
        )
    bars.sort(key=lambda item: item.date)
    refreshed = str(metadata.get("3. Last Refreshed", bars[-1].date.isoformat()))
    return AlphaVantageImport(symbol, tuple(bars), refreshed, source_mode, cache_path)


def write_prices_csv(path: str | Path, imported: AlphaVantageImport) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(
            target,
            fieldnames=[
                "ticker",
                "date",
                "adjusted_high",
                "adjusted_low",
                "adjusted_close",
                "source_provider",
            ],
        )
        writer.writeheader()
        for bar in imported.bars:
            writer.writerow(
                {
                    "ticker": bar.ticker,
                    "date": bar.date.isoformat(),
                    "adjusted_high": str(bar.adjusted_high),
                    "adjusted_low": str(bar.adjusted_low),
                    "adjusted_close": str(bar.adjusted_close),
                    "source_provider": bar.source_provider,
                }
            )


def render_prices_report(imported: AlphaVantageImport, as_of: date) -> str:
    _validate_as_of(imported, as_of)
    return "\n".join(
        [
            "# Alpha Vantage Adjusted Price Adapter",
            "",
            f"- Ticker: `{imported.ticker}`",
            f"- Source mode: `{imported.source_mode}`",
            f"- Last refreshed field: `{imported.last_refreshed}`",
            f"- Normalized bars: `{len(imported.bars)}`",
            f"- Date range: `{imported.bars[0].date.isoformat()}` to `{imported.bars[-1].date.isoformat()}`",
            f"- Official documentation: <{DOCUMENTATION_URL}>",
            "",
            "The Alpha Vantage daily adjusted response supplies raw daily high/low/close",
            "and an adjusted close. MarketWitness derives adjusted high and adjusted low",
            "with the per-row factor `adjusted_close / raw_close`, preserving the",
            "intraday target-hit test on a split/dividend-adjusted scale.",
            "",
            "Live use is cache-first and requests one symbol per command invocation.",
            "The provider currently identifies `TIME_SERIES_DAILY_ADJUSTED` as a",
            "premium function; provider terms and publication rights must be approved",
            "before these real-data outputs feed a public scorecard.",
            "",
        ]
    )


def write_prices_report(path: str | Path, imported: AlphaVantageImport, as_of: date) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_prices_report(imported, as_of), encoding="utf-8")


def render_prices_html(imported: AlphaVantageImport, as_of: date) -> str:
    _validate_as_of(imported, as_of)
    mode = escape(imported.source_mode)
    rows = "".join(
        "<tr>"
        f"<td>{bar.date.isoformat()}</td><td>{bar.adjusted_high}</td>"
        f"<td>{bar.adjusted_low}</td><td>{bar.adjusted_close}</td>"
        "</tr>"
        for bar in imported.bars[-10:]
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MarketWitness | Adjusted Prices</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;--blue:#62a6ff;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1120px;margin:auto;padding:30px 28px}}nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}h1{{font-size:clamp(34px,5vw,54px);line-height:1.06;margin:38px 0 14px}}.lead{{color:var(--muted);font-size:17px;max-width:820px}}.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:35px 0}}.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px}}.card p{{margin:0;color:var(--muted)}}.card strong{{font-size:32px;color:var(--mint);display:block}}.notice{{border-left:3px solid var(--gold);color:var(--muted);padding:15px 18px}}h2{{margin-top:42px}}.table-wrap{{overflow:hidden;margin-top:16px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left}}th{{text-transform:uppercase;font-size:12px;color:var(--muted);font-weight:500}}a{{color:var(--mint);text-decoration:none}}.mode{{color:var(--blue)}}
@media(max-width:720px){{.cards{{grid-template-columns:1fr}}.table-wrap{{overflow-x:auto}}table{{min-width:560px}}}}
</style></head><body><header><nav><a href="/dashboard/reports">Report Center</a> / <a href="/dashboard/financials-evidence">Financials Evidence Center</a> / Price Evidence</nav>
<h1>Adjusted prices.<br>Visible provenance.</h1><p class="lead">A normalized adjusted-price import for <strong>{escape(imported.ticker)}</strong>, prepared for target evaluation only after data-use approval.</p>
<p class="meta">Generated as of {as_of.isoformat()}</p><section class="cards"><article class="card"><p>Bars normalized</p><strong>{len(imported.bars)}</strong></article><article class="card"><p>Input mode</p><strong class="mode">{mode}</strong></article><article class="card"><p>Last refreshed</p><strong>{escape(imported.last_refreshed)}</strong></article></section></header>
<main><p class="notice">The endpoint returns raw high/low plus adjusted close. MarketWitness scales intraday bounds by adjusted close / raw close. Alpha Vantage currently marks this daily-adjusted API as premium; public output rights remain under review.</p>
<h2>Most recent normalized bars</h2><div class="table-wrap"><table><thead><tr><th>Date</th><th>Adjusted high</th><th>Adjusted low</th><th>Adjusted close</th></tr></thead><tbody>{rows}</tbody></table></div>
<p><a href="{DOCUMENTATION_URL}">Official Alpha Vantage documentation</a> &nbsp; <a href="{PREMIUM_URL}">Plan and usage-limit reference</a></p></main></body></html>"""


def write_prices_html(path: str | Path, imported: AlphaVantageImport, as_of: date) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_prices_html(imported, as_of), encoding="utf-8")


def _symbol(ticker: str) -> str:
    symbol = ticker.strip().upper()
    if not _SYMBOL_PATTERN.fullmatch(symbol):
        raise AlphaVantageDataError(f"Invalid Alpha Vantage symbol: {ticker!r}.")
    return symbol


def _validate_as_of(imported: AlphaVantageImport, as_of: date) -> None:
    if not imported.bars:
        raise AlphaVantageDataError("No normalized price bars were generated.")
    if any(bar.date > as_of for bar in imported.bars):
        raise AlphaVantageDataError("Price import includes a bar after the report cutoff.")
