"""Dash Dashboard: Chilean Videojuegos Analysis — Cyberpunk Arcade Edition."""

from pathlib import Path

import dash
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

SCANLINE_CSS = """
@keyframes pulse-glow { 0%,100%{opacity:1} 50%{opacity:0.7} }
@keyframes crt-flicker { 0%,100%{opacity:1} 92%{opacity:1} 93%{opacity:0.8} 94%{opacity:1} }
"""

app = dash.Dash(
    __name__,
    title="Videojuegos Chilenos — Análisis",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server

app.index_string = """<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    <style>
    @keyframes pulse-glow { 0%,100%{opacity:1} 50%{opacity:0.7} }
    @keyframes crt-flicker { 0%,100%{opacity:1} 92%{opacity:1} 93%{opacity:0.8} 94%{opacity:1} }
    </style>
</head>
<body>
    {%app_entry%}
    <footer>{%config%}{%scripts%}{%renderer%}</footer>
</body>
</html>
"""

NEON_CYAN = "#00fff9"
NEON_PINK = "#ff0080"
NEON_GREEN = "#39ff14"
BG_BLACK = "#0a0a0a"
CARD_BG = "rgba(13, 13, 13, 0.80)"
TEXT_WHITE = "#e0e0e0"
TEXT_MUTED = "#8892b0"
GRID_DOT = "#1a1a1a"

SCANLINE_CSS = """
@keyframes scanline {
  0% { background-position: 0 0; }
  100% { background-position: 0 4px; }
}
@keyframes flicker {
  0%, 95%, 100% { opacity: 1; }
  96% { opacity: 0.6; }
  97% { opacity: 1; }
  98% { opacity: 0.7; }
}
@keyframes pulse-glow {
  0%, 100% { text-shadow: 0 0 8px #00fff9, 0 0 16px #00fff9; }
  50% { text-shadow: 0 0 14px #00fff9, 0 0 28px #00fff9, 0 0 42px #00fff9; }
}
@keyframes pulse-glow-pink {
  0%, 100% { box-shadow: 0 0 6px #ff0080, inset 0 0 6px rgba(255,0,128,0.05); }
  50% { box-shadow: 0 0 14px #ff0080, inset 0 0 10px rgba(255,0,128,0.08); }
}
@keyframes pulse-glow-cyan {
  0%, 100% { box-shadow: 0 0 6px #00fff9, inset 0 0 6px rgba(0,255,249,0.05); }
  50% { box-shadow: 0 0 14px #00fff9, inset 0 0 10px rgba(0,255,249,0.08); }
}
"""

BASE = Path(__file__).parent
PROCESSED = BASE / "data" / "processed" / "games.csv"
ENRICHED = BASE / "data" / "export" / "chilean_games_final.csv"


def load_data():
    if ENRICHED.exists():
        return pd.read_csv(ENRICHED)
    if PROCESSED.exists():
        return pd.read_csv(PROCESSED)
    return pd.DataFrame()


DATA = load_data()


def card(title, children, glow_color=NEON_PINK):
    child_list = children if isinstance(children, list) else [children]
    return html.Div(
        style={
            "backgroundColor": CARD_BG,
            "borderRadius": "8px",
            "padding": "24px",
            "marginBottom": "24px",
            "border": f"1px solid {glow_color}44",
            "boxShadow": f"0 0 10px {glow_color}33, inset 0 0 6px {glow_color}08",
            "backdropFilter": "blur(6px)",
            "transition": "box-shadow 0.3s ease, border-color 0.3s ease",
        },
        children=[
            html.H3(
                title,
                style={
                    "color": glow_color,
                    "fontFamily": "Consolas, 'Courier New', monospace",
                    "fontSize": "1.15rem",
                    "fontWeight": "700",
                    "marginBottom": "14px",
                    "paddingBottom": "10px",
                    "borderBottom": f"1px solid {glow_color}55",
                    "textShadow": f"0 0 8px {glow_color}",
                    "letterSpacing": "2px",
                    "textTransform": "uppercase",
                },
            ),
        ] + child_list,
    )


def stat_row(stats):
    return html.Div(
        style={"display": "flex", "gap": "14px", "flexWrap": "wrap", "marginBottom": "24px"},
        children=[
            html.Div(
                style={
                    "flex": "1",
                    "minWidth": "150px",
                    "backgroundColor": CARD_BG,
                    "borderRadius": "8px",
                    "padding": "22px 16px",
                    "textAlign": "center",
                    "border": f"1px solid {NEON_CYAN}44",
                    "boxShadow": f"0 0 10px {NEON_CYAN}22, inset 0 0 6px {NEON_CYAN}08",
                    "backdropFilter": "blur(4px)",
                    "animation": "pulse-glow-cyan 3s ease-in-out infinite",
                },
                children=[
                    html.Div(
                        str(val),
                        style={
                            "fontSize": "2rem",
                            "fontWeight": "800",
                            "color": NEON_CYAN,
                            "fontFamily": "Consolas, 'Courier New', monospace",
                            "textShadow": f"0 0 10px {NEON_CYAN}, 0 0 20px {NEON_CYAN}",
                            "animation": "pulse-glow 2.5s ease-in-out infinite",
                        },
                    ),
                    html.Div(
                        label,
                        style={
                            "fontSize": "0.78rem",
                            "color": TEXT_MUTED,
                            "marginTop": "6px",
                            "fontFamily": "Consolas, 'Courier New', monospace",
                            "letterSpacing": "1px",
                            "textTransform": "uppercase",
                        },
                    ),
                ],
            )
            for val, label in stats
        ],
    )


def _tab_style():
    return {
        "style": {
            "backgroundColor": "rgba(13,13,13,0.6)",
            "color": TEXT_MUTED,
            "border": f"1px solid {NEON_CYAN}33",
            "borderRadius": "6px",
            "fontFamily": "Consolas, 'Courier New', monospace",
            "fontSize": "0.82rem",
            "letterSpacing": "1.5px",
            "textTransform": "uppercase",
            "padding": "10px 18px",
            "margin": "0 3px",
            "transition": "all 0.3s ease",
            "boxShadow": f"0 0 4px {NEON_CYAN}11",
        },
        "selected_style": {
            "backgroundColor": "rgba(0, 255, 249, 0.12)",
            "color": NEON_CYAN,
            "border": f"1px solid {NEON_CYAN}",
            "borderRadius": "6px",
            "fontFamily": "Consolas, 'Courier New', monospace",
            "fontSize": "0.82rem",
            "letterSpacing": "1.5px",
            "textTransform": "uppercase",
            "padding": "10px 18px",
            "margin": "0 3px",
            "boxShadow": f"0 0 14px {NEON_CYAN}66, inset 0 0 8px {NEON_CYAN}22",
            "textShadow": f"0 0 6px {NEON_CYAN}",
        },
    }


def cyberplot_layout(title=""):
    return {
        "template": "plotly_dark",
        "paper_bgcolor": "rgba(10,10,10,0)",
        "plot_bgcolor": "rgba(10,10,10,0.5)",
        "font": {"family": "Consolas, 'Courier New', monospace", "color": TEXT_WHITE},
        "title": {"text": title, "font": {"color": NEON_CYAN, "family": "Consolas, monospace", "size": 14}},
        "xaxis": {
            "gridcolor": "#1a1a2e",
            "zerolinecolor": "#1a1a2e",
            "tickfont": {"color": TEXT_MUTED, "size": 11},
        },
        "yaxis": {
            "gridcolor": "#1a1a2e",
            "zerolinecolor": "#1a1a2e",
            "tickfont": {"color": TEXT_MUTED, "size": 11},
        },
        "legend": {"font": {"color": TEXT_MUTED, "size": 11}},
        "margin": {"l": 50, "r": 20, "t": 50, "b": 50},
    }


NEON_PLATFORM_COLORS = {"steam": NEON_CYAN, "itch": NEON_PINK}

app.layout = html.Div(
    style={
        "backgroundColor": BG_BLACK,
        "minHeight": "100vh",
        "fontFamily": "Consolas, 'Courier New', monospace",
        "color": TEXT_WHITE,
        "backgroundImage": (
            "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,255,249,0.012) 2px, rgba(0,255,249,0.012) 4px),"
            "radial-gradient(circle at 1px 1px, rgba(255,255,255,0.03) 1px, transparent 0)"
        ),
        "backgroundSize": "100% 4px, 20px 20px",
    },
    children=[
        html.Div(
            style={
                "background": f"linear-gradient(135deg, {BG_BLACK} 0%, #0d0d1a 50%, {BG_BLACK} 100%)",
                "padding": "44px 20px 36px",
                "textAlign": "center",
                "borderBottom": f"2px solid {NEON_CYAN}44",
                "boxShadow": f"0 0 30px {NEON_CYAN}15",
                "position": "relative",
            },
            children=[
                html.H1(
                    "VIDEOJUEGOS CHILENOS",
                    style={
                        "fontSize": "2.6rem",
                        "fontWeight": "800",
                        "color": NEON_CYAN,
                        "margin": "0",
                        "fontFamily": "Consolas, 'Courier New', monospace",
                        "textShadow": f"0 0 12px {NEON_CYAN}, 0 0 24px {NEON_CYAN}, 0 0 48px {NEON_CYAN}88",
                        "letterSpacing": "6px",
                        "textTransform": "uppercase",
                    },
                ),
                html.P(
                    "ETL  ·  CLUSTERING  ·  REVENUE",
                    style={
                        "color": NEON_PINK,
                        "marginTop": "10px",
                        "fontSize": "0.95rem",
                        "fontFamily": "Consolas, 'Courier New', monospace",
                        "letterSpacing": "4px",
                        "animation": "flicker 3s infinite",
                        "textShadow": f"0 0 6px {NEON_PINK}, 0 0 12px {NEON_PINK}",
                    },
                ),
                html.P(
                    "Análisis de 150 juegos — Steam & Itch.io",
                    style={
                        "color": TEXT_MUTED,
                        "marginTop": "6px",
                        "fontSize": "0.85rem",
                        "fontFamily": "Consolas, 'Courier New', monospace",
                        "letterSpacing": "1px",
                    },
                ),
            ],
        ),
        dcc.Tabs(
            id="tabs",
            value="overview",
            style={
                "backgroundColor": "rgba(10,10,10,0.9)",
                "borderBottom": f"1px solid {NEON_CYAN}22",
                "padding": "10px 20px",
            },
            children=[
                dcc.Tab(label="▸ RESUMEN", value="overview", **_tab_style()),
                dcc.Tab(label="▸ PRECIOS", value="prices", **_tab_style()),
                dcc.Tab(label="▸ REVENUE", value="revenue", **_tab_style()),
                dcc.Tab(label="▸ GÉNEROS", value="genres", **_tab_style()),
                dcc.Tab(label="▸ CORRELACIÓN", value="correlation", **_tab_style()),
            ],
        ),
        html.Div(
            id="tab-content",
            style={"maxWidth": "1200px", "margin": "0 auto", "padding": "30px 20px"},
        ),
    ],
)


@callback(Output("tab-content", "children"), Input("tabs", "value"))
def render_tab(tab):
    if DATA.empty:
        return card("ERROR", html.P("No hay datos disponibles", style={"color": NEON_PINK}))
    funcs = {
        "overview": overview_tab,
        "prices": prices_tab,
        "revenue": revenue_tab,
        "genres": genres_tab,
        "correlation": correlation_tab,
    }
    return funcs.get(tab, overview_tab)()


def overview_tab():
    df = DATA
    stats = stat_row([
        (str(len(df)), "Juegos"),
        (str(df["source"].nunique()), "Plataformas"),
        (
            f"${df[df['price_usd'] > 0]['price_usd'].mean():.1f}"
            if "price_usd" in df.columns
            else "N/A",
            "Precio promedio USD",
        ),
        (
            str(df["primary_genre"].nunique())
            if "primary_genre" in df.columns
            else str(df["genres"].nunique()),
            "Géneros",
        ),
    ])

    fig_platform = px.pie(
        df,
        names="source",
        hole=0.35,
        color_discrete_map=NEON_PLATFORM_COLORS,
    )
    fig_platform.update_layout(**cyberplot_layout("Distribución por Plataforma"), height=400)
    fig_platform.update_traces(
        marker=dict(line=dict(color=BG_BLACK, width=2)),
        textfont=dict(color=TEXT_WHITE, family="Consolas, monospace"),
    )

    if "year" in df.columns:
        year_df = df[df["year"] != "Unknown"].copy()
        if not year_df.empty:
            year_counts = year_df.groupby(["year", "source"]).size().reset_index(name="count")
            fig_timeline = px.bar(
                year_counts,
                x="year",
                y="count",
                color="source",
                color_discrete_map=NEON_PLATFORM_COLORS,
            )
            fig_timeline.update_layout(**cyberplot_layout("Lanzamientos por Año"), height=400)
            fig_timeline.update_xaxes(title_text="Año", title_font=dict(color=TEXT_MUTED))
            fig_timeline.update_yaxes(title_text="Juegos", title_font=dict(color=TEXT_MUTED))
            return html.Div([
                stats,
                card("Plataformas", dcc.Graph(figure=fig_platform), NEON_CYAN),
                card("Lanzamientos", dcc.Graph(figure=fig_timeline), NEON_GREEN),
            ])
    return html.Div([
        stats,
        card("Plataformas", dcc.Graph(figure=fig_platform), NEON_CYAN),
    ])


def prices_tab():
    df = DATA
    if "price_usd" not in df.columns:
        return card("Precios", html.P("Columna price_usd no disponible", style={"color": NEON_PINK}))

    paid = df[df["price_usd"] > 0]
    fig_hist = px.histogram(
        paid,
        x="price_usd",
        color="source",
        nbins=30,
        color_discrete_map=NEON_PLATFORM_COLORS,
    )
    fig_hist.update_layout(**cyberplot_layout("Distribución de Precios (USD)"), height=400)
    fig_hist.update_xaxes(title_text="Precio USD", title_font=dict(color=TEXT_MUTED))
    fig_hist.update_yaxes(title_text="Cantidad", title_font=dict(color=TEXT_MUTED))

    genre_col = "primary_genre" if "primary_genre" in df.columns else "genres"
    neon_genre = px.colors.qualitative.Set3
    fig_box = px.box(paid, x=genre_col, y="price_usd", color=genre_col, color_discrete_sequence=neon_genre)
    fig_box.update_layout(**cyberplot_layout("Precios por Género"), height=500, showlegend=False)

    compare = df.groupby("source")["price_usd"].agg(["mean", "median", "count"]).reset_index()
    fig_compare = go.Figure()
    fig_compare.add_trace(go.Bar(
        x=compare["source"], y=compare["mean"], name="Promedio",
        marker_color=NEON_CYAN,
        marker_line=dict(color=NEON_CYAN, width=1),
    ))
    fig_compare.add_trace(go.Bar(
        x=compare["source"], y=compare["median"], name="Mediana",
        marker_color=NEON_PINK,
        marker_line=dict(color=NEON_PINK, width=1),
    ))
    fig_compare.update_layout(
        **cyberplot_layout("Precio Promedio vs Mediana"),
        barmode="group",
        height=350,
    )

    return html.Div([
        card("Distribución de Precios", dcc.Graph(figure=fig_hist), NEON_CYAN),
        card("Precios por Género", dcc.Graph(figure=fig_box), NEON_GREEN),
        card("Comparación Steam vs Itch.io", dcc.Graph(figure=fig_compare), NEON_PINK),
    ])


def revenue_tab():
    df = DATA
    if "gross_revenue_est_usd" not in df.columns:
        return card("Revenue", html.P("Columna gross_revenue_est_usd no disponible", style={"color": NEON_PINK}))

    top10 = df.nlargest(10, "gross_revenue_est_usd")
    fig_top = px.bar(
        top10,
        x="gross_revenue_est_usd",
        y="name",
        orientation="h",
        color="source",
        color_discrete_map=NEON_PLATFORM_COLORS,
    )
    fig_top.update_layout(**cyberplot_layout("Top 10 Juegos por Revenue Estimado"), height=500)
    fig_top.update_yaxes(categoryorder="total ascending", tickfont=dict(color=TEXT_WHITE))

    if "recommendations" in df.columns:
        scatter_df = df[df["recommendations"] > 0]
        fig_scatter = px.scatter(
            scatter_df,
            x="recommendations",
            y="gross_revenue_est_usd",
            color="source",
            hover_name="name",
            color_discrete_map=NEON_PLATFORM_COLORS,
        )
        fig_scatter.update_layout(**cyberplot_layout("Recomendaciones vs Revenue"), height=450)
        fig_scatter.update_traces(marker=dict(size=9, line=dict(width=1, color=BG_BLACK)))
    else:
        fig_scatter = go.Figure()

    genre_col = "primary_genre" if "primary_genre" in df.columns else "genres"
    rev_genre = df.groupby(genre_col)["gross_revenue_est_usd"].sum().sort_values(ascending=False).head(10).reset_index()
    fig_genre = px.bar(
        rev_genre,
        x=genre_col,
        y="gross_revenue_est_usd",
        color=genre_col,
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig_genre.update_layout(**cyberplot_layout("Revenue por Género"), height=400, showlegend=False)

    return html.Div([
        card("Top 10 Revenue", dcc.Graph(figure=fig_top), NEON_GREEN),
        card("Recomendaciones vs Revenue", dcc.Graph(figure=fig_scatter), NEON_CYAN),
        card("Revenue por Género", dcc.Graph(figure=fig_genre), NEON_PINK),
    ])


def genres_tab():
    df = DATA
    genre_col = "primary_genre" if "primary_genre" in df.columns else "genres"

    fig_treemap = px.treemap(
        df,
        path=["source", genre_col],
        color=genre_col,
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig_treemap.update_layout(**cyberplot_layout("Juegos por Plataforma > Género"), height=500)
    fig_treemap.update_traces(
        textfont=dict(color=TEXT_WHITE, family="Consolas, monospace"),
        marker=dict(line=dict(color=BG_BLACK, width=1)),
    )

    pivot = df.groupby(["source", genre_col]).size().reset_index(name="count")
    fig_heat = px.density_heatmap(
        pivot,
        x=genre_col,
        y="source",
        z="count",
        color_continuous_scale=[
            [0.0, BG_BLACK],
            [0.2, "#0d0d2a"],
            [0.5, "#00334d"],
            [0.8, NEON_CYAN],
            [1.0, NEON_GREEN],
        ],
    )
    fig_heat.update_layout(**cyberplot_layout("Heatmap: Plataforma vs Género"), height=400)

    return html.Div([
        card("Treemap de Géneros", dcc.Graph(figure=fig_treemap), NEON_GREEN),
        card("Heatmap Plataforma vs Género", dcc.Graph(figure=fig_heat), NEON_PINK),
    ])


def correlation_tab():
    df = DATA
    numeric_cols = ["price_usd", "recommendations", "gross_revenue_est_usd", "metacritic"]
    available = [c for c in numeric_cols if c in df.columns]
    if len(available) < 2:
        return card("Correlación", html.P("No hay suficientes columnas numéricas", style={"color": NEON_PINK}))

    corr = df[available].corr()
    fig_corr = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale=[
            [0.0, NEON_PINK],
            [0.5, BG_BLACK],
            [1.0, NEON_CYAN],
        ],
        zmin=-1,
        zmax=1,
    )
    fig_corr.update_layout(**cyberplot_layout("Matriz de Correlación"), height=500)

    scatter_figs = []
    pairs = [
        ("price_usd", "recommendations"),
        ("price_usd", "gross_revenue_est_usd"),
        ("recommendations", "gross_revenue_est_usd"),
    ]
    for x, y in pairs:
        if x in df.columns and y in df.columns:
            sub = df[df[x] > 0] if x == "price_usd" else df
            fig = px.scatter(
                sub,
                x=x,
                y=y,
                color="source",
                hover_name="name",
                color_discrete_map=NEON_PLATFORM_COLORS,
            )
            fig.update_layout(**cyberplot_layout(f"{x} vs {y}"), height=350)
            fig.update_traces(marker=dict(size=8, line=dict(width=1, color=BG_BLACK)))
            scatter_figs.append(fig)

    children = [card("Matriz de Correlación", dcc.Graph(figure=fig_corr), NEON_CYAN)]
    for f in scatter_figs:
        children.append(card(f.layout.title.text, dcc.Graph(figure=f), NEON_PINK))
    return html.Div(children)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8053)))
