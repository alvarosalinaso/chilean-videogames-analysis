@echo off
echo ==========================================
echo  Actualizando Analisis de Videojuegos CL
echo ==========================================

echo 1. Buscando nuevos juegos (Steam)...
python src/collect.py

echo 2. Buscando nuevos juegos (Itch.io)...
python src/collect_itch.py

echo 3. Procesando y generando CSV final...
python src/analyze_all.py

echo 4. Subiendo a GitHub...
git add .
git commit -m "Auto-update: Datos actualizados %date% %time%"
git push origin main

echo ==========================================
echo  Listo! Los datos en GitHub estan al dia.
echo  Tu Google Sheet se actualizara en breve.
echo ==========================================
pause
