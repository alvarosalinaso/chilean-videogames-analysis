import pandas as pd
import streamlit as st

from pathlib import Path
@st.cache_data
def cargar_datos_historicos():
    # levanta los datos raw y pisa tipos
    p = Path(__file__).parent.parent.parent / "data" / "raw" / "streamlit_data.csv"
    df = pd.read_csv(p)
    df['release_date'] = pd.to_datetime(df['release_date'])
    df['year'] = df['release_date'].dt.year
    return df

@st.cache_data
def calcular_kpis_globales(df):
    return {"n_juegos": len(df), "total_revenue": df["revenue_est"].sum(), "avg_score": df["score"].mean()}

@st.cache_data
def cargar_market_benchmark():
    p = Path(__file__).parent.parent.parent / "data" / "raw" / "market_benchmark.csv"
    return pd.read_csv(p)
