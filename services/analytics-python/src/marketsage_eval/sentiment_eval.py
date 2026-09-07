"""Sentiment fallback quality on the FiQA test split.

Gold labels come from the sign of the FiQA score: positive above zero, negative
below, neutral at exactly zero. The lexicon returns neutral whenever it matches
nothing, so coverage and accuracy-when-committed are reported alongside plain
accuracy, and the confidence field is checked for calibration (ECE).
"""

from collections import Counter
from typing import Any

from marketsage_core.config import Settings
from marketsage_core.models import SentimentRequest
from marketsage_core.sentiment import score_text
from marketsage_eval.fixtures import fiqa

LABELS = ("positive", "negative", "neutral")
ECE_BINS = 10


def run(settings: Settings) -> dict[str, Any]:
    rows = fiqa()
    confusion: Counter[tuple[str, str]] = Counter()
    committed: list[tuple[float, bool]] = []
    model_id = None
    for row in rows:
        data, _ = score_text(SentimentRequest(text=row["sentence"]), settings)
        model_id = data.model_id
        confusion[(row["label"], data.label)] += 1
        if data.label != "neutral":
            committed.append((data.confidence, data.label == row["label"]))

    total = len(rows)
    correct = sum(count for (gold, pred), count in confusion.items() if gold == pred)
    gold_counts = Counter(row["label"] for row in rows)
    majority = max(gold_counts.values()) / total

    return {
        "rows": total,
        "model_id": model_id,
        "gold_distribution": dict(sorted(gold_counts.items())),
        "accuracy": round(correct / total, 4),
        "majority_class_accuracy": round(majority, 4),
        "macro_f1_pos_neg": round(_macro_f1(confusion, ("positive", "negative")), 4),
        "coverage": round(len(committed) / total, 4),
        "accuracy_when_committed": (
            round(sum(1 for _, ok in committed if ok) / len(committed), 4) if committed else 0.0
        ),
        "expected_calibration_error": round(_ece(committed), 4),
        "confusion": {
            f"{gold}->{pred}": confusion[(gold, pred)]
            for gold in LABELS
            for pred in LABELS
            if confusion[(gold, pred)]
        },
    }


def _macro_f1(confusion: Counter[tuple[str, str]], labels: tuple[str, ...]) -> float:
    scores = []
    for label in labels:
        tp = confusion[(label, label)]
        fp = sum(n for (gold, pred), n in confusion.items() if pred == label and gold != label)
        fn = sum(n for (gold, pred), n in confusion.items() if gold == label and pred != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        scores.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    return sum(scores) / len(scores)


def _ece(committed: list[tuple[float, bool]]) -> float:
    if not committed:
        return 0.0
    bins: dict[int, list[tuple[float, bool]]] = {}
    for confidence, ok in committed:
        index = min(int(confidence * ECE_BINS), ECE_BINS - 1)
        bins.setdefault(index, []).append((confidence, ok))
    total = len(committed)
    error = 0.0
    for members in bins.values():
        mean_confidence = sum(c for c, _ in members) / len(members)
        accuracy = sum(1 for _, ok in members if ok) / len(members)
        error += (len(members) / total) * abs(accuracy - mean_confidence)
    return error
