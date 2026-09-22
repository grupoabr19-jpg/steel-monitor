# Steel Monitor — Sistema de Monitoramento de Preço e Sourcing de Aço

Coleta automática e gratuita de dados para apoiar decisão de compra
(sourcing) e precificação de aço, comparando mercado nacional, internacional
e concorrentes.

## O que ele coleta

| Módulo | Fonte | Custo |
|---|---|---|
| `collectors/b3_quotes.py` | Ações de siderúrgicas na B3 (brapi.dev) | Grátis |
| `collectors/currency.py` | Câmbio USD/BRL, EUR/BRL (AwesomeAPI) | Grátis |
| `collectors/comex_trade.py` | Importação/exportação por NCM (Comex Stat / MDIC) | Grátis |
| `collectors/competitor_prices.py` | Preço de concorrentes (scraping — **você precisa mapear as URLs**) | Grátis |

## Instalação

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Uso manual

```bash
python main.py
```

Isso gera/atualiza arquivos CSV em `data/`:
- `data/b3_quotes.csv`
- `data/currency.csv`
- `data/comex_import.csv`
- `data/comex_export.csv`

## Automatizar de graça (GitHub Actions)

1. Suba esta pasta como um repositório no GitHub (pode ser privado).
2. O workflow em `.github/workflows/monitor.yml` já está configurado para
   rodar 2x por dia útil, de graça (dentro do limite gratuito de ~2.000
   min/mês do GitHub Actions).
3. **Obrigatório**: cadastre-se em brapi.dev, pegue um token gratuito em
   "Chaves de API" no dashboard, e salve como secret `BRAPI_TOKEN` no
   repositório (Settings → Secrets and variables → Actions → New repository
   secret). Desde a migração da brapi para a API v2, todo ticker exige
   token — sem ele, a coleta de ações falha com erro 401.
   O token nunca deve ser colocado direto no código nem em arquivo
   versionado — só como variável de ambiente / secret.

## Próximos passos recomendados

1. **Preços de concorrentes**: edite `collectors/competitor_prices.py` com
   as URLs reais e os seletores CSS de cada concorrente que você quer
   monitorar. É o único módulo que exige customização manual — não existe
   API pública para isso.
2. **Cálculo de margem**: `main.py` já tem a função `calcular_alerta_margem()`
   pronta — falta conectar com seu custo real (planilha de custos ou ERP).
3. **Dashboard**: a forma mais simples e gratuita é exportar os CSVs para o
   Google Sheets (via `gspread`, também gratuito) e conectar o Google Looker
   Studio nele — ele atualiza os gráficos sozinho a cada nova linha.
4. **Alertas**: adicione uma chamada a um webhook do Slack/Telegram (grátis)
   dentro de `main.py`, disparada quando `risco_margem` for `True`.

## Limitações conhecidas

- A API do Comex Stat tem rate limit agressivo — o código já tenta de novo
  automaticamente, mas evite rodar com muita frequência.
- Sem token, a brapi.dev entrega cotação com cache de alguns minutos (ainda
  assim gratuito e suficiente para decisão gerencial, não para trading).
- O scraping de concorrentes quebra se o site mudar o layout — é normal,
  precisa de manutenção pontual.
