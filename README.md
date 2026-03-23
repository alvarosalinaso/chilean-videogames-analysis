# Videogames Analytics Chile 🇨🇱🎮

Datos duros sobre el mercado chileno de videojuegos (Steam + Itch.io). Cero humo corporativo.

## El Negocio Real

- La escena indie reventó post-2020. Itch.io es la zona de pruebas, Steam es donde se factura.
- Claves de Steam: Juegos de Acción y Estrategia acaparan el segmento $8-$10 USD.
- Top Revenues: *Rock of Ages*, *Tormented Souls*, *Zeno Clash*. El resto se pelea el long-tail, pero existe un nicho súper sólido de $50k-$200k facturados por estudios de 2-3 personas.

![Timeline](assets/figures_v2/1_timeline_releases.png)

## Estructura

```
chilean-videogames-analysis/
├── src/ # scrapers y transformers
├── data/
│   ├── raw/ # ignorado en repo
│   └── export/ # dataset final para BI
└── assets/figures_v2/
```

## Setup & Run

1. `pip install -r requirements.txt`
2. Baja los datos brutos: `python src/collect.py`
3. Mastica la data: `python src/analyze_all.py`
