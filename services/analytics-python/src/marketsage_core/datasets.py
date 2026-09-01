from dataclasses import dataclass

from marketsage_core.config import Settings
from marketsage_core.models import DatasetEntry
from marketsage_core.storage import write_dataset_manifest


@dataclass(frozen=True)
class DatasetDefinition:
    dataset_id: str
    config: str
    split: str
    rows_count: int
    license: str
    source_url: str
    role: str
    local_status: str = "metadata-ready"

    def to_entry(self) -> DatasetEntry:
        return DatasetEntry(
            dataset_id=self.dataset_id,
            config=self.config,
            split=self.split,
            rows_count=self.rows_count,
            license=self.license,
            source_url=self.source_url,
            role=self.role,
            local_status=self.local_status,
        )


DATASETS = [
    DatasetDefinition(
        dataset_id="zeroshot/twitter-financial-news-sentiment",
        config="default",
        split="train",
        rows_count=9543,
        license="MIT",
        source_url="https://huggingface.co/datasets/zeroshot/twitter-financial-news-sentiment",
        role="Seed sentiment examples.",
    ),
    DatasetDefinition(
        dataset_id="zeroshot/twitter-financial-news-sentiment",
        config="default",
        split="validation",
        rows_count=2388,
        license="MIT",
        source_url="https://huggingface.co/datasets/zeroshot/twitter-financial-news-sentiment",
        role="Seed sentiment validation examples.",
    ),
    DatasetDefinition(
        dataset_id="TheFinAI/fiqa-sentiment-classification",
        config="default",
        split="train",
        rows_count=822,
        license="MIT",
        source_url="https://huggingface.co/datasets/TheFinAI/fiqa-sentiment-classification",
        role="Sentiment evaluation fixture.",
    ),
    DatasetDefinition(
        dataset_id="TheFinAI/fiqa-sentiment-classification",
        config="default",
        split="test",
        rows_count=234,
        license="MIT",
        source_url="https://huggingface.co/datasets/TheFinAI/fiqa-sentiment-classification",
        role="Sentiment evaluation fixture.",
    ),
    DatasetDefinition(
        dataset_id="TheFinAI/fiqa-sentiment-classification",
        config="default",
        split="valid",
        rows_count=117,
        license="MIT",
        source_url="https://huggingface.co/datasets/TheFinAI/fiqa-sentiment-classification",
        role="Sentiment evaluation fixture.",
    ),
    DatasetDefinition(
        dataset_id="mteb/FinanceBenchRetrieval",
        config="corpus",
        split="test",
        rows_count=145,
        license="MIT",
        source_url="https://huggingface.co/datasets/mteb/FinanceBenchRetrieval",
        role="Evidence retrieval corpus fixture.",
    ),
    DatasetDefinition(
        dataset_id="mteb/FinanceBenchRetrieval",
        config="qrels",
        split="test",
        rows_count=150,
        license="MIT",
        source_url="https://huggingface.co/datasets/mteb/FinanceBenchRetrieval",
        role="Evidence retrieval relevance fixture.",
    ),
    DatasetDefinition(
        dataset_id="mteb/FinanceBenchRetrieval",
        config="queries",
        split="test",
        rows_count=150,
        license="MIT",
        source_url="https://huggingface.co/datasets/mteb/FinanceBenchRetrieval",
        role="Evidence retrieval query fixture.",
    ),
    DatasetDefinition(
        dataset_id="glopardo/sp500-earnings-transcripts",
        config="default",
        split="train",
        rows_count=20681,
        license="license-check-required",
        source_url="https://huggingface.co/datasets/glopardo/sp500-earnings-transcripts",
        role="Optional transcript corpus after license check.",
        local_status="blocked-license-review",
    ),
]


def dataset_entries(settings: Settings) -> list[DatasetEntry]:
    entries = [dataset.to_entry() for dataset in DATASETS]
    write_dataset_manifest(settings, entries)
    return entries
