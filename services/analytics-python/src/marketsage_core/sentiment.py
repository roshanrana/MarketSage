from hashlib import sha256

from marketsage_core.config import Settings
from marketsage_core.models import SentimentData, SentimentRequest

POSITIVE_TERMS = {
    "beat",
    "beats",
    "growth",
    "improved",
    "profit",
    "profits",
    "raise",
    "raised",
    "record",
    "strong",
    "upside",
}

NEGATIVE_TERMS = {
    "cut",
    "decline",
    "declined",
    "downgrade",
    "loss",
    "miss",
    "missed",
    "pressure",
    "risk",
    "weak",
    "weakness",
}


def score_text(request: SentimentRequest, settings: Settings) -> tuple[SentimentData, list[str]]:
    if settings.model_downloads_enabled and request.model_preference in {"auto", "finbert"}:
        try:
            return _score_with_finbert(request), []
        except Exception as exc:
            fallback, warnings = _score_with_lexicon(request)
            warnings.append(f"FinBERT unavailable; used deterministic fallback: {exc}")
            return fallback, warnings

    return _score_with_lexicon(request)


def _score_with_lexicon(request: SentimentRequest) -> tuple[SentimentData, list[str]]:
    tokens = {token.strip(".,:;!?()[]{}\"'").lower() for token in request.text.split()}
    positives = sorted(tokens & POSITIVE_TERMS)
    negatives = sorted(tokens & NEGATIVE_TERMS)
    raw_score = len(positives) - len(negatives)
    if raw_score > 0:
        label = "positive"
    elif raw_score < 0:
        label = "negative"
    else:
        label = "neutral"

    confidence = min(0.9, 0.55 + abs(raw_score) * 0.1)
    if label == "neutral":
        confidence = 0.55

    return (
        SentimentData(
            label=label,
            confidence=confidence,
            model_id="marketsage-lexicon-v0",
            fallback=True,
            text_hash=sha256(request.text.encode("utf8")).hexdigest(),
            matched_terms=[*positives, *negatives],
        ),
        ["Using deterministic fallback sentiment; enable model downloads for FinBERT."],
    )


def _score_with_finbert(request: SentimentRequest) -> tuple[SentimentData, list[str]]:
    from transformers import pipeline  # type: ignore

    classifier = pipeline("sentiment-analysis", model="ProsusAI/finbert")
    result = classifier(request.text[:4000])[0]
    label = str(result["label"]).lower()
    if label not in {"positive", "negative", "neutral"}:
        label = "neutral"

    return (
        SentimentData(
            label=label,
            confidence=float(result["score"]),
            model_id="ProsusAI/finbert",
            fallback=False,
            text_hash=sha256(request.text.encode("utf8")).hexdigest(),
            matched_terms=[],
        ),
        [],
    )
