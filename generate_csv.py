import pandas as pd, numpy as np, random, os

def dump_mock_data():
    np.random.seed(42); random.seed(42)
    t = [f"Juego {i}" for i in range(1, 251)]
    g = random.choices(["Acción", "Aventura", "RPG", "Estrategia", "Puzzles", "Terror", "Simulación", "Plataformas"], k=250)
    p_opts = [["PC"], ["PC", "Consola"], ["Móvil"], ["PC", "Móvil"], ["PC", "Consola", "Móvil"]]
    
    rows = []
    for i in range(250):
        gen = g[i]
        
        # pricing bruto adaptado
        base_p = np.random.normal(19.99, 5) if gen in ["RPG", "Estrategia"] else (np.random.normal(4.99, 2) if gen in ["Móvil", "Puzzles"] else np.random.normal(12.99, 4))
        base_p = max(0.0, min(base_p, 39.99))
        
        plats = random.choice(p_opts)
        is_free = (random.random() < 0.7) if ("Móvil" in plats and len(plats)==1) else (random.random() < 0.15)
        price = 0.0 if is_free else round(base_p, 2)
        
        v_base = np.random.lognormal(mean=8, sigma=1.5) if is_free else np.random.lognormal(mean=7, sigma=1.2)
        u = int(v_base)
        
        sc = np.clip(np.random.normal(70, 15), 10, 100)
        sent = np.clip(np.random.normal(0.2, 0.4), -1.0, 1.0)
        
        rev = (u * np.random.uniform(0.1, 1.5)) if is_free else (u * price * 0.7)
        r_date = pd.to_datetime(f"{random.randint(2018, 2024)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}")

        rows.append({
            "title": t[i], "genre": gen, "platforms": ", ".join(plats),
            "is_f2p": is_free, "price": price, "units_sold": u,
            "revenue_est": round(rev, 2), "score": round(sc, 1),
            "sentiment": round(sent, 2), "release_date": r_date
        })

    os.makedirs("data/raw", exist_ok=True)
    pd.DataFrame(rows).to_csv("data/raw/streamlit_data.csv", index=False)
    print("dumped data/raw/streamlit_data.csv")

if __name__ == "__main__": dump_mock_data()
