# Valuation Ciano

Programa que roda o valuation por EBIT projetado (método P/L a valor presente
+ FCD do EBIT, 3 cenários) para uma ou várias empresas de uma vez, buscando
os dados automaticamente no Fundamentus.

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

```bash
python main.py PETR4 VALE3 ITSA4 BBAS3
```

Isso gera `valuation_resultado.xlsx` com uma linha por ticker, os 3 cenários
(pessimista/intermediário/otimista) e o veredito automático (sobrepreço /
desconto / dentro da faixa).

## Arquivos

- `valuation_engine.py` — as fórmulas puras (testável isoladamente, já validado
  contra os números do PETR4 conferidos no chat).
- `fundamentus_scraper.py` — busca preço, EBIT e nº de ações no Fundamentus.
- `main.py` — junta os dois e exporta Excel.

## Próximos passos sugeridos

1. **Interface web local**: trocar o `main.py` por um app Streamlit
   (`streamlit run app.py`) com inputs editáveis por cenário, igual ao widget
   testado no chat.
2. **Cache/agendamento**: salvar a tabela do Fundamentus localmente (ela muda
   pouco intradia) e agendar atualização diária via cron/Task Scheduler.
3. **Ajuste de colunas**: se o Fundamentus mudar o HTML da tabela, o
   `fundamentus_scraper.py` precisa de ajuste nos nomes de coluna
   (`colunas_uteis` no topo do arquivo).
4. **Fontes alternativas**: para ADRs ou ações fora da B3 (ex: NEE), este
   scraper não serve — seria preciso outra fonte (ex: Yahoo Finance API).

## Observação sobre o EBIT

O Fundamentus não expõe EBIT diretamente na tabela de resultado — ele é
derivado via `EBIT por ação = Preço / (P/EBIT)`, depois multiplicado pelo
número de ações. Isso reproduz o EBIT dos últimos 12 meses usado na
metodologia original.
