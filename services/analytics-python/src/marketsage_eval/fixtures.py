import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from marketsage_core.repo import repo_root


def fixtures_dir() -> Path:
    return repo_root() / "data" / "fixtures"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


@dataclass(frozen=True)
class RetrievalFixture:
    queries: list[dict[str, Any]]
    relevant: dict[str, set[str]]
    corpus_size: int


@lru_cache(maxsize=1)
def financebench() -> RetrievalFixture:
    base = fixtures_dir() / "financebench"
    queries = load_jsonl(base / "queries.jsonl")
    relevant: dict[str, set[str]] = {}
    for row in load_jsonl(base / "qrels.jsonl"):
        if int(row["score"]) > 0:
            relevant.setdefault(row["query_id"], set()).add(row["corpus_id"])
    corpus_size = len(load_jsonl(base / "corpus.jsonl"))
    return RetrievalFixture(queries=queries, relevant=relevant, corpus_size=corpus_size)


@lru_cache(maxsize=1)
def fiqa() -> list[dict[str, Any]]:
    return load_jsonl(fixtures_dir() / "fiqa" / "test.jsonl")


@lru_cache(maxsize=1)
def manifest() -> dict[str, Any]:
    return json.loads((fixtures_dir() / "manifest.json").read_text(encoding="utf-8"))
