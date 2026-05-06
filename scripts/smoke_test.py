"""Prueba el parser sobre los .DAT de las elecciones municipales de 2019."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Forzamos UTF-8 en stdout para que la consola de Windows no peste con acentos.
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

# Permitir ejecución directa sin instalar el paquete
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from infoelectoral.parser import detect_dat_files, parse_file  # noqa: E402

REF = Path(__file__).resolve().parent.parent / "reference" / "files" / "municipales" / "04201905_MESA"

if not REF.exists():
    raise SystemExit(f"No existe {REF}")

metas = detect_dat_files(REF)
print(f"Detectados {len(metas)} ficheros .DAT en {REF.name}\n")
for m in metas:
    print(f"  {m.filename}  ->  fichero {m.file_code} ({m.file_desc}) | proceso {m.process_code} ({m.process_desc}) | {m.year}-{m.month:02d}")

print("\nProcesando cada fichero…\n")
for m in metas:
    res = parse_file(m.path)
    print(f"  {m.filename}: {len(res.rows)} filas, {res.skipped_lines} saltadas, {len(res.error_lines)} errores")
    if res.error_lines:
        for line_no, err, sample in res.error_lines[:3]:
            print(f"     ! línea {line_no}: {err}")
            print(f"       crudo: {sample}")

# Filtrar Noia (15057) en el fichero 09 (datos de mesas)
print("\n--- Filas del 09 (mesas) en Noia (provincia 'A Coruña', municipio 'Noia') ---")
for m in metas:
    if m.file_code == "09":
        res = parse_file(m.path)
        noia_rows = [r for r in res.rows if r.get("Municipio") == "Noia"]
        print(f"  {len(noia_rows)} mesas en Noia")
        for r in noia_rows[:3]:
            print(json.dumps(r, ensure_ascii=False, indent=2))
        break

# Ejemplo del 04 (candidatos): primer candidato
print("\n--- Primer candidato del 04 ---")
for m in metas:
    if m.file_code == "04":
        res = parse_file(m.path)
        if res.rows:
            print(json.dumps(res.rows[0], ensure_ascii=False, indent=2))
        # Y candidatos de Noia
        noia_cands = [r for r in res.rows if r.get("Municipio") == "Noia"]
        print(f"\n  {len(noia_cands)} candidatos en Noia")
        if noia_cands:
            print(json.dumps(noia_cands[0], ensure_ascii=False, indent=2))
        break
