import pandas as pd
import numpy as np
import random
import os

def generar_datos_base():
    np.random.seed(42)
    random.seed(42)

    titles = [f"Juego {i}" for i in range(1, 251)]
    genres = random.choices(["Acción", "Aventura", "RPG", "Estrategia", "Puzzles", "Terror", "Simulación", "Plataformas"], k=250)
    platforms_list = [["PC"], ["PC", "Consola"], ["Móvil"], ["PC", "Móvil"], ["PC", "Consola", "Móvil"]]
    
    data = []
    for i in range(250):
        genre = genres[i]
        # Precios base según género
        if genre in ["RPG", "Estrategia"]:
            base_price = np.random.normal(19.99, 5)
        elif genre in ["Móvil", "Puzzles"]:
            base_price = np.random.normal(4.99, 2)
        else:
            base_price = np.random.normal(12.99, 4)
            
        base_price = max(0.0, min(base_price, 39.99)) # Limitar precio
        
        platforms = random.choice(platforms_list)
        if "Móvil" in platforms and len(platforms) == 1:
             is_f2p = random.random() < 0.7
        else:
             is_f2p = random.random() < 0.15

        price = 0.0 if is_f2p else round(base_price, 2)
        
        # Unidades vendidas
        vol_base = np.random.lognormal(mean=8, sigma=1.5) if is_f2p else np.random.lognormal(mean=7, sigma=1.2)
        units = int(vol_base)
        
        score = np.clip(np.random.normal(70, 15), 10, 100)
        sentiment = np.clip(np.random.normal(0.2, 0.4), -1.0, 1.0)
        
        # Ajustar revenue por modelo Boxleiter (simplificado)
        if is_f2p:
           revenue = units * np.random.uniform(0.1, 1.5) # ARPU muy básico
        else:
           revenue = units * price * 0.7 # Asumiendo corte de plataforma comercial del 30%
           
        release_date = pd.to_datetime(f"{random.randint(2018, 2024)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}")

        data.append({
            "title": titles[i],
            "genre": genre,
            "platforms": ", ".join(platforms),
            "is_f2p": is_f2p,
            "price": price,
            "units_sold": units,
            "revenue_est": round(revenue, 2),
            "score": round(score, 1),
            "sentiment": round(sentiment, 2),
            "release_date": release_date
        })

    df = pd.DataFrame(data)
    os.makedirs("data/raw", exist_ok=True)
    df.to_csv("data/raw/streamlit_data.csv", index=False)
    print("✅ Datos extraídos y guardados en data/raw/streamlit_data.csv")

if __name__ == "__main__":
    generar_datos_base()
