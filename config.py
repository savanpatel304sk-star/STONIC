"""Configuration loading with stable source and PyInstaller resource paths."""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

FROZEN = bool(getattr(sys, "frozen", False))
ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)).resolve()


def _dotenv_paths() -> tuple[Path, ...]:
    paths = [ROOT / ".env"]
    if FROZEN:
        paths.insert(0, Path(sys.executable).resolve().parent / ".env")
        local_appdata = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local"))
        paths.insert(0, local_appdata / "STONIC" / ".env")
    paths.append(Path.home() / ".stonic" / ".env")
    return tuple(dict.fromkeys(paths))


def _read_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if key:
            values[key] = value
    return values


def _environment() -> dict[str, str]:
    values: dict[str, str] = {}
    for path in _dotenv_paths():
        values.update(_read_dotenv(path))
    values.update(os.environ)
    return values


@dataclass(frozen=True)
class Config:
    root: Path
    data_dir: Path
    logs_dir: Path
    database_path: Path
    ai_provider: str
    ai_model: str
    ai_base_url: str
    openai_api_key: str
    personality_name: str
    user_title: str
    response_style: str
    port: int

    @property
    def ai_configured(self) -> bool:
        return self.ai_provider.lower() == "openai" and bool(self.openai_api_key.strip())


def load_config() -> Config:
    env = _environment()
    root = ROOT
    if FROZEN:
        base = Path(env.get("LOCALAPPDATA", Path.home() / ".local")) / "STONIC"
    else:
        base = root
    data_dir = Path(env.get("STONIC_DATA_DIR", base / "data")).expanduser().resolve()
    logs_dir = Path(env.get("STONIC_LOGS_DIR", base / "logs")).expanduser().resolve()
    try:
        port = int(env.get("PORT", "8000"))
    except ValueError:
        port = 8000
    return Config(
        root=root,
        data_dir=data_dir,
        logs_dir=logs_dir,
        database_path=data_dir / "stonic.sqlite3",
        ai_provider=env.get("AI_PROVIDER", "openai").strip().lower(),
        ai_model=env.get("AI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini",
        ai_base_url=env.get("AI_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
        openai_api_key=env.get("OPENAI_API_KEY", "").strip(),
        personality_name=env.get("PERSONALITY_NAME", "STONIC").strip() or "STONIC",
        user_title=env.get("USER_TITLE", "Boss").strip() or "Boss",
        response_style=env.get("RESPONSE_STYLE", "natural").strip() or "natural",
        port=max(1, min(port, 65535)),
    )
