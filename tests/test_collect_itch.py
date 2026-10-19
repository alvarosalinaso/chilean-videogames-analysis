"""Tests for collect_itch module (chilean-videogames-analysis)."""

from pathlib import Path

import pandas as pd
import pytest
from bs4 import BeautifulSoup

from chilean_videogames.collect_itch import DEFAULT_PRICE_TEXT, PRICE_SELECTOR, extract_price_text

REPO = Path(__file__).resolve().parents[1]
PROCESSED_CSV = REPO / "data" / "processed" / "games.csv"

# Markup real de itch.io para un juego pago en /games/store/tag-chile
PAID_CELL_HTML = """
<div class="game_cell has_cover lazy_images" data-game_id="4536578" dir="auto">
  <div class="game_cell_data">
    <div class="game_title">
      <a class="title game_link" href="https://profefreddy.itch.io/gincananexus">GincanaNexus</a>
      <div class="price_tag meta_tag" title="Pay $2.90 or more for this game">
        <div class="price_value">$2.90</div>
      </div>
    </div>
    <div class="game_text" title="Juego educativo">Juego educativo</div>
    <div class="game_author"><a href="https://profefreddy.itch.io">ProfeFreddy</a></div>
  </div>
</div>
"""

# Markup real del listado general (tag-chile): sin precio
FREE_CELL_HTML = """
<div class="game_cell has_cover lazy_images" data-game_id="519410" dir="auto">
  <div class="game_cell_data">
    <div class="game_title">
      <a class="title game_link" href="https://merge-branch-games.itch.io/dreamnesthesia">Dreamnesthesia</a>
    </div>
    <div class="game_text" title="A tactical RPG game">A tactical RPG game</div>
    <div class="game_author"><a href="https://merge-branch-games.itch.io">Merge Branch Games</a></div>
  </div>
</div>
"""


def test_price_selector_matches_itch_paid_markup():
    """El selector de precio coincide con el markup real de itch.io."""
    cell = BeautifulSoup(PAID_CELL_HTML, "html.parser").select_one(".game_cell")
    price_elem = cell.select_one(PRICE_SELECTOR)
    assert price_elem is not None, "PRICE_SELECTOR no coincide con el markup pagado"
    assert price_elem.get_text(strip=True) == "$2.90"
    assert extract_price_text(cell, {}) == "$2.90"


def test_price_selector_falls_back_to_paid_map_then_default():
    """Sin precio en la celda se usa el listado pagado y si no, Free/NYP."""
    cell = BeautifulSoup(FREE_CELL_HTML, "html.parser").select_one(".game_cell")
    assert cell.select_one(PRICE_SELECTOR) is None
    assert extract_price_text(cell, {"519410": "$1.00"}) == "$1.00"
    assert extract_price_text(cell, {}) == DEFAULT_PRICE_TEXT == "Free/NYP"


@pytest.mark.skipif(not PROCESSED_CSV.exists(), reason="games.csv no encontrado")
def test_itch_prices_include_positive_values():
    """Tras el re-scrape al menos un juego de itch.io tiene precio > 0."""
    df = pd.read_csv(PROCESSED_CSV)
    itch = df[df["source"].astype(str).str.casefold().str.strip() == "itch"]
    assert len(itch) > 0, "no hay juegos itch en el dataset"
    paid = itch[itch["price"].astype(float) > 0]
    assert len(paid) >= 1, "ningún precio de itch.io es > 0 (selector de precio roto)"
