import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

st.set_page_config(
    page_title="Chilean Videogames | Market Intel",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Exo+2:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'Exo 2', sans-serif; }
h1, h2, h3 { font-family: 'Orbitron', monospace; color: #00E5FF; letter-spacing: 2px; }
.metric-card {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
    border: 1px solid #1f2937;
    border-top: 2px solid #00E5FF;
    border-radius: 8px;
    padding: 1rem 1.2rem;
}
.metric-val { font-size: 1.8rem; font-weight: 700; color: #00E5FF; font-family: 'Orbitron', monospace; }
.metric-lab { font-size: 0.7rem; color: #6b7280; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ── DATOS ──────────────────────────────────────────────────────────────────────
np.random.seed(42)
N = 200

GENRES = ["RPG", "Action", "Platformer", "Puzzle", "Adventure", "Simulation", "Horror", "Shooter", "Strategy"]
GENRE_W = [0.18, 0.16, 0.15, 0.12, 0.12, 0.10, 0.07, 0.06, 0.04]
GENRE_REV = {"RPG": 32000, "Shooter": 26000, "Action": 20000, "Strategy": 18000,
              "Adventure": 14000, "Simulation": 13000, "Horror": 11000, "Platformer": 9000, "Puzzle": 6500}

BENCHMARK = {"Chile": 0, "Brasil": 18000, "Argentina": 14000, "Colombia": 11000,
             "Global (mediana)": 32000, "USA": 48000, "Europa": 40000}

data = []
for i in range(N):
    genre = np.random.choice(GENRES, p=GENRE_W)
    is_f2p = np.random.random() < 0.28
    base = GENRE_REV[genre]
    rev = max(200, np.random.lognormal(np.log(base * (1.3 if is_f2p else 1.0)), 0.85))
    score = np.clip(np.random.normal(72, 12), 30, 98)
    sentiment = np.clip(np.random.normal(0.72, 0.14), 0.1, 1.0)
    year = np.random.choice(range(2015, 2025), p=[0.03]*3 + [0.07]*3 + [0.12, 0.16, 0.20, 0.22])
    month = np.random.randint(1, 13)
    dev_cost = np.random.uniform(12000, 110000)
    data.append({
        "title": f"Juego_{i:03d}", "genre": genre, "is_f2p": is_f2p,
        "revenue_est": round(rev, 0), "score": round(score, 1),
        "sentiment": round(sentiment, 3), "year": year, "month": month,
        "dev_cost": round(dev_cost, 0), "is_success": int(rev > 10000),
        "tags": np.random.randint(3, 15), "reviews": int(rev / 8 + np.random.randint(0, 200))
    })

df = pd.DataFrame(data)

# Entrenar modelo RF una vez
le = LabelEncoder()
df["genre_enc"] = le.fit_transform(df["genre"])
X = df[["genre_enc", "is_f2p", "score", "sentiment", "year"]]
clf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
clf.fit(X, df["is_success"])
reg = RandomForestRegressor(n_estimators=100, random_state=42)
reg.fit(X, np.log1p(df["revenue_est"]))

# ── SIDEBAR ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎮 Filtros")
    st.markdown("---")

    vista = st.selectbox("Vista", [
        "Panorama de mercado", "Análisis por género",
        "Score vs Revenue", "Benchmark global", "Simulador ML"
    ])

    genres_sel = st.multiselect("Géneros", GENRES, default=GENRES)
    model_sel = st.radio("Modelo de negocio", ["Todos", "Solo Premium", "Solo F2P"])
    year_range = st.slider("Años", 2015, 2024, (2015, 2024))
    platform_cut = st.slider("Corte plataforma Steam %", 0, 40, 30)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem; color:#4b5563;'>
    Álvaro Salinas Ortiz<br>
    <a href='https://github.com/alvarosalinaso' style='color:#00E5FF;'>github.com/alvarosalinaso</a>
    </div>
    """, unsafe_allow_html=True)

# Aplicar filtros
df_f = df[df["genre"].isin(genres_sel) & df["year"].between(*year_range)].copy()
if model_sel == "Solo Premium":
    df_f = df_f[~df_f["is_f2p"]]
elif model_sel == "Solo F2P":
    df_f = df_f[df_f["is_f2p"]]
df_f["rev_net"] = df_f["revenue_est"] * (1 - platform_cut / 100)

# ── HEADER ──────────────────────────────────────────────────────────────────────
st.markdown("# CHILE GAME DEV")
st.markdown(f"### {vista.upper()}")
st.markdown("---")

# Actualizar benchmark con datos reales
BENCHMARK["Chile"] = df_f["rev_net"].median()

# ── VISTAS ──────────────────────────────────────────────────────────────────────

if vista == "Panorama de mercado":
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='metric-card'><div class='metric-val'>{len(df_f)}</div><div class='metric-lab'>Juegos analizados</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-card'><div class='metric-val'>${df_f['rev_net'].sum():,.0f}</div><div class='metric-lab'>Net Revenue total</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric-card'><div class='metric-val'>{df_f['score'].mean():.1f}</div><div class='metric-lab'>Score promedio</div></div>", unsafe_allow_html=True)
    with c4:
        success_rate = df_f["is_success"].mean() * 100
        st.markdown(f"<div class='metric-card'><div class='metric-val'>{success_rate:.0f}%</div><div class='metric-lab'>Tasa de éxito</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        yearly = df_f.groupby(["year", "genre"]).size().reset_index(name="count")
        fig = px.bar(yearly, x="year", y="count", color="genre",
                     title="Lanzamientos por año y género",
                     color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_layout(template="plotly_dark", paper_bgcolor="#0d1117",
                          plot_bgcolor="#0d1117", height=320, font=dict(family="Exo 2"))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        genre_rev = df_f.groupby("genre")["rev_net"].median().sort_values(ascending=True).reset_index()
        fig2 = px.bar(genre_rev, x="rev_net", y="genre", orientation="h",
                      title="Mediana Net Revenue por género (USD)",
                      color="rev_net", color_continuous_scale=[[0,"#0d2137"],[0.5,"#0077B6"],[1,"#00E5FF"]])
        fig2.update_layout(template="plotly_dark", paper_bgcolor="#0d1117",
                           plot_bgcolor="#0d1117", height=320,
                           coloraxis_showscale=False, font=dict(family="Exo 2"))
        st.plotly_chart(fig2, use_container_width=True)

elif vista == "Análisis por género":
    fig = px.box(df_f, x="genre", y="rev_net", color="is_f2p",
                 log_y=True,
                 color_discrete_map={True: "#00E5FF", False: "#FF6B35"},
                 title="Distribución de Net Revenue por género y modelo (escala log)",
                 labels={"rev_net": "Net Revenue USD", "is_f2p": "F2P", "genre": "Género"})
    fig.update_layout(template="plotly_dark", paper_bgcolor="#0d1117",
                      plot_bgcolor="#0d1117", height=420, font=dict(family="Exo 2"))
    st.plotly_chart(fig, use_container_width=True)

    matrix = df_f.groupby("genre").agg(
        median_rev=("rev_net", "median"),
        avg_sentiment=("sentiment", "mean"),
        count=("title", "count"),
        success_rate=("is_success", "mean")
    ).reset_index()

    fig2 = px.scatter(matrix, x="avg_sentiment", y="median_rev", size="count",
                      color="success_rate", text="genre",
                      color_continuous_scale=[[0,"#1a1a2e"],[0.5,"#0077B6"],[1,"#00E5FF"]],
                      title="Matriz de oportunidad: Sentimiento vs Revenue (burbuja = N° juegos, color = éxito)",
                      labels={"avg_sentiment": "Sentimiento promedio", "median_rev": "Mediana Net Revenue USD",
                              "success_rate": "Tasa éxito"})
    fig2.update_traces(textposition="top center")
    fig2.add_hline(y=matrix["median_rev"].mean(), line_dash="dash", line_color="#444")
    fig2.add_vline(x=matrix["avg_sentiment"].mean(), line_dash="dash", line_color="#444")
    fig2.update_layout(template="plotly_dark", paper_bgcolor="#0d1117",
                       plot_bgcolor="#0d1117", height=420, font=dict(family="Exo 2"))
    st.plotly_chart(fig2, use_container_width=True)

elif vista == "Score vs Revenue":
    col_a, col_b = st.columns([3, 1])
    with col_b:
        log_scale = st.checkbox("Escala logarítmica Y", True)
        highlight = st.selectbox("Resaltar por", ["genre", "is_f2p", "year"])

    fig = px.scatter(df_f, x="score", y="rev_net", color=highlight,
                     log_y=log_scale, size="reviews",
                     hover_data=["title", "genre", "year", "sentiment"],
                     title="Metascore vs Net Revenue",
                     color_discrete_sequence=px.colors.qualitative.Vivid)
    corr = df_f[["score", "sentiment", "rev_net"]].corr()["rev_net"]
    fig.add_annotation(x=90, y=np.log10(df_f["rev_net"].max()) if log_scale else df_f["rev_net"].max(),
                       text=f"Corr Score: {corr['score']:.2f} | Corr Sentiment: {corr['sentiment']:.2f}",
                       showarrow=False, bgcolor="rgba(0,229,255,0.1)",
                       font=dict(color="#00E5FF", size=12))
    fig.update_layout(template="plotly_dark", paper_bgcolor="#0d1117",
                      plot_bgcolor="#0d1117", height=500, font=dict(family="Exo 2"))
    st.plotly_chart(fig, use_container_width=True)

elif vista == "Benchmark global":
    bench_df = pd.DataFrame([
        {"region": k, "median_rev": v, "is_chile": k == "Chile"}
        for k, v in BENCHMARK.items()
    ]).sort_values("median_rev")

    fig = go.Figure(go.Bar(
        x=bench_df["region"], y=bench_df["median_rev"],
        marker_color=["#00E5FF" if r else "#1f3a4d" for r in bench_df["is_chile"]],
        text=[f"${v:,.0f}" for v in bench_df["median_rev"]],
        textposition="outside"
    ))
    fig.update_layout(template="plotly_dark", paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
                      title="Mediana Net Revenue — Chile vs mercados globales",
                      yaxis_title="USD (mediana)", height=420, font=dict(family="Exo 2"))
    st.plotly_chart(fig, use_container_width=True)

    chile_val = BENCHMARK["Chile"]
    global_val = BENCHMARK["Global (mediana)"]
    gap = global_val - chile_val
    pct = gap / global_val * 100
    st.info(f"Chile está **${gap:,.0f} USD** por debajo de la mediana global ({pct:.0f}% de brecha). "
            f"Con corte de plataforma al {platform_cut}%, el net revenue chileno promedio es **${chile_val:,.0f}**.")

elif vista == "Simulador ML":
    st.markdown("### Evalúa la viabilidad comercial de tu proyecto")
    col1, col2 = st.columns(2)

    with col1:
        genre_input = st.selectbox("Género del juego", GENRES)
        model_input = st.radio("Modelo de negocio", ["Premium", "F2P"])
        score_input = st.slider("Metascore estimado", 30, 98, 72)

    with col2:
        sentiment_input = st.slider("Sentimiento esperado (0=negativo, 1=positivo)", 0.0, 1.0, 0.72)
        year_input = st.selectbox("Año de lanzamiento", range(2025, 2028))

    if st.button("🚀 Evaluar proyecto", type="primary"):
        genre_enc = le.transform([genre_input])[0]
        is_f2p = 1 if model_input == "F2P" else 0
        X_pred = [[genre_enc, is_f2p, score_input, sentiment_input, year_input]]

        prob = clf.predict_proba(X_pred)[0][1]
        rev_pred = int(np.expm1(reg.predict(X_pred)[0]))
        rev_net_pred = int(rev_pred * (1 - platform_cut / 100))
        verdict = "VIABLE" if prob >= 0.5 else "RIESGO ALTO"
        color = "#00E5FF" if prob >= 0.5 else "#FF4444"

        st.markdown(f"""
        <div style='background:#0d1117;border:1px solid {color};border-radius:12px;padding:1.5rem;margin-top:1rem'>
            <h3 style='color:{color};font-family:Orbitron,monospace;'>{verdict}</h3>
            <div style='display:flex;gap:2rem;margin-top:1rem;flex-wrap:wrap'>
                <div><div style='font-size:1.5rem;font-weight:700;color:#f0f0f0'>${rev_pred:,.0f}</div>
                     <div style='color:#6b7280;font-size:0.75rem;text-transform:uppercase'>Revenue bruto est.</div></div>
                <div><div style='font-size:1.5rem;font-weight:700;color:#00E5FF'>${rev_net_pred:,.0f}</div>
                     <div style='color:#6b7280;font-size:0.75rem;text-transform:uppercase'>Net Revenue (con {platform_cut}% corte)</div></div>
                <div><div style='font-size:1.5rem;font-weight:700;color:{color}'>{prob*100:.1f}%</div>
                     <div style='color:#6b7280;font-size:0.75rem;text-transform:uppercase'>Probabilidad de éxito</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        feat_imp = pd.Series(clf.feature_importances_,
                             index=["Género", "F2P", "Score", "Sentimiento", "Año"])
        fig_fi = px.bar(feat_imp.sort_values(), orientation="h",
                        title="Importancia de variables en la predicción",
                        color=feat_imp.sort_values(),
                        color_continuous_scale=[[0,"#1a1a2e"],[1,"#00E5FF"]])
        fig_fi.update_layout(template="plotly_dark", paper_bgcolor="#0d1117",
                             plot_bgcolor="#0d1117", height=260,
                             coloraxis_showscale=False, font=dict(family="Exo 2"))
        st.plotly_chart(fig_fi, use_container_width=True)
