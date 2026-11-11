@echo off
cd /d "%~dp0"
py -m streamlit run app_acompanhamento.py --server.port 8503
