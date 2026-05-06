# -*- mode: python ; coding: utf-8 -*-
# Spec de PyInstaller para construir un .exe único con la GUI infoelectoral.
# Ejecutar:  .venv/Scripts/pyinstaller.exe infoelectoral.spec --clean --noconfirm

from pathlib import Path

ROOT = Path(SPECPATH).resolve()

a = Analysis(
    ['src/infoelectoral/__main__.py'],
    pathex=[str(ROOT / 'src')],
    binaries=[],
    datas=[
        # Empaquetamos la carpeta data/ como recurso. resources.py la encuentra
        # vía sys._MEIPASS al arrancar.
        (str(ROOT / 'data'), 'data'),
    ],
    hiddenimports=[
        # PyInstaller suele detectar PySide6 automáticamente, pero por si acaso:
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Excluimos módulos pesados de PySide6 que no usamos para reducir el .exe.
        'PySide6.Qt3DAnimation',
        'PySide6.Qt3DCore',
        'PySide6.Qt3DInput',
        'PySide6.Qt3DLogic',
        'PySide6.Qt3DRender',
        'PySide6.Qt3DExtras',
        'PySide6.QtCharts',
        'PySide6.QtDataVisualization',
        'PySide6.QtMultimedia',
        'PySide6.QtMultimediaWidgets',
        'PySide6.QtNetwork',
        'PySide6.QtNetworkAuth',
        'PySide6.QtOpenGL',
        'PySide6.QtOpenGLWidgets',
        'PySide6.QtPdf',
        'PySide6.QtPdfWidgets',
        'PySide6.QtPositioning',
        'PySide6.QtPrintSupport',
        'PySide6.QtQml',
        'PySide6.QtQuick',
        'PySide6.QtQuickWidgets',
        'PySide6.QtSql',
        'PySide6.QtTest',
        'PySide6.QtWebChannel',
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtWebSockets',
        'PySide6.QtXml',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='infoelectoral',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,           # ventana sin consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
