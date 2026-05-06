# infoelectoral · visor de microdatos electorales del Ministerio del Interior

> ⚠️ **Esta aplicación es una obra derivada del trabajo de [**Jaime Gómez-Obregón**](https://github.com/JaimeObregon/infoelectoral)**.
> Sin su decodificación de los ficheros `.DAT`, sin sus tablas INE y sin su
> documentación, esta aplicación no podría existir.
> **Gracias, Jaime.**

[![Licencia: AGPL-3.0](https://img.shields.io/badge/Licencia-AGPL--3.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-green.svg)](https://wiki.qt.io/Qt_for_Python)
[![Plataforma](https://img.shields.io/badge/Plataforma-Windows-lightgrey.svg)](#)

Aplicación de escritorio (Windows `.exe`, también ejecutable en macOS/Linux con
Python) para **inspeccionar, filtrar y exportar a CSV** los ficheros `.DAT`
que publica el Ministerio del Interior español tras cada convocatoria
electoral.

Funciona con cualquier municipio. El parser cubre los **12 tipos de fichero**
del Ministerio: control, identificación del proceso, candidaturas, candidatos,
agregados municipales y de ámbito superior, mesas, CERA, municipios pequeños.
Cubre todas las elecciones desde 1979.

## ✨ Qué hace

- **Drag-and-drop** de la carpeta de una elección o de ficheros `.DAT` sueltos.
- **Decodifica los 12 tipos de fichero** del Ministerio, incluyendo los fixups
  documentados por Jaime Obregón para registros corruptos del propio
  Ministerio.
- **Tabla con ordenación, búsqueda libre y filtro por municipio**.
- **Presets configurables**: define tus propios grupos (Mi pueblo, Mi
  comarca…) y selecciónalos con un click. Se guardan entre sesiones.
- **Exportación a CSV** con cabeceras canónicas en español y BOM UTF-8 (Excel
  lo abre correctamente con acentos).
  - Solo filas visibles
  - Solo selección manual
  - Todas las filas del fichero actual
  - **Volcado por carpeta**: un CSV por cada `.DAT` detectado.
- **Diálogo «Ver errores…»** para inspeccionar líneas que el parser no
  consigue decodificar (con guardado a `.txt`).
- **Modo CLI**: `infoelectoral.exe --diag <fichero.DAT>` para diagnosticar
  desde terminal sin abrir la GUI.

## 🙏 Agradecimientos al creador original

El núcleo técnico de esta aplicación —la especificación de los `.DAT`, el parser,
las tablas INE, los fixups de registros corruptos— viene **directamente** del
proyecto [**JaimeObregon/infoelectoral**](https://github.com/JaimeObregon/infoelectoral)
y de años de trabajo de Jaime decodificando los datos del Ministerio.

Este proyecto se limita a:
1. Portar su parser PHP a Python.
2. Envolverlo en una GUI Qt.
3. Empaquetarlo como `.exe` para que personas sin conocimientos técnicos
   puedan usarlo.

**Si este software te resulta útil, considera dar las gracias a Jaime:**
- ⭐ Estrella su repo: [github.com/JaimeObregon/infoelectoral](https://github.com/JaimeObregon/infoelectoral)
- 🐦 Sigue su trabajo de transparencia: [@JaimeObregon en Twitter/X](https://twitter.com/JaimeObregon)
- 💸 Apóyale económicamente si puedes — el resto de su trabajo de
  transparencia (los premios "Inocenta", contratos públicos, etc.) también
  vive de eso.

Detalle completo de la atribución en [`NOTICE.md`](NOTICE.md).

## 📦 Descarga

### Binario para Windows

> Una vez publicado en GitHub Releases.

Descarga `infoelectoral.exe` (~50 MB), **doble click** y listo. No necesita
instalación ni Python.

### Desde el código fuente

Necesitas Python 3.11 o superior.

```bash
git clone <este-repo>
cd infoelectoral
python -m venv .venv

# Linux/macOS
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m infoelectoral

# Windows
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m infoelectoral
```

## 🚀 Cómo usarlo

1. Doble click en `infoelectoral.exe` (o `python -m infoelectoral`).
2. **Suelta una carpeta** del Ministerio (por ejemplo `04201905_MESA/`) en la
   ventana, o ficheros `.DAT` sueltos.
3. La columna izquierda muestra los ficheros detectados; pincha el que te
   interese para verlo en la tabla.
4. **Filtra**: usa la caja de búsqueda libre, o el campo «Municipio», o un
   *preset* que hayas creado.
5. **Exporta**: con `Ctrl+E` exportas las filas visibles, o usa los botones
   de la barra de herramientas para otros modos.

### Crear un preset (recomendado para uso recurrente)

1. Pulsa **Presets…** en la barra de herramientas.
2. **Nuevo** → ponle un nombre («Mi pueblo», «Comarca de X»).
3. Provincia: el nombre tal cual aparece en el `.DAT` (`A Coruña`, `Madrid`,
   `Sevilla`…).
4. Municipios: uno por línea, también tal cual los devuelve el parser (`Noia`,
   `Pobra do Caramiñal, A`…). Si no estás seguro del nombre exacto, carga
   primero un fichero `.DAT` y mira la columna `Municipio`.
5. Acepta. El preset aparece ya en el desplegable de la barra de filtros y
   queda guardado en tu carpeta de usuario.

## 🛠 Compilar el `.exe`

```bash
.venv\Scripts\pip install -r requirements-dev.txt
.\build.bat
```

El binario aparece en `dist\infoelectoral.exe` (~46-50 MB, sin dependencias
externas).

## 🗂 Estructura

```
infoelectoral/
├── data/
│   ├── municipios/<año>.json        # tablas INE -> JSON, generadas
│   └── municipios_inexistentes.json
├── scripts/
│   ├── extract_constants.py         # PHP -> JSON, una sola vez tras clonar
│   ├── smoke_test.py                # verifica el parser sobre 2019
│   └── gui_smoke.py                 # verifica la GUI offscreen
├── src/infoelectoral/
│   ├── constants.py                 # autonomías, provincias, ficheros, procesos, distritos
│   ├── municipios.py                # carga la tabla INE del año pedido
│   ├── formats.py                   # spec completa de los 12 tipos de fichero
│   ├── parser.py                    # parse_line, parse_file, detect_dat_files
│   ├── exporter.py                  # CSV con BOM y orden canónico
│   ├── resources.py                 # localiza data/ en dev y dentro del .exe
│   ├── settings.py                  # presets + preferencias en %APPDATA%
│   ├── __main__.py                  # entry point + CLI --diag --version
│   └── gui/
│       ├── app.py                   # main(), aplica el tema
│       ├── theme.py                 # Fusion + paleta + stylesheet
│       ├── main_window.py           # ventana principal, presets, filtros
│       ├── data_model.py            # QAbstractTableModel + QSortFilterProxyModel
│       ├── drop_zone.py             # widget de drag-and-drop
│       ├── preset_dialog.py         # editor de presets
│       └── about_dialog.py          # créditos a Jaime
├── infoelectoral.spec               # PyInstaller
├── build.bat                        # construye el .exe
├── LICENSE                          # AGPL-3.0
├── NOTICE.md                        # atribución detallada
├── CITATION.cff                     # cómo citar (incluye al original)
├── CHANGELOG.md
├── CONTRIBUTING.md
└── README.md                        # este fichero
```

## 🧪 Tipos de fichero soportados

| Código | Descripción |
| ------ | ----------- |
| 01 | Control |
| 02 | Identificación del proceso electoral |
| 03 | Candidaturas (cabeceras de partido) |
| 04 | Candidatos (orden, sexo, fecha nacimiento, DNI, elegido) |
| 05 | Datos globales de ámbito municipal |
| 06 | Resultados de candidaturas a nivel municipal |
| 07 | Datos globales de ámbito superior al municipio |
| 08 | Resultados de candidaturas a nivel superior |
| 09 | Datos globales de mesas y CERA |
| 10 | Resultados de candidaturas en mesas y CERA |
| 11 | Datos globales en municipios <250 habitantes (solo municipales) |
| 12 | Candidaturas en municipios <250 habitantes (solo municipales) |

## 📜 Licencia

[GNU AGPL-3.0](LICENSE), igual que el proyecto original. Es contagiosa: cualquier
modificación o redistribución debe seguir siendo software libre y mantener la
atribución a Jaime Obregón. Si despliegas esto como servicio en red, debes
ofrecer también el código fuente a los usuarios del servicio.

## 👥 Créditos

- **Especificación de los ficheros .DAT, parser de referencia, tablas INE
  por año, fixups para registros corruptos del Ministerio**:
  [Jaime Gómez-Obregón](https://github.com/JaimeObregon)
  ([@JaimeObregon](https://twitter.com/JaimeObregon))
  → [proyecto original `infoelectoral`](https://github.com/JaimeObregon/infoelectoral)
- **Datos primarios**: Ministerio del Interior de España
  ([infoelectoral.mir.es](https://www.infoelectoral.mir.es/infoelectoral/min/))
- **GUI Qt, empaquetado PyInstaller, presets**: contribuidores de este proyecto.

---

> **Una vez más: gracias, Jaime.** Que más gente conozca tu trabajo.
