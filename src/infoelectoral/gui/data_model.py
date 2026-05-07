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
        # Cache lazy para filtrado libre (texto en cualquier columna). Solo se
        # construye la primera vez que se invoca `haystack()`. Evita los ~40s
        # de carga para ficheros grandes (10 con 550k filas) cuando el usuario
        # solo va a filtrar por columna concreta.
        self._haystacks: list[str] | None = None

    def _build_haystacks(self) -> list[str]:
        out: list[str] = []
        cols = self._columns
        for r in self._rows:
            parts: list[str] = []
            for c in cols:
                v = r.get(c)
                if v is not None:
                    parts.append(str(v))
            out.append(" ".join(parts).lower())
        return out

    # ---- Acceso rápido (saltándose Qt) para el proxy ----------------------

    def row_dict(self, source_row: int) -> dict[str, Any]:
        """Devuelve el dict de la fila sin pasar por la pila de Qt (rápido)."""
        if 0 <= source_row < len(self._rows):
            return self._rows[source_row]
        return {}

    def haystack(self, source_row: int) -> str:
        """Cadena con todos los valores concatenados en minúsculas (lazy)."""
        if self._haystacks is None:
            self._haystacks = self._build_haystacks()
        if 0 <= source_row < len(self._haystacks):
            return self._haystacks[source_row]
        return ""

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
        self._haystacks = None  # invalida el cache; se reconstruirá al primer filtro libre
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

        # Acceso rápido al dict de la fila si el modelo lo expone (DatTableModel).
        # Esto se salta toda la pila de Qt (model.index + model.data) que es
        # significativamente más lenta cuando hay 250k+ filas a evaluar.
        row_dict = None
        if hasattr(model, "row_dict"):
            row_dict = model.row_dict(source_row)
        cols_list: list[str] = getattr(model, "_columns", []) if row_dict is not None else []
        n_cols = len(cols_list) if row_dict is not None else model.columnCount(source_parent)

        # Filtros por columna (substring): AND
        for col, needle in self._column_filters.items():
            if col < 0 or col >= n_cols:
                continue
            if row_dict is not None:
                cell = str(row_dict.get(cols_list[col]) or "").lower()
            else:
                idx = model.index(source_row, col, source_parent)
                cell = (model.data(idx, Qt.DisplayRole) or "").lower()
            if needle not in cell:
                return False

        # Filtros por pertenencia a conjunto: AND
        for col, allowed in self._column_in_set.items():
            if col < 0 or col >= n_cols:
                continue
            if row_dict is not None:
                cell = str(row_dict.get(cols_list[col]) or "")
            else:
                idx = model.index(source_row, col, source_parent)
                cell = model.data(idx, Qt.DisplayRole) or ""
            if cell not in allowed:
                return False

        # Texto libre: usamos el haystack pre-computado del modelo (O(1) por fila).
        if self._free_text:
            if hasattr(model, "haystack"):
                if self._free_text not in model.haystack(source_row):
                    return False
            else:
                # Fallback al recorrido columna a columna
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
