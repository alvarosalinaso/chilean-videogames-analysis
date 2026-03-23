import pandas as pd
import numpy as np

def map_real_data():
    df_real = pd.read_csv("data/export/chilean_games_final.csv")
    
    # Filtrar anomalías detectadas del scraping inicial original
    anomalias = ["Microsoft Flight Simulator", "Door Kickers 2", "MENACE", "The Rise of the Golden Idol"]
    mask = df_real['name'].str.contains('|'.join(anomalias), na=False)
    df_real = df_real[~mask]
    
    df_stm = pd.DataFrame()
    df_stm['title'] = df_real['name']
    df_stm['genre'] = df_real['primary_genre']
    df_stm['platforms'] = df_real['source'].apply(lambda x: "PC" if x == "steam" else "Web/PC")
    df_stm['is_f2p'] = df_real['is_free']
    df_stm['price'] = df_real['price_usd']
    df_stm['units_sold'] = df_real['estimated_copies']
    df_stm['revenue_est'] = df_real['gross_revenue_est_usd']
    
    # Metacritic score has NaNs, fill with simulated or default
    np.random.seed(42)
    simulated_scores = np.random.normal(70, 15, len(df_real))
    df_stm['score'] = df_real['metacritic'].fillna(pd.Series(simulated_scores)).clip(10, 100).round(1)
    
    # Sentiment is completely simulated since we don't have review text
    df_stm['sentiment'] = np.clip(np.random.normal(0.2, 0.4, len(df_real)), -1.0, 1.0).round(2)
    
    # Release Date
    # Parse what can be parsed, else fake a date
    df_stm['release_date'] = pd.to_datetime(df_real['release_date'], errors='coerce')
    df_stm['release_date'] = df_stm['release_date'].fillna(pd.to_datetime('2021-06-15'))
    
    # year
    df_stm['year'] = pd.to_numeric(df_real['year'], errors='coerce').fillna(2021).astype(int)
    
    df_stm.to_csv("data/raw/streamlit_data.csv", index=False)
    print("✅ Datos reales exportados a streamlit_data.csv con éxito!")

if __name__ == "__main__":
    map_real_data()
