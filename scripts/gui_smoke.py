"""
Smoke test offscreen de la GUI: instancia la ventana, carga una carpeta de prueba,
selecciona un fichero y verifica que la tabla tiene filas. NO abre ninguna ventana
real (usa la plataforma 'offscreen' de Qt).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

# Forzamos el plugin offscreen ANTES de importar nada de Qt.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from infoelectoral.gui.main_window import MainWindow  # noqa: E402

REF = ROOT / "reference" / "files" / "municipales" / "04201905_MESA"
if not REF.exists():
    raise SystemExit(f"No existe {REF}")

app = QApplication(sys.argv)
win = MainWindow()
win.show()

# Disparamos el handler de drop como si el usuario hubiera soltado la carpeta
win._on_paths_dropped([REF])

assert win._metas, "No se han detectado ficheros"
print(f"OK detectados {len(win._metas)} ficheros .DAT en {REF.name}")

# Comprobamos que el primero ha cargado y la tabla tiene filas
assert win.model.rowCount() > 0, "La tabla está vacía tras el primer click"
print(f"OK primer fichero ({win._current_meta.filename}) cargado: {win.model.rowCount()} filas")
print(f"   columnas: {win.model.columns}")

# Buscamos el fichero 09 y lo cargamos a mano
target_meta = next(m for m in win._metas if m.file_code == "09")
win._load_meta(target_meta)
print(f"OK 09 cargado: {win.model.rowCount()} filas")

# Activamos el preset Noia
win.only_noia_cb.setChecked(True)
visible = win.proxy.rowCount()
print(f"OK filtro 'Solo Noia' aplicado: {visible} filas visibles (deberían ser 18 mesas)")
assert visible == 18, f"Esperaba 18 mesas en Noia, tengo {visible}"

# Y Barbanza
win.only_noia_cb.setChecked(False)
win.only_barbanza_cb.setChecked(True)
visible = win.proxy.rowCount()
print(f"OK filtro 'Solo Barbanza' aplicado: {visible} filas visibles (mesas en los 11 concellos)")

# Texto libre
win.only_barbanza_cb.setChecked(False)
win.search_edit.setText("Noia")
visible = win.proxy.rowCount()
print(f"OK filtro de texto 'Noia' aplicado: {visible} filas visibles")

# Limpiar y verificar
win._clear_filters()
print(f"OK limpiar filtros: {win.proxy.rowCount()} filas (debería ser {win.model.rowCount()})")
assert win.proxy.rowCount() == win.model.rowCount()

# Exportación a un CSV temporal
import tempfile
tmp = Path(tempfile.gettempdir()) / "infoelectoral_smoke.csv"
win.only_noia_cb.setChecked(True)
visible_rows = win._visible_rows_in_proxy_order()
from infoelectoral.exporter import export_rows
n = export_rows(visible_rows, tmp, columns=win.model.columns)
print(f"OK exportadas {n} filas a {tmp}")

print("\n=== TODO OK ===")
