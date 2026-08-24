# Visualización: Embed Snippets

Snippets listos para pegar. Cada uno apunta a un CSV generado por `src/export_visualizations.py`.

---

## 1. Datawrapper — Cuadrante de Rentabilidad

**Archivo de datos:** `data/export/dw_quadrant_rentabilidad.csv`

<!-- Reemplaza DATAWRAPPER_ID con el ID de tu gráfico creado en Datawrapper -->
<div id="dw-quadrant" style="max-width:100%; overflow:hidden;">
  <noscript>
    <p>Gráfico de cuadrante: Rentabilidad vs Saturación por género.
       Consulta <code>data/export/dw_quadrant_rentabilidad.csv</code> para los datos.</p>
  </noscript>
  <iframe
    title="Cuadrante de Rentabilidad — Géneros de Videojuegos Chilenos"
    aria-label="Gráfico de cuadrante mostrando ingresos promedio vs cantidad de juegos por género"
    src="https://datawrapper.dwcdn.net/DATAWRAPPER_ID/"
    style="width:100%; border:none; min-height:520px;"
    loading="lazy"
  ></iframe>
</div>

---

## 2. Flourish — Treemap de Géneros

**Archivo de datos:** `data/export/flourish_treemap_genero.csv`

<!-- Reemplaza FLOURISH_ID con el ID de tu visualización en Flourish -->
<div id="flourish-treemap" style="max-width:100%; overflow:hidden;">
  <noscript>
    <p>Mapa de árbol: Jerarquía Plataforma → Género → Juego.
       Consulta <code>data/export/flourish_treemap_genero.csv</code> para los datos.</p>
  </noscript>
  <div
    class="flourish-embed flourish-type-hierarchy"
    data-src="visualisation/FLOURISH_ID"
    style="width:100%; max-width:100%;"
  >
    <noscript>
      <a href="https://public.flourish.studio/visualisation/FLOURISH_ID/">Ver visualización</a>
    </noscript>
  </div>
  <script src="https://public.flourish.studio/resources/embed.js" async></script>
</div>

---

## 3. Observable Plot — Distribución de Ingresos

**Archivo de datos:** `data/export/observable_distribucion.csv`

<!-- Este snippet usa Observable Plot desde CDN. Carga el CSV vía fetch. -->
<div id="observable-dist" style="max-width:100%; overflow:hidden;">
  <noscript>
    <p>Distribución de ingresos por género.
       Consulta <code>data/export/observable_distribucion.csv</code> para los datos.</p>
  </noscript>
  <figure
    id="observable-figure"
    role="img"
    aria-label="Distribución de ingresos estimados por género de videojuegos chilenos"
    style="width:100%; overflow-x:auto;"
  >
    <figcaption>Distribución de ingresos por género — Observable Plot</figcaption>
    <div id="observable-plot" style="width:100%; min-height:300px;">
      <noscript>Gráfico interactivo. Activa JavaScript para verlo.</noscript>
    </div>
  </figure>
  <script type="module">
    import * as Plot from "https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6/+esm";

    const res = await fetch("../data/export/observable_distribucion.csv");
    const text = await res.text();
    const rows = text.split("\n").slice(1).map(line => {
      const [game, genre, price, copies, revenue, mc, year, dev, is_free, is_paid, has_mc] = line.split(",");
      return {
        game,
        genre,
        price_usd: +price,
        copies_sold: +copies,
        revenue_usd: +revenue,
        metacritic: mc ? +mc : null,
        year,
        is_paid: is_paid === "True",
      };
    }).filter(d => d.genre && d.revenue_usd > 0);

    const chart = Plot.plot({
      width: 800,
      marginLeft: 140,
      marginBottom: 40,
      x: { label: "Revenue estimado (USD)", grid: true },
      y: { label: null },
      color: { legend: true },
      marks: [
        Plot.barX(rows, Plot.groupY({ x: "sum" }, { y: "genre", x: "revenue_usd", fill: "genre", sort: { y: "-x" } })),
        Plot.ruleX([0]),
      ],
    });

    document.getElementById("observable-plot").appendChild(chart);
  </script>
</div>
