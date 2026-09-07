"""The MarketSage response contracts as one JSON Schema document.

``packages/contracts/marketsage.schema.json`` is generated from the Pydantic
models here, so the schema can never drift from what the API actually emits.
``export_schema`` writes it; the evaluation harness and the test suite compare
the committed file with a fresh export and validate live responses against it.
"""

import json
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter

from marketsage_core.models import (
    DatasetStatusData,
    EvidenceSearchData,
    HealthData,
    MarketSnapshotData,
    PriceHistoryData,
    ResearchBriefData,
    ResponseEnvelope,
    SavedResearchRunData,
    SentimentData,
)
from marketsage_core.repo import repo_root

SCHEMA_ID = "https://marketsage.local/schemas/marketsage.schema.json"

# Endpoint path -> (envelope definition name, data model). One entry per tool
# the Go gateway exposes, plus the saved-run resource.
ENDPOINTS: dict[str, tuple[str, type[Any]]] = {
    "/health": ("HealthEnvelope", HealthData),
    "/datasets": ("DatasetStatusEnvelope", DatasetStatusData),
    "/market/snapshot": ("MarketSnapshotEnvelope", MarketSnapshotData),
    "/market/history": ("PriceHistoryEnvelope", PriceHistoryData),
    "/sentiment/text": ("SentimentEnvelope", SentimentData),
    "/evidence/search": ("EvidenceSearchEnvelope", EvidenceSearchData),
    "/briefs/research": ("ResearchBriefEnvelope", ResearchBriefData),
    "/runs/{run_id}": ("SavedResearchRunEnvelope", SavedResearchRunData),
}


def schema_path() -> Path:
    return repo_root() / "packages" / "contracts" / "marketsage.schema.json"


def build_schema() -> dict[str, Any]:
    defs: dict[str, Any] = {}
    envelopes: dict[str, Any] = {}
    for path, (envelope_name, data_model) in ENDPOINTS.items():
        adapter = TypeAdapter(ResponseEnvelope[data_model])  # type: ignore[valid-type]
        raw = adapter.json_schema(ref_template="#/$defs/{model}", mode="serialization")
        nested = raw.pop("$defs", {})
        for name, definition in nested.items():
            defs[name] = _strict(definition)
        raw.pop("title", None)
        defs[envelope_name] = _strict(raw)
        envelopes[envelope_name] = path
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": SCHEMA_ID,
        "title": "MarketSage Contracts",
        "description": (
            "Generated from marketsage_core.models by marketsage_core.contracts. "
            "Do not edit by hand; run `npm run contracts`."
        ),
        "type": "object",
        "endpoints": envelopes,
        "$defs": dict(sorted(defs.items())),
    }


def export_schema(path: Path | None = None) -> Path:
    target = path or schema_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_schema(build_schema()), encoding="utf-8", newline="\n")
    return target


def render_schema(schema: dict[str, Any]) -> str:
    return json.dumps(schema, indent=2, sort_keys=False) + "\n"


def committed_schema() -> dict[str, Any]:
    return json.loads(schema_path().read_text(encoding="utf-8"))


def envelope_schema(schema: dict[str, Any], endpoint: str) -> dict[str, Any]:
    """A self-contained schema for one endpoint, usable with any validator."""
    envelope_name = ENDPOINTS[endpoint][0]
    return {
        "$schema": schema["$schema"],
        "$defs": schema["$defs"],
        **schema["$defs"][envelope_name],
    }


def _strict(definition: dict[str, Any]) -> dict[str, Any]:
    """Objects reject unknown keys, so both languages must agree on every field."""
    if definition.get("type") == "object" and "properties" in definition:
        return {**definition, "additionalProperties": False}
    return definition


if __name__ == "__main__":
    print(export_schema())
