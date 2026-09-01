import re
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

Mode = Literal["seeded", "live", "hybrid"]
DependencyState = Literal["ok", "degraded", "unavailable"]
HealthState = Literal["ok", "degraded", "unavailable"]

class DependencyStatus(BaseModel):
    name: str
    status: DependencyState
    detail: str = ""


class ConfigSummary(BaseModel):
    mode: Mode
    data_dir: str
    model_downloads_enabled: bool
    http_auth_required: bool


class HealthData(BaseModel):
    service: str
    status: HealthState
    version: str
    config: ConfigSummary
    dependencies: list[DependencyStatus]


class ResponseEnvelope[T](BaseModel):
    request_id: str
    mode: Mode
    generated_at: datetime
    source: str
    data: T
    warnings: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class DatasetEntry(BaseModel):
    dataset_id: str
    config: str
    split: str
    rows_count: int
    license: str
    source_url: str
    role: str
    local_status: str


class DatasetStatusData(BaseModel):
    count: int
    datasets: list[DatasetEntry]


class TickerRequest(BaseModel):
    ticker: str
    provider_mode: Mode | None = None

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, value: str) -> str:
        ticker = value.strip().upper()
        if not re.fullmatch(r"[A-Z][A-Z0-9.\-]{0,9}", ticker):
            raise ValueError("ticker must be 1 to 10 uppercase market-symbol characters")
        return ticker


class PriceHistoryRequest(TickerRequest):
    start: date | None = None
    end: date | None = None
    interval: str = "1d"

    @field_validator("interval")
    @classmethod
    def validate_interval(cls, value: str) -> str:
        allowed = {"1d", "1wk", "1mo"}
        if value not in allowed:
            raise ValueError(f"interval must be one of {sorted(allowed)}")
        return value


class PriceObservation(BaseModel):
    date: date
    close: float
    volume: int | None = None


class MarketSnapshotData(BaseModel):
    ticker: str
    name: str
    as_of: datetime
    price: float
    currency: str
    change: float
    change_percent: float
    volume: int
    sector: str
    source_name: str
    source_url: str | None = None


class PriceHistoryData(BaseModel):
    ticker: str
    interval: str
    observations: list[PriceObservation]
    source_name: str
    source_url: str | None = None


class SentimentRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    ticker: str | None = None
    model_preference: str = "auto"

    @field_validator("ticker")
    @classmethod
    def validate_optional_ticker(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return TickerRequest(ticker=value).ticker


class SentimentData(BaseModel):
    label: Literal["positive", "negative", "neutral"]
    confidence: float
    model_id: str
    fallback: bool
    text_hash: str
    matched_terms: list[str] = Field(default_factory=list)


class EvidenceSearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    ticker: str | None = None
    dataset: str | None = None
    top_k: int = Field(default=5, ge=1, le=10)

    @field_validator("ticker")
    @classmethod
    def validate_optional_ticker(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return TickerRequest(ticker=value).ticker


class EvidenceSnippet(BaseModel):
    id: str
    document_id: str
    dataset_id: str
    ticker: str
    title: str
    text: str
    score: float
    source_url: str
    license: str


class EvidenceSearchData(BaseModel):
    query: str
    count: int
    retrieval_mode: Literal["lexical", "embedding"]
    results: list[EvidenceSnippet]


class ResearchBriefRequest(BaseModel):
    tickers: list[str] = Field(min_length=1, max_length=5)
    horizon: str = Field(default="1w", max_length=20)
    sections: list[str] = Field(
        default_factory=lambda: ["market", "sentiment", "evidence", "caveats"]
    )
    provider_mode: Mode | None = None

    @field_validator("tickers")
    @classmethod
    def validate_tickers(cls, value: list[str]) -> list[str]:
        return [TickerRequest(ticker=ticker).ticker for ticker in value]


class BriefSection(BaseModel):
    title: str
    bullets: list[str]


class ResearchBriefData(BaseModel):
    run_id: str
    title: str
    tickers: list[str]
    horizon: str
    generated_at: datetime
    sections: list[BriefSection]
    market_snapshots: list[MarketSnapshotData]
    sentiment: SentimentData | None
    evidence: list[EvidenceSnippet]


class SavedResearchRunData(BaseModel):
    run_id: str
    created_at: datetime
    input: dict
    output: ResearchBriefData
