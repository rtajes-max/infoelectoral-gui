"""
Constantes pequeñas (autonomías, provincias, ficheros, procesos, distritos electorales).

Portado literalmente de `reference/src/includes/constants.php` de JaimeObregon/infoelectoral
(AGPL-3.0). Las tablas grandes (municipios) se cargan en `municipios.py`.
"""

from __future__ import annotations

AUTONOMIAS: dict[str, str] = {
    "01": "Andalucía",
    "02": "Aragón",
    "03": "Asturias",
    "04": "Baleares",
    "05": "Canarias",
    "06": "Cantabria",
    "07": "Castilla La Mancha",
    "08": "Castilla y León",
    "09": "Cataluña",
    "10": "Extremadura",
    "11": "Galicia",
    "12": "Madrid",
    "13": "Navarra",
    "14": "País Vasco",
    "15": "Murcia",
    "16": "La Rioja",
    "17": "Comunidad Valenciana",
    "18": "Ceuta",
    "19": "Melilla",
}

PROVINCIAS: dict[str, str] = {
    "01": "Álava", "02": "Albacete", "03": "Alicante", "04": "Almería", "05": "Ávila",
    "06": "Badajoz", "07": "Baleares", "08": "Barcelona", "09": "Burgos", "10": "Cáceres",
    "11": "Cádiz", "12": "Castellón", "13": "Ciudad Real", "14": "Córdoba", "15": "A Coruña",
    "16": "Cuenca", "17": "Girona", "18": "Granada", "19": "Guadalajara", "20": "Guipúzcoa",
    "21": "Huelva", "22": "Huesca", "23": "Jaén", "24": "León", "25": "Lleida",
    "26": "La Rioja", "27": "Lugo", "28": "Madrid", "29": "Málaga", "30": "Murcia",
    "31": "Navarra", "32": "Ourense", "33": "Asturias", "34": "Palencia", "35": "Las Palmas",
    "36": "Pontevedra", "37": "Salamanca", "38": "Santa Cruz de Tenerife", "39": "Cantabria",
    "40": "Segovia", "41": "Sevilla", "42": "Soria", "43": "Tarragona", "44": "Teruel",
    "45": "Toledo", "46": "Valencia", "47": "Valladolid", "48": "Vizcaya", "49": "Zamora",
    "50": "Zaragoza", "51": "Ceuta", "52": "Melilla",
}

FICHEROS: dict[str, str] = {
    "01": "Control",
    "02": "Identificación del proceso electoral",
    "03": "Candidaturas",
    "04": "Candidatos",
    "05": "Datos globales de ámbito municipal",
    "06": "Datos de candidaturas de ámbito municipal",
    "07": "Datos globales de ámbito superior al municipio",
    "08": "Datos de candidaturas de ámbito superior al municipio",
    "09": "Datos globales de mesas",
    "10": "Datos de candidaturas de mesas",
    "11": "Datos globales de municipios menores de 250 habitantes (en elecciones municipales)",
    "12": "Datos de candidaturas de municipios menores de 250 habitantes (en elecciones municipales)",
}

PROCESOS: dict[str, str] = {
    "01": "Referéndum",
    "02": "Congreso",
    "03": "Senado",
    "04": "Municipales",
    "05": "Autonómicas",
    "06": "Cabildos",
    "07": "Parlamento Europeo",
    "10": "Partidos judiciales y diputaciones provinciales",
    "15": "Juntas Generales",
}

# Distritos electorales: DISTRITOS[proceso][provincia][código] -> nombre
DISTRITOS: dict[str, dict[str, dict[str, str]]] = {
    "03": {  # Senado
        "07": {"1": "Mallorca", "2": "Menorca", "3": "Ibiza-Formentera"},
        "35": {"1": "Gran Canaria", "2": "Lanzarote", "3": "Fuerteventura"},
        "38": {"4": "Tenerife", "5": "La Palma", "6": "La Gomera", "7": "El Hierro"},
    },
    "05": {  # Autonómicas
        "07": {"1": "Mallorca", "2": "Menorca", "3": "Ibiza", "4": "Formentera"},
        "30": {"1": "Primera", "2": "Segunda", "3": "Tercera", "4": "Cuarta", "5": "Quinta"},
        "33": {"1": "Oriente", "2": "Centro", "3": "Occidente"},
        "35": {"1": "Gran Canaria", "2": "Lanzarote", "3": "Fuerteventura"},
        "38": {"4": "Tenerife", "5": "La Palma", "6": "La Gomera", "7": "El Hierro"},
    },
    "06": {  # Cabildos
        "35": {"1": "Gran Canaria", "2": "Lanzarote", "3": "Fuerteventura"},
        # Nota: en el original PHP "La Palmaa" es typo upstream; lo dejamos como en la fuente.
        "38": {"4": "Tenerife", "5": "La Palmaa", "6": "La Gomera", "7": "El Hierro"},
    },
    "15": {  # Juntas Generales
        "01": {"1": "Vitoria-Gasteiz", "2": "Aira-Ayala", "3": "Resto"},
        "20": {"1": "Deba-Urola", "2": "Bidasoa-Oyarzun", "3": "Donostialdea", "4": "Oria"},
        "48": {"1": "Bilbao", "2": "Encartaciones", "3": "Durango-Arratia", "4": "Busturia-Uribe"},
    },
}

# Procesos electorales que sí usan ámbito autonómico en el campo "Ámbito" del fichero 02.
PROCESOS_AMBITO_AUTONOMICO = {"05", "06", "15"}
