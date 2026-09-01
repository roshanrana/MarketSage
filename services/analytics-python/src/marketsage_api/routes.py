from datetime import UTC, datetime
from time import perf_counter
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from marketsage_core.briefs import build_research_brief
from marketsage_core.config import Settings
from marketsage_core.datasets import dataset_entries
from marketsage_core.models import (
    ConfigSummary,
    DatasetStatusData,
    DependencyStatus,
    EvidenceSearchData,
    EvidenceSearchRequest,
    HealthData,
    MarketSnapshotData,
    PriceHistoryData,
    PriceHistoryRequest,
    ResearchBriefData,
    ResearchBriefRequest,
    ResponseEnvelope,
    SavedResearchRunData,
    SentimentData,
    SentimentRequest,
    TickerRequest,
)
from marketsage_core.openbb_adapter import MarketDataError, market_snapshot, price_history
from marketsage_core.retrieval import search_evidence
from marketsage_core.sentiment import score_text
from marketsage_core.storage import ensure_database, get_research_run, write_audit_event

router = APIRouter()


def _settings() -> Settings:
    try:
        return Settings.from_env()
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def _envelope(
    settings: Settings,
    source: str,
    data,
    warnings: list[str] | None = None,
    caveats: list[str] | None = None,
    started_at: float | None = None,
):
    request_id = str(uuid4())
    warning_list = warnings or []
    _try_write_audit_event(
        settings,
        request_id=request_id,
        tool_name=source,
        status="ok",
        duration_ms=_duration_ms(started_at),
        mode=settings.mode,
        warning_count=len(warning_list),
    )
    return ResponseEnvelope(
        request_id=request_id,
        mode=settings.mode,
        generated_at=datetime.now(UTC),
        source=source,
        data=data,
        warnings=warning_list,
        caveats=caveats
        or ["Research demo only. MarketSage does not provide investment advice or execute trades."],
    )


def _duration_ms(started_at: float | None) -> float:
    if started_at is None:
        return 0.0
    return round((perf_counter() - started_at) * 1000, 3)


def _record_failure(
    settings: Settings,
    source: str,
    started_at: float,
    detail: str,
) -> None:
    _try_write_audit_event(
        settings,
        request_id=str(uuid4()),
        tool_name=source,
        status="error",
        duration_ms=_duration_ms(started_at),
        mode=settings.mode,
        warning_count=0,
        detail=detail,
    )


def _try_write_audit_event(
    settings: Settings,
    *,
    request_id: str,
    tool_name: str,
    status: str,
    duration_ms: float,
    mode: str,
    warning_count: int,
    detail: str | None = None,
) -> None:
    try:
        write_audit_event(
            settings,
            request_id=request_id,
            tool_name=tool_name,
            status=status,
            duration_ms=duration_ms,
            mode=mode,
            warning_count=warning_count,
            detail=detail,
        )
    except Exception:
        return


@router.get("/health", response_model=ResponseEnvelope[HealthData])
def health() -> ResponseEnvelope[HealthData]:
    started_at = perf_counter()
    settings = _settings()
    duckdb_status = ensure_database(settings)
    dependencies = [
        duckdb_status,
        DependencyStatus(
            name="openbb",
            status="ok" if settings.mode in {"seeded", "hybrid"} else "degraded",
            detail=(
                "Seeded market adapter ready; live OpenBB requires optional dependencies/config."
            ),
        ),
        DependencyStatus(
            name="huggingface",
            status="ok",
            detail="Curated dataset manifest ready; bounded downloads are planned after M1.",
        ),
    ]
    status = "ok" if all(dep.status in {"ok", "degraded"} for dep in dependencies) else "degraded"

    return _envelope(
        settings,
        "marketsage.analytics.health",
        HealthData(
            service="marketsage-analytics",
            status=status,
            version="0.1.0",
            config=ConfigSummary(
                mode=settings.mode,
                data_dir=str(settings.data_dir),
                model_downloads_enabled=settings.model_downloads_enabled,
                http_auth_required=settings.http_token is not None,
            ),
            dependencies=dependencies,
        ),
        started_at=started_at,
    )


@router.get("/datasets", response_model=ResponseEnvelope[DatasetStatusData])
def datasets() -> ResponseEnvelope[DatasetStatusData]:
    started_at = perf_counter()
    settings = _settings()
    entries = dataset_entries(settings)
    return _envelope(
        settings,
        "marketsage.analytics.datasets",
        DatasetStatusData(count=len(entries), datasets=entries),
        warnings=[
            "Large transcript corpus is blocked until license review; use MIT fixtures for MVP.",
        ],
        started_at=started_at,
    )


@router.post("/market/snapshot", response_model=ResponseEnvelope[MarketSnapshotData])
def market_snapshot_route(request: TickerRequest) -> ResponseEnvelope[MarketSnapshotData]:
    started_at = perf_counter()
    source = "marketsage.analytics.market.snapshot"
    settings = _settings()
    try:
        data, warnings = market_snapshot(request, settings)
    except MarketDataError as exc:
        _record_failure(settings, source, started_at, str(exc))
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    return _envelope(settings, source, data, warnings=warnings, started_at=started_at)


@router.post("/market/history", response_model=ResponseEnvelope[PriceHistoryData])
def price_history_route(request: PriceHistoryRequest) -> ResponseEnvelope[PriceHistoryData]:
    started_at = perf_counter()
    source = "marketsage.analytics.market.history"
    settings = _settings()
    try:
        data, warnings = price_history(request, settings)
    except MarketDataError as exc:
        _record_failure(settings, source, started_at, str(exc))
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    return _envelope(settings, source, data, warnings=warnings, started_at=started_at)


@router.post("/sentiment/text", response_model=ResponseEnvelope[SentimentData])
def sentiment_text_route(request: SentimentRequest) -> ResponseEnvelope[SentimentData]:
    started_at = perf_counter()
    settings = _settings()
    data, warnings = score_text(request, settings)
    return _envelope(
        settings,
        "marketsage.analytics.sentiment.text",
        data,
        warnings=warnings,
        started_at=started_at,
    )


@router.post("/evidence/search", response_model=ResponseEnvelope[EvidenceSearchData])
def evidence_search_route(
    request: EvidenceSearchRequest,
) -> ResponseEnvelope[EvidenceSearchData]:
    started_at = perf_counter()
    settings = _settings()
    data, warnings = search_evidence(request, settings)
    return _envelope(
        settings,
        "marketsage.analytics.evidence.search",
        data,
        warnings=warnings,
        started_at=started_at,
    )


@router.post("/briefs/research", response_model=ResponseEnvelope[ResearchBriefData])
def research_brief_route(
    request: ResearchBriefRequest,
) -> ResponseEnvelope[ResearchBriefData]:
    started_at = perf_counter()
    settings = _settings()
    data, warnings = build_research_brief(request, settings)
    return _envelope(
        settings,
        "marketsage.analytics.briefs.research",
        data,
        warnings=warnings,
        started_at=started_at,
    )


@router.get("/runs/{run_id}", response_model=ResponseEnvelope[SavedResearchRunData])
def research_run_route(run_id: str) -> ResponseEnvelope[SavedResearchRunData]:
    started_at = perf_counter()
    source = "marketsage.analytics.runs"
    settings = _settings()
    data = get_research_run(settings, run_id)
    if data is None:
        _record_failure(settings, source, started_at, f"Research run {run_id} was not found")
        raise HTTPException(status_code=404, detail=f"Research run {run_id} was not found")
    return _envelope(settings, source, data, started_at=started_at)
