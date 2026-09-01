from pathlib import Path


def repo_root() -> Path:
    for candidate in [Path.cwd(), *Path(__file__).resolve().parents]:
        if (candidate / "STATE.md").exists():
            return candidate
    return Path.cwd()
