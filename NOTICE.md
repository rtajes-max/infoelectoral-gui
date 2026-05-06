# NOTICE — atribución y agradecimientos

Esta aplicación es una **obra derivada** del proyecto:

> **infoelectoral** — intérprete de microdatos electorales del Ministerio del Interior español
> Copyright © 2020 Jaime Gómez-Obregón
> https://github.com/JaimeObregon/infoelectoral
> Licencia: GNU AGPL-3.0

---

## Lo que viene del proyecto original de Jaime Obregón

- **Especificación de campos** de los ficheros `.DAT` del Ministerio
  (`src/infoelectoral/formats.py` es una traducción a Python directa de
  `includes/formats.php` del proyecto original, con todas sus convenciones de
  posiciones, formatters y manejo de casos especiales).
- **Tablas de municipios INE** por año (`data/municipios/*.json`), generadas a
  partir de los ficheros PHP mantenidos por Jaime en `includes/municipios/`.
- **Tablas auxiliares** (autonomías, provincias, ficheros, procesos, distritos
  electorales, municipios inexistentes), todas portadas de
  `includes/constants.php`.
- **Fixups para registros corruptos** del Ministerio (la línea de Linda M.
  Peeters en municipales 2015, las líneas malformadas de 1979 fichero 11, los
  problemas de padding en 1983 fichero 12), descubiertos y documentados por
  Jaime tras años de trabajo con los datos.
- **Conocimiento de dominio** que hace que el parser funcione: que los .DAT
  son ASCII de ancho fijo en latin-1, que las mesas únicas se codifican como
  'U' o 'A' según el año, que `99` significa "total nacional", que las
  candidaturas tienen jerarquía provincial/autonómica/nacional, etc.

Sin nada de lo anterior, esta aplicación no podría existir.

## Lo que añade este proyecto

- Una interfaz gráfica de escritorio (Qt/PySide6) sobre el parser de Jaime.
- Un sistema de presets de filtro por municipio configurable por el usuario.
- Exportación a CSV con cabeceras canónicas y BOM UTF-8 (Excel-friendly).
- Un fixup adicional para 1979 fichero 12 cuando el `.DAT` viene del
  Ministerio sin pre-normalizar (los del repo de Jaime ya están normalizados).
- Empaquetado como `.exe` independiente para Windows con PyInstaller.

## Licencia y obligaciones

Esta obra derivada se distribuye bajo **GNU AGPL-3.0**, la misma licencia que
el proyecto original. Esto significa, entre otras cosas:

- Cualquier modificación o redistribución debe mantener esta atribución.
- El código fuente debe seguir siendo accesible.
- Si despliegas este software como servicio en red, debes ofrecer también el
  código fuente a quien use el servicio.

## Reconocimiento

> A Jaime Gómez-Obregón ([@JaimeObregon](https://twitter.com/JaimeObregon))
> nuestro agradecimiento más profundo. Su trabajo de años decodificando los
> ficheros del Ministerio, su decisión de publicar todo en abierto, y su labor
> de divulgación de la transparencia electoral en España son la base sobre la
> que se construye esto.
>
> **Obrigado, Jaime.**
