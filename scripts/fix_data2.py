import csv
import os

NON_CHILEAN = [
    "Microsoft Flight Simulator (2020) 40th Anniversary Edition",
    "Door Kickers 2: Task Force North",
    "The Rise of the Golden Idol",
    "MENACE",
]

BASE = r"C:\Users\Alvaro\github-limpio\chilean-videogames-analysis\data\export"

# flourish_treemap has "Game" column
filepath = os.path.join(BASE, "flourish_treemap_genero.csv")
with open(filepath, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = [row for row in reader]

original = len(rows)
cleaned = [row for row in rows if row.get("Game", "") not in NON_CHILEAN]
removed = original - len(cleaned)

with open(filepath, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(cleaned)

print(f"flourish_treemap: {original} -> {len(cleaned)} (-{removed})")

# observable_distribucion - check if it has game names
filepath2 = os.path.join(BASE, "observable_distribucion.csv")
with open(filepath2, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = [row for row in reader]

# Check if any row has a non-Chilean game name
cleaned2 = [
    row for row in rows if row.get("name", row.get("Name", "")) not in NON_CHILEAN
]
if len(cleaned2) != len(rows):
    with open(filepath2, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned2)
    print(
        f"observable_distribucion: {len(rows)} -> {len(cleaned2)} (-{len(rows) - len(cleaned2)})"
    )
else:
    print(f"observable_distribucion: no changes needed ({len(rows)} rows)")

print("\nDone!")
