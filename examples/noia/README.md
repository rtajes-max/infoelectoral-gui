# Ejemplo: el caso de Noia

Caso real de uso del visor `infoelectoral` para construir un Excel histórico
completo de un municipio (Noia, A Coruña, INE 15057), desde 1979 hasta 2023.

## Qué hay aquí

- **`extract_noia_excel.py`** — Script que recorre los `.DAT` del Ministerio
  para los 12 procesos municipales 1979→2023, filtra Noia (provincia 15,
  municipio 057), cruza con los datos auxiliares de los `.json` de esta misma
  carpeta y produce un Excel multi-hoja con:
    - Cobertura: qué hay en cada año
    - Resumen: totales municipales por convocatoria
    - Partidos por elección: votos y escaños por candidatura
    - Candidatos: 1979-1999 transcritos a mano del BOP, 2003-2023 del .DAT
    - Mesa a mesa: censo, votantes, blancos, nulos por mesa (1987+)
    - Mesas × partido: votos por (mesa × candidatura)
- **`candidaturas_pre2003_noia.json`** — Listas completas de candidatos a
  Noia 1979, 1983, 1987, 1991, 1995, 1999 transcritos a mano del Boletín
  Oficial de la Provincia de A Coruña (los `.DAT` del Ministerio en esos
  años no traían los nombres de los candidatos para Noia).
- **`locales_electorales_noia.json`** — Para cada mesa de cada elección
  1987-2023, el local físico donde se votó (Casa do Concello, IES Virxe do
  Mar, Local Social de Boa, etc.) y su dirección.
- **`regression_user_files.py`** — Script de regresión que parsea los 138
  ficheros `.DAT` que el autor del ejemplo tenía en una carpeta local y
  reporta cuántas filas decodifica cada uno y qué errores deja.

## Cómo usarlo como plantilla

Si quieres construir un Excel histórico equivalente para **tu municipio**:

1. Descarga los `.DAT` del Ministerio:
   [infoelectoral.mir.es](https://www.infoelectoral.mir.es/infoelectoral/min/).
2. Copia esta carpeta a `examples/<tu-municipio>/`.
3. Edita el script y reemplaza `NOIA_NAME = "Noia"` por el nombre de tu
   municipio tal cual aparece en los `.DAT` (carga primero un fichero con
   la GUI y mira la columna `Municipio`).
4. Si tu municipio está en provincia distinta de A Coruña, ajusta también
   el filtro de `Provincia` y la ruta `USER_BASE`.
5. Para 1979-1999 los `.DAT` del Ministerio no suelen traer los nombres de
   candidatos: tendrás que transcribirlos a mano del BOP de tu provincia
   (los Boletines son públicos y están todos digitalizados).
6. Lanza:
   ```bash
   python examples/<tu-municipio>/extract_<tu-municipio>_excel.py
   ```

## Nota sobre el método

El cruce entre las listas del BOP (pre-2003) y los códigos de candidatura del
`.DAT` se hace por una **tabla de aliases por siglas** dentro del script,
porque las siglas del Ministerio cambian entre años (PSOE → PSG-PSOE → PSDG-PSOE
→ PSdeG-PSOE…). Para tu municipio probablemente tengas que añadir aliases para
candidaturas locales propias.

---

> Igual que el resto del proyecto, este ejemplo se construye sobre el trabajo
> de [Jaime Gómez-Obregón](https://github.com/JaimeObregon/infoelectoral).
