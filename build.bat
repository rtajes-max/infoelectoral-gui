@echo off
REM Construye dist\infoelectoral.exe a partir del entorno virtual del proyecto.
REM Antes de ejecutarlo:
REM   1) python -m venv .venv
REM   2) .venv\Scripts\pip install -r requirements-dev.txt
REM   3) python scripts\extract_constants.py   (solo la primera vez tras clonar)

setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\pyinstaller.exe" (
    echo PyInstaller no encontrado. Instala primero requirements-dev.txt:
    echo     .venv\Scripts\pip install -r requirements-dev.txt
    exit /b 1
)

if not exist "data\municipios" (
    echo Falta data\municipios. Ejecuta primero:
    echo     .venv\Scripts\python scripts\extract_constants.py
    exit /b 1
)

".venv\Scripts\pyinstaller.exe" infoelectoral.spec --clean --noconfirm
if errorlevel 1 (
    echo.
    echo ERROR al construir el .exe
    exit /b 1
)

echo.
echo Hecho. El .exe esta en:  dist\infoelectoral.exe
endlocal
