# Cómo contribuir

¡Gracias por interesarte! Este proyecto es **AGPL-3.0** y se construye sobre
[infoelectoral de Jaime Gómez-Obregón](https://github.com/JaimeObregon/infoelectoral).
Si tu contribución mejora el parser o las tablas de datos, considera abrir
también un PR en el repo original — beneficiarás a más gente.

## Antes de empezar

1. Abre primero un *issue* describiendo lo que quieres cambiar. Para correcciones
   pequeñas (typos, fixes obvios) un PR directo está bien.
2. Si tu cambio toca el parser o el formato de los `.DAT`, comprueba que no rompe
   ningún fichero histórico — el script `scripts/regression_user_files.py` o
   `scripts/smoke_test.py` deberían seguir verdes.

## Setup local

```bash
git clone <este-repo>
cd infoelectoral
python -m venv .venv
.venv\Scripts\pip install -r requirements-dev.txt

# (Solo la primera vez) regenerar las tablas INE desde el repo de Jaime:
git clone --depth 1 https://github.com/JaimeObregon/infoelectoral.git reference
python scripts\extract_constants.py

# Probar la GUI sin compilar:
python -m infoelectoral

# Compilar el .exe:
build.bat
```

## Estilo de código

- Python 3.11+ con type hints.
- `ruff` configurado en `pyproject.toml` — corre `ruff format` y `ruff check`.
- Comentarios y mensajes de UI **en español o gallego** (el dominio del proyecto
  es electoral español).
- Variables, funciones y commits **en español o inglés**, lo que sea claro.

## Commits y PRs

- Commits pequeños y atómicos, mensaje claro en imperativo.
- Si añades un fix sobre datos del Ministerio, **documéntalo en el commit**
  citando el fichero y la línea concreta — esto ahorra horas a quien venga después.
- Los PRs grandes (refactors, nuevas features) deben tocar también el `CHANGELOG.md`.

## Reportar bugs de parseo

Si te falla un `.DAT` concreto:

1. Lanza el `.exe` con `--diag <fichero>` y guarda la salida.
2. Si la GUI te muestra "Ver errores…", guarda el log con ese botón.
3. Abre un issue con **el log completo** (la cabecera trae versión y ruta).

Si puedes, comparte también el `.DAT` problemático — sin él no podemos reproducir.
La mayoría de los `.DAT` del Ministerio son datos públicos y se pueden compartir.

## Reconocimiento al proyecto original

Si tu PR mejora la decodificación de los `.DAT`, **considera abrir también un
PR equivalente en el repo de Jaime** ([github.com/JaimeObregon/infoelectoral](https://github.com/JaimeObregon/infoelectoral)).
Su PHP es la fuente de la verdad y muchos otros proyectos dependen de él.
