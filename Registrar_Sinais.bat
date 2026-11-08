@echo off
rem Registra o sinal do mes do preditor do Ibovespa e publica o registro no GitHub.
rem Rode uma vez por mes (da primeira semana em diante). Um registro por mes, nunca sobrescreve.
cd /d "%~dp0"
py registrar_sinais.py --publicar
echo.
pause
