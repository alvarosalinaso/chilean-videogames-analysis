import requests
from bs4 import BeautifulSoup
import json
import time
import re
from pathlib import Path
from utils import setup_logger

logger = setup_logger("collect_itch")

def fetch_itch_games():
    base_url = "https://itch.io/games/tag-chile"
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    games_found = []
    page = 1
    
    logger.info("Iniciando scraping de Itch.io (tag: chile)...")
    
    while True:
        logger.info(f"Procesando página {page}...")
        try:
            url = f"{base_url}?page={page}"
            r = requests.get(url)
            if r.status_code != 200:
                logger.warning(f"Fin de paginación o error (Status {r.status_code})")
                break
                
            soup = BeautifulSoup(r.text, 'html.parser')
            game_cells = soup.select('.game_cell')
            
            if not game_cells:
                logger.info("No se encontraron más juegos en esta página.")
                break
                
            for cell in game_cells:
                # Extraer datos básicos
                title_elem = cell.select_one('.game_title a')
                if not title_elem: continue
                
                title = title_elem.text.strip()
                link = title_elem['href']
                game_id = cell.get('data-game_id')
                
                author = "Unknown"
                author_elem = cell.select_one('.game_author a')
                if author_elem:
                    author = author_elem.text.strip()
                    
                genre = "Unknown"
                genre_elem = cell.select_one('.game_genre')
                if genre_elem:
                    genre = genre_elem.text.strip()
                    
                price_elem = cell.select_one('.game_text a.price_value')
                
                game_data = {
                    "source": "itch",
                    "id": game_id,
                    "name": title,
                    "url": link,
                    "author": author,
                    "genre": genre,
                    "price_text": price_elem.text.strip() if price_elem else "Free/NYP",
                    "year": "Unknown" 
                }
                
                # Save
                out_file = raw_dir / f"itch_{game_id}.json"
                with open(out_file, "w", encoding="utf-8") as f:
                    json.dump(game_data, f, indent=4, ensure_ascii=False)
                
                games_found.append(game_data)
                
            page += 1
            time.sleep(1.0) # Be nice
            
        except Exception as e:
            logger.error(f"Error en página {page}: {e}")
            break
            
    logger.info(f"Finalizado. {len(games_found)} juegos de Itch.io guardados.")

if __name__ == "__main__":
    fetch_itch_games()
