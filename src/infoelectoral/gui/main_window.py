"""
Ventana principal del visor.

Layout:
    +--------------------------------------------------------------+
    |  toolbar (acciones principales · About · Presets · ayuda)    |
    +--------------------------------------------------------------+
    |  [drop zone]                                                  |
    +-------+------------------------------------------------------+
    | files |  filtros: buscar texto · municipio · presets         |
    | side  +------------------------------------------------------+
    | bar   |  QTableView (filas decodificadas)                    |
    |       |                                                      |
    +-------+------------------------------------------------------+
    | barra de estado: total / visibles / seleccionadas | tiempo   |
    +--------------------------------------------------------------+

La aplicación es genérica: no asume ningún municipio concreto. El usuario crea
sus propios «presets» (Mi pueblo, Mi comarca, …) en el diálogo de Presets, y
los selecciona desde la barra de filtros.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import QSortFilterProxyModel, Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from ..exporter import export_rows
from ..parser import FileMeta, ParseResult, detect_dat_files, parse_file
from ..settings import Preset, load_presets, load_settings, save_presets, update_setting
from .about_dialog import AboutDialog
from .data_model import DatFilterProxy, DatTableModel
from .drop_zone import DropZone
from .preset_dialog import PresetDialog


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("infoelectoral · visor de microdatos del Ministerio")
        self.resize(1320, 840)

        self._current_meta: FileMeta | None = None
        self._current_result: ParseResult | None = None
        self._metas: list[FileMeta] = []
        self._presets: list[Preset] = load_presets()
        self._settings: dict[str, Any] = load_settings()

        self._build_ui()
        self._build_toolbar()
        self._refresh_preset_combo()

    # ---- Construcción de la UI --------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(10)

        # Drop zone
        self.drop_zone = DropZone()
        self.drop_zone.paths_dropped.connect(self._on_paths_dropped)
        outer.addWidget(self.drop_zone)

        # Splitter sidebar | tabla
        splitter = QSplitter(Qt.Horizontal)
        outer.addWidget(splitter, 1)

        # Sidebar
        sidebar = QWidget()
        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(0, 0, 0, 0)
        sb.setSpacing(6)
        self.sidebar_label = QLabel("<b>Ficheros detectados</b>")
        sb.addWidget(self.sidebar_label)
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self._on_file_clicked)
        sb.addWidget(self.file_list, 1)
        splitter.addWidget(sidebar)

        # Panel derecho: filtros + tabla
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(8)

        # Barra de filtros
        filters = QHBoxLayout()
        filters.setSpacing(8)

        filters.addWidget(QLabel("🔍"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Texto libre — busca en todas las columnas")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.textChanged.connect(self._on_search_changed)
        filters.addWidget(self.search_edit, 2)

        filters.addWidget(QLabel("Municipio"))
        self.muni_edit = QLineEdit()
        self.muni_edit.setPlaceholderText("(cualquiera)")
        self.muni_edit.setClearButtonEnabled(True)
        self.muni_edit.textChanged.connect(self._on_muni_changed)
        filters.addWidget(self.muni_edit, 1)

        filters.addWidget(QLabel("Preset"))
        self.preset_combo = QComboBox()
        self.preset_combo.setMinimumWidth(180)
        self.preset_combo.currentIndexChanged.connect(self._on_preset_changed)
        filters.addWidget(self.preset_combo, 1)

        clear_btn = QPushButton("Limpiar filtros")
        clear_btn.clicked.connect(self._clear_filters)
        filters.addWidget(clear_btn)
        rl.addLayout(filters)

        # Tabla
        from PySide6.QtWidgets import QTableView

        self.table = QTableView()
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.ExtendedSelection)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionsMovable(True)
        self.table.verticalHeader().setVisible(False)
        rl.addWidget(self.table, 1)

        self.model = DatTableModel(columns=[], rows=[])
        self.proxy: QSortFilterProxyModel = DatFilterProxy(self)
        self.proxy.setSourceModel(self.model)
        self.table.setModel(self.proxy)
        self.table.selectionModel().selectionChanged.connect(self._update_status)

        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([300, 1000])

        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Sin datos cargados.")
        self.status_bar.addWidget(self.status_label, 1)

    def _build_toolbar(self) -> None:
        tb = QToolBar("Acciones")
        tb.setMovable(False)
        self.addToolBar(tb)

        self.act_export_visible = QAction("Exportar visibles", self)
        self.act_export_visible.setShortcut(QKeySequence("Ctrl+E"))
        self.act_export_visible.triggered.connect(self._export_visible)
        tb.addAction(self.act_export_visible)

        self.act_export_selected = QAction("Exportar selección", self)
        self.act_export_selected.setShortcut(QKeySequence("Ctrl+Shift+E"))
        self.act_export_selected.triggered.connect(self._export_selected)
        tb.addAction(self.act_export_selected)

        self.act_export_all = QAction("Exportar todo", self)
        self.act_export_all.triggered.connect(self._export_all)
        tb.addAction(self.act_export_all)

        tb.addSeparator()

        self.act_export_batch = QAction("Volcar carpeta a CSVs…", self)
        self.act_export_batch.triggered.connect(self._export_batch)
        tb.addAction(self.act_export_batch)

        tb.addSeparator()

        self.act_show_errors = QAction("Ver errores…", self)
        self.act_show_errors.triggered.connect(self._show_errors_dialog)
        self.act_show_errors.setEnabled(False)
        tb.addAction(self.act_show_errors)

        self.act_presets = QAction("Presets…", self)
        self.act_presets.triggered.connect(self._open_presets_dialog)
        tb.addAction(self.act_presets)

        # Spacer + About
        spacer = QWidget()
        spacer.setSizePolicy(spacer.sizePolicy().horizontalPolicy().Expanding,
                             spacer.sizePolicy().verticalPolicy())
        tb.addWidget(spacer)

        self.act_about = QAction("Acerca de", self)
        self.act_about.triggered.connect(self._show_about)
        tb.addAction(self.act_about)

        self._set_export_enabled(False)

    def _set_export_enabled(self, enabled: bool) -> None:
        for a in (self.act_export_visible, self.act_export_selected, self.act_export_all):
            a.setEnabled(enabled)
        self.act_export_batch.setEnabled(bool(self._metas))

    # ---- Manejo de drop / sidebar -----------------------------------------

    def _on_paths_dropped(self, paths: list[Path]) -> None:
        all_metas: list[FileMeta] = []
        for p in paths:
            if not p.exists():
                continue
            if p.is_file():
                from ..parser import parse_name

                m = parse_name(p)
                if m is not None:
                    all_metas.append(m)
            else:
                all_metas.extend(detect_dat_files(p))

        # Dedup por ruta
        seen: set[Path] = set()
        unique: list[FileMeta] = []
        for m in all_metas:
            if m.path not in seen:
                seen.add(m.path)
                unique.append(m)

        if not unique:
            QMessageBox.warning(
                self, "Sin ficheros",
                "No se han encontrado ficheros .DAT del Ministerio en lo que has soltado."
            )
            return

        # Recordamos el último directorio
        try:
            update_setting("last_directory", str(paths[0]))
        except Exception:
            pass

        self._metas = unique
        self._populate_sidebar()
        self.drop_zone.set_status(
            f"Cargados {len(unique)} ficheros .DAT — pincha uno en la columna izquierda."
        )
        self.act_export_batch.setEnabled(True)

    def _populate_sidebar(self) -> None:
        self.file_list.clear()
        for m in self._metas:
            label = f"{m.filename}  ·  {m.process_desc} {m.year}/{m.month:02d}  ·  ficha {m.file_code}"
            tooltip = f"{m.path}\n{m.file_desc}"
            item = QListWidgetItem(label)
            item.setToolTip(tooltip)
            item.setData(Qt.UserRole, m)
            self.file_list.addItem(item)
        self.sidebar_label.setText(f"<b>Ficheros detectados ({len(self._metas)})</b>")
        if self.file_list.count():
            self.file_list.setCurrentRow(0)
            self._on_file_clicked(self.file_list.item(0))

    def _on_file_clicked(self, item: QListWidgetItem) -> None:
        meta: FileMeta = item.data(Qt.UserRole)
        self._load_meta(meta)

    def _load_meta(self, meta: FileMeta) -> None:
        self.statusBar().showMessage(f"Decodificando {meta.filename}…")
        try:
            result = parse_file(meta.path)
        except Exception as e:
            QMessageBox.critical(self, "Error de decodificación",
                                  f"No he podido decodificar {meta.filename}:\n\n{e}")
            return
        self._current_meta = meta
        self._current_result = result

        from ..parser import column_names

        # Limpiamos filtros del proxy ANTES de cargar el nuevo modelo. Los
        # índices de columna del modelo viejo no son válidos en el nuevo
        # (el número y orden de columnas cambia entre tipos de fichero).
        # El proxy también lo hace en setSourceModel/modelReset, pero blindamos.
        self.proxy.clear_filters()

        self.model.reset_rows(column_names(meta.file_code), result.rows)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)

        # Re-aplicamos filtros del UI sobre el modelo nuevo
        self._reapply_filters()
        self._set_export_enabled(True)
        self.act_show_errors.setEnabled(bool(result.error_lines))
        self._update_status()
        if result.error_lines:
            self.statusBar().showMessage(
                f"{meta.filename}: {len(result.rows):,} filas OK · "
                f"{len(result.error_lines):,} líneas con errores — pulsa «Ver errores…».",
                10000,
            )
        else:
            self.statusBar().showMessage(
                f"{meta.filename}: {len(result.rows):,} filas decodificadas sin errores.", 5000)

    # ---- Filtros ----------------------------------------------------------

    def _on_search_changed(self, text: str) -> None:
        try:
            self.proxy.set_free_text(text)
            self._update_status()
        except Exception as e:
            QMessageBox.warning(self, "Error en filtro de texto", str(e))

    def _on_muni_changed(self, text: str) -> None:
        try:
            cols = self.model.columns
            if "Municipio" not in cols:
                return
            col_idx = cols.index("Municipio")
            text = text.strip()
            if text:
                # Si hay texto, prevalece sobre el preset: quitamos el set
                # exacto y aplicamos contains.
                self.proxy.set_column_in_set(col_idx, None)
                self.proxy.set_column_filter(col_idx, text)
            else:
                self.proxy.set_column_filter(col_idx, "")
                # Volvemos a aplicar el preset si está seleccionado
                self._reapply_preset_only()
            self._update_status()
        except Exception as e:
            QMessageBox.warning(self, "Error en filtro de municipio", str(e))

    def _on_preset_changed(self, idx: int) -> None:
        # idx 0 = "(ninguno)"; idx N = preset N-1
        try:
            cols = self.model.columns
            if "Municipio" not in cols:
                return
            col_idx = cols.index("Municipio")
            prov_idx = cols.index("Provincia") if "Provincia" in cols else -1

            if idx <= 0:
                self.proxy.set_column_in_set(col_idx, None)
                if prov_idx >= 0:
                    self.proxy.set_column_in_set(prov_idx, None)
            else:
                if not (0 <= idx - 1 < len(self._presets)):
                    return
                preset = self._presets[idx - 1]
                municipios_set = set(preset.municipios) if preset.municipios else None
                self.proxy.set_column_in_set(col_idx, municipios_set)
                if prov_idx >= 0 and preset.provincia:
                    self.proxy.set_column_in_set(prov_idx, {preset.provincia})
                elif prov_idx >= 0:
                    self.proxy.set_column_in_set(prov_idx, None)

            self._update_status()
        except Exception as e:
            QMessageBox.warning(self, "Error al aplicar preset", str(e))

    def _reapply_filters(self) -> None:
        self._on_search_changed(self.search_edit.text())
        self._on_muni_changed(self.muni_edit.text())
        self._on_preset_changed(self.preset_combo.currentIndex())

    def _reapply_preset_only(self) -> None:
        self._on_preset_changed(self.preset_combo.currentIndex())

    def _refresh_preset_combo(self) -> None:
        current = self.preset_combo.currentText() if self.preset_combo.count() else ""
        self.preset_combo.blockSignals(True)
        self.preset_combo.clear()
        self.preset_combo.addItem("(ninguno)")
        for p in self._presets:
            self.preset_combo.addItem(p.name)
        # Restauramos selección si encaja
        idx = self.preset_combo.findText(current)
        self.preset_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.preset_combo.blockSignals(False)

    def _clear_filters(self) -> None:
        self.search_edit.clear()
        self.muni_edit.clear()
        self.preset_combo.setCurrentIndex(0)
        self.proxy.clear_filters()
        self._update_status()

    # ---- Estado -----------------------------------------------------------

    def _update_status(self) -> None:
        total = self.model.rowCount()
        visible = self.proxy.rowCount()
        selected = len(self.table.selectionModel().selectedRows()) if self.table.selectionModel() else 0
        info = (
            f"{visible:,} visibles / {total:,} totales · {selected:,} seleccionadas"
            if self._current_meta
            else "Sin datos cargados."
        )
        if self._current_meta:
            info += f"  ·  {self._current_meta.filename} ({self._current_meta.file_desc})"
        if self._current_result and self._current_result.error_lines:
            info += f"  ·  ⚠ {len(self._current_result.error_lines):,} líneas con errores"
        self.status_label.setText(info)

    # ---- Diálogos --------------------------------------------------------

    def _show_about(self) -> None:
        AboutDialog(self).exec()

    def _open_presets_dialog(self) -> None:
        dlg = PresetDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self._presets = dlg.presets()
            self._refresh_preset_combo()

    def _show_errors_dialog(self) -> None:
        if not self._current_result or not self._current_result.error_lines:
            QMessageBox.information(self, "Sin errores",
                                     "No hay líneas con errores en este fichero.")
            return
        from .. import __build_time__, __version__
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Errores en {self._current_meta.filename if self._current_meta else ''}")
        dlg.resize(900, 520)
        lay = QVBoxLayout(dlg)
        header = QLabel(
            f"<b>infoelectoral {__version__}</b> (build {__build_time__})<br>"
            f"<b>Fichero:</b> {self._current_meta.path if self._current_meta else '?'}<br><br>"
            f"<b>{len(self._current_result.error_lines):,} líneas no se han podido decodificar.</b> "
            f"Cada bloque muestra el número de línea, el campo donde falla y el contenido crudo."
        )
        header.setWordWrap(True)
        lay.addWidget(header)

        text = QPlainTextEdit()
        text.setReadOnly(True)
        text.setLineWrapMode(QPlainTextEdit.NoWrap)
        chunks: list[str] = []
        for ln, err, sample in self._current_result.error_lines[:500]:
            chunks.append(f"Línea {ln}\n  Error: {err}\n  Crudo (len={len(sample)}): {sample}\n")
        if len(self._current_result.error_lines) > 500:
            chunks.append(f"\n… y {len(self._current_result.error_lines) - 500:,} más.")
        text.setPlainText("\n".join(chunks))
        lay.addWidget(text, 1)

        btns = QHBoxLayout()
        save_btn = QPushButton("Guardar como .txt…")
        close_btn = QPushButton("Cerrar")
        save_btn.clicked.connect(lambda: self._save_error_log(text.toPlainText()))
        close_btn.clicked.connect(dlg.accept)
        btns.addStretch(1)
        btns.addWidget(save_btn)
        btns.addWidget(close_btn)
        lay.addLayout(btns)

        dlg.exec()

    def _save_error_log(self, content: str) -> None:
        from datetime import datetime

        from .. import __build_time__, __version__

        default = "errores.txt"
        if self._current_meta:
            default = f"{self._current_meta.path.stem}_errores.txt"
        path, _ = QFileDialog.getSaveFileName(self, "Guardar log de errores",
                                                default, "Texto (*.txt)")
        if not path:
            return
        header = (
            f"# infoelectoral {__version__} (build {__build_time__})\n"
            f"# Fichero analizado: {self._current_meta.path if self._current_meta else '?'}\n"
            f"# Generado: {datetime.now().isoformat(timespec='seconds')}\n\n"
        )
        Path(path).write_text(header + content, encoding="utf-8")
        QMessageBox.information(self, "Guardado", f"Log escrito en\n{path}")

    # ---- Exportación ------------------------------------------------------

    def _ask_csv_path(self, default_name: str) -> Path | None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar CSV", default_name, "CSV (*.csv);;Todos los ficheros (*)"
        )
        if not path:
            return None
        p = Path(path)
        if p.suffix.lower() != ".csv":
            p = p.with_suffix(".csv")
        return p

    def _visible_rows_in_proxy_order(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        cols = self.model.columns
        n_visible = self.proxy.rowCount()
        for r in range(n_visible):
            src_index = self.proxy.mapToSource(self.proxy.index(r, 0))
            src_row = src_index.row()
            row_dict = {c: self.model.data(self.model.index(src_row, i), Qt.EditRole)
                        for i, c in enumerate(cols)}
            rows.append(row_dict)
        return rows

    def _selected_rows_in_proxy_order(self) -> list[dict[str, Any]]:
        sel = self.table.selectionModel().selectedRows()
        cols = self.model.columns
        rows: list[dict[str, Any]] = []
        sel_sorted = sorted(sel, key=lambda i: i.row())
        for sproxy in sel_sorted:
            src_index = self.proxy.mapToSource(sproxy)
            src_row = src_index.row()
            row_dict = {c: self.model.data(self.model.index(src_row, i), Qt.EditRole)
                        for i, c in enumerate(cols)}
            rows.append(row_dict)
        return rows

    def _default_basename(self, scope: str) -> str:
        m = self._current_meta
        if not m:
            return f"export_{scope}.csv"
        return f"{m.path.stem}_{scope}.csv"

    def _export(self, rows: list[dict[str, Any]], default_name: str) -> None:
        if not rows:
            QMessageBox.information(self, "Nada que exportar", "No hay filas para exportar.")
            return
        out = self._ask_csv_path(default_name)
        if out is None:
            return
        cols = self.model.columns
        n = export_rows(rows, out, columns=cols)
        QMessageBox.information(self, "Exportado", f"He escrito {n:,} filas en\n{out}")

    def _export_visible(self) -> None:
        rows = self._visible_rows_in_proxy_order()
        self._export(rows, self._default_basename("visibles"))

    def _export_selected(self) -> None:
        rows = self._selected_rows_in_proxy_order()
        self._export(rows, self._default_basename("seleccion"))

    def _export_all(self) -> None:
        if self._current_result is None:
            return
        self._export(list(self._current_result.rows), self._default_basename("todo"))

    def _export_batch(self) -> None:
        if not self._metas:
            return
        directory = QFileDialog.getExistingDirectory(self, "Carpeta de salida para los CSV")
        if not directory:
            return
        out_dir = Path(directory)
        apply_filter = False
        if self._has_any_filter():
            ans = QMessageBox.question(
                self, "Filtros activos",
                "Tienes filtros aplicados. ¿Quieres aplicarlos también al volcado por carpeta?\n\n"
                "Sí = solo filas que pasan los filtros actuales (donde la columna aplique)\n"
                "No = volcar todas las filas",
            )
            apply_filter = ans == QMessageBox.Yes

        from ..parser import column_names

        report: list[str] = []
        for meta in self._metas:
            try:
                result = parse_file(meta.path)
            except Exception as e:
                report.append(f"!! {meta.filename}: error — {e}")
                continue
            cols = column_names(meta.file_code)
            rows = result.rows
            if apply_filter:
                rows = [r for r in rows if self._row_matches_active_filters(r, cols)]
            out = out_dir / f"{meta.path.stem}.csv"
            n = export_rows(rows, out, columns=cols)
            report.append(f"  {meta.filename:24s} → {out.name}  ({n:,} filas)")

        QMessageBox.information(
            self, "Volcado terminado",
            "Se han exportado:\n\n" + "\n".join(report) + f"\n\nCarpeta: {out_dir}",
        )

    def _has_any_filter(self) -> bool:
        return (
            bool(self.search_edit.text().strip())
            or bool(self.muni_edit.text().strip())
            or self.preset_combo.currentIndex() > 0
        )

    def _row_matches_active_filters(self, row: dict[str, Any], cols: list[str]) -> bool:
        # Preset
        idx = self.preset_combo.currentIndex()
        if idx > 0:
            preset = self._presets[idx - 1]
            if "Municipio" in cols and preset.municipios:
                if row.get("Municipio") not in preset.municipios:
                    return False
            if "Provincia" in cols and preset.provincia:
                if row.get("Provincia") != preset.provincia:
                    return False

        # Texto en columna Municipio
        muni_text = self.muni_edit.text().strip().lower()
        if muni_text and "Municipio" in cols:
            if muni_text not in (row.get("Municipio") or "").lower():
                return False

        # Texto libre
        text = self.search_edit.text().strip().lower()
        if text:
            joined = " ".join(str(v) for v in row.values()).lower()
            if text not in joined:
                return False
        return True
