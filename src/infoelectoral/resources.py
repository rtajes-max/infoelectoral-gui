"""Localiza el directorio `data/` tanto en desarrollo como dentro del .exe (PyInstaller)."""

from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def data_dir() -> Path:
    # En el .exe PyInstaller descomprime los recursos en `sys._MEIPASS`.
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass) / "data"
    # En desarrollo: data/ vive en la raíz del repo, dos niveles por encima de este fichero.
    return Path(__file__).resolve().parent.parent.parent / "data"
