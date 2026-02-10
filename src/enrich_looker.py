import pandas as pd
from pathlib import Path
import numpy as np

# Mapeo manual de Estudios -> Ciudad
# Basado en conocimiento general de la industria chilena
STUDIO_LOCATIONS = {
    "ACE Team": "Santiago",
    "AOne Games": "Santiago",
    "IguanaBee": "Santiago",
    "Dual Effect": "Santiago",
    "Octeto Studios": "Santiago",
    "Abstract Digital": "Santiago",
    "Time Hunters": "Santiago",
    "Nidal Games": "Santiago",
    "Gamaga": "Santiago",
    "Behavior Santiago": "Santiago",
    "Wanako Games": "Santiago",
    "Playmestudio": "Valparaíso",
    "Giant Monkey Robot": "Santiago",
    "Bitplay": "Santiago",
    "Glitchy Pixel": "Santiago",
    "Invader Studios": "Santiago", # check
    "Movistar GameClub": "Santiago",
    "Micropsia Games": "Santiago",
    "Unknown": "Unknown"
}

def get_location(developers):
    if pd.isna(developers):
        return "Chile (General)"
    
    # Buscar si alguno de los devs está en nuestra lista
    for dev in developers.split(','):
        dev = dev.strip()
        # Búsqueda parcial
        for studio, city in STUDIO_LOCATIONS.items():
            if studio.lower() in dev.lower():
                return city
    
    return "Chile (General)"

def main():
    input_path = Path("data/processed/games.csv")
    output_dir = Path("data/export")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Cargando datos procesados...")
    df = pd.read_csv(input_path)
    
    # 1. Estimación de Ventas (Boxleiter Method)
    # Factor típico indie: 30x - 50x reviews. Usaremos 40x promedio.
    BOXLEITER_FACTOR = 40
    
    # Solo aplicable a Steam (Itch no muestra counts fiables de reviews en grid)
    # En Itch 'recommendations' es diferente, pero usaremos la misma col base
    df['estimated_copies'] = df.apply(
        lambda x: int(x['recommendations'] * BOXLEITER_FACTOR) if x['source'] == 'steam' and x['recommendations'] > 0 else 0,
        axis=1
    )
    
    # 2. Estimación de Revenue Bruto (Gross Revenue)
    # Precio * Copias. Muy rústico (ignora sales, regional pricing, steam cut).
    # Normalizar precio a CLP para Looker (o USD). Usaremos USD estimado.
    def get_price_usd(row):
        if row['is_free']: return 0.0
        if row['currency'] == 'CLP':
            return row['price'] / 950.0 # Tasa aprox
        return row['price']

    df['price_usd_est'] = df.apply(get_price_usd, axis=1)
    df['gross_revenue_est_usd'] = df['estimated_copies'] * df['price_usd_est']
    
    # 3. Mapeo de Ubicación
    df['dev_location'] = df['developers'].apply(get_location)
    
    # 4. Enriquecimiento de Géneros (Primary Genre)
    # Tomar el primero de la lista como "Principal" para simplificar gráficos de torta
    df['primary_genre'] = df['genres'].apply(
        lambda x: x.split(',')[0].strip() if pd.notna(x) and x != '' else 'Unknown'
    )
    
    # 5. Rangos de Fecha
    # Convertir year a fecha real (1 de Enero) para timeline en Looker si hace falta
    # O mantener year como dimensión
    
    # Guardar
    output_file = output_dir / "chilean_games_metrics.csv"
    df.to_csv(output_file, index=False, encoding='utf-8-sig') # sig para excel
    
    print(f"Exportación completada en: {output_file}")
    print(f"Total Revenue Estimado (Muestra): ${df['gross_revenue_est_usd'].sum():,.0f} USD")
    print("Top Locations:")
    print(df['dev_location'].value_counts())

if __name__ == "__main__":
    main()
