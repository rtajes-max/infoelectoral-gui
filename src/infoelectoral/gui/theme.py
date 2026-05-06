"""Tema visual de la aplicación: paleta + stylesheet."""

from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


def apply_theme(app: QApplication) -> None:
    """Aplica el tema 'Fusion + paleta clara cuidada'.

    El estilo Fusion es consistente entre Windows/macOS/Linux y respeta nuestros
    overrides de paleta. Stylesheet añade detalles para tabla, headers, botones.
    """
    app.setStyle("Fusion")

    palette = QPalette()
    # Fondos y textos base
    palette.setColor(QPalette.Window, QColor("#F7F8FA"))
    palette.setColor(QPalette.WindowText, QColor("#1F2430"))
    palette.setColor(QPalette.Base, QColor("#FFFFFF"))
    palette.setColor(QPalette.AlternateBase, QColor("#F2F4F7"))
    palette.setColor(QPalette.Text, QColor("#1F2430"))
    palette.setColor(QPalette.Button, QColor("#FFFFFF"))
    palette.setColor(QPalette.ButtonText, QColor("#1F2430"))

    # Selección
    palette.setColor(QPalette.Highlight, QColor("#1A73E8"))
    palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))

    # Tooltips
    palette.setColor(QPalette.ToolTipBase, QColor("#1F2430"))
    palette.setColor(QPalette.ToolTipText, QColor("#FFFFFF"))

    # Disabled
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor("#9AA0A6"))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor("#9AA0A6"))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#9AA0A6"))

    app.setPalette(palette)

    app.setStyleSheet(_STYLESHEET)


_STYLESHEET = """
* {
    font-size: 13px;
}

QMainWindow, QDialog {
    background: #F7F8FA;
}

QToolBar {
    background: #FFFFFF;
    border: none;
    border-bottom: 1px solid #E1E5EB;
    padding: 4px;
    spacing: 4px;
}

QToolBar QToolButton {
    padding: 6px 10px;
    border-radius: 6px;
    color: #1F2430;
}

QToolBar QToolButton:hover {
    background: #EDF1F7;
}

QToolBar QToolButton:disabled {
    color: #B0B6BD;
}

QToolBar QToolButton[buttonStyle="primary"] {
    color: #FFFFFF;
    background: #1A73E8;
}
QToolBar QToolButton[buttonStyle="primary"]:hover {
    background: #1765C2;
}

QStatusBar {
    background: #FFFFFF;
    border-top: 1px solid #E1E5EB;
    color: #5F6368;
}

QLabel {
    color: #1F2430;
}

QLineEdit, QComboBox, QPlainTextEdit {
    background: #FFFFFF;
    border: 1px solid #DADCE0;
    border-radius: 6px;
    padding: 5px 8px;
    selection-background-color: #1A73E8;
    selection-color: #FFFFFF;
}

QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus {
    border-color: #1A73E8;
}

QPushButton {
    background: #FFFFFF;
    border: 1px solid #DADCE0;
    border-radius: 6px;
    padding: 6px 14px;
    color: #1F2430;
}
QPushButton:hover {
    background: #F2F4F7;
}
QPushButton:default {
    background: #1A73E8;
    color: #FFFFFF;
    border-color: #1A73E8;
}
QPushButton:default:hover {
    background: #1765C2;
    border-color: #1765C2;
}

QCheckBox {
    spacing: 8px;
}

QListWidget {
    background: #FFFFFF;
    border: 1px solid #E1E5EB;
    border-radius: 6px;
    padding: 4px;
}
QListWidget::item {
    padding: 6px 8px;
    border-radius: 4px;
}
QListWidget::item:hover {
    background: #F2F4F7;
}
QListWidget::item:selected {
    background: #E8F0FE;
    color: #1A73E8;
}

QTableView {
    background: #FFFFFF;
    alternate-background-color: #F8F9FB;
    gridline-color: #ECEEF2;
    border: 1px solid #E1E5EB;
    border-radius: 6px;
    selection-background-color: #E8F0FE;
    selection-color: #1F2430;
}

QHeaderView::section {
    background: #F2F4F7;
    border: none;
    border-right: 1px solid #E1E5EB;
    border-bottom: 1px solid #E1E5EB;
    padding: 6px 10px;
    font-weight: 600;
    color: #1F2430;
}

QSplitter::handle {
    background: #E1E5EB;
}

QFrame#dropZone {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFFFFF, stop:1 #F7F8FA);
    border: 2px dashed #CDD2DA;
    border-radius: 10px;
    min-height: 100px;
}
QFrame#dropZone[dragOver="true"] {
    background: #E8F0FE;
    border-color: #1A73E8;
}

QPlainTextEdit {
    font-family: "Consolas", "Menlo", monospace;
}
"""
