"""Diálogo para gestionar presets de filtro por municipio."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ..settings import Preset, load_presets, save_presets


class PresetDialog(QDialog):
    """
    Editor de presets de filtro por municipio.

    Cada preset tiene:
      - Nombre (lo que aparece en el desplegable de la barra de filtros)
      - Provincia (nombre tal cual figura en el .DAT, p. ej. "A Coruña")
      - Lista de municipios (nombres tal cual los devuelve el parser)
      - Descripción opcional
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Presets de filtro por municipio")
        self.resize(720, 480)
        self._presets: list[Preset] = load_presets()

        outer = QVBoxLayout(self)

        intro = QLabel(
            "Crea grupos de municipios para filtrar rápidamente. Los nombres deben "
            "coincidir <b>literalmente</b> con los del Ministerio (p. ej. «A Coruña», "
            "«Noia», «Pobra do Caramiñal, A»). Los presets se guardan en tu carpeta "
            "de usuario y persisten entre sesiones."
        )
        intro.setWordWrap(True)
        outer.addWidget(intro)

        splitter = QSplitter(Qt.Horizontal)
        outer.addWidget(splitter, 1)

        # Sidebar: lista de presets
        sidebar = QWidget()
        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(0, 0, 0, 0)
        sb.addWidget(QLabel("<b>Presets</b>"))
        self.list = QListWidget()
        self.list.currentItemChanged.connect(self._on_select)
        sb.addWidget(self.list, 1)
        sb_btns = QHBoxLayout()
        self.btn_new = QPushButton("Nuevo")
        self.btn_dup = QPushButton("Duplicar")
        self.btn_del = QPushButton("Borrar")
        self.btn_new.clicked.connect(self._on_new)
        self.btn_dup.clicked.connect(self._on_duplicate)
        self.btn_del.clicked.connect(self._on_delete)
        sb_btns.addWidget(self.btn_new)
        sb_btns.addWidget(self.btn_dup)
        sb_btns.addWidget(self.btn_del)
        sb.addLayout(sb_btns)
        splitter.addWidget(sidebar)

        # Editor del preset seleccionado
        editor = QWidget()
        ed = QVBoxLayout(editor)
        ed.setContentsMargins(8, 0, 0, 0)

        ed.addWidget(QLabel("<b>Nombre del preset</b> (como aparecerá en el menú de filtros)"))
        self.edit_name = QLineEdit()
        self.edit_name.editingFinished.connect(self._save_current)
        ed.addWidget(self.edit_name)

        ed.addWidget(QLabel("<b>Provincia</b> (opcional, restringe el match)"))
        self.edit_provincia = QLineEdit()
        self.edit_provincia.setPlaceholderText("Ej. A Coruña")
        self.edit_provincia.editingFinished.connect(self._save_current)
        ed.addWidget(self.edit_provincia)

        ed.addWidget(QLabel("<b>Municipios</b> — un nombre por línea, tal cual aparece en el Ministerio"))
        self.edit_municipios = QLineEdit()
        self.edit_municipios.setVisible(False)  # placeholder, lo sustituimos por QPlainTextEdit
        from PySide6.QtWidgets import QPlainTextEdit
        self.txt_municipios = QPlainTextEdit()
        self.txt_municipios.setPlaceholderText("Noia\nLousame\nOutes\n…")
        self.txt_municipios.textChanged.connect(self._save_current)
        ed.addWidget(self.txt_municipios, 1)

        ed.addWidget(QLabel("<b>Descripción</b> (opcional)"))
        self.edit_desc = QLineEdit()
        self.edit_desc.editingFinished.connect(self._save_current)
        ed.addWidget(self.edit_desc)

        splitter.addWidget(editor)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([220, 500])

        # Botones
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)

        self._populate_list()
        if self._presets:
            self.list.setCurrentRow(0)
        else:
            self._set_editor_enabled(False)

    # ---- Helpers ---------------------------------------------------------

    def _populate_list(self) -> None:
        self.list.clear()
        for p in self._presets:
            item = QListWidgetItem(p.name or "(sin nombre)")
            self.list.addItem(item)

    def _set_editor_enabled(self, enabled: bool) -> None:
        for w in (self.edit_name, self.edit_provincia, self.txt_municipios, self.edit_desc):
            w.setEnabled(enabled)

    def _current_index(self) -> int:
        return self.list.currentRow()

    # ---- Slots -----------------------------------------------------------

    def _on_select(self, current: QListWidgetItem | None, _previous) -> None:
        if current is None:
            self._set_editor_enabled(False)
            self.edit_name.clear()
            self.edit_provincia.clear()
            self.txt_municipios.clear()
            self.edit_desc.clear()
            return
        self._set_editor_enabled(True)
        i = self.list.row(current)
        if 0 <= i < len(self._presets):
            p = self._presets[i]
            # Bloqueamos señales para no disparar _save_current durante la carga
            for w in (self.edit_name, self.edit_provincia, self.txt_municipios, self.edit_desc):
                w.blockSignals(True)
            self.edit_name.setText(p.name)
            self.edit_provincia.setText(p.provincia)
            self.txt_municipios.setPlainText("\n".join(p.municipios))
            self.edit_desc.setText(p.description)
            for w in (self.edit_name, self.edit_provincia, self.txt_municipios, self.edit_desc):
                w.blockSignals(False)

    def _save_current(self) -> None:
        i = self._current_index()
        if not (0 <= i < len(self._presets)):
            return
        municipios = [
            line.strip()
            for line in self.txt_municipios.toPlainText().splitlines()
            if line.strip()
        ]
        self._presets[i] = Preset(
            name=self.edit_name.text().strip(),
            provincia=self.edit_provincia.text().strip(),
            municipios=municipios,
            description=self.edit_desc.text().strip(),
        )
        # Refrescamos el label en la lista
        self.list.item(i).setText(self._presets[i].name or "(sin nombre)")

    def _on_new(self) -> None:
        name, ok = QInputDialog.getText(self, "Nuevo preset", "Nombre del preset:")
        if not ok or not name.strip():
            return
        self._presets.append(Preset(name=name.strip()))
        self._populate_list()
        self.list.setCurrentRow(len(self._presets) - 1)

    def _on_duplicate(self) -> None:
        i = self._current_index()
        if not (0 <= i < len(self._presets)):
            return
        original = self._presets[i]
        copy = Preset(
            name=f"{original.name} (copia)",
            provincia=original.provincia,
            municipios=list(original.municipios),
            description=original.description,
        )
        self._presets.insert(i + 1, copy)
        self._populate_list()
        self.list.setCurrentRow(i + 1)

    def _on_delete(self) -> None:
        i = self._current_index()
        if not (0 <= i < len(self._presets)):
            return
        ans = QMessageBox.question(
            self,
            "Borrar preset",
            f"¿Borrar el preset «{self._presets[i].name}»?",
        )
        if ans != QMessageBox.Yes:
            return
        del self._presets[i]
        self._populate_list()
        if self._presets:
            self.list.setCurrentRow(max(0, i - 1))

    # ---- Persistencia ----------------------------------------------------

    def accept(self) -> None:
        self._save_current()
        # Eliminamos presets vacíos de nombre
        self._presets = [p for p in self._presets if p.name]
        save_presets(self._presets)
        super().accept()

    def presets(self) -> list[Preset]:
        return list(self._presets)
