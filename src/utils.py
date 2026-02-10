import re
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd

# Configuración de Logging
def setup_logger(name=__name__):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

logger = setup_logger()

def parse_price_steam(price_data):
    """
    Extrae precio en formato numérico desde objeto Steam.
    Steam API retorna en centavos (e.g. 1000 = 10.00).
    """
    if not price_data:
        return 0.0
    return price_data.get('final', 0) / 100.0

def parse_price_itch(price_text):
    """
    Extrae precio desde texto de Itch.io (ej: '$5.00', 'Free').
    Retorna float.
    """
    if not price_text: 
        return 0.0
    if 'free' in price_text.lower():
        return 0.0
    
    # Extraer números
    try:
        # Remover símbolos de moneda y limpiar
        clean_text = re.sub(r'[^\d.]', '', price_text)
        if clean_text:
            return float(clean_text)
    except Exception as e:
        logger.warning(f"Error parseando precio Itch '{price_text}': {e}")
        
    return 0.0

def parse_date(date_str):
    """
    Normaliza fechas de lanzamiento.
    Intenta extraer formatos comunes o devuelve el string original si falla.
    """
    if not date_str:
        return None
    
    date_str = str(date_str).strip()
    
    # Intentar detectar año con regex simple si es formato texto libre
    # Ej: "Coming 2024", "Q1 2025" -> extraemos 2024/2025 para la columna 'year'
    return date_str

def extract_year(date_str):
    """
    Extrae el año como entero o string de una fecha variada.
    """
    if not date_str:
        return "Unknown"
        
    match = re.search(r'\d{4}', str(date_str))
    if match:
        return match.group(0)
    return "Unknown"

def normalize_currency_to_usd(price, currency):
    """
    Convierte precio a USD (Estimado).
    Tasa fija para simplicidad histórica: 950 CLP = 1 USD.
    """
    if price == 0:
        return 0.0
    
    currency = str(currency).upper()
    
    if currency == 'CLP':
        return round(price / 950.0, 2)
    elif currency == 'USD':
        return float(price)
    elif currency == 'EUR':
        return round(price * 1.1, 2) # Aprox
    
    return float(price) # Asumir USD por defecto si desconocido

# Mapeo manual de Estudios -> Ciudad
STUDIO_LOCATIONS = {
    "ACE Team": "Santiago",
    "AOne Games": "Santiago",
    "IguanaBee": "Santiago",
    "Dual Effect": "Santiago",
    "Octeto Studios": "Santiago",
    "Abstract Digital": "Santiago",
    "Time Hunters": "Santiago",
    "Nidal Games": "Santiago",
    "Gamaga": "Santiago",
    "Behavior Santiago": "Santiago",
    "Wanako Games": "Santiago",
    "Playmestudio": "Valparaíso",
    "Giant Monkey Robot": "Santiago",
    "Bitplay": "Santiago",
    "Glitchy Pixel": "Santiago",
    "Invader Studios": "Santiago",
    "Movistar GameClub": "Santiago",
    "Micropsia Games": "Santiago",
    "Niebla Games": "Valparaíso",
    "Unknown": "Unknown"
}

def get_location(developers):
    """
    Asigna una ciudad basada en el nombre del desarrollador.
    """
    if not developers or pd.isna(developers):
        return "Chile (General)"
    
    # Buscar si alguno de los devs está en nuestra lista
    for dev in str(developers).split(','):
        dev = dev.strip()
        # Búsqueda parcial
        for studio, city in STUDIO_LOCATIONS.items():
            if studio.lower() in dev.lower():
                return city
    
    return "Chile (General)"
