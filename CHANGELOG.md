# Changelog

Todos los cambios reseñables se documentan aquí. El formato sigue
[Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y la versión sigue
[Semantic Versioning](https://semver.org/lang/es/).

## [0.3.2] — Filtros responsivos al teclear

### Corregido

- **La app dejaba de responder al escribir letra a letra en las cajas de
  filtro.** Cada keystroke disparaba un re-filtrado completo del modelo
  (250-550k filas en ficheros 04 y 10), bloqueando el thread de UI.

### Cambiado

- **Debounce de 280 ms** en los inputs de búsqueda y municipio: el filtro real
  solo se aplica cuando el usuario para de teclear. Mientras tanto la barra
  de estado muestra «Filtrando…» y los inputs siguen siendo escribibles.
- **`filterAcceptsRow` ~5× más rápido**: accede al `row_dict` directo del
  modelo en vez de pasar por la pila de Qt (`model.index` + `model.data`),
  que es muy costosa para cientos de miles de filas.
- **Cache de búsqueda libre lazy**: la cadena concatenada por fila para texto
  libre se construye solo la primera vez que se hace búsqueda libre, no al
  cargar el fichero. Para usuarios que solo filtran por columna, la carga
  inicial es más rápida.

## [0.3.1] — Hardening de filtros

### Corregido

- **Crash al cambiar de fichero con un preset/filtro activo.** Los índices de
  columna del modelo viejo quedaban referenciando posiciones que en el nuevo
  modelo apuntaban a otras columnas (o no existían). Ahora el proxy se
  resetea automáticamente cuando cambia el `sourceModel` o se emite
  `modelReset`, y `filterAcceptsRow` valida bounds antes de leer.
- Los slots de UI de los filtros (`_on_search_changed`, `_on_muni_changed`,
  `_on_preset_changed`) ahora envuelven todo en `try/except` y muestran un
  `QMessageBox` en lugar de cerrar la app silenciosamente.

### Añadido

- **`sys.excepthook` global** que escribe cualquier excepción no manejada a
  `%APPDATA%/infoelectoral/errors.log` y muestra un diálogo con el resumen y
  la ruta del log. Útil para diagnosticar futuros bugs sin tener consola.

## [0.3.0] — Aplicación genérica + UI mejorada

### Añadido

- **Sistema de presets configurables** (Mi pueblo, Mi comarca…). Cada usuario
  define sus propios grupos de municipios y los selecciona en la barra de
  filtros. Se guardan en `%APPDATA%/infoelectoral/presets.json`.
- **Diálogo de gestión de presets** (`Presets…` en la barra de herramientas):
  crear, duplicar, borrar, editar.
- **Diálogo «Acerca de»** con créditos prominentes a Jaime Gómez-Obregón.
- **Tema visual nuevo** (estilo Fusion + paleta cuidada + stylesheet propio).
  Tabla con cabeceras destacadas, drop-zone con feedback visual de drag-over,
  campos de filtro con border-radius, botones primarios resaltados.
- **Filtro de municipio libre** (caja de texto independiente del preset).
- `LICENSE` (AGPL-3.0) y `NOTICE.md` con la atribución a Jaime.
- `CITATION.cff` para que herramientas como Zenodo/GitHub puedan generar
  citas que mencionen también el proyecto original.

### Cambiado

- **La aplicación ya no asume Noia ni Barbanza.** Eliminados los hardcodes;
  cualquier municipio funciona vía presets.
- README reescrito con créditos prominentes a Jaime y portabilidad mejorada.

### Reconocimiento

Esta versión refleja con mayor claridad que el proyecto es una obra derivada
del trabajo de [Jaime Gómez-Obregón](https://github.com/JaimeObregon/infoelectoral).

---

## [0.2.0]

### Añadido

- **Diálogo «Ver errores…»** para inspeccionar líneas de `.DAT` que el parser
  no consigue decodificar, con botón de exportar a `.txt`.
- **Modo CLI `--diag`** para diagnosticar desde terminal sin abrir la GUI.
- **Modo CLI `--version`**.
- Cabecera con versión y `build_time` en cada log de errores guardado.
- Fixup para el fichero 12 de **1979 sin pre-normalizar** (el del Ministerio
  trae espacio trailing extra y campos desplazados; los del repo de Jaime ya
  están normalizados).

### Cambiado

- Mensajes de status bar más claros (sin referencias a una "consola"
  inexistente).

---

## [0.1.0]

### Añadido

- Parser portado de PHP a Python (todos los ficheros 01-12 del Ministerio).
- GUI básica con drag-and-drop, sidebar de ficheros detectados, tabla con
  ordenación y filtrado, exportación a CSV.
- Empaquetado como `.exe` único con PyInstaller (~46 MB).
