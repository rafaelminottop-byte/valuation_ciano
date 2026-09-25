@echo off
chcp 65001 >nul
title Valuation Ciano - Inicializador
cd /d "C:\Users\Micro\Desktop\valuation_ciano"

echo ============================================================
echo   VALUATION CIANO - subindo o app e o link publico...
echo ============================================================
echo.

REM 1) Sobe o app Streamlit numa janela propria
start "Valuation Ciano - APP (nao feche)" cmd /k py -m streamlit run app.py --server.headless true --server.port 8501

REM 2) Espera o app iniciar
echo Aguardando o app iniciar (8 segundos)...
timeout /t 8 /nobreak >nul

REM 3) Sobe o tunel publico noutra janela (cloudflared.exe esta nesta pasta)
start "Valuation Ciano - LINK PUBLICO (nao feche)" cmd /k cloudflared.exe tunnel --url http://localhost:8501 --no-autoupdate

echo.
echo ============================================================
echo   PRONTO!
echo.
echo   - Seu app local:  http://localhost:8501
echo   - O LINK PUBLICO para os socios aparece na janela
echo     "Valuation Ciano - LINK PUBLICO", numa linha assim:
echo         https://xxxx-xxxx.trycloudflare.com
echo.
echo   Copie esse link e mande para os socios.
echo   Deixe as DUAS janelas abertas enquanto eles usam.
echo   Para desligar, feche as duas janelas.
echo ============================================================
echo.
pause
