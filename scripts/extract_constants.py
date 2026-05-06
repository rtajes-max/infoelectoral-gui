"""
Extrae las tablas grandes de los .php de JaimeObregon/infoelectoral a JSON.

Lee `reference/src/includes/constants.php` y `reference/src/includes/municipios/*.php`
y escribe en `data/`:
  - data/municipios/<año>.json   (un dict código_INE -> nombre)
  - data/municipios_inexistentes.json

El resto de constantes (AUTONOMIAS, PROVINCIAS, FICHEROS, PROCESOS, DISTRITOS) son
pequeñas y van directamente como literales en infoelectoral/constants.py — no se
extraen aquí.

Ejecutar una sola vez tras clonar `reference/`:

    python scripts/extract_constants.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF_INCLUDES = ROOT / "reference" / "src" / "includes"
OUT_DIR = ROOT / "data"

# Captura líneas tipo:   '15057' => 'Noia',
# El nombre puede contener apóstrofo PHP escapado como \' y barras /.
LINE_RE = re.compile(r"^\s*'(\d{5})'\s*=>\s*'((?:[^'\\]|\\.)*)'\s*,?\s*$")
# Para MUNICIPIOS_INEXISTENTES el valor puede ser null
LINE_RE_NULLABLE = re.compile(
    r"^\s*'(\d{5})'\s*=>\s*(?:null|'((?:[^'\\]|\\.)*)')\s*,?\s*$"
)


def _unescape_php_single_quoted(s: str) -> str:
    return s.replace(r"\\", "\\").replace(r"\'", "'")


def parse_php_assoc_array(php_text: str, *, allow_null: bool = False) -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    pattern = LINE_RE_NULLABLE if allow_null else LINE_RE
    for line in php_text.splitlines():
        m = pattern.match(line)
        if not m:
            continue
        code = m.group(1)
        # group(2) será None si el valor era `null`
        raw = m.group(2)
        out[code] = _unescape_php_single_quoted(raw) if raw is not None else None
    return out


def extract_municipios_year(year_php: Path, out_path: Path) -> int:
    text = year_php.read_text(encoding="utf-8")
    table = parse_php_assoc_array(text, allow_null=False)
    if not table:
        raise SystemExit(f"No se han extraído municipios de {year_php}")
    out_path.write_text(json.dumps(table, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return len(table)


def extract_municipios_inexistentes(constants_php: Path, out_path: Path) -> int:
    text = constants_php.read_text(encoding="utf-8")
    # MUNICIPIOS_INEXISTENTES es la última constante del fichero.
    # Cogemos solo el bloque entre `MUNICIPIOS_INEXISTENTES = [` y el `];` que cierra.
    start = text.find("const MUNICIPIOS_INEXISTENTES")
    if start < 0:
        raise SystemExit("No encuentro MUNICIPIOS_INEXISTENTES en constants.php")
    block = text[start:]
    end = block.find("];")
    if end < 0:
        raise SystemExit("Bloque MUNICIPIOS_INEXISTENTES no cerrado")
    block = block[: end + 2]
    table = parse_php_assoc_array(block, allow_null=True)
    out_path.write_text(json.dumps(table, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return len(table)


def main() -> int:
    if not REF_INCLUDES.exists():
        print(f"No existe {REF_INCLUDES}.", file=sys.stderr)
        print("Clona primero el repo de referencia:", file=sys.stderr)
        print("  git clone --depth 1 https://github.com/JaimeObregon/infoelectoral.git reference", file=sys.stderr)
        return 1

    (OUT_DIR / "municipios").mkdir(parents=True, exist_ok=True)

    years_dir = REF_INCLUDES / "municipios"
    php_files = sorted(years_dir.glob("*.php"))
    if not php_files:
        print(f"No hay ficheros .php en {years_dir}", file=sys.stderr)
        return 1

    total = 0
    for php in php_files:
        year = php.stem
        out = OUT_DIR / "municipios" / f"{year}.json"
        n = extract_municipios_year(php, out)
        total += n
        print(f"  {year}: {n:>5} municipios -> {out.relative_to(ROOT)}")

    inex = extract_municipios_inexistentes(REF_INCLUDES / "constants.php", OUT_DIR / "municipios_inexistentes.json")
    print(f"  inexistentes: {inex} entradas -> data/municipios_inexistentes.json")
    print(f"\nTotal: {total} entradas en {len(php_files)} años")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
