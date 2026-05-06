"""
Carga las tablas de municipios INE en función del año del proceso electoral.

Replica la lógica de `parse.php`:
    require sprintf('includes/municipios/%s.php', $año >= 2001 ? $año : '2001');
    const MUNICIPIOS = MUNICIPIOS_INE + MUNICIPIOS_INEXISTENTES;

Si el año pedido no está disponible se usa el más cercano (con mensaje de aviso).
Cachea cada tabla en memoria.
"""

from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path

from .resources import data_dir


@lru_cache(maxsize=1)
def _municipios_inexistentes() -> dict[str, str | None]:
    path = data_dir() / "municipios_inexistentes.json"
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def _ine_table_for_year(year: int) -> dict[str, str]:
    available = sorted(int(p.stem) for p in (data_dir() / "municipios").glob("*.json"))
    if not available:
        raise RuntimeError("No hay tablas de municipios en data/municipios/. Ejecuta scripts/extract_constants.py.")

    if year < available[0]:
        # Igual que en el PHP original: usar la tabla más antigua para todo lo anterior.
        chosen = available[0]
    elif year > available[-1]:
        chosen = available[-1]
        print(f"[municipios] Aviso: no hay tabla para {year}, uso {chosen}", file=sys.stderr)
    elif year in available:
        chosen = year
    else:
        # Año intermedio sin tabla — toma la más cercana hacia atrás.
        chosen = max(y for y in available if y <= year)

    path = data_dir() / "municipios" / f"{chosen}.json"
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def municipios_for_year(year: int) -> dict[str, str | None]:
    """Devuelve el merge MUNICIPIOS_INE + MUNICIPIOS_INEXISTENTES."""
    out: dict[str, str | None] = dict(_ine_table_for_year(year))
    # En PHP el operador `+` no machaca claves existentes: las del INE prevalecen.
    for code, name in _municipios_inexistentes().items():
        out.setdefault(code, name)
    return out


def lookup_municipio(year: int, codigo_5dig: str) -> str | None:
    return municipios_for_year(year).get(codigo_5dig)
