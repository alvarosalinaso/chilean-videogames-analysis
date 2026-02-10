# Guía de Conexión Automática a Looker Studio 🚀

Esta es la forma más **sencilla y óptima** de conectar tu proyecto. Usaremos GitHub como servidor de datos gratuito.

## 1. El Flujo de Trabajo
1.  Haces doble clic en `update_data.bat` (en tu carpeta del proyecto).
2.  Esto actualiza los datos y los envía a GitHub.
3.  Google Sheets lee los datos de GitHub.
4.  Looker Studio muestra los cambios.

## 2. Configurar el Puente (Google Sheets)
1.  Crea una nueva **Google Sheet** (Hoja de Cálculo) vacía.
2.  En la celda **A1**, pega la siguiente fórmula mágica:
    ```excel
    =IMPORTDATA("https://raw.githubusercontent.com/alvarosalinaso/chilean-videogames-analysis/main/data/export/chilean_games_final.csv")
    ```
3.  ¡Listo! Verás que los datos de tus juegos aparecen automáticamente.
    *   *Tip*: Renombra la hoja a "Data_Juegos".

## 3. Conectar a Looker Studio
1.  Ve a [Looker Studio](https://lookerstudio.google.com/) y crea un informe.
2.  Elige el conector **"Hojas de cálculo de Google"** (Google Sheets).
3.  Selecciona la hoja que acabas de crear.
4.  Haz clic en **Conectar**.

## 4. Configuración de Campos (Importante)
Looker a veces adivina mal los tipos de datos. Ajusta esto en la pestaña de campos:

| Campo | Tipo Correcto | Para qué sirve |
| :--- | :--- | :--- |
| `dev_location` | **Geo > Ciudad** | Mapas geográficos |
| `gross_revenue_est_usd` | **Moneda > USD** | Sumar dinero |
| `year` | **Fecha > Año (YYYY)** | Gráficos de tiempo |

---
**¡Ya está!** Ahora, cada vez que quieras actualizar tu dashboard con nuevos juegos:
1.  Corre `update_data.bat` en tu PC.
2.  Espera unos minutos y refresca tu Looker.
