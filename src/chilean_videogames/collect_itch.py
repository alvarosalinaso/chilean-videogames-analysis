"""Scraping del tag chile en itch.io.

El listado general (``/games/tag-chile``) NO incluye precios en su HTML: el
markup ``.game_text`` contiene la descripción del juego, no el precio. Los
precios solo aparecen en el listado pagado (``/games/store/tag-chile``) dentro de
``.price_tag > .price_value`` (un ``div``, no un ``a``). Por eso se consultan
ambos listados y se cruzan los precios por ``data-game_id``.
"""

import json
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from .utils import setup_logger

logger = setup_logger("collect_itch")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; chilean-videogames-analysis/0.1; "
        "+https://github.com/alvarosalinaso/chilean-videogames-analysis)"
    )
}
TAG_URL = "https://itch.io/games/tag-chile"
PAID_URL = "https://itch.io/games/store/tag-chile"
# El precio vive en .price_tag > .price_value dentro de .game_title
PRICE_SELECTOR = ".price_tag .price_value"
DEFAULT_PRICE_TEXT = "Free/NYP"
PAGE_DELAY_S = 1.5


def _fetch_soup(url: str) -> BeautifulSoup | None:
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
    except requests.RequestException as exc:
        logger.error(f"Error en {url}: {exc}")
        return None
    if response.status_code != 200:
        logger.warning(f"Status {response.status_code} en {url}")
        return None
    return BeautifulSoup(response.text, "html.parser")


def _iter_pages(base_url: str, page_delay: float = PAGE_DELAY_S):
    """Genera la lista de .game_cell por página, con pausa entre requests."""
    page = 1
    while True:
        logger.info(f"Procesando página {page}: {base_url}")
        soup = _fetch_soup(f"{base_url}?page={page}")
        if soup is None:
            return
        cells = soup.select(".game_cell")
        if not cells:
            logger.info("No se encontraron más juegos en esta página.")
            return
        yield cells
        page += 1
        time.sleep(page_delay)


def fetch_paid_prices(page_delay: float = PAGE_DELAY_S) -> dict[str, str]:
    """Precios del listado pagado: {data-game_id: texto de precio}."""
    prices: dict[str, str] = {}
    for cells in _iter_pages(PAID_URL, page_delay):
        for cell in cells:
            game_id = cell.get("data-game_id")
            price_elem = cell.select_one(PRICE_SELECTOR)
            if game_id and price_elem:
                prices[game_id] = price_elem.get_text(strip=True)
    logger.info(f"Juegos con precio en el listado pagado: {len(prices)}")
    return prices


def extract_price_text(cell: BeautifulSoup, paid_prices: dict[str, str]) -> str:
    """Precio de una celda: el del listado, el pagado o el predeterminado."""
    price_elem = cell.select_one(PRICE_SELECTOR)
    if price_elem:
        return price_elem.get_text(strip=True)
    game_id = cell.get("data-game_id")
    if game_id and game_id in paid_prices:
        return paid_prices[game_id]
    return DEFAULT_PRICE_TEXT


def fetch_itch_games(
    raw_dir: Path = Path("data/raw"), page_delay: float = PAGE_DELAY_S
) -> list[dict]:
    raw_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Obteniendo precios del listado pagado de Itch.io...")
    paid_prices = fetch_paid_prices(page_delay)

    games_found: list[dict] = []
    logger.info("Iniciando scraping de Itch.io (tag: chile)...")

    for cells in _iter_pages(TAG_URL, page_delay):
        for cell in cells:
            title_elem = cell.select_one(".game_title a")
            if not title_elem:
                continue

            title = title_elem.text.strip()
            link = title_elem["href"]
            game_id = cell.get("data-game_id")

            author = "Unknown"
            author_elem = cell.select_one(".game_author a")
            if author_elem:
                author = author_elem.text.strip()

            genre = "Unknown"
            genre_elem = cell.select_one(".game_genre")
            if genre_elem:
                genre = genre_elem.text.strip()

            game_data = {
                "source": "itch",
                "id": game_id,
                "name": title,
                "url": link,
                "author": author,
                "genre": genre,
                "price_text": extract_price_text(cell, paid_prices),
                "year": "Unknown",
            }

            out_file = raw_dir / f"itch_{game_id}.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(game_data, f, indent=4, ensure_ascii=False)

            games_found.append(game_data)

    paid_count = sum(1 for g in games_found if g["price_text"] != DEFAULT_PRICE_TEXT)
    logger.info(
        f"Finalizado. {len(games_found)} juegos de Itch.io guardados ({paid_count} con precio > 0)."
    )
    return games_found


if __name__ == "__main__":
    fetch_itch_games()
