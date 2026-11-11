@echo off
chcp 65001 >nul
title Carteira do Cliente - Ciano
cd /d "%~dp0"
start "Carteira do Cliente (nao feche)" cmd /k py -m streamlit run app_cliente.py --server.headless true --server.port 8502 --theme.base light --theme.primaryColor "#0E2266" --theme.backgroundColor "#FAF8F3" --theme.secondaryBackgroundColor "#F3EFE6" --theme.textColor "#1C2541"
timeout /t 6 /nobreak >nul
start "" http://localhost:8502
