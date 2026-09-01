from datetime import UTC, datetime
from uuid import uuid4

from marketsage_core.config import Settings
from marketsage_core.models import (
    BriefSection,
    EvidenceSearchRequest,
    ResearchBriefData,
    ResearchBriefRequest,
    SentimentRequest,
    TickerRequest,
)
from marketsage_core.openbb_adapter import MarketDataError, market_snapshot
from marketsage_core.retrieval import search_evidence
from marketsage_core.sentiment import score_text
from marketsage_core.storage import save_research_run


def build_research_brief(
    request: ResearchBriefRequest,
    settings: Settings,
) -> tuple[ResearchBriefData, list[str]]:
    warnings: list[str] = []
    snapshots = []
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
        EvidenceSearchRequest(query=query, ticker=request.tickers[0], top_k=5),
        settings,
    )
    warnings.extend(evidence_warnings)

    sentiment = None
    if evidence_data.results:
        sentiment_text = " ".join(item.text for item in evidence_data.results[:3])
        sentiment, sentiment_warnings = score_text(
            SentimentRequest(text=sentiment_text, ticker=request.tickers[0]),
            settings,
        )
        warnings.extend(sentiment_warnings)

    sections = [
        BriefSection(
            title="Market Snapshot",
            bullets=[
                f"{item.ticker}: {item.price:.2f} {item.currency}, "
                f"{item.change_percent:+.2f}% as of {item.as_of.isoformat()}"
                for item in snapshots
            ]
            or ["No seeded or live market snapshot was available."],
        ),
        BriefSection(
            title="Sentiment",
            bullets=[
                (
                    f"{sentiment.label.title()} sentiment "
                    f"({sentiment.confidence:.0%} confidence, {sentiment.model_id})."
                )
                if sentiment
                else "No sentiment evidence was available."
            ],
        ),
        BriefSection(
            title="Evidence",
            bullets=[
                f"{item.ticker} | {item.title}: {item.text[:180]}"
                for item in evidence_data.results[:3]
            ]
            or ["No matching evidence snippets were found."],
        ),
        BriefSection(
            title="Caveats",
            bullets=[
                "Seeded data is illustrative and not current market data.",
                "This output is research support, not investment advice.",
                "Live OpenBB mode and model downloads are optional runtime paths.",
            ],
        ),
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


def _brief_query(request: ResearchBriefRequest, snapshots) -> str:
    sectors = sorted({snapshot.sector for snapshot in snapshots})
    return " ".join(
        [
            *request.tickers,
            request.horizon,
            "revenue margin cash flow risk growth",
            *sectors,
        ]
    )
