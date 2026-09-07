import os
from dataclasses import dataclass
from pathlib import Path

VALID_MODES = {"seeded", "live", "hybrid"}
VALID_SCORERS = {"bm25", "overlap"}


@dataclass(frozen=True)
class Settings:
    mode: str
    data_dir: Path
    model_downloads_enabled: bool
    log_level: str
    http_token: str | None
    retrieval_scorer: str = "bm25"

    @classmethod
    def from_env(cls) -> "Settings":
        mode = os.getenv("MARKETSAGE_MODE", "seeded").strip().lower()
        if mode not in VALID_MODES:
            raise ValueError(
                f"MARKETSAGE_MODE must be one of {sorted(VALID_MODES)}, got {mode!r}"
            )

        data_dir = Path(os.getenv("MARKETSAGE_DATA_DIR", "data/local")).expanduser()
        model_downloads_enabled = os.getenv(
            "MARKETSAGE_ENABLE_MODEL_DOWNLOADS", "false"
        ).strip().lower() in {"1", "true", "yes", "on"}

        scorer = os.getenv("MARKETSAGE_RETRIEVAL_SCORER", "bm25").strip().lower()
        if scorer not in VALID_SCORERS:
            raise ValueError(
                f"MARKETSAGE_RETRIEVAL_SCORER must be one of {sorted(VALID_SCORERS)}, "
                f"got {scorer!r}"
            )

        return cls(
            mode=mode,
            data_dir=data_dir,
            model_downloads_enabled=model_downloads_enabled,
            log_level=os.getenv("MARKETSAGE_LOG_LEVEL", "info").strip().lower(),
            http_token=os.getenv("MARKETSAGE_HTTP_TOKEN") or None,
            retrieval_scorer=scorer,
        )
