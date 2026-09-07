from marketsage_core.config import Settings
from marketsage_core.models import EvidenceSearchRequest
from marketsage_core.retrieval import corpus_size, corpus_tickers, rank_documents, search_evidence
from marketsage_eval.fixtures import financebench


def settings(scorer: str = "bm25") -> Settings:
    return Settings(
        mode="seeded",
        data_dir=None,  # type: ignore[arg-type]
        model_downloads_enabled=False,
        log_level="info",
        http_token=None,
        retrieval_scorer=scorer,
    )


def test_corpus_is_the_committed_financebench_fixture():
    assert corpus_size() == financebench().corpus_size == 145
    assert "MSFT" in corpus_tickers()
    assert len(corpus_tickers()) == 32


def test_bm25_finds_the_labelled_document_for_a_named_query():
    fixture = financebench()
    query = next(q for q in fixture.queries if q["id"] == "00000")

    ranked = [doc.id for doc, _ in rank_documents(query["text"], "bm25")]

    assert fixture.relevant["00000"] & set(ranked[:5])


def test_ticker_filter_only_returns_that_company():
    data, warnings = search_evidence(
        EvidenceSearchRequest(query="cash flow from operations", ticker="MSFT", top_k=5),
        settings(),
    )

    assert data.count >= 1
    assert {item.ticker for item in data.results} == {"MSFT"}
    assert data.scorer == "bm25"
    assert all(item.dataset_id == "mteb/FinanceBenchRetrieval" for item in data.results)
    assert not any("No committed evidence" in warning for warning in warnings)


def test_uncovered_ticker_returns_nothing_and_says_so():
    data, warnings = search_evidence(
        EvidenceSearchRequest(query="cash flow from operations", ticker="XOM"), settings()
    )

    assert data.count == 0
    assert any("No committed evidence covers XOM" in warning for warning in warnings)


def test_scorer_setting_selects_the_overlap_scorer():
    data, _ = search_evidence(
        EvidenceSearchRequest(query="net revenue increase", top_k=3), settings("overlap")
    )

    assert data.scorer == "overlap"
    assert all(0 < item.score <= 1 for item in data.results)


def test_ranking_is_deterministic():
    first = rank_documents("operating margin change", "bm25")
    second = rank_documents("operating margin change", "bm25")

    assert [(d.id, s) for d, s in first] == [(d.id, s) for d, s in second]
