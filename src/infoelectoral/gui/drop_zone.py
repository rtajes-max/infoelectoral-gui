"""Zona drag-and-drop para soltar carpetas o ficheros .DAT."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QFileDialog, QFrame, QLabel, QPushButton, QVBoxLayout, QWidget


class DropZone(QFrame):
    """Frame con borde discontinuo que acepta drag-drop de carpetas y ficheros."""

    paths_dropped = Signal(list)  # list[Path]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("dropZone")
        self.setStyleSheet(
            """
            QFrame#dropZone {
                border: 2px dashed #888;
                border-radius: 8px;
                background: #fafafa;
                min-height: 110px;
            }
            QFrame#dropZone[dragOver="true"] {
                border-color: #1a73e8;
                background: #eaf2ff;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(6)

        self.label = QLabel(
            "Arrastra aquí la carpeta de una elección\n(o ficheros .DAT sueltos)"
        )
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: #555; font-size: 13px;")
        layout.addWidget(self.label)

        self.browse_btn = QPushButton("Elegir carpeta…")
        self.browse_btn.clicked.connect(self._open_folder_dialog)
        layout.addWidget(self.browse_btn, alignment=Qt.AlignCenter)

    # ---- Drag and drop -----------------------------------------------------

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:  # noqa: N802
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setProperty("dragOver", True)
            self.style().unpolish(self)
            self.style().polish(self)
        else:
            event.ignore()

    def dragLeaveEvent(self, event) -> None:  # noqa: N802
        self.setProperty("dragOver", False)
        self.style().unpolish(self)
        self.style().polish(self)
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:  # noqa: N802
        self.setProperty("dragOver", False)
        self.style().unpolish(self)
        self.style().polish(self)
        urls = event.mimeData().urls()
        paths = [Path(u.toLocalFile()) for u in urls if u.isLocalFile()]
        if paths:
            self.paths_dropped.emit(paths)
            event.acceptProposedAction()

    # ---- Diálogo manual ----------------------------------------------------

    def _open_folder_dialog(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Elegir carpeta de elección")
        if directory:
            self.paths_dropped.emit([Path(directory)])

    def set_status(self, text: str) -> None:
        self.label.setText(text)

    def reset(self) -> None:
        self.label.setText(
            "Arrastra aquí la carpeta de una elección\n(o ficheros .DAT sueltos)"
        )
