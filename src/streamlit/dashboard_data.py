import pandas as pd
import streamlit as st

@st.cache_data
def cargar_datos_historicos():
    # levanta los datos raw y pisa tipos
    df = pd.read_csv("data/raw/streamlit_data.csv")
    df['release_date'] = pd.to_datetime(df['release_date'])
    df['year'] = df['release_date'].dt.year
    return df

@st.cache_data
def calcular_kpis_globales(df):
    return {"n_juegos": len(df), "total_revenue": df["revenue_est"].sum(), "avg_score": df["score"].mean()}
