"""
Modelo Qt para mostrar las filas decodificadas de un .DAT en un QTableView.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt


class DatTableModel(QAbstractTableModel):
    """Tabla bidimensional sobre una lista de dicts (uno por fila)."""

    def __init__(self, columns: list[str], rows: list[dict[str, Any]], parent=None):
        super().__init__(parent)
        self._columns: list[str] = columns
        self._rows: list[dict[str, Any]] = rows

    # ---- Lectura -----------------------------------------------------------

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: B008, N802
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: B008, N802
        return 0 if parent.isValid() else len(self._columns)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:  # noqa: N802
        if not index.isValid():
            return None
        row = self._rows[index.row()]
        col_name = self._columns[index.column()]
        value = row.get(col_name)
        if role == Qt.DisplayRole:
            if value is None:
                return ""
            return str(value)
        if role == Qt.EditRole:
            return value
        if role == Qt.UserRole:
            # Para ordenación numérica nativa del proxy
            return value
        if role == Qt.TextAlignmentRole:
            if isinstance(value, (int, float)):
                return int(Qt.AlignRight | Qt.AlignVCenter)
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:  # noqa: N802
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._columns[section]
        return str(section + 1)

    # ---- Mutación masiva ---------------------------------------------------

    def reset_rows(self, columns: list[str], rows: list[dict[str, Any]]) -> None:
        self.beginResetModel()
        self._columns = columns
        self._rows = rows
        self.endResetModel()

    # ---- Acceso para exportación ------------------------------------------

    @property
    def columns(self) -> list[str]:
        return list(self._columns)

    def rows_at(self, indices: Iterable[int]) -> list[dict[str, Any]]:
        return [self._rows[i] for i in indices if 0 <= i < len(self._rows)]


class DatFilterProxy(QSortFilterProxyModel):
    """
    Proxy con dos filtros combinables:
      - texto libre (substring case-insensitive sobre cualquier columna visible)
      - filtros por columna concretos: dict columna_idx -> substring

    También ordena numéricamente cuando la celda es int/float.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._free_text = ""
        self._column_filters: dict[int, str] = {}
        self._column_in_set: dict[int, set[str]] = {}
        self.setSortRole(Qt.UserRole)
        self.setDynamicSortFilter(True)

    def setSourceModel(self, sourceModel) -> None:  # noqa: N802, N803
        """Limpia los filtros cuando cambia el modelo (las columnas pueden cambiar)."""
        previous = self.sourceModel()
        if previous is not None:
            try:
                previous.modelReset.disconnect(self._on_source_reset)
            except (RuntimeError, TypeError):
                pass
        super().setSourceModel(sourceModel)
        if sourceModel is not None:
            sourceModel.modelReset.connect(self._on_source_reset)
        self._on_source_reset()

    def _on_source_reset(self) -> None:
        # Cuando el modelo se resetea, los índices de columna pueden quedar
        # obsoletos (cambia el número y orden de columnas). Limpiamos filtros
        # de columna; el caller (main_window) los volverá a aplicar contra el
        # nuevo modelo si procede.
        self._column_filters.clear()
        self._column_in_set.clear()
        self.invalidateRowsFilter()

    def set_free_text(self, text: str) -> None:
        self._free_text = text.strip().lower()
        self.invalidateRowsFilter()

    def set_column_filter(self, column: int, text: str) -> None:
        text = text.strip().lower()
        if text:
            self._column_filters[column] = text
        else:
            self._column_filters.pop(column, None)
        self.invalidateRowsFilter()

    def set_column_in_set(self, column: int, values: set[str] | None) -> None:
        """Pertenencia exacta (case-sensitive) a un conjunto. None desactiva el filtro."""
        if values:
            self._column_in_set[column] = set(values)
        else:
            self._column_in_set.pop(column, None)
        self.invalidateRowsFilter()

    def clear_filters(self) -> None:
        self._free_text = ""
        self._column_filters.clear()
        self._column_in_set.clear()
        self.invalidateRowsFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:  # noqa: N802
        model = self.sourceModel()
        if model is None:
            return True
        n_cols = model.columnCount(source_parent)

        # Filtros por columna (substring): AND
        for col, needle in self._column_filters.items():
            if col < 0 or col >= n_cols:
                # El filtro apunta a una columna que ya no existe (cambió el modelo).
                # Lo ignoramos silenciosamente.
                continue
            idx = model.index(source_row, col, source_parent)
            cell = (model.data(idx, Qt.DisplayRole) or "").lower()
            if needle not in cell:
                return False

        # Filtros por pertenencia a conjunto: AND
        for col, allowed in self._column_in_set.items():
            if col < 0 or col >= n_cols:
                continue
            idx = model.index(source_row, col, source_parent)
            cell = model.data(idx, Qt.DisplayRole) or ""
            if cell not in allowed:
                return False

        # Texto libre: OR sobre todas las columnas
        if self._free_text:
            for c in range(n_cols):
                idx = model.index(source_row, c, source_parent)
                cell = (model.data(idx, Qt.DisplayRole) or "").lower()
                if self._free_text in cell:
                    return True
            return False

        return True

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:  # noqa: N802
        model = self.sourceModel()
        if model is None:
            return False
        a = model.data(left, Qt.UserRole)
        b = model.data(right, Qt.UserRole)
        # Comparación tolerante a None y a tipos mixtos.
        if a is None and b is None:
            return False
        if a is None:
            return True
        if b is None:
            return False
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a < b
        try:
            return str(a) < str(b)
        except Exception:
            return False
