"""Visor y exportador de microdatos electorales del Ministerio del Interior."""

from __future__ import annotations

import datetime as _dt
import sys as _sys
from pathlib import Path as _Path

__version__ = "0.3.2"


def _detect_build_time() -> str:
    # Dentro del .exe: timestamp del propio binario (sys.executable).
    # En dev: timestamp del __init__.py.
    try:
        if getattr(_sys, "frozen", False):
            target = _Path(_sys.executable)
        else:
            target = _Path(__file__)
        return _dt.datetime.fromtimestamp(target.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "desconocido"


__build_time__ = _detect_build_time()
