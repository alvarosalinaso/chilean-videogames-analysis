import requests, json, time, re
from pathlib import Path
from bs4 import BeautifulSoup
from utils import setup_logger

log = setup_logger("collect_steam")

GAME_NAMES = [
    "Yomo : Keep Your Cool!", "Lilly & Willy", "Forgotten – Whispers of the Past", "Valiants: Arena",
    "Microlandia", "BALSEO: The Sea Beyond", "Isekai Guild", "Re:Agent", "WAFIEU", "SAI: Servicio de Auxilio Inmediato", 
    "Stick Out!", "Colorbound", "Gallery of Shadows – Lycans Returns", "Elemental Wizards", "The Eightfold Path", 
    "Space Evolver", "Chromatic Battles", "Kami’s Garden: Bound To The Pages", "ZOMBI ROCKSTAR", "Virus Blast", 
    "Don Pepe y sus globos", "NBB.EXE", "Tormented Souls 2", "Hybrid Blood", "Jumpy Paws – World Adventures", 
    "Avoidthis", "Hoverise Rebellion", "Oriontis", "Aura: Echoes of Pain", "Crystal Crepes: Tales of Food and Magic", 
    "Stop, Pawssport Check", "PaRoKuuu", "Generic Fighter Maybe", "Membrillo Hid My Socks", "Mutter", "Sketchy Driver",
    "Orphans", "Selve", "Dungeon of the Forgotten King", "Leap Galaxy", "Forge the Fates", "Bulbo’s Belief System", 
    "Night in Delirium", "Unlinked Mask", "Scarleth", "UNGALAND!", "Arm Around!", "Soul Catcher: The Moon Coliseum", 
    "Daybreak Slam", "Cosmic Horror Tales: Roots Below", "Ink of Fate", "Scalpel, Please!", "Mecha Survivors", 
    "El Pasante Elementalista", "Dungeon Shifters", "3D Ultra Minigolf Adventures", "Asterminer", "Bandits", 
    "Cubito Mayhem", "Dirty Wars: September 11", "El Culto", "Gematombe", "Genimas: Life reborn", 
    "Heroes of The Sacred Tree", "Hijos del Invierno", "Jet & Sky", "Last Eclipse", "Little League World Series Baseball 2022",
    "Madness in the Banaverse", "Logic Circuit: Marble Puzzle", "Omnibion War", "Operation8 Project", "Opus Ludum", 
    "PartySaur: Dino Mayhem", "Posable Heroes", "Protoplanet Express", "Rise of Jericho", "Rivers of Rain", 
    "Santa Rockstar", "Selknam Defense", "Sinner’s Tavern", "Skull Island: Rise of Kong", "SPELLRAIN", "Stoppa!", 
    "Mix the Forgotten", "Afterlife Gladiator", "Kyubu Kyubu Dice", "Tiles in Time", "The Trolley Solution", 
    "Tactical Operations Force", "Zeno Clash", "Zeno Clash 2", "Rock of Ages", "Rock of Ages 2", "Rock of Ages 3",
    "Abyss Odyssey", "The Eternal Cylinder", "Clash: Artifacts of Chaos", "Tormented Souls", "Omen of Sorrow", 
    "Causa, Voices of the Dusk", "What Lies in the Multiverse", "The Signifier", "Cyber Ops", "Defenders of Ekron", 
    "Long Gone Days", "The Horror Of Salazar House", "The Rangers In The South", "Urbek City Builder"
]

def sniff_id(g_name):
    try:
        url = "https://store.steampowered.com/search/"
        p = {'term': g_name, 'category1': 998, 'l': 'spanish'}
        c = {'birthtime': '568022401', 'lastagecheckage': '1-0-1988'} # bypass age gate
        
        r = requests.get(url, params=p, cookies=c)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        for res in soup.select('a.search_result_row'):
            tit = res.select_one('.title').text.strip()
            appid = res.get('data-ds-appid')
            
            # loose check
            t1, t2 = set(re.findall(r'\w+', g_name.lower())), set(re.findall(r'\w+', tit.lower()))
            if not t1.intersection(t2) and (g_name.lower() not in tit.lower() and tit.lower() not in g_name.lower()):
                continue

            if appid:
                log.info(f"Got {g_name} -> {appid}")
                return appid
    except: pass
    log.warning(f"Missed: {g_name}")
    return None

def pull_data(a_id):
    try:
        req = requests.get(f"http://store.steampowered.com/api/appdetails?appids={a_id}&l=spanish")
        if req.status_code == 200:
            d = req.json()
            if d.get(str(a_id), {}).get('success'): return d[str(a_id)]['data']
    except Exception as e: log.error(f"Failed pulling {a_id}: {e}")
    return None

def run():
    out_dir = Path("data/raw")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    seen = {p.stem for p in out_dir.glob("*.json")}
    log.info(f"Batch tracking {len(GAME_NAMES)} titles")
    
    for n in GAME_NAMES:
        a_id = sniff_id(n)
        if a_id:
            a_id = a_id.split(',')[0] if ',' in a_id else a_id
            if a_id in seen: continue
                
            game_d = pull_data(a_id)
            if game_d:
                with open(out_dir / f"{a_id}.json", "w", encoding="utf-8") as f:
                    json.dump(game_d, f, indent=2, ensure_ascii=False)
                seen.add(str(a_id))
            time.sleep(1) # throttle
        time.sleep(0.5)

if __name__ == "__main__": run()
