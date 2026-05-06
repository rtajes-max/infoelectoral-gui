"""
Configuración persistente de la aplicación.

Guarda en %APPDATA%/infoelectoral/ (Windows) o ~/.config/infoelectoral/ (Linux/macOS):
  - presets.json      → presets de filtro por municipio (Noia, Barbanza, mi pueblo X…)
  - settings.json     → preferencias generales (último directorio, idioma, tema)

Los presets son un diccionario {nombre → {provincia, lista_municipios, descripción}}.
Cuando no hay fichero de presets, se cargan unos por defecto (vacíos para que el
usuario los cree, no orientados a ningún municipio concreto).
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Preset:
    """Un preset de filtro: 'Solo X' o 'Solo grupo Y'."""
    name: str
    provincia: str = ""           # nombre tal cual aparece en el .DAT, ej. "A Coruña"
    municipios: list[str] = field(default_factory=list)  # nombres tal cual los devuelve el parser
    description: str = ""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Preset":
        return cls(
            name=d.get("name", ""),
            provincia=d.get("provincia", ""),
            municipios=list(d.get("municipios", [])),
            description=d.get("description", ""),
        )


def config_dir() -> Path:
    """Directorio donde guardamos preferencias del usuario, por OS."""
    if sys.platform == "win32":
        base = Path.home() / "AppData" / "Roaming"
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".config"
    d = base / "infoelectoral"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _presets_path() -> Path:
    return config_dir() / "presets.json"


def _settings_path() -> Path:
    return config_dir() / "settings.json"


# ---------------------------------------------------------------------------
# Presets de filtro
# ---------------------------------------------------------------------------

def load_presets() -> list[Preset]:
    p = _presets_path()
    if not p.exists():
        return []
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
        return [Preset.from_dict(d) for d in raw]
    except Exception:
        return []


def save_presets(presets: list[Preset]) -> None:
    p = _presets_path()
    p.write_text(
        json.dumps([asdict(pr) for pr in presets], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Preferencias generales
# ---------------------------------------------------------------------------

def load_settings() -> dict[str, Any]:
    p = _settings_path()
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_settings(s: dict[str, Any]) -> None:
    p = _settings_path()
    p.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")


def update_setting(key: str, value: Any) -> None:
    s = load_settings()
    s[key] = value
    save_settings(s)
