import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

PLOTLY_THEME = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#e6edf3",
    hoverlabel=dict(bgcolor="#161b22", font_size=12, font_color="#e6edf3"),
    margin=dict(l=40, r=20, t=60, b=40)
)

def graficar_lanzamientos(df_f):
    fig = px.histogram(df_f, x="year", color="genre",
                       title="Lanzamientos por Año y Género",
                       labels={"year": "Año", "count": "Lanzamientos"},
                       color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_layout(barmode="stack", **PLOTLY_THEME)
    return fig

def graficar_heatmap_mes(df_f):
    df_f['month'] = df_f['release_date'].dt.month
    heatmap_data = pd.crosstab(df_f['month'], df_f['genre'])
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values, x=heatmap_data.columns, y=heatmap_data.index,
        colorscale="Viridis"
    ))
    fig.update_layout(title="Densidad de Lanzamientos (Mes vs Género)",
                      yaxis=dict(title="Mes (1-12)", tickmode="linear"), **PLOTLY_THEME)
    return fig

def graficar_barras_genero(df_final):
    # Se espera df_final ordenado
    fig = go.Figure(go.Bar(
        y=df_final["genre"], x=df_final[df_final.columns[1]], # usar la primera metrica
        orientation="h",
        marker=dict(color=df_final[df_final.columns[1]], colorscale="viridis")
    ))
    fig.update_layout(
        title="Métricas por Género",
        yaxis=dict(autorange="reversed"),
        **PLOTLY_THEME
    )
    return fig

def graficar_sentiment_box(df_f, is_platform=False):
    col = "platforms" if is_platform else "genre"
    title_text = "Dispersión de Sentimiento por Plataforma" if is_platform else "Dispersión de Sentimiento por Género"
    fig = px.box(df_f, x=col, y="sentiment", color=col,
                 title=title_text,
                 points="all",
                 color_discrete_sequence=px.colors.qualitative.Dark2)
    fig.add_hline(y=0, line_dash="dash", line_color="#da3633")
    fig.update_layout(**PLOTLY_THEME, showlegend=False)
    return fig

def graficar_cuadrante_oportunidad(df_f, is_log=False, col_y="revenue_est"):
    df_plot = df_f.copy()
    # Hotfix preventivo: px.scatter 'size' truena (ValueError) si hay NaNs
    df_plot["score"] = df_plot["score"].fillna(df_plot["score"].median())
    
    axis_title = "Net Revenue / Ganancia Líquida (USD)" if col_y == "revenue_est_net" else "Revenue Gross (USD)"
    
    fig = px.scatter(df_plot, x="sentiment", y=col_y,
                     size="score", color="genre", hover_name="title",
                     hover_data=["platforms", "price", "units_sold"],
                     log_y=is_log,
                     title="Mapa de Oportunidad Financiera (Contexto INDIE)",
                     labels={"sentiment": "Índice de Aceptación Comunitaria (-1 a +1)", col_y: axis_title},
                     color_discrete_sequence=px.colors.qualitative.Bold)
    
    # Línea base de supervivencia independiente LATAM (~$50,000 USD gross)
    survival_threshold = 50000 
    fig.add_hline(y=survival_threshold, line_dash="dash", line_color="#8b949e", opacity=0.8)
    fig.add_annotation(x=-0.8, y=survival_threshold * (1.1 if is_log else 1.05), text="Supervivencia Estudio Indie ($50k)", showarrow=False, font=dict(color="#8b949e", size=10))
    fig.add_vline(x=0, line_dash="dash", line_color="#8b949e", opacity=0.5)
    
    fig.add_annotation(x=0.5, y=df_f[col_y].max()*0.8, text="⭐ Alta Rentabilidad Líquida", showarrow=False, font=dict(color="#2ea043"))
    fig.add_annotation(x=-0.5, y=df_f[col_y].min() if len(df_f)>0 else 0, text="⚠️ Riesgo de Bancarrota", showarrow=False, font=dict(color="#da3633"))
    
    # Achicar el margen visual (enfocar sobre las verdaderas métricas indies) y formatear el eje Y
    max_rev = df_f[col_y].max()
    upper_bound = max_rev * 1.5 if max_rev > 0 else 1000000
    
    fig.update_layout(
        **PLOTLY_THEME, 
        height=550,
        yaxis=dict(tickformat="$,.0f", title=axis_title),
        xaxis=dict(range=[-1.1, 1.1])
    )
    if not is_log:
        fig.update_layout(yaxis=dict(range=[-10000, upper_bound]))
    return fig
