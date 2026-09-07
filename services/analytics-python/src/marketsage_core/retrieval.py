"""Lexical evidence retrieval over the committed FinanceBench corpus.

Two scorers are available. ``bm25`` is the default. ``overlap`` is the original
query-term overlap ratio and is kept so the evaluation harness can report the
difference. Both are deterministic, in-process and need no network.
"""

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache

from marketsage_core.config import Settings
from marketsage_core.models import EvidenceSearchData, EvidenceSearchRequest, EvidenceSnippet
from marketsage_core.repo import repo_root

# Letters and digits are separate tokens so "FY2018" and "Q2" match "2018" and "2".
TOKEN_PATTERN = re.compile(r"[a-zA-Z]+|[0-9]+")
SNIPPET_CHARS = 700
BM25_K1 = 1.5
BM25_B = 0.75
CORPUS_DATASET_ID = "mteb/FinanceBenchRetrieval"
CORPUS_SOURCE_URL = "https://huggingface.co/datasets/mteb/FinanceBenchRetrieval"
CORPUS_LICENSE = "MIT"


@dataclass(frozen=True)
class Document:
    id: str
    ticker: str | None
    company: str | None
    text: str


@dataclass(frozen=True)
class Index:
    documents: tuple[Document, ...]
    term_counts: tuple[Counter[str], ...]
    lengths: tuple[int, ...]
    document_frequency: Counter[str]
    average_length: float


def search_evidence(
    request: EvidenceSearchRequest,
    settings: Settings,
    scorer: str | None = None,
) -> tuple[EvidenceSearchData, list[str]]:
    scorer_name = scorer or settings.retrieval_scorer
    ranked = rank_documents(request.query, scorer_name, ticker=request.ticker)
    if request.dataset and request.dataset != CORPUS_DATASET_ID:
        ranked = []

    selected = [
        _snippet(document, score) for document, score in ranked[: request.top_k]
    ]
    warnings = [
        f"Lexical {scorer_name} retrieval over the committed FinanceBench corpus; "
        "embedding retrieval is an optional enhancement.",
    ]
    if request.ticker and not ranked and not request.dataset:
        warnings.append(
            f"No committed evidence covers {request.ticker}; the corpus holds "
            f"{len(corpus_tickers())} companies."
        )
    return (
        EvidenceSearchData(
            query=request.query,
            count=len(selected),
            retrieval_mode="lexical",
            scorer=scorer_name,
            results=selected,
        ),
        warnings,
    )


def rank_documents(
    query: str,
    scorer: str,
    ticker: str | None = None,
) -> list[tuple[Document, float]]:
    """Return every matching document with a positive score, best first."""
    index = _index()
    query_terms = _tokens(query)
    if not query_terms:
        return []

    scored: list[tuple[Document, float]] = []
    for position, document in enumerate(index.documents):
        if ticker and document.ticker != ticker:
            continue
        if scorer == "bm25":
            score = _bm25(query_terms, index, position)
        elif scorer == "overlap":
            score = _overlap(query_terms, index.term_counts[position])
        else:
            raise ValueError(f"unknown scorer {scorer!r}")
        if score > 0:
            scored.append((document, round(score, 4)))

    scored.sort(key=lambda item: (-item[1], item[0].id))
    return scored


def corpus_tickers() -> list[str]:
    return sorted({doc.ticker for doc in _index().documents if doc.ticker})


def corpus_size() -> int:
    return len(_index().documents)


def _snippet(document: Document, score: float) -> EvidenceSnippet:
    text = " ".join(document.text.split())
    if len(text) > SNIPPET_CHARS:
        text = text[: SNIPPET_CHARS - 1].rstrip() + "…"
    company = document.company or "Unattributed"
    return EvidenceSnippet(
        id=f"financebench-{document.id}",
        document_id=document.id,
        dataset_id=CORPUS_DATASET_ID,
        ticker=document.ticker or "",
        title=f"{company} filing excerpt (FinanceBench corpus {document.id})",
        text=text,
        score=score,
        source_url=CORPUS_SOURCE_URL,
        license=CORPUS_LICENSE,
    )


@lru_cache(maxsize=1)
def _index() -> Index:
    path = repo_root() / "data" / "fixtures" / "financebench" / "corpus.jsonl"
    documents: list[Document] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            documents.append(
                Document(
                    id=row["id"],
                    ticker=row.get("ticker"),
                    company=row.get("company"),
                    text=row["text"],
                )
            )
    term_counts = tuple(_tokens(doc.text) for doc in documents)
    lengths = tuple(sum(counts.values()) for counts in term_counts)
    document_frequency: Counter[str] = Counter()
    for counts in term_counts:
        document_frequency.update(counts.keys())
    average_length = sum(lengths) / len(lengths) if lengths else 0.0
    return Index(
        documents=tuple(documents),
        term_counts=term_counts,
        lengths=lengths,
        document_frequency=document_frequency,
        average_length=average_length,
    )


def _tokens(text: str) -> Counter[str]:
    return Counter(token.lower() for token in TOKEN_PATTERN.findall(text))


def _overlap(query_terms: Counter[str], doc_terms: Counter[str]) -> float:
    overlap = sum(min(count, doc_terms.get(term, 0)) for term, count in query_terms.items())
    return overlap / sum(query_terms.values())


def _bm25(query_terms: Counter[str], index: Index, position: int) -> float:
    doc_terms = index.term_counts[position]
    length_norm = 1 - BM25_B + BM25_B * (index.lengths[position] / index.average_length)
    total_docs = len(index.documents)
    score = 0.0
    for term in query_terms:
        frequency = doc_terms.get(term, 0)
        if frequency == 0:
            continue
        df = index.document_frequency[term]
        idf = math.log(1 + (total_docs - df + 0.5) / (df + 0.5))
        score += idf * (frequency * (BM25_K1 + 1)) / (frequency + BM25_K1 * length_norm)
    return score
