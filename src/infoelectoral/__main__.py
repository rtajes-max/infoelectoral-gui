"""
Punto de entrada para `python -m infoelectoral` y para el .exe de PyInstaller.

Modos:
    infoelectoral             # arranca la GUI
    infoelectoral --version   # imprime versión + build time
    infoelectoral --diag      # imprime dónde encuentra los recursos y termina
    infoelectoral --diag FICHERO.DAT
                              # además parsea el fichero y reporta filas/errores
"""

from __future__ import annotations

import sys
from pathlib import Path

from infoelectoral import __build_time__, __version__


def _print_version() -> int:
    print(f"infoelectoral {__version__}  (build {__build_time__})")
    return 0


def _diag(args: list[str]) -> int:
    from infoelectoral.resources import data_dir

    print(f"infoelectoral {__version__}  (build {__build_time__})")
    d = data_dir()
    print(f"data_dir = {d}")
    print(f"  existe   = {d.exists()}")
    if d.exists():
        print(f"  contenido = {sorted(p.name for p in d.iterdir())}")
        muni = d / "municipios"
        if muni.exists():
            files = list(muni.glob("*.json"))
            print(f"  municipios .json = {len(files)}")
            print(f"  ejemplos       = {[p.name for p in files[:3]]}")
    print(f"sys._MEIPASS = {getattr(sys, '_MEIPASS', None)}")

    if not args:
        return 0

    target = Path(args[0])
    if not target.exists():
        print(f"\n!! No existe: {target}")
        return 1

    print(f"\n--- Parseando {target} ---")
    from infoelectoral.parser import parse_file

    try:
        res = parse_file(target)
    except Exception as e:
        print(f"!! Excepción global: {e}")
        return 2
    print(f"Filas OK     : {len(res.rows)}")
    print(f"Saltadas     : {res.skipped_lines}")
    print(f"Con errores  : {len(res.error_lines)}")
    if res.error_lines:
        print("\nPrimeros errores únicos:")
        seen: set[str] = set()
        for ln, err, sample in res.error_lines:
            key = err.split(":")[0]
            if key in seen:
                continue
            seen.add(key)
            print(f"  línea {ln}: {err}")
            print(f"    crudo (len={len(sample)}): {sample!r}")
            if len(seen) >= 5:
                break
    elif res.rows:
        print("\nPrimera fila:")
        for k, v in res.rows[0].items():
            print(f"  {k:30s} = {v!r}")
    return 0


def main_cli() -> int:
    if len(sys.argv) > 1:
        flag = sys.argv[1]
        if flag in ("--version", "-V"):
            return _print_version()
        if flag == "--diag":
            return _diag(sys.argv[2:])
    from infoelectoral.gui.app import main
    return main()


raise SystemExit(main_cli())
