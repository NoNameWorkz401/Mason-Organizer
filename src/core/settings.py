"""Settings persistence for Mason Organizer."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

SETTINGS_PATH = Path("config/settings.json")


@dataclass
class AppSettings:
    default_folder: str = ""
    preview_before_organize: bool = True
    confirm_before_organize: bool = True
    include_hidden_files: bool = False
    accent_theme: str = "Midnight"
    local_ai_mode: str = "Rule-Based Local"
    export_logs_folder: str = "logs"


def load_settings(path: str | Path = SETTINGS_PATH) -> AppSettings:
    settings_path = Path(path)
    if not settings_path.exists():
        return AppSettings()

    try:
        data: dict[str, Any] = json.loads(settings_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return AppSettings()

    defaults = asdict(AppSettings())
    defaults.update({key: value for key, value in data.items() if key in defaults})
    return AppSettings(**defaults)


def save_settings(settings: AppSettings, path: str | Path = SETTINGS_PATH) -> Path:
    settings_path = Path(path)
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")
    return settings_path
