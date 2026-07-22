from __future__ import annotations

import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path


DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "config.toml"
USER_CONFIG = Path.home() / ".config" / "voice-type" / "config.toml"


@dataclass
class Config:
    hotkey: str = "<f8>"
    model: str = "large-v3-turbo"
    device: str = "cuda"
    compute_type: str = "float16"
    language: str = "auto"
    beam_size: int = 5
    notifications: bool = True
    sample_rate: int = 16000
    audio_backend: str = "pulse"
    device_name: str = "default"
    model_dir: Path = Path.home() / ".cache" / "voice-type" / "models"

    @classmethod
    def load(cls, path: Path | None = None) -> Config:
        cfg = cls()
        for candidate in (path, USER_CONFIG, DEFAULT_CONFIG):
            if candidate is None or not candidate.is_file():
                continue
            with candidate.open("rb") as f:
                data = tomllib.load(f)
            general = data.get("general", {})
            audio = data.get("audio", {})
            cfg.hotkey = general.get("hotkey", cfg.hotkey)
            cfg.model = general.get("model", cfg.model)
            cfg.device = general.get("device", cfg.device)
            cfg.compute_type = general.get("compute_type", cfg.compute_type)
            cfg.language = general.get("language", cfg.language)
            cfg.beam_size = int(general.get("beam_size", cfg.beam_size))
            cfg.notifications = bool(general.get("notifications", cfg.notifications))
            cfg.sample_rate = int(audio.get("sample_rate", cfg.sample_rate))
            cfg.audio_backend = audio.get("backend", cfg.audio_backend)
            cfg.device_name = audio.get("device_name", cfg.device_name)
            break
        cfg.model_dir.mkdir(parents=True, exist_ok=True)
        return cfg


def ensure_python() -> None:
    if sys.version_info < (3, 10):
        raise SystemExit("Python 3.10+ is required")
