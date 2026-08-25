import csv
import os

NON_CHILEAN = [
    "Microsoft Flight Simulator (2020) 40th Anniversary Edition",
    "Door Kickers 2: Task Force North",
    "The Rise of the Golden Idol",
    "MENACE",
]

BASE = r"C:\Users\Alvaro\github-limpio\chilean-videogames-analysis\data"

FILES = [
    os.path.join(BASE, "processed", "games.csv"),
    os.path.join(BASE, "export", "chilean_games_final.csv"),
    os.path.join(BASE, "export", "chilean_games_metrics.csv"),
    os.path.join(BASE, "export", "dw_quadrant_rentabilidad.csv"),
    os.path.join(BASE, "export", "flourish_treemap_genero.csv"),
    os.path.join(BASE, "export", "observable_distribucion.csv"),
]

for filepath in FILES:
    if not os.path.exists(filepath):
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
        f"OK: {os.path.basename(filepath)}: {original_count} -> {len(cleaned)} (-{removed})"
    )

print("\nDone!")
