import requests, json, time, re
from bs4 import BeautifulSoup
from pathlib import Path
from utils import setup_logger

log = setup_logger("collect_itch")

def pull_itch_cl_tag():
    b_url = "https://itch.io/games/tag-chile"
    out_dir = Path("data/raw")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    games = []
    p = 1
    
    log.info("Scraping Itch.io tag-chile...")
    
    while True:
        log.info(f"Page {p}...")
        try:
            r = requests.get(f"{b_url}?page={p}")
            if r.status_code != 200: break
                
            soup = BeautifulSoup(r.text, 'html.parser')
            cells = soup.select('.game_cell')
            
            if not cells: break
                
            for c in cells:
                t_el = c.select_one('.game_title a')
                if not t_el: continue
                
                gid = c.get('data-game_id')
                a_el = c.select_one('.game_author a')
                g_el = c.select_one('.game_genre')
                p_el = c.select_one('.game_text a.price_value')
                
                gd = {
                    "source": "itch",
                    "id": gid,
                    "name": t_el.text.strip(),
                    "url": t_el['href'],
                    "author": a_el.text.strip() if a_el else "Unknown",
                    "genre": g_el.text.strip() if g_el else "Unknown",
                    "price_text": p_el.text.strip() if p_el else "Free/NYP",
                    "year": "Unknown" 
                }
                
                with open(out_dir / f"itch_{gid}.json", "w", encoding="utf-8") as f:
                    json.dump(gd, f, indent=2, ensure_ascii=False)
                
                games.append(gd)
                
            p += 1
            time.sleep(1) # throttle
            
        except Exception as e:
            log.error(f"Failing at page {p}: {e}"); break
            
    log.info(f"Done. {len(games)} records grabbed.")

if __name__ == "__main__": pull_itch_cl_tag()
