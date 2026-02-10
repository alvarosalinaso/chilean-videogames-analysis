import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def main():
    # Load enriched data
    input_path = Path("data/export/chilean_games_metrics.csv")
    if not input_path.exists():
        print("Error: No se encontró el dataset enriquecido.")
        return

    df = pd.read_csv(input_path)
    figs_dir = Path("assets/figures")
    figs_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generando gráficos avanzados para {len(df)} juegos...")

    # 1. Top 10 Juegos por Revenue Estimado
    # Filtrar revenue > 0
    df_rev = df[df['gross_revenue_est_usd'] > 0].sort_values('gross_revenue_est_usd', ascending=False).head(10)
    
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df_rev, y='name', x='gross_revenue_est_usd', hue='name', palette='magma', legend=False)
    plt.title('Top 10 Videojuegos Chilenos por Ingresos Estimados (Steam)')
    plt.xlabel('Ingresos Brutos Estimados (USD)')
    plt.ylabel('Juego')
    # Formatear eje X a millones/miles
    current_values = plt.gca().get_xticks()
    plt.gca().set_xticklabels(['${:,.0f}'.format(x) for x in current_values])
    plt.tight_layout()
    plt.savefig(figs_dir / 'top_revenue_games.png')
    plt.close()

    # 2. Distribución de Desarrolladores por Ubicación
    # Contar estudios únicos (approx) o juegos por ciudad? Juegos por ciudad es más directo con este dataset.
    loc_counts = df['dev_location'].value_counts()
    
    plt.figure(figsize=(8, 6))
    sns.barplot(x=loc_counts.values, y=loc_counts.index, hue=loc_counts.index, palette='viridis', legend=False)
    plt.title('Concentración de Desarrollo de Videojuegos en Chile')
    plt.xlabel('Cantidad de Títulos')
    plt.tight_layout()
    plt.savefig(figs_dir / 'dev_locations.png')
    plt.close()

    # 3. Revenue por Género Principal (Boxplot para ver distribución)
    # Filtrar géneros con pocos juegos para limpiar el gráfico
    top_genres = df['primary_genre'].value_counts().nlargest(8).index
    df_genre = df[df['primary_genre'].isin(top_genres) & (df['gross_revenue_est_usd'] > 0)]
    
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df_genre, x='primary_genre', y='gross_revenue_est_usd', hue='primary_genre', palette='Set2')
    plt.yscale('log') # Escala logarítmica porque hay mucha diferencia
    plt.title('Distribución de Ingresos por Género (Escala Log)')
    plt.xlabel('Género Principal')
    plt.ylabel('Ingresos Estimados (USD)')
    plt.tight_layout()
    plt.savefig(figs_dir / 'revenue_by_genre.png')
    plt.close()

    print("Gráficos generados en assets/figures/")

if __name__ == "__main__":
    main()
