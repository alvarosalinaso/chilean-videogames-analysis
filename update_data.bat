@echo off
echo ==========================================
echo  Actualizando Analisis de Videojuegos CL
echo ==========================================

echo 1. Buscando nuevos juegos (Steam)...
python -m chilean_videogames.collect

echo 2. Buscando nuevos juegos (Itch.io)...
python -m chilean_videogames.collect_itch

echo 3. Limpiando y consolidando data cruda...
python -m chilean_videogames.clean

echo 4. Analizando, graficando y exportando...
python -m chilean_videogames.analyze_all
python -m chilean_videogames.export_visualizations

echo 5. Subiendo a GitHub (solo archivos de datos)...
git add data/processed/games.csv data/export/chilean_games_final.csv
git commit -m "Auto-update: Datos actualizados %date% %time%"
git push origin main

echo ==========================================
echo  Listo! Los datos en GitHub estan al dia.
echo  Tu Google Sheet se actualizara en breve.
echo ==========================================
pause
