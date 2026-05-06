"""
Parser de ficheros .DAT del Ministerio del Interior.

Equivalente Python de `parseLine`, `parseFile`, `parseName` del PHP de JaimeObregon.
Lee los ficheros como `latin-1` (la codificación original del Ministerio).
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .constants import FICHEROS, PROCESOS
from .formats import FORMATS

ENCODING = "latin-1"

# Regex del nombre de fichero: nnxxaamm.dat
_FILENAME_RE = re.compile(r"(\d{2})(\d{2})(\d{2})(\d{2})\.DAT$", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class FileMeta:
    """Metadatos extraídos del nombre del fichero."""

    path: Path
    filename: str
    file_code: str       # 'nn' — código de tipo de fichero (01..12)
    file_desc: str       # descripción legible
    process_code: str    # 'xx' — código de proceso electoral
    process_desc: str    # descripción legible
    year: int            # año completo (1979, 2019, ...)
    month: int           # mes


@dataclass(slots=True)
class ParseResult:
    meta: FileMeta
    rows: list[dict[str, Any]] = field(default_factory=list)
    skipped_lines: int = 0
    error_lines: list[tuple[int, str, str]] = field(default_factory=list)
    # tuplas: (nº de línea 1-based, mensaje de error, contenido crudo recortado)


def parse_name(filename: str | Path) -> FileMeta | None:
    """Decodifica el nombre del fichero. Devuelve None si no encaja con el patrón."""
    p = Path(filename)
    m = _FILENAME_RE.search(p.name)
    if not m:
        return None
    nn, xx, aa, mm = m.group(1), m.group(2), m.group(3), m.group(4)
    if nn not in FORMATS:
        return None
    year = int(("19" if int(aa) > 70 else "20") + aa)
    return FileMeta(
        path=p,
        filename=p.name,
        file_code=nn,
        file_desc=FICHEROS.get(nn, "Desconocido"),
        process_code=xx,
        process_desc=PROCESOS.get(xx, "Desconocido"),
        year=year,
        month=int(mm),
    )


# --- Fixups conocidos para registros corruptos en la fuente original --------

_LINDA_RE = re.compile(r"^042015051439153090873009TLinda")


def _line_fixups(format_code: str, line: str) -> str | None:
    """
    Corrige línea por línea los problemas de calidad documentados en functions.php.
    Devuelve `None` si la línea debe ser descartada.
    """
    # Fichero 04, candidata Linda M. Peeters (municipales 2015)
    if format_code == "04" and _LINDA_RE.match(line):
        line = line.replace("7000000001", "F00000000 ", 1)

    # Fichero 11, líneas que no acaban en S/N están corruptas y se descartan
    if format_code == "11":
        # Quitamos solo el salto de línea para chequear; espacios finales son significativos.
        candidate = line.rstrip("\r\n")
        if not candidate or candidate[-1] not in ("S", "N"):
            return None

    # Fichero 12, líneas con un padding ausente en algunos años (1983 sobre todo)
    if format_code == "12" and re.search(r" {30}\d{3}[SN] {50}$", line):
        # Insertamos 50 espacios en la posición 69 (para reponer el bloque ausente)
        # Replicamos `substr_replace(trim($line), str_pad('', 50, ' '), 69, 0)` del PHP.
        trimmed = line.rstrip()
        line = trimmed[:69] + (" " * 50) + trimmed[69:]

    # Fichero 12 publicado por el Ministerio en 1979: la línea tiene la longitud
    # esperada (123 chars) pero los campos `Votos` y `Elegido` están desplazados
    # 1 carácter a la izquierda y aparece un espacio extra al final.
    # El repo de referencia de JaimeObregon trae estos ficheros ya normalizados;
    # los descargados directos del Ministerio no.
    # Detectamos por el patrón final `<3 dígitos><S|N><espacio>$` y desplazamos
    # insertando 1 espacio en la posición del Sexo (pos 101 = idx 100), que está
    # vacío en 1979.
    if format_code == "12" and len(line) == 123 and re.search(r"\d{3}[SN] $", line):
        line = line[:100] + " " + line[100:122]

    return line


def parse_line(format_code: str, line: str) -> dict[str, Any] | None:
    """Decodifica una línea según su tipo de fichero. None = línea descartada."""
    if format_code not in FORMATS:
        raise KeyError(f"Tipo de fichero desconocido: {format_code!r}")

    fixed = _line_fixups(format_code, line)
    if fixed is None:
        return None
    line = fixed

    out: dict[str, Any] = {}
    for fld in FORMATS[format_code]:
        raw = line[fld.start - 1 : fld.start - 1 + fld.length]
        try:
            value = fld.formatter(raw, line)
        except Exception as e:
            raise ValueError(f"Campo '{fld.name}' (start={fld.start}, len={fld.length}, raw={raw!r}): {e}") from e
        if value is not None:
            out[fld.name] = value
    return out


def iter_parsed(meta: FileMeta) -> Iterator[tuple[int, dict[str, Any] | None, str | None]]:
    """
    Itera línea a línea: yields (línea_1based, fila_dict_o_None, mensaje_error_o_None).

    Permite procesar streams sin cargar toda la lista en memoria.
    """
    with meta.path.open("r", encoding=ENCODING, newline="") as f:
        for i, raw in enumerate(f, start=1):
            # Quitamos solo el salto de línea final; los demás caracteres son significativos.
            line = raw.rstrip("\r\n")
            if not line.strip():
                yield i, None, None
                continue
            try:
                row = parse_line(meta.file_code, line)
            except Exception as e:
                yield i, None, str(e)
                continue
            yield i, row, None


def parse_file(filename: str | Path) -> ParseResult:
    """Parsea el fichero entero a `ParseResult`."""
    meta = parse_name(filename)
    if meta is None:
        raise ValueError(f"Nombre de fichero no válido: {filename}")

    result = ParseResult(meta=meta)
    for line_no, row, err in iter_parsed(meta):
        if err is not None:
            # Recortamos la línea cruda para que el mensaje no sea inmanejable
            try:
                with meta.path.open("r", encoding=ENCODING) as f:
                    for j, candidate in enumerate(f, start=1):
                        if j == line_no:
                            sample = candidate.rstrip("\r\n")[:120]
                            break
                    else:
                        sample = ""
            except OSError:
                sample = ""
            result.error_lines.append((line_no, err, sample))
            continue
        if row is None:
            result.skipped_lines += 1
            continue
        result.rows.append(row)
    return result


def column_names(format_code: str) -> list[str]:
    """Nombres canónicos de columnas para un tipo de fichero."""
    return [f.name for f in FORMATS[format_code]]


def detect_dat_files(folder: str | Path) -> list[FileMeta]:
    """
    Encuentra todos los .DAT decodificables en una carpeta (y sus subcarpetas) y devuelve
    sus metadatos. Útil para el drop de carpetas en la GUI.
    """
    folder = Path(folder)
    if folder.is_file():
        candidates = [folder]
    else:
        candidates = sorted(folder.rglob("*.DAT")) + sorted(folder.rglob("*.dat"))
    out = []
    seen = set()
    for p in candidates:
        if p in seen:
            continue
        seen.add(p)
        meta = parse_name(p)
        if meta is not None:
            out.append(meta)
    return out
