# Valuation Ciano

Programa que roda o valuation por EBIT projetado (método P/L a valor presente
+ FCD do EBIT, 3 cenários) para uma ou várias empresas de uma vez, buscando
os dados automaticamente no Fundamentus.

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

### Linha de comando (gera Excel)

```bash
python main.py PETR4 VALE3 ITSA4 BBAS3
```

Isso gera `valuation_resultado.xlsx` com uma linha por ticker, os 3 cenários
(pessimista/intermediário/otimista) e o veredito automático (sobrepreço /
desconto / dentro da faixa).

### Interface web local (Streamlit)

```bash
streamlit run app.py
```

Abre uma página no navegador onde você busca um ticker no Fundamentus (ou
digita Preço e P/EBIT à mão), edita as premissas e os 3 cenários na barra
lateral, e vê o valuation por ação com o veredito e um gráfico comparando
com o preço atual.

## Arquivos

- `valuation_engine.py` — as fórmulas puras (testável isoladamente, já validado
  contra os números do PETR4 conferidos no chat).
- `fundamentus_scraper.py` — busca preço, EBIT e nº de ações no Fundamentus.
- `main.py` — junta os dois e exporta Excel.
- `app.py` — interface web local (Streamlit).

## Próximos passos sugeridos

1. **Cache/agendamento**: salvar a tabela do Fundamentus localmente (ela muda
   pouco intradia) e agendar atualização diária via cron/Task Scheduler.
2. **Ajuste de colunas**: se o Fundamentus mudar o HTML da tabela, o
   `fundamentus_scraper.py` precisa de ajuste nos nomes de coluna
   (`COLUNAS_UTEIS` no topo do arquivo).
3. **Fontes alternativas**: para ADRs ou ações fora da B3 (ex: NEE), este
   scraper não serve — seria preciso outra fonte (ex: Yahoo Finance API).

## Observação sobre o EBIT

O Fundamentus não expõe EBIT diretamente na tabela de resultado — ele é
derivado via `EBIT por ação = Preço / (P/EBIT)`. O valuation final é sempre
por ação e o número de ações se cancela na conta (ver `valuation_engine.py`),
então o scraper normaliza o total para 1 ação. Isso também dispensa a coluna
"Valor de mercado", que a tabela `resultado.php` do Fundamentus deixou de
expor.
