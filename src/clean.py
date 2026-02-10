import json
import pandas as pd
from pathlib import Path
from utils import setup_logger, parse_price_steam, parse_price_itch, parse_date, extract_year

logger = setup_logger("clean_data")

def main():
    raw_dir = Path("data/raw")
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    games_list = []
    logger.info(f"Leyendo archivos RAW desde {raw_dir}...")
    
    for file_path in raw_dir.glob("*.json"):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Error decodificando {file_path}")
                continue
            
            game = {}
            
            # Detectar Fuente
            if "source" in data and data["source"] == "itch":
                # --- ITCH.IO ---
                price_val = parse_price_itch(data.get('price_text'))
                
                game = {
                    'source': 'itch',
                    'steam_id': None,
                    'name': data.get('name', 'Unknown'),
                    'release_date': None,
                    'year': 'Unknown', # Hard to get from simple scrape
                    'is_free': price_val == 0,
                    'price': price_val,
                    'currency': 'USD',
                    'metacritic': None,
                    'recommendations': 0,
                    'genres': data.get('genre', 'Unknown'),
                    'developers': data.get('author', 'Unknown'),
                    'publishers': 'Self-published'
                }
            else:
                # --- STEAM ---
                steam_id = data.get('steam_appid')
                if not steam_id: continue
                
                raw_date = data.get('release_date', {}).get('date')
                
                game = {
                    'source': 'steam',
                    'steam_id': steam_id,
                    'name': data.get('name', 'Unknown'),
                    'release_date': raw_date,
                    'year': extract_year(raw_date),
                    'is_free': data.get('is_free', False),
                    'price': parse_price_steam(data.get('price_overview')),
                    'currency': data.get('price_overview', {}).get('currency', 'CLP'),
                    'metacritic': data.get('metacritic', {}).get('score'),
                    'recommendations': data.get('recommendations', {}).get('total', 0),
                    'genres': ", ".join([g['description'] for g in data.get('genres', [])]),
                    'developers': ", ".join(data.get('developers', [])),
                    'publishers': ", ".join(data.get('publishers', []))
                }

            games_list.append(game)
            
    df = pd.DataFrame(games_list)
    
    # Post-proceso: Asegurar año en Itch si es posible (future work) o limpiar
    # Eliminar duplicados si hubiese
    df.drop_duplicates(subset=['name', 'source'], inplace=True)

    output_path = processed_dir / "games.csv"
    df.to_csv(output_path, index=False)
    
    logger.info(f"Dataset consolidado generado: {output_path}")
    logger.info(f"Total registros: {len(df)}")
    logger.info(f"Desglose por fuente:\n{df['source'].value_counts()}")

if __name__ == "__main__":
    main()
