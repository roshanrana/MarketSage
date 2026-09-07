"""Retrieval quality on FinanceBench: recall@k, MRR and nDCG@10 per scorer."""

import math
from typing import Any

from marketsage_core.retrieval import rank_documents
from marketsage_eval.fixtures import financebench

K_VALUES = (1, 5, 10)
NDCG_K = 10
SCORERS = ("bm25", "overlap")


def evaluate(scorer: str, ticker_scoped: bool = False) -> dict[str, Any]:
    fixture = financebench()
    hits = {k: 0.0 for k in K_VALUES}
    reciprocal_ranks: list[float] = []
    ndcgs: list[float] = []
    misses = 0

    for query in fixture.queries:
        relevant = fixture.relevant.get(query["id"], set())
        ticker = query.get("ticker") if ticker_scoped else None
        ranked = [doc.id for doc, _ in rank_documents(query["text"], scorer, ticker=ticker)]
        for k in K_VALUES:
            found = len(relevant & set(ranked[:k]))
            hits[k] += found / len(relevant) if relevant else 0.0
        first = next((i for i, doc_id in enumerate(ranked) if doc_id in relevant), None)
        reciprocal_ranks.append(0.0 if first is None else 1 / (first + 1))
        ndcgs.append(_ndcg(ranked[:NDCG_K], relevant))
        if first is None or first >= NDCG_K:
            misses += 1

    total = len(fixture.queries)
    return {
        "scorer": scorer,
        "ticker_scoped": ticker_scoped,
        "queries": total,
        "corpus_size": fixture.corpus_size,
        "recall": {str(k): round(hits[k] / total, 4) for k in K_VALUES},
        "mrr": round(sum(reciprocal_ranks) / total, 4),
        "ndcg_at_10": round(sum(ndcgs) / total, 4),
        "missed_in_top_10": misses,
    }


def run() -> dict[str, Any]:
    return {
        "bm25": evaluate("bm25"),
        "overlap": evaluate("overlap"),
        "bm25_ticker_scoped": evaluate("bm25", ticker_scoped=True),
    }


def _ndcg(ranked: list[str], relevant: set[str]) -> float:
    if not relevant:
        return 0.0
    dcg = sum(1 / math.log2(i + 2) for i, doc_id in enumerate(ranked) if doc_id in relevant)
    ideal = sum(1 / math.log2(i + 2) for i in range(min(len(relevant), len(ranked) or 1)))
    return dcg / ideal if ideal else 0.0
