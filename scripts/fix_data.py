import csv
import os
from pathlib import Path

NON_CHILEAN = [
    "Microsoft Flight Simulator (2020) 40th Anniversary Edition",
    "Door Kickers 2: Task Force North",
    "The Rise of the Golden Idol",
    "MENACE",
]

BASE = Path(__file__).parent.parent / "data"

FILES = [
    BASE / "processed" / "games.csv",
    BASE / "export" / "chilean_games_final.csv",
    BASE / "export" / "chilean_games_metrics.csv",
    BASE / "export" / "dw_quadrant_rentabilidad.csv",
    BASE / "export" / "flourish_treemap_genero.csv",
    BASE / "export" / "observable_distribucion.csv",
]

for filepath in FILES:
    if not filepath.exists():
        print(f"SKIP (not found): {filepath}")
        continue

    with open(filepath, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = [row for row in reader]

    original_count = len(rows)
    cleaned = [row for row in rows if row.get("name", "") not in NON_CHILEAN]
    removed = original_count - len(cleaned)

    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned)

    print(
        f"OK: {filepath.name}: {original_count} -> {len(cleaned)} (-{removed})"
    )

print("\nDone!")
