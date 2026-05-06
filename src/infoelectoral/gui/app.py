"""Punto de entrada de la GUI."""

from __future__ import annotations

import sys

from PySide6.QtCore import QLocale
from PySide6.QtWidgets import QApplication

from .main_window import MainWindow
from .theme import apply_theme


def main() -> int:
    QLocale.setDefault(QLocale(QLocale.Spanish, QLocale.Spain))
    app = QApplication(sys.argv)
    app.setApplicationName("infoelectoral")
    app.setOrganizationName("infoelectoral-gui")
    apply_theme(app)
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
