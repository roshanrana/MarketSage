import os
from dataclasses import dataclass
from pathlib import Path

VALID_MODES = {"seeded", "live", "hybrid"}


@dataclass(frozen=True)
class Settings:
    mode: str
    data_dir: Path
    model_downloads_enabled: bool
    log_level: str
    http_token: str | None

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

        return cls(
            mode=mode,
            data_dir=data_dir,
            model_downloads_enabled=model_downloads_enabled,
            log_level=os.getenv("MARKETSAGE_LOG_LEVEL", "info").strip().lower(),
            http_token=os.getenv("MARKETSAGE_HTTP_TOKEN") or None,
        )
