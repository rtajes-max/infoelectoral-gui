"""Exportación de filas decodificadas a CSV."""

from __future__ import annotations

import csv
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .formats import FORMATS


def column_order_for(format_code: str) -> list[str]:
    """Orden canónico de columnas para un tipo de fichero (el de la spec del Ministerio)."""
    return [f.name for f in FORMATS[format_code]]


def export_rows(
    rows: Iterable[dict[str, Any]],
    output_path: str | Path,
    *,
    columns: list[str] | None = None,
    delimiter: str = ",",
    encoding: str = "utf-8-sig",
) -> int:
    """
    Escribe `rows` en CSV. Devuelve el número de filas escritas.

    - `utf-8-sig` lleva BOM para que Excel en Windows lo abra con acentos correctos.
    - Si no se pasan `columns`, se infiere de las claves vistas (en orden de aparición).
    - El parser puede omitir campos cuando son `None`; las celdas vacías quedan vacías.
    """
    rows = list(rows)
    if not rows and columns is None:
        # Sin columnas y sin datos: escribe solo BOM + EOL para que el fichero exista.
        Path(output_path).write_text("", encoding=encoding)
        return 0

    if columns is None:
        # Inferimos columnas conservando orden de aparición.
        seen: dict[str, None] = {}
        for r in rows:
            for k in r:
                seen.setdefault(k, None)
        columns = list(seen)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding=encoding, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, delimiter=delimiter, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    return len(rows)
