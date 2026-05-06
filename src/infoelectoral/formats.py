"""
Especificación de campos de los ficheros .DAT del Ministerio del Interior.

Portado de `reference/src/includes/formats.php` (JaimeObregon/infoelectoral, AGPL-3.0).
La especificación oficial es el documento `FICHEROS.doc` que viene en el repo de Jaime.

Convención (idéntica a PHP):
- `start` es 1-based: la posición del primer carácter dentro de la línea.
- `length` es la longitud del campo en caracteres.
- `formatter(raw, line)` recibe el substring crudo y la línea completa, y devuelve
  el valor decodificado o `None` si el campo no aplica para esta fila concreta.
  Cuando el formatter devuelve `None` el campo no aparece en el dict resultante.

Algunas posiciones tienen varios formatters (p. ej. `Municipio` y `CERA` en el 09);
cada uno discrimina por el contenido y devuelve `None` cuando no es su caso.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .constants import (
    AUTONOMIAS,
    DISTRITOS,
    FICHEROS,
    PROCESOS,
    PROCESOS_AMBITO_AUTONOMICO,
    PROVINCIAS,
)
from .municipios import lookup_municipio

Formatter = Callable[[str, str], Any]


@dataclass(frozen=True, slots=True)
class Field:
    name: str
    start: int  # 1-based
    length: int
    formatter: Formatter


# ---------------------------------------------------------------------------
# Helpers de formatter
# ---------------------------------------------------------------------------

YES_NO = {"S": "Sí", "N": "No"}
ONE_ZERO = {"1": "Sí", "0": "No"}
SEXOS = {"M": "Hombre", "F": "Mujer", " ": None}
TIPOS_CAND = {"T": "Titular", "S": "Suplente"}
TIPO_AMBITO = {"N": "Nacional", "A": "Autonómico"}
TIPO_MUN_250 = {"08": "Entre 100 y 250 habitantes", "09": "Menos de 100 habitantes"}


def _str(raw: str, _line: str) -> str | None:
    s = raw.strip()
    return s or None


def _str_required(raw: str, _line: str) -> str:
    return raw.strip()


def _int(raw: str, _line: str) -> int:
    return int(raw) if raw.strip() else 0


def _int_or_none(raw: str, _line: str) -> int | None:
    return int(raw) or None if raw.strip() else None


def _passthrough(raw: str, _line: str) -> str:
    return raw


def _yes_no(raw: str, _line: str) -> str | None:
    return YES_NO.get(raw)


def _one_zero(raw: str, _line: str) -> str | None:
    return ONE_ZERO.get(raw)


def _proceso(raw: str, _line: str) -> str | None:
    return PROCESOS.get(raw)


def _autonomia(raw: str, _line: str) -> str | None:
    return AUTONOMIAS.get(raw)


def _autonomia_or_none_99(raw: str, _line: str) -> str | None:
    return None if raw == "99" else AUTONOMIAS.get(raw)


def _provincia(raw: str, _line: str) -> str | None:
    return PROVINCIAS.get(raw)


def _provincia_or_none_99(raw: str, _line: str) -> str | None:
    return None if raw == "99" else PROVINCIAS.get(raw)


def _year_of(line: str) -> int:
    """Año del proceso, posiciones 3-6 (1-based) = índices 2-5 (0-based) en casi todos los ficheros."""
    return int(line[2:6])


def _proceso_of(line: str) -> str:
    return line[0:2]


# ---------------------------------------------------------------------------
# Formatters específicos
# ---------------------------------------------------------------------------

def _sexo(raw: str, _line: str) -> str | None:
    return SEXOS.get(raw)


def _tipo_candidato(raw: str, _line: str) -> str | None:
    return TIPOS_CAND.get(raw)


def _dni(raw: str, _line: str) -> str | None:
    s = raw.strip()
    if s == "00000000" or not s:
        return None
    return s


def _tipo_ambito(raw: str, _line: str) -> str | None:
    return TIPO_AMBITO.get(raw)


def _ambito_autonomia_si_aplica(raw: str, line: str) -> str | None:
    """Solo devuelve el ámbito autonómico si el proceso lo usa."""
    proceso = _proceso_of(line)
    ambito = line[9:10]
    if proceso in PROCESOS_AMBITO_AUTONOMICO or (proceso == "01" and ambito == "A"):
        return AUTONOMIAS.get(raw)
    return None


def _distrito_4_or_5(raw: str, line: str) -> str | None:
    """Distrito en fichero 04 (start 12) y similares (campo de 1 carácter)."""
    if raw == "9":
        return None
    if raw == "0":
        # En `municipales/04199906_*` puede ser '0' aunque no esté en spec.
        return None
    proceso = _proceso_of(line)
    provincia = line[9:11]
    return DISTRITOS.get(proceso, {}).get(provincia, {}).get(raw)


def _municipio_04(raw: str, line: str) -> str | None:
    proceso = _proceso_of(line)
    if proceso != "04":
        return None
    provincia = line[9:11]
    return lookup_municipio(_year_of(line), provincia + raw)


def _orden_senador_04(raw: str, line: str) -> int | None:
    proceso = _proceso_of(line)
    if proceso != "03":
        return None
    return int(raw)


def _municipio_05(raw: str, line: str) -> str | None:
    provincia = line[11:13]
    return lookup_municipio(_year_of(line), provincia + raw)


def _nombre_municipio_05(raw: str, line: str) -> str | None:
    distrito = line[16:18]
    return raw.strip() if distrito == "99" else None


def _nombre_distrito_05(raw: str, line: str) -> str | None:
    distrito = line[16:18]
    return raw.strip() if distrito != "99" else None


def _distrito_2chars_or_none_99(raw: str, _line: str) -> str | None:
    return None if raw == "99" else raw


def _municipio_06(raw: str, line: str) -> str | None:
    provincia = line[9:11]
    return lookup_municipio(_year_of(line), provincia + raw)


def _codigo_candidatura_excepto_03(raw: str, line: str) -> str | None:
    return raw if _proceso_of(line) != "03" else None


def _distrito_6chars_para_03(raw: str, line: str) -> str | None:
    if _proceso_of(line) != "03":
        return None
    provincia = raw[0:2]
    distrito = raw[2:3]
    if distrito == "9":
        return None
    return DISTRITOS.get("03", {}).get(provincia, {}).get(distrito)


def _orden_senador_6chars(raw: str, line: str) -> int | None:
    if _proceso_of(line) != "03":
        return None
    return int(raw[3:6])


def _vuelta_o_pregunta_vuelta(raw: str, line: str) -> str | None:
    """En referéndum (proceso 01) este campo es número de pregunta, no vuelta."""
    return raw if _proceso_of(line) != "01" else None


def _vuelta_o_pregunta_pregunta(raw: str, line: str) -> str | None:
    return raw if _proceso_of(line) == "01" else None


def _distrito_electoral_07(raw: str, line: str) -> str | None:
    if raw == "9":
        return None
    proceso = _proceso_of(line)
    provincia = line[11:13]
    return DISTRITOS.get(proceso, {}).get(provincia, {}).get(raw)


def _municipio_09_o_none_si_cera(raw: str, line: str) -> str | None:
    if raw == "999":
        return None
    provincia = line[11:13]
    return lookup_municipio(_year_of(line), provincia + raw)


def _cera_si_es_999(raw: str, _line: str) -> str | None:
    return "Sí" if raw == "999" else None


def _distrito_09(raw: str, _line: str) -> str | None:
    return None if raw == "01" else raw


def _seccion_09(raw: str, _line: str) -> str | None:
    return None if raw == "0000" else raw


def _mesa_09(raw: str, _line: str) -> str | None:
    return None if raw == "U" else raw


def _censo_zero7_to_none(raw: str, _line: str) -> int | None:
    return None if raw == "0000000" else int(raw)


def _censo_escrutinio_09(raw: str, line: str) -> int | None:
    municipio = line[13:16]
    return int(raw) if municipio != "999" else None


def _censo_cera_09(raw: str, line: str) -> int | None:
    municipio = line[13:16]
    return int(raw) if municipio == "999" else None


def _tipo_municipio_250(raw: str, _line: str) -> str | None:
    return TIPO_MUN_250.get(raw)


def _municipio_11_12(raw: str, line: str) -> str | None:
    # En ficheros 11/12 la provincia está en posiciones distintas.
    # Para el 11 está en 12-13 (1-based) = índices 11-12; para el 12 en 10-11 = 9-10.
    # Inferimos por el "tipo de fichero": el 11 empieza por '08'/'09' y luego año (4) +
    # mes (2) + vuelta (1) + comunidad (2) + provincia (2). Para el 12 no hay comunidad,
    # provincia va inmediatamente después de la vuelta.
    # En lugar de inferir, distinguimos por la longitud probable: en el 11 los nombres
    # están en pos 17 (length 100), en el 12 NO existe nombre. Aquí lo determinamos por
    # contexto pasando la pista en `line` — no es necesario, simplemente probamos las dos
    # posiciones y devolvemos la que produzca un acierto.
    year = _year_of(line)
    # Intento 11: provincia en 11..12 (0-based)
    cand = line[11:13] + raw
    name = lookup_municipio(year, cand)
    if name is not None:
        return name
    # Intento 12: provincia en 9..10 (0-based)
    cand = line[9:11] + raw
    return lookup_municipio(year, cand)


# Para distinguir 11 y 12 sin ambigüedad, definimos formatters dedicados.
def _municipio_11(raw: str, line: str) -> str | None:
    provincia = line[11:13]
    return lookup_municipio(_year_of(line), provincia + raw)


def _municipio_12(raw: str, line: str) -> str | None:
    provincia = line[9:11]
    return lookup_municipio(_year_of(line), provincia + raw)


# ---------------------------------------------------------------------------
# Generador de los flags "Contiene el fichero NN" del fichero 01
# ---------------------------------------------------------------------------

def _contiene(start: int, file_code: str) -> Field:
    return Field(
        name=f"Contiene el fichero {file_code} ({FICHEROS[file_code[:2] if len(file_code) > 2 else file_code]})",
        start=start,
        length=1,
        formatter=_one_zero,
    )


# ---------------------------------------------------------------------------
# Especificación de cada tipo de fichero
# ---------------------------------------------------------------------------

FORMATS: dict[str, list[Field]] = {
    # Fichero 01 — Control
    "01": [
        Field("Tipo de elección", 1, 2, _proceso),
        Field("Año", 3, 4, _passthrough),
        Field("Mes", 7, 2, _int),
        Field("Vuelta", 9, 1, _passthrough),
        _contiene(11, "02"),
        _contiene(12, "03"),
        _contiene(13, "04"),
        _contiene(14, "05"),
        _contiene(15, "06"),
        _contiene(16, "07"),
        _contiene(17, "08"),
        _contiene(18, "09"),
        _contiene(19, "10"),
        _contiene(20, "1104"),
        _contiene(21, "1204"),
        _contiene(22, "0510"),
        _contiene(23, "0610"),
        _contiene(24, "0710"),
        _contiene(25, "0810"),
    ],
    # Fichero 02 — Identificación del proceso electoral
    "02": [
        Field("Tipo de elección", 1, 2, _proceso),
        Field("Año", 3, 4, _passthrough),
        Field("Mes", 7, 2, _int),
        Field("Vuelta", 9, 1, _passthrough),
        Field("Tipo de ámbito", 10, 1, _tipo_ambito),
        Field("Ámbito", 11, 2, _ambito_autonomia_si_aplica),
        Field("Día de celebración", 13, 2, _int),
        Field("Mes de celebración", 15, 2, _int),
        Field("Año de celebración", 17, 4, _passthrough),
        Field("Hora de apertura", 21, 5, _passthrough),
        Field("Hora de cierre", 26, 5, _passthrough),
        Field("Hora del primer avance de participación", 31, 5, _passthrough),
        Field("Hora del segundo avance de participación", 36, 5, _passthrough),
    ],
    # Fichero 03 — Candidaturas
    "03": [
        Field("Tipo de elección", 1, 2, _proceso),
        Field("Año", 3, 4, _passthrough),
        Field("Mes", 7, 2, _int),
        Field("Código", 9, 6, _passthrough),
        Field("Siglas", 15, 50, _str_required),
        Field("Candidatura", 65, 150, _str_required),
        Field("Candidatura provincial", 215, 6, _passthrough),
        Field("Candidatura autonómica", 221, 6, _passthrough),
        Field("Candidatura nacional", 227, 6, _passthrough),
    ],
    # Fichero 04 — Relación de candidatos
    "04": [
        Field("Tipo de elección", 1, 2, _proceso),
        Field("Año", 3, 4, _passthrough),
        Field("Mes", 7, 2, _int),
        Field("Vuelta", 9, 1, _passthrough),
        Field("Provincia", 10, 2, lambda r, _l: None if r == "99" else PROVINCIAS.get(r)),
        Field("Distrito", 12, 1, _distrito_4_or_5),
        Field("Municipio", 13, 3, _municipio_04),
        Field("Número de orden de senador", 13, 3, _orden_senador_04),
        Field("Candidatura", 16, 6, _passthrough),
        Field("Número de orden del candidato", 22, 3, _int),
        Field("Tipo de candidato", 25, 1, _tipo_candidato),
        Field("Nombre", 26, 25, _str_required),
        Field("Primer apellido", 51, 25, _str),
        Field("Segundo apellido", 76, 25, _str),
        Field("Sexo", 101, 1, _sexo),
        Field("Día de nacimiento", 102, 2, _int_or_none),
        Field("Mes de nacimiento", 104, 2, _int_or_none),
        Field("Año de nacimiento", 106, 4, _int_or_none),
        Field("DNI", 110, 10, _dni),
        Field("Elegido", 120, 1, _yes_no),
    ],
    # Fichero 05 — Datos comunes de municipios
    "05": [
        Field("Tipo de elección", 1, 2, _proceso),
        Field("Año", 3, 4, _passthrough),
        Field("Mes", 7, 2, _int),
        Field("Vuelta", 9, 1, _passthrough),
        Field("Comunidad autónoma", 10, 2, _autonomia),
        Field("Provincia", 12, 2, _provincia),
        Field("Municipio", 14, 3, _municipio_05),
        Field("Número de distrito", 17, 2, _distrito_2chars_or_none_99),
        Field("Nombre del municipio", 19, 100, _nombre_municipio_05),
        Field("Nombre del distrito", 19, 100, _nombre_distrito_05),
        Field("Distrito electoral", 119, 1, _int_or_none),
        Field("Partido judicial", 120, 3, _passthrough),
        Field("Diputación provincial", 123, 3, _passthrough),
        Field("Comarca", 126, 3, _passthrough),
        Field("Población de derecho", 129, 8, _int),
        Field("Número de mesas", 137, 5, _int),
        Field("Censo del INE", 142, 8, _int),
        Field("Censo de escrutinio", 150, 8, _int),
        Field("Censo CERE en escrutinio", 158, 8, _int),
        Field("Total votantes CERE", 166, 8, _int),
        Field("Votantes del primer avance", 174, 8, _int),
        Field("Votantes del segundo avance", 182, 8, _int),
        Field("Votantes en blanco", 190, 8, _int),
        Field("Votantes nulos", 198, 8, _int),
        Field("Votantes a candidaturas", 206, 8, _int),
        Field("Número de escaños", 214, 3, _int_or_none),
        Field("Votos afirmativos", 217, 8, _int_or_none),
        Field("Votos negativos", 225, 8, _int_or_none),
        Field("Datos oficiales", 233, 1, _yes_no),
    ],
    # Fichero 06 — Datos de candidaturas de municipios
    "06": [
        Field("Tipo de elección", 1, 2, _proceso),
        Field("Año", 3, 4, _passthrough),
        Field("Mes", 7, 2, _int),
        Field("Vuelta", 9, 1, _passthrough),
        Field("Provincia", 10, 2, _provincia),
        Field("Municipio", 12, 3, _municipio_06),
        Field("Número de distrito", 15, 2, _distrito_2chars_or_none_99),
        Field("Código de candidatura", 17, 6, _codigo_candidatura_excepto_03),
        Field("Distrito", 17, 6, _distrito_6chars_para_03),
        Field("Número de orden de senador", 17, 6, _orden_senador_6chars),
        Field("Votos obtenidos", 23, 8, _int),
        Field("Número de candidatos obtenidos", 31, 3, _int),
    ],
    # Fichero 07 — Datos comunes de ámbito superior al municipio
    "07": [
        Field("Tipo de elección", 1, 2, _proceso),
        Field("Año", 3, 4, _passthrough),
        Field("Mes", 7, 2, _int),
        Field("Vuelta", 9, 1, _vuelta_o_pregunta_vuelta),
        Field("Número de pregunta", 9, 1, _vuelta_o_pregunta_pregunta),
        Field("Comunidad autónoma", 10, 2, _autonomia_or_none_99),
        Field("Provincia", 12, 2, _provincia_or_none_99),
        Field("Distrito electoral", 14, 1, _distrito_electoral_07),
        Field("Ámbito territorial", 15, 50, _str_required),
        Field("Población de derecho", 65, 8, _int),
        Field("Número de mesas", 73, 5, _int),
        Field("Censo del INE", 78, 8, _int),
        Field("Censo de escrutinio", 86, 8, _int),
        Field("Censo CERE en escrutinio", 94, 8, _int),
        Field("Total votantes CERE", 102, 8, _int),
        Field("Votantes del primer avance", 110, 8, _int),
        Field("Votantes del segundo avance", 118, 8, _int),
        Field("Votantes en blanco", 126, 8, _int),
        Field("Votantes nulos", 134, 8, _int),
        Field("Votantes a candidaturas", 142, 8, _int),
        Field("Número de escaños", 150, 6, _int_or_none),
        Field("Votos afirmativos", 156, 8, _int_or_none),
        Field("Votos negativos", 164, 8, _int_or_none),
        Field("Datos oficiales", 172, 1, _yes_no),
    ],
    # Fichero 08 — Datos de candidaturas de ámbito superior al municipio
    "08": [
        Field("Tipo de elección", 1, 2, _proceso),
        Field("Año", 3, 4, _passthrough),
        Field("Mes", 7, 2, _int),
        Field("Vuelta", 9, 1, _passthrough),
        Field("Comunidad autónoma", 10, 2, _autonomia_or_none_99),
        Field("Provincia", 12, 2, _provincia_or_none_99),
        Field("Distrito electoral", 14, 1, _distrito_electoral_07),
        Field("Código de candidatura", 15, 6, _codigo_candidatura_excepto_03),
        Field("Distrito", 15, 6, _distrito_6chars_para_03),
        Field("Número de orden de senador", 15, 6, _orden_senador_6chars),
        Field("Votos obtenidos", 21, 8, _int),
        Field("Número de candidatos obtenidos", 29, 5, _int),
    ],
    # Fichero 09 — Datos comunes de mesas y CERA
    "09": [
        Field("Tipo de elección", 1, 2, _proceso),
        Field("Año", 3, 4, _passthrough),
        Field("Mes", 7, 2, _int),
        Field("Vuelta", 9, 1, _vuelta_o_pregunta_vuelta),
        Field("Número de pregunta", 9, 1, _vuelta_o_pregunta_pregunta),
        Field("Comunidad autónoma", 10, 2, _autonomia_or_none_99),
        Field("Provincia", 12, 2, _provincia_or_none_99),
        Field("Municipio", 14, 3, _municipio_09_o_none_si_cera),
        Field("CERA", 14, 3, _cera_si_es_999),
        Field("Número de distrito", 17, 2, _distrito_09),
        Field("Código de sección", 19, 4, _seccion_09),
        Field("Código de mesa", 23, 1, _mesa_09),
        Field("Censo del INE", 24, 7, _censo_zero7_to_none),
        Field("Censo de escrutinio", 31, 7, _censo_escrutinio_09),
        Field("Censo CERA", 31, 7, _censo_cera_09),
        Field("Censo CERE en escrutinio", 38, 7, _censo_zero7_to_none),
        Field("Total votantes CERE", 45, 7, _censo_zero7_to_none),
        Field("Votantes del primer avance", 52, 7, _censo_zero7_to_none),
        Field("Votantes del segundo avance", 59, 7, _censo_zero7_to_none),
        Field("Votantes en blanco", 66, 7, _int),
        Field("Votantes nulos", 73, 7, _int),
        Field("Votantes a candidaturas", 80, 7, _int),
        Field("Votos afirmativos", 87, 7, _int_or_none),
        Field("Votos negativos", 94, 7, _int_or_none),
        Field("Datos oficiales", 101, 1, _yes_no),
    ],
    # Fichero 10 — Datos de candidaturas de mesas y CERA
    "10": [
        Field("Tipo de elección", 1, 2, _proceso),
        Field("Año", 3, 4, _passthrough),
        Field("Mes", 7, 2, _int),
        Field("Vuelta", 9, 1, _passthrough),
        Field("Comunidad autónoma", 10, 2, _autonomia_or_none_99),
        Field("Provincia", 12, 2, _provincia_or_none_99),
        Field("Municipio", 14, 3, _municipio_09_o_none_si_cera),
        Field("CERA", 14, 3, _cera_si_es_999),
        Field("Número de distrito", 17, 2, _distrito_09),
        Field("Código de sección", 19, 4, _seccion_09),
        Field("Código de mesa", 23, 1, _mesa_09),
        Field("Código de candidatura", 24, 6, _codigo_candidatura_excepto_03),
        Field("Distrito", 24, 6, _distrito_6chars_para_03),
        Field("Número de orden de senador", 24, 6, _orden_senador_6chars),
        Field("Votos obtenidos", 30, 7, _int),
    ],
    # Fichero 11 — Datos comunes en municipios <250 habitantes (solo municipales)
    "11": [
        Field("Tipo de municipio", 1, 2, _tipo_municipio_250),
        Field("Año", 3, 4, _passthrough),
        Field("Mes", 7, 2, _int),
        Field("Vuelta", 9, 1, _passthrough),
        Field("Comunidad autónoma", 10, 2, _autonomia),
        Field("Provincia", 12, 2, _provincia),
        Field("Municipio", 14, 3, _municipio_11),
        Field("Nombre del municipio", 17, 100, _str_required),
        Field("Partido judicial", 117, 3, _passthrough),
        Field("Diputación provincial", 120, 3, _passthrough),
        Field("Comarca", 123, 3, _passthrough),
        Field("Población de derecho", 126, 3, _int),
        Field("Número de mesas", 129, 2, _int),
        Field("Censo del INE", 131, 3, _int),
        Field("Censo de escrutinio", 134, 3, _int),
        Field("Censo CERE en escrutinio", 137, 3, _int),
        Field("Total votantes CERE", 140, 3, _int),
        Field("Votantes del primer avance", 143, 3, _int),
        Field("Votantes del segundo avance", 146, 3, _int),
        Field("Votantes en blanco", 149, 3, _int),
        Field("Votantes nulos", 152, 3, _int),
        Field("Votantes a candidaturas", 155, 3, _int),
        Field("Número de escaños", 158, 2, _int_or_none),
        Field("Datos oficiales", 160, 1, _yes_no),
    ],
    # Fichero 12 — Candidaturas en municipios <250 habitantes (solo municipales)
    "12": [
        Field("Tipo de municipio", 1, 2, _tipo_municipio_250),
        Field("Año", 3, 4, _passthrough),
        Field("Mes", 7, 2, _int),
        Field("Vuelta", 9, 1, _passthrough),
        Field("Provincia", 10, 2, _provincia),
        Field("Municipio", 12, 3, _municipio_12),
        Field("Código", 15, 6, _passthrough),
        Field("Votos obtenidos por la candidatura", 21, 3, _int),
        Field("Número de candidatos obtenidos", 24, 2, _int),
        Field("Nombre", 26, 25, _str_required),
        Field("Primer apellido", 51, 25, _str),
        Field("Segundo apellido", 76, 25, _str),
        Field("Sexo", 101, 1, _sexo),
        Field("Día de nacimiento", 102, 2, _int_or_none),
        Field("Mes de nacimiento", 104, 2, _int_or_none),
        Field("Año de nacimiento", 106, 4, _int_or_none),
        Field("DNI", 110, 10, _dni),
        Field("Votos obtenidos por el candidato", 120, 3, _int),
        Field("Elegido", 123, 1, _yes_no),
    ],
}
