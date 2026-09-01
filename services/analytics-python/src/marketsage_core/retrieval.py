import json
import re
from collections import Counter
from typing import Any

from marketsage_core.config import Settings
from marketsage_core.models import EvidenceSearchData, EvidenceSearchRequest, EvidenceSnippet
from marketsage_core.repo import repo_root

TOKEN_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9]+")


def search_evidence(
    request: EvidenceSearchRequest,
    settings: Settings,
) -> tuple[EvidenceSearchData, list[str]]:
    del settings
    query_terms = _tokens(request.query)
    results: list[EvidenceSnippet] = []
    for row in _seed_evidence():
        if request.ticker and row["ticker"] != request.ticker:
            continue
        if request.dataset and row["dataset_id"] != request.dataset:
            continue
        score = _score(query_terms, _tokens(row["text"] + " " + row["title"]))
        if score == 0:
            continue
        results.append(EvidenceSnippet(score=score, **row))

    results.sort(key=lambda item: (-item.score, item.ticker, item.id))
    selected = results[: request.top_k]
    return (
        EvidenceSearchData(
            query=request.query,
            count=len(selected),
            retrieval_mode="lexical",
            results=selected,
        ),
        ["Using lexical retrieval; embedding retrieval is planned as an optional enhancement."],
    )


def _seed_evidence() -> list[dict[str, Any]]:
    path = repo_root() / "data" / "seed" / "evidence_seed.json"
    return json.loads(path.read_text(encoding="utf8"))["evidence"]


def _tokens(text: str) -> Counter[str]:
    return Counter(token.lower() for token in TOKEN_PATTERN.findall(text))


def _score(query_terms: Counter[str], doc_terms: Counter[str]) -> float:
    if not query_terms:
        return 0.0
    overlap = sum(min(count, doc_terms.get(term, 0)) for term, count in query_terms.items())
    return round(overlap / sum(query_terms.values()), 4)
