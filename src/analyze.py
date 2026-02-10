import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def main():
    # sns.set_theme(style="whitegrid")
    data_path = Path("data/processed/games.csv")
    if not data_path.exists():
        print("No se encontró games.csv.")
        return

    print("Cargando CSV...")
    df = pd.read_csv(data_path)
    print("CSV Cargado.")
    figs_dir = Path("assets/figures")
    figs_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Dataset cargado: {len(df)} juegos total.")
    print(df['source'].value_counts())
    
    # Asegurar que year es string
    df['year'] = df['year'].astype(str)

    # 1. Timeline Comparativo (Steam vs Itch) - Solo años válidos
    df_timeline = df[df['year'].str.match(r'^\d{4}$', na=False)].copy()
    df_timeline['year'] = df_timeline['year'].astype(int)
    df_timeline = df_timeline[df_timeline['year'] >= 2010] # Enfocar en era moderna
    
    print("info timeline:")
    print(df_timeline.info())
    print(df_timeline.head())

    print("Generando Gráfico 1: Timeline...")
    plt.figure(figsize=(12, 6))
    if not df_timeline.empty:
        # sns.countplot(data=df_timeline, x='year', hue='source')
        # Fallback manual plot to debug
        counts = df_timeline.groupby(['year', 'source']).size().unstack(fill_value=0)
        counts.plot(kind='bar', stacked=True, figsize=(12,6))
        
        plt.title('Lanzamientos de Videojuegos Chilenos: Steam vs Itch.io')
        plt.xticks(rotation=45)
        plt.ylabel('Cantidad')
        plt.xlabel('Año')
        plt.legend(title='Plataforma')
        plt.tight_layout()
        plt.savefig(figs_dir / 'timeline_steam_vs_itch.png')
        plt.close()
        print("Gráfico 1 generado.")
    else:
        print("No hay datos suficientes para Timeline.")

    # 2. Distribución de Precios (Normalizada a USD aprox para visualización)
    # Steam está en CLP (mayoria), Itch en USD.
    # Conversión rústica: 1000 CLP ~= 1 USD
    def normalize_price(row):
        if row['price'] == 0: return 0
        if row['currency'] == 'CLP': return row['price'] / 950
        return row['price']
        
    df['price_usd'] = df.apply(normalize_price, axis=1)
    
    print("Generando Gráfico 2: Precios...")
    plt.figure(figsize=(10, 6))
    # Filtrar outliers (precios > $50 USD son raros en indies)
    df_prices = df[df['price_usd'] <= 50]
    if not df_prices.empty:
        # Simplificado: sin element="step", sin bins complejos
        sns.histplot(data=df_prices, x='price_usd', hue='source', multiple="stack")
        plt.title('Distribución de Precios (Estimado USD)')
        plt.xlabel('Precio (USD)')
        plt.axvline(x=0, color='red', linestyle='--', label='Gratis')
        plt.legend()
        plt.tight_layout()
        plt.savefig(figs_dir / 'precios_distribucion.png')
        plt.close()
        print("Gráfico 2 generado.")
    else:
        print("No hay datos de precios.")
    
    # 3. Top Tags/Géneros (Nube de palabras simple)
    # Steam tiene 'genres', Itch tiene 'genres' (uno solo usualmente)
    all_genres = []
    for genres in df['genres'].dropna():
        # Split por coma y limpiar
        parts = [g.strip() for g in genres.split(',')]
        all_genres.extend(parts)
        
    genre_counts = pd.Series(all_genres).value_counts().head(10)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x=genre_counts.values, y=genre_counts.index, palette='rocket')
    plt.title('Top 10 Géneros/Etiquetas en la Industria Chilena')
    plt.xlabel('Frecuencia')
    plt.tight_layout()
    plt.savefig(figs_dir / 'top_generos.png')
    plt.close()

    print("Gráficos generados en assets/figures.")

if __name__ == "__main__":
    main()
