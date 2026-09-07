from datetime import UTC, datetime
from uuid import uuid4

from marketsage_core.config import Settings
from marketsage_core.models import (
    BriefSection,
    EvidenceSearchRequest,
    EvidenceSnippet,
    MarketSnapshotData,
    ResearchBriefData,
    ResearchBriefRequest,
    SentimentData,
    SentimentRequest,
    TickerRequest,
)
from marketsage_core.openbb_adapter import MarketDataError, market_snapshot
from marketsage_core.retrieval import search_evidence
from marketsage_core.sentiment import score_text
from marketsage_core.storage import save_research_run

EVIDENCE_TOP_K = 5
EVIDENCE_BULLETS = 3
SENTIMENT_SNIPPETS = 3
BULLET_TEXT_CHARS = 180


def build_research_brief(
    request: ResearchBriefRequest,
    settings: Settings,
) -> tuple[ResearchBriefData, list[str]]:
    warnings: list[str] = []
    snapshots: list[MarketSnapshotData] = []
    for ticker in request.tickers:
        try:
            snapshot, snapshot_warnings = market_snapshot(
                TickerRequest(ticker=ticker, provider_mode=request.provider_mode),
                settings,
            )
            snapshots.append(snapshot)
            warnings.extend(snapshot_warnings)
        except MarketDataError as exc:
            warnings.append(f"{ticker}: {exc}")

    query = _brief_query(request, snapshots)
    evidence_data, evidence_warnings = search_evidence(
        EvidenceSearchRequest(query=query, ticker=request.tickers[0], top_k=EVIDENCE_TOP_K),
        settings,
    )
    warnings.extend(evidence_warnings)

    sentiment = None
    if evidence_data.results:
        sentiment_text = " ".join(
            item.text for item in evidence_data.results[:SENTIMENT_SNIPPETS]
        )
        sentiment, sentiment_warnings = score_text(
            SentimentRequest(text=sentiment_text, ticker=request.tickers[0]),
            settings,
        )
        warnings.extend(sentiment_warnings)

    sections = [
        _market_section(snapshots),
        _sentiment_section(sentiment),
        _evidence_section(evidence_data.results),
        _caveats_section(),
    ]

    brief = ResearchBriefData(
        run_id=str(uuid4()),
        title=f"MarketSage brief: {', '.join(request.tickers)}",
        tickers=request.tickers,
        horizon=request.horizon,
        generated_at=datetime.now(UTC),
        sections=sections,
        market_snapshots=snapshots,
        sentiment=sentiment,
        evidence=evidence_data.results,
    )
    save_research_run(settings, request, brief)
    return brief, warnings


def _market_section(snapshots: list[MarketSnapshotData]) -> BriefSection:
    if not snapshots:
        return BriefSection(
            title="Market Snapshot",
            bullets=["No seeded or live market snapshot was available."],
            references=[""],
        )
    return BriefSection(
        title="Market Snapshot",
        bullets=[
            f"{item.ticker}: {item.price:.2f} {item.currency}, "
            f"{item.change_percent:+.2f}% as of {item.as_of.isoformat()}"
            for item in snapshots
        ],
        references=[f"snapshot:{item.ticker}" for item in snapshots],
    )


def _sentiment_section(sentiment: SentimentData | None) -> BriefSection:
    if sentiment is None:
        return BriefSection(
            title="Sentiment",
            bullets=["No sentiment evidence was available."],
            references=[""],
        )
    return BriefSection(
        title="Sentiment",
        bullets=[
            f"{sentiment.label.title()} sentiment "
            f"({sentiment.confidence:.0%} confidence, {sentiment.model_id})."
        ],
        references=[f"sentiment:{sentiment.text_hash}"],
    )


def _evidence_section(evidence: list[EvidenceSnippet]) -> BriefSection:
    if not evidence:
        return BriefSection(
            title="Evidence",
            bullets=["No matching evidence snippets were found."],
            references=[""],
        )
    selected = evidence[:EVIDENCE_BULLETS]
    return BriefSection(
        title="Evidence",
        bullets=[
            f"{item.ticker or 'Unattributed'} | {item.title}: {item.text[:BULLET_TEXT_CHARS]}"
            for item in selected
        ],
        references=[f"evidence:{item.id}" for item in selected],
    )


def _caveats_section() -> BriefSection:
    return BriefSection(
        title="Caveats",
        bullets=[
            "Seeded data is illustrative and not current market data.",
            "This output is research support, not investment advice.",
            "Live OpenBB mode and model downloads are optional runtime paths.",
        ],
        references=["policy:seeded-data", "policy:not-advice", "policy:optional-live"],
    )


def _brief_query(request: ResearchBriefRequest, snapshots: list[MarketSnapshotData]) -> str:
    sectors = sorted({snapshot.sector for snapshot in snapshots})
    return " ".join(
        [
            *request.tickers,
            request.horizon,
            "revenue margin cash flow risk growth",
            *sectors,
        ]
    )
