# Chilean Video Games Market Analysis

[![CI](https://github.com/alvarosalinaso/chilean-videogames-analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/alvarosalinaso/chilean-videogames-analysis/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)

---

## What is this?

EN: There's no structured data about the Chilean indie game market. I scraped Steam and Itch.io to build a dataset of 150 Chilean games, then analyzed pricing, genres, revenue estimates, and platform differences.

ES: No hay datos estructurados sobre el mercado indie de videojuegos chilenos. Hice scraping de Steam e Itch.io para construir un dataset de 150 juegos chilenos, y analicé precios, géneros, estimaciones de revenue y diferencias por plataforma.

---

## Dataset

- **150 games** (84 Steam, 66 Itch.io)
- **Period:** 2009–2025
- **Genres:** 20 categories
- **Data sources:** Steam API + Itch.io scraping

---

## Questions I asked

| ID | Question |
|----|----------|
| RQ1 | How have releases evolved by year and platform? |
| RQ2 | How do price distributions differ between Steam and Itch.io? |
| RQ3 | Which genres generate the most estimated revenue? |
| RQ4 | How concentrated is the market by genre (HHI)? |
| RQ5 | Is there a correlation between recommendations and revenue? |

---

## How it works

### 1. Data collection

- **Steam:** `src/collect.py` — API `appdetails` + BeautifulSoup
- **Itch.io:** `src/collect_itch.py` — HTML scraping with pagination

### 2. Cleaning

- Deduplication by (name, source)
- USD normalization (fixed rates)
- Year extraction from heterogeneous dates

### 3. Analysis

- ARIMA revenue forecasting (2026–2028)
- K-Means clustering of genres with cross-validation
- A/B testing Steam vs Itch.io (Cohen's d, power analysis)
- HHI concentration index by genre

---

## Key findings

| Finding | Value |
|---------|-------|
| Total games | 150 (84 Steam, 66 Itch.io) |
| Dominant genre | Acción (35 games) |
| Steam median price | ~$4 USD |
| Itch.io | Mostly free/pay-what-you-want |
| Market concentration | Low (HHI < 1500) |

---

## Visualizations

<details>
<summary><strong>Datawrapper — Revenue quadrant</strong></summary>

<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;max-width:100%;">
  <iframe src="https://datawrapper.dwcdn.net/MBqIQ/" title="Revenue Quadrant" style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" loading="lazy" allowfullscreen></iframe>
</div>
</details>

---

## How to run

```bash
git clone https://github.com/alvarosalinaso/chilean-videogames-analysis
cd chilean-videogames-analysis
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python src/collect.py
python src/collect_itch.py
python src/clean.py
python src/analyze_all.py
```

---

## Limitations

- Revenue estimates use the BoxLeiter 40x multiplier (approximate)
- 35% of titles have no recommendation data
- Survival bias: only games still on the platform are included
- Itch.io revenue data is mostly self-reported

---

> **Álvaro Salinas Ortiz**
> [LinkedIn](https://www.linkedin.com/in/alvaro-salinas-ortiz) | [Portfolio](https://alvarosalinaso.github.io/portfolio-web/)
