"""
utils.py — Utilidades compartidas para el análisis de videojuegos chilenos.
"""
import logging
import re
from pathlib import Path

import pandas as pd

# ── Logging ───────────────────────────────────────────────────────────────────

def setup_logger(name: str = __name__) -> logging.Logger:
    """Configura y retorna un logger con formato estándar."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s — %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


# ── Parsers de precio ─────────────────────────────────────────────────────────

def parse_price_steam(price_data: dict) -> float:
    """
    Extrae precio en USD desde el objeto price_overview de la Steam API.
    Steam devuelve precios en centavos (ej. 1000 = $10.00).

    Args:
        price_data: Diccionario con clave 'final' (int en centavos).

    Returns:
        Precio como float en la moneda original dividida por 100.
    """
    if not price_data:
        return 0.0
    return round(price_data.get("final", 0) / 100.0, 2)


def parse_price_itch(price_text: str) -> float:
    """
    Extrae precio numérico desde texto de Itch.io (ej. '$5.00', 'Free', '3,99€').

    Args:
        price_text: String con el precio tal como aparece en Itch.io.

    Returns:
        Precio como float. Retorna 0.0 si es gratis o no parseable.
    """
    if not price_text:
        return 0.0
    if "free" in str(price_text).lower():
        return 0.0
    try:
        clean = re.sub(r"[^\d.]", "", str(price_text).replace(",", "."))
        return float(clean) if clean else 0.0
    except ValueError:
        return 0.0


# ── Parsers de fecha ──────────────────────────────────────────────────────────

def parse_date(date_str: str) -> str:
    """
    Normaliza strings de fecha. Retorna el string tal cual si no se puede parsear.

    Args:
        date_str: String de fecha en cualquier formato.

    Returns:
        String de fecha normalizado o el original.
    """
    return str(date_str).strip() if date_str else ""


def extract_year(date_str: str) -> str:
    """
    Extrae el año (4 dígitos) de un string de fecha.

    Args:
        date_str: String con alguna representación de fecha.

    Returns:
        Año como string de 4 dígitos, o 'Unknown' si no se encontró.
    """
    if not date_str:
        return "Unknown"
    match = re.search(r"\b(19|20)\d{2}\b", str(date_str))
    return match.group(0) if match else "Unknown"


# ── Conversión de moneda ──────────────────────────────────────────────────────

# Tasas de conversión aproximadas a USD (para análisis histórico)
_TASAS_A_USD: dict[str, float] = {
    "CLP": 1 / 950.0,
    "USD": 1.0,
    "EUR": 1.10,
    "GBP": 1.27,
    "ARS": 1 / 850.0,
    "BRL": 1 / 5.0,
}


def normalize_currency_to_usd(price: float, currency: str) -> float:
    """
    Convierte un precio a USD usando tasas fijas aproximadas.

    Args:
        price: Precio en la moneda origen.
        currency: Código ISO de moneda (ej. 'CLP', 'USD', 'EUR').

    Returns:
        Precio en USD, redondeado a 2 decimales.
    """
    if price == 0:
        return 0.0
    tasa = _TASAS_A_USD.get(str(currency).upper(), 1.0)
    return round(price * tasa, 2)


# ── Mapeo de estudios ─────────────────────────────────────────────────────────

_STUDIO_LOCATIONS: dict[str, str] = {
    "ACE Team":           "Santiago",
    "AOne Games":         "Santiago",
    "IguanaBee":          "Santiago",
    "Dual Effect":        "Santiago",
    "Octeto Studios":     "Santiago",
    "Abstract Digital":   "Santiago",
    "Time Hunters":       "Santiago",
    "Nidal Games":        "Santiago",
    "Gamaga":             "Santiago",
    "Behavior Santiago":  "Santiago",
    "Wanako Games":       "Santiago",
    "Giant Monkey Robot": "Santiago",
    "Bitplay":            "Santiago",
    "Glitchy Pixel":      "Santiago",
    "Invader Studios":    "Santiago",
    "Movistar GameClub":  "Santiago",
    "Micropsia Games":    "Santiago",
    "Playmestudio":       "Valparaíso",
    "Niebla Games":       "Valparaíso",
    "Estudio Mirlo":      "Valparaíso",
}


def get_location(developers: str) -> str:
    """
    Asigna una ciudad chilena basándose en el nombre del desarrollador.

    Args:
        developers: String con uno o varios desarrolladores separados por coma.

    Returns:
        Ciudad del primer estudio reconocido, o 'Chile (General)'.
    """
    if not developers or pd.isna(developers):
        return "Chile (General)"
    for dev in str(developers).split(","):
        dev = dev.strip()
        for studio, city in _STUDIO_LOCATIONS.items():
            if studio.lower() in dev.lower():
                return city
    return "Chile (General)"
