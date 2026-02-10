import requests
import json
import time
import re
from pathlib import Path
from bs4 import BeautifulSoup
from utils import setup_logger

logger = setup_logger("collect_steam")

# Lista extraída de Chile Games Database (y manuales previos)
GAME_NAMES = [
    # Page 1
    "Yomo : Keep Your Cool!", "Lilly & Willy", "Forgotten – Whispers of the Past", "Valiants: Arena",
    "Microlandia", "BALSEO: The Sea Beyond", "Isekai Guild", "Re:Agent", "WAFIEU",
    "SAI: Servicio de Auxilio Inmediato", "Stick Out!", "Colorbound", "Gallery of Shadows – Lycans Returns",
    "Elemental Wizards", "The Eightfold Path", "Space Evolver", "Chromatic Battles", "Kami’s Garden: Bound To The Pages",
    # Page 2
    "ZOMBI ROCKSTAR", "Virus Blast", "Don Pepe y sus globos", "NBB.EXE", "Tormented Souls 2",
    "Hybrid Blood", "Jumpy Paws – World Adventures", "Avoidthis", "Hoverise Rebellion", "Oriontis",
    "Aura: Echoes of Pain", "Crystal Crepes: Tales of Food and Magic", "Stop, Pawssport Check",
    "PaRoKuuu", "Generic Fighter Maybe", "Membrillo Hid My Socks", "Mutter", "Sketchy Driver",
    # Page 3
    "Orphans", "Selve", "Dungeon of the Forgotten King", "Leap Galaxy", "Forge the Fates",
    "Bulbo’s Belief System", "Night in Delirium", "Unlinked Mask", "Scarleth", "UNGALAND!",
    "Arm Around!", "Soul Catcher: The Moon Coliseum", "Daybreak Slam", "Cosmic Horror Tales: Roots Below",
    "Ink of Fate", "Scalpel, Please!", "Mecha Survivors", "El Pasante Elementalista",
    # Page 4
    "Dungeon Shifters", "3D Ultra Minigolf Adventures", "Asterminer", "Bandits", "Cubito Mayhem",
    "Dirty Wars: September 11", "El Culto", "Gematombe", "Genimas: Life reborn", "Heroes of The Sacred Tree",
    "Hijos del Invierno", "Jet & Sky", "Last Eclipse", "Little League World Series Baseball 2022",
    "Madness in the Banaverse", "Logic Circuit: Marble Puzzle", "Omnibion War", "Operation8 Project",
    # Page 5
    "Opus Ludum", "PartySaur: Dino Mayhem", "Posable Heroes", "Protoplanet Express", "Rise of Jericho",
    "Rivers of Rain", "Santa Rockstar", "Selknam Defense", "Sinner’s Tavern", "Skull Island: Rise of Kong",
    "SPELLRAIN", "Stoppa!", "Mix the Forgotten", "Afterlife Gladiator", "Kyubu Kyubu Dice", "Tiles in Time",
    "The Trolley Solution", "Tactical Operations Force",
    # Legacy / Manual
    "Zeno Clash", "Zeno Clash 2", "Rock of Ages", "Rock of Ages 2", "Rock of Ages 3",
    "Abyss Odyssey", "The Eternal Cylinder", "Clash: Artifacts of Chaos", "Tormented Souls",
    "Omen of Sorrow", "Causa, Voices of the Dusk", "What Lies in the Multiverse", "The Signifier",
    "Cyber Ops", "Defenders of Ekron", "Long Gone Days", "The Horror Of Salazar House",
    "The Rangers In The South", "Urbek City Builder"
]

def search_steam_id(game_name):
    """Busca el AppID de un juego por nombre en la tienda de Steam."""
    try:
        # Usar term=nombre y category1=998 (Game)
        url = "https://store.steampowered.com/search/"
        params = {'term': game_name, 'category1': 998, 'l': 'spanish'}
        # Cookie de edad para evitar gate
        cookies = {'birthtime': '568022401', 'lastagecheckage': '1-0-1988'} 
        
        r = requests.get(url, params=params, cookies=cookies)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Buscar el primer resultado que sea un juego
        results = soup.select('a.search_result_row')
        
        for res in results:
            title = res.select_one('.title').text.strip()
            appid = res.get('data-ds-appid')
            
            # Verificación de Similitud Simple
            q_tokens = set(re.findall(r'\w+', game_name.lower()))
            t_tokens = set(re.findall(r'\w+', title.lower()))
            
            if not q_tokens.intersection(t_tokens):
                 if game_name.lower() not in title.lower() and title.lower() not in game_name.lower():
                     logger.debug(f"  [Descartado] '{title}' (AppID: {appid}) no coincide con '{game_name}'")
                     continue

            if appid:
                logger.info(f"  [Encontrado] '{game_name}' -> ID: {appid} ('{title}')")
                return appid
    except Exception as e:
        logger.error(f"  [Error Búsqueda] {game_name}: {e}")
    
    logger.warning(f"  [No Encontrado] '{game_name}'")
    return None

def fetch_game_data(app_id):
    """Obtiene datos de la API de Steam."""
    url = f"http://store.steampowered.com/api/appdetails?appids={app_id}&l=spanish"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data and str(app_id) in data and data[str(app_id)]['success']:
                return data[str(app_id)]['data']
    except Exception as e:
        logger.error(f"Error fetching {app_id}: {e}")
    return None

def main():
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    processed_ids = set()
    for p in raw_dir.glob("*.json"):
        processed_ids.add(p.stem)
        
    logger.info(f"Iniciando búsqueda para {len(GAME_NAMES)} títulos...")
    
    for name in GAME_NAMES:
        # Paso 1: Buscar ID
        app_id = search_steam_id(name)
        
        if app_id:
            if ',' in app_id:
                app_id = app_id.split(',')[0]
                
            if app_id in processed_ids:
                logger.debug(f"  -> Ya existe (ID: {app_id})")
                continue
                
            # Paso 2: Descargar datos
            game_info = fetch_game_data(app_id)
            if game_info:
                with open(raw_dir / f"{app_id}.json", "w", encoding="utf-8") as f:
                    json.dump(game_info, f, indent=4, ensure_ascii=False)
                processed_ids.add(str(app_id))
                logger.info(f"  -> DATOS GUARDADOS para {app_id}")
            else:
                logger.warning(f"  -> Falló API Details para {app_id}")
            
            time.sleep(1.0) # Rate limit friendly
        
        time.sleep(0.5)

if __name__ == "__main__":
    main()
