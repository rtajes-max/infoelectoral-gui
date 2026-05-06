"""
Pasa el parser por todos los .DAT del usuario y reporta filas OK / errores
agrupado por año y tipo de fichero. Útil para detectar formatos antiguos
del Ministerio que requieran fixups adicionales.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from infoelectoral.parser import parse_file  # noqa: E402

USER_BASE = Path(r"D:\PSdeG-PSOE de Noia\Datos Elecciones")

if not USER_BASE.exists():
    raise SystemExit(f"No existe {USER_BASE}")

# Agrupamos por (año, tipo_fichero) para no parsear duplicados (TOTA / Mesas / Superior)
seen: dict[tuple[str, str], Path] = {}
for p in sorted(USER_BASE.rglob("*.DAT")):
    if p.stat().st_size == 0:
        continue
    # nombre tipo NNXXAAMM.DAT
    nn, xx, aa, mm = p.stem[0:2], p.stem[2:4], p.stem[4:6], p.stem[6:8]
    key = (aa, nn)
    # Preferimos la copia "Mesas" (la más completa) si está; si no, lo que haya
    parent = p.parent.name
    priority = {"Mesas": 0, "Superior": 1}.get(parent, 2)
    if key not in seen or priority < seen[key][1]:
        seen[key] = (p, priority)

total_files = total_rows = total_errors = total_skipped = 0
problems: list[tuple[Path, int, int, str]] = []

print(f"{'fichero':28s}  {'filas OK':>10s}  {'errores':>8s}  {'saltadas':>8s}  primer error")
print("-" * 110)
for (aa, nn), (path, _) in sorted(seen.items()):
    try:
        res = parse_file(path)
    except Exception as e:
        print(f"{path.name:28s}  EXCEPCIÓN: {e}")
        continue

    total_files += 1
    total_rows += len(res.rows)
    total_errors += len(res.error_lines)
    total_skipped += res.skipped_lines

    sample = ""
    if res.error_lines:
        sample = res.error_lines[0][1][:70]
        problems.append((path, len(res.rows), len(res.error_lines), sample))

    label = f"{aa}/{nn}  {path.parent.name[:8]}"
    print(f"{label:28s}  {len(res.rows):>10d}  {len(res.error_lines):>8d}  {res.skipped_lines:>8d}  {sample}")

print("-" * 110)
print(f"\nTotal: {total_files} ficheros · {total_rows:,} filas OK · {total_errors:,} errores · {total_skipped:,} saltadas")

if problems:
    print(f"\n=== Ficheros con errores ({len(problems)}) ===")
    for p, ok, err, sample in problems:
        print(f"  {p}")
        print(f"    {ok:,} OK / {err:,} errores  ·  ejemplo: {sample}")
