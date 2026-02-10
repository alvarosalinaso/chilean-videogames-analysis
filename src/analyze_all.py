import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from utils import setup_logger, normalize_currency_to_usd, extract_year

logger = setup_logger("analysis")

def load_and_enrich_data():
    """Carga data limpia y añade columnas calculadas (estimaciones)."""
    input_path = Path("data/processed/games.csv")
    if not input_path.exists():
        logger.error("No se encontró data/processed/games.csv")
        return None
        
    df = pd.read_csv(input_path)
    
    # --- Enriquecimiento ---
    # 1. Normalizar Year
    df['year'] = df['year'].astype(str).apply(extract_year)
    
    # 2. Revenue Estimado (Steam)
    BOXLEITER_FACTOR = 40
    df['estimated_copies'] = df.apply(
        lambda x: int(x['recommendations'] * BOXLEITER_FACTOR) if x['source'] == 'steam' and x['recommendations'] > 0 else 0,
        axis=1
    )
    
    # 3. Precio USD Estimado
    df['price_usd'] = df.apply(lambda x: normalize_currency_to_usd(x['price'], x['currency']), axis=1)
    
    # 4. Gross Revenue
    df['gross_revenue_est_usd'] = df['estimated_copies'] * df['price_usd']
    
    # 5. Género Principal
    df['primary_genre'] = df['genres'].apply(
        lambda x: x.split(',')[0].strip() if pd.notna(x) and x != '' else 'Unknown'
    )

    return df

def plot_timeline(df, output_dir):
    """Lanzamientos por año."""
    df_chart = df[df['year'].str.match(r'^\d{4}$', na=False)].copy()
    df_chart['year'] = df_chart['year'].astype(int)
    df_chart = df_chart[df_chart['year'] >= 2010]
    
    plt.figure(figsize=(12, 6))
    sns.countplot(data=df_chart, x='year', hue='source')
    plt.title('Evolución de Lanzamientos: Steam vs Itch.io')
    plt.ylabel('Cantidad')
    plt.xlabel('Año')
    plt.xticks(rotation=45)
    plt.legend(title='Plataforma')
    plt.tight_layout()
    plt.savefig(output_dir / '1_timeline_releases.png')
    plt.close()
    logger.info("Plot generado: Timeline")

def plot_price_dist(df, output_dir):
    """Distribución de precios."""
    plt.figure(figsize=(10, 6))
    df_prices = df[df['price_usd'] <= 50] # Filtro visual
    
    sns.histplot(data=df_prices, x='price_usd', hue='source', multiple="stack", bins=20)
    plt.title('Distribución de Precios (USD Estimado)')
    plt.xlabel('Precio USD')
    plt.axvline(x=0, color='red', linestyle='--', label='Gratis')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / '2_price_distribution.png')
    plt.close()
    logger.info("Plot generado: Precios")

def plot_top_revenue(df, output_dir):
    """Top 10 ingresos."""
    df_top = df.sort_values('gross_revenue_est_usd', ascending=False).head(10)
    
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df_top, y='name', x='gross_revenue_est_usd', hue='name', palette='magma', legend=False)
    plt.title('Top 10 Revenue Estimado (Steam)')
    plt.xlabel('USD (Bruto)')
    plt.ylabel('')
    
    # Format K/M
    ax = plt.gca()
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M' if x >= 1e6 else f'${x/1e3:.0f}K'))
    
    plt.tight_layout()
    plt.savefig(output_dir / '3_top_revenue.png')
    plt.close()
    logger.info("Plot generado: Top Revenue")

def plot_revenue_by_genre(df, output_dir):
    """Revenue por Género."""
    top_genres = df['primary_genre'].value_counts().nlargest(8).index
    df_chart = df[df['primary_genre'].isin(top_genres) & (df['gross_revenue_est_usd'] > 0)]
    
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df_chart, x='primary_genre', y='gross_revenue_est_usd', hue='primary_genre', palette='Set2')
    plt.yscale('log')
    plt.title('Ingresos por Género Principal (Log Scale)')
    plt.xlabel('Género')
    plt.ylabel('Revenue USD')
    plt.tight_layout()
    plt.savefig(output_dir / '4_revenue_genre.png')
    plt.close()
    logger.info("Plot generado: Revenue por Género")

def main():
    figs_dir = Path("assets/figures_v2")
    figs_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Cargando y enriqueciendo datos...")
    df = load_and_enrich_data()
    
    if df is not None:
        plot_timeline(df, figs_dir)
        plot_price_dist(df, figs_dir)
        plot_top_revenue(df, figs_dir)
        plot_revenue_by_genre(df, figs_dir)
        
        # Guardar dataset enriquecido final
        out_csv = Path("data/export/chilean_games_final.csv")
        out_csv.parent.mkdir(exist_ok=True, parents=True)
        df.to_csv(out_csv, index=False, encoding='utf-8-sig')
        logger.info(f"Dataset final exportado a: {out_csv}")
        
if __name__ == "__main__":
    main()
