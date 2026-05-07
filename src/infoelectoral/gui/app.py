"""Punto de entrada de la GUI."""

from __future__ import annotations

import datetime as _dt
import sys
import traceback as _tb
from pathlib import Path

from PySide6.QtCore import QLocale, QTimer
from PySide6.QtWidgets import QApplication, QMessageBox

from ..settings import config_dir
from .main_window import MainWindow
from .theme import apply_theme


_LOG_PATH: Path | None = None


def _log_path() -> Path:
    global _LOG_PATH
    if _LOG_PATH is None:
        _LOG_PATH = config_dir() / "errors.log"
    return _LOG_PATH


def _excepthook(exc_type, exc_value, exc_tb) -> None:
    """Captura cualquier excepción no manejada: la escribe a archivo y muestra un diálogo."""
    msg = "".join(_tb.format_exception(exc_type, exc_value, exc_tb))
    timestamp = _dt.datetime.now().isoformat(timespec="seconds")
    try:
        with _log_path().open("a", encoding="utf-8") as f:
            f.write(f"\n=== {timestamp} ===\n{msg}\n")
    except Exception:
        pass
    # Mostramos el error al usuario (en lugar de que la app desaparezca silenciosa)
    try:
        if QApplication.instance() is not None:
            short = f"{exc_type.__name__}: {exc_value}"
            QMessageBox.critical(
                None,
                "Error inesperado",
                (
                    f"Se ha producido un error que la aplicación no esperaba:\n\n{short}\n\n"
                    f"Detalle completo en:\n{_log_path()}\n\n"
                    "La app sigue funcionando, pero la última operación puede haber quedado a medias."
                ),
            )
    except Exception:
        pass


def main() -> int:
    QLocale.setDefault(QLocale(QLocale.Spanish, QLocale.Spain))
    sys.excepthook = _excepthook

    app = QApplication(sys.argv)
    app.setApplicationName("infoelectoral")
    app.setOrganizationName("infoelectoral-gui")
    apply_theme(app)

    # Aseguramos que el directorio de logs existe
    try:
        _log_path().parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
