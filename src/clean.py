"""
clean.py — Limpieza y consolidación de datos crudos de videojuegos chilenos.

Lee JSONs desde data/raw/ (Steam e Itch.io) y genera data/processed/games.csv.
"""
import json
import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from utils import setup_logger, parse_price_steam, parse_price_itch, extract_year

logger = setup_logger("clean")

_PROJECT_ROOT  = Path(__file__).parent.parent
_RAW_DIR       = _PROJECT_ROOT / "data" / "raw"
_PROCESSED_DIR = _PROJECT_ROOT / "data" / "processed"


def _parse_steam(data: dict) -> Optional[dict]:
    """Extrae campos relevantes de un JSON de Steam API."""
    steam_id = data.get("steam_appid")
    if not steam_id:
        return None

    raw_date = data.get("release_date", {}).get("date", "")
    price_obj = data.get("price_overview", {})

    return {
        "source":          "steam",
        "steam_id":        steam_id,
        "name":            data.get("name", "Unknown"),
        "release_date":    raw_date,
        "year":            extract_year(raw_date),
        "is_free":         data.get("is_free", False),
        "price":           parse_price_steam(price_obj),
        "currency":        price_obj.get("currency", "CLP"),
        "metacritic":      (data.get("metacritic") or {}).get("score"),
        "recommendations": (data.get("recommendations") or {}).get("total", 0),
        "genres":          ", ".join(g["description"] for g in data.get("genres", [])),
        "developers":      ", ".join(data.get("developers", [])),
        "publishers":      ", ".join(data.get("publishers", [])),
    }


def _parse_itch(data: dict) -> dict:
    """Extrae campos relevantes de un JSON scrapeado de Itch.io."""
    price_val = parse_price_itch(data.get("price_text", ""))
    return {
        "source":          "itch",
        "steam_id":        None,
        "name":            data.get("name", "Unknown"),
        "release_date":    data.get("release_date", ""),
        "year":            extract_year(data.get("release_date", "")),
        "is_free":         price_val == 0,
        "price":           price_val,
        "currency":        "USD",
        "metacritic":      None,
        "recommendations": 0,
        "genres":          data.get("genre", "Unknown"),
        "developers":      data.get("author", "Unknown"),
        "publishers":      "Self-published",
    }


def build_dataset(raw_dir: Path = _RAW_DIR) -> pd.DataFrame:
    """
    Lee todos los JSONs en raw_dir y retorna un DataFrame consolidado.

    Args:
        raw_dir: Directorio con los JSONs crudos.

    Returns:
        DataFrame limpio y deduplicado.
    """
    json_files = sorted(raw_dir.glob("*.json"))
    if not json_files:
        logger.warning(f"No se encontraron JSONs en: {raw_dir}")
        return pd.DataFrame()

    logger.info(f"Procesando {len(json_files)} archivo(s) desde {raw_dir}...")
    games = []

    for fp in json_files:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            logger.error(f"  ❌ Error leyendo {fp.name}: {exc}")
            continue

        if data.get("source") == "itch":
            game = _parse_itch(data)
        else:
            game = _parse_steam(data)

        if game:
            games.append(game)

    df = pd.DataFrame(games)
    if df.empty:
        return df

    before = len(df)
    df.drop_duplicates(subset=["name", "source"], inplace=True)
    dupes = before - len(df)
    if dupes:
        logger.info(f"  Eliminados {dupes} duplicado(s)")

    return df.reset_index(drop=True)


def main():
    df = build_dataset()

    if df.empty:
        logger.error("No se generó dataset. Revisa los JSONs en data/raw/")
        return

    _PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out = _PROCESSED_DIR / "games.csv"
    df.to_csv(out, index=False, encoding="utf-8-sig")

    logger.info(f"\n✅ Dataset guardado: {out}")
    logger.info(f"   Total registros : {len(df)}")
    logger.info(f"   Por fuente      :\n{df['source'].value_counts().to_string()}")


if __name__ == "__main__":
    main()
