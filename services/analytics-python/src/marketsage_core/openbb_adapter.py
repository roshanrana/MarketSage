import json
from datetime import UTC, datetime
from typing import Any

from marketsage_core.config import Settings
from marketsage_core.models import (
    MarketSnapshotData,
    PriceHistoryData,
    PriceHistoryRequest,
    PriceObservation,
    TickerRequest,
)
from marketsage_core.repo import repo_root


class MarketDataError(RuntimeError):
    def __init__(self, message: str, status_code: int = 503):
        super().__init__(message)
        self.status_code = status_code


def market_snapshot(
    request: TickerRequest,
    settings: Settings,
) -> tuple[MarketSnapshotData, list[str]]:
    mode = request.provider_mode or settings.mode
    if mode == "seeded":
        return _seed_snapshot(request.ticker), []

    try:
        return _live_snapshot(request.ticker), []
    except Exception as exc:
        if mode == "hybrid":
            data = _seed_snapshot(request.ticker)
            return data, [f"Live OpenBB snapshot unavailable; used seeded fallback: {exc}"]
        raise MarketDataError(f"Live OpenBB snapshot unavailable: {exc}") from exc


def price_history(
    request: PriceHistoryRequest,
    settings: Settings,
) -> tuple[PriceHistoryData, list[str]]:
    mode = request.provider_mode or settings.mode
    if mode == "seeded":
        return _seed_history(request), []

    try:
        return _live_history(request), []
    except Exception as exc:
        if mode == "hybrid":
            data = _seed_history(request)
            return data, [f"Live OpenBB history unavailable; used seeded fallback: {exc}"]
        raise MarketDataError(f"Live OpenBB history unavailable: {exc}") from exc


def _seed_data() -> dict[str, Any]:
    path = repo_root() / "data" / "seed" / "market_seed.json"
    return json.loads(path.read_text(encoding="utf8"))


def _seed_instrument(ticker: str) -> dict[str, Any]:
    seed = _seed_data()
    instruments = seed["instruments"]
    if ticker not in instruments:
        raise MarketDataError(f"No seeded data is available for ticker {ticker}", status_code=404)
    instrument = dict(instruments[ticker])
    instrument["ticker"] = ticker
    instrument["as_of"] = seed["as_of"]
    instrument["source_name"] = seed["source_name"]
    instrument["source_url"] = seed.get("source_url")
    return instrument


def _seed_snapshot(ticker: str) -> MarketSnapshotData:
    instrument = _seed_instrument(ticker)
    return MarketSnapshotData(**instrument)


def _seed_history(request: PriceHistoryRequest) -> PriceHistoryData:
    instrument = _seed_instrument(request.ticker)
    observations = [
        PriceObservation(**point)
        for point in instrument["history"]
        if (request.start is None or point["date"] >= request.start.isoformat())
        and (request.end is None or point["date"] <= request.end.isoformat())
    ]
    return PriceHistoryData(
        ticker=request.ticker,
        interval=request.interval,
        observations=observations,
        source_name=instrument["source_name"],
        source_url=instrument.get("source_url"),
    )


def _live_snapshot(ticker: str) -> MarketSnapshotData:
    obb = _load_openbb()
    quote = obb.equity.price.quote(symbol=ticker)
    row = _first_row(quote)
    price = _number(row, ["last_price", "price", "close", "last", "bid"])
    previous_close = _number(row, ["prev_close", "previous_close"], default=price)
    change = price - previous_close
    change_percent = 0.0 if previous_close == 0 else (change / previous_close) * 100
    return MarketSnapshotData(
        ticker=ticker,
        name=str(row.get("name") or row.get("symbol") or ticker),
        as_of=datetime.now(UTC),
        price=price,
        currency=str(row.get("currency") or "USD"),
        change=change,
        change_percent=change_percent,
        volume=int(_number(row, ["volume"], default=0)),
        sector=str(row.get("sector") or "unknown"),
        source_name="OpenBB live provider",
        source_url="https://docs.openbb.co/odp/python",
    )


def _live_history(request: PriceHistoryRequest) -> PriceHistoryData:
    obb = _load_openbb()
    history = obb.equity.price.historical(
        symbol=request.ticker,
        start_date=request.start.isoformat() if request.start else None,
        end_date=request.end.isoformat() if request.end else None,
        interval=request.interval,
    )
    rows = _rows(history)
    observations = [
        PriceObservation(
            date=_date(row.get("date") or row.get("timestamp")),
            close=_number(row, ["close", "adj_close", "price"]),
            volume=int(_number(row, ["volume"], default=0)),
        )
        for row in rows[:250]
    ]
    return PriceHistoryData(
        ticker=request.ticker,
        interval=request.interval,
        observations=observations,
        source_name="OpenBB live provider",
        source_url="https://docs.openbb.co/odp/python",
    )


def _load_openbb() -> Any:
    try:
        from openbb import obb  # type: ignore
    except Exception as exc:
        raise MarketDataError("OpenBB is not installed. Run uv sync --extra live.") from exc
    return obb


def _rows(openbb_result: Any) -> list[dict[str, Any]]:
    if hasattr(openbb_result, "to_df"):
        frame = openbb_result.to_df()
        return list(frame.to_dict(orient="records"))
    if isinstance(openbb_result, list):
        return [dict(item) for item in openbb_result]
    if isinstance(openbb_result, dict):
        return [openbb_result]
    raise MarketDataError(f"Unsupported OpenBB result shape: {type(openbb_result).__name__}")


def _first_row(openbb_result: Any) -> dict[str, Any]:
    rows = _rows(openbb_result)
    if not rows:
        raise MarketDataError("OpenBB returned no rows")
    return rows[0]


def _number(row: dict[str, Any], keys: list[str], default: float | None = None) -> float:
    for key in keys:
        value = row.get(key)
        if value is not None:
            return float(value)
    if default is not None:
        return default
    raise MarketDataError(f"OpenBB result is missing numeric field from {keys}")


def _date(value: Any):
    if hasattr(value, "date"):
        return value.date()
    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()
