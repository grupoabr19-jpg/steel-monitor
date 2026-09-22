"""
Orquestrador principal do sistema de monitoramento de aço.

Roda todos os coletores, salva os resultados em CSV (append) e calcula
alertas simples de margem. Pensado para rodar via GitHub Actions (cron)
ou manualmente: `python main.py`.

Para conectar isso a uma planilha Google Sheets em vez de CSV local,
troque a função save_csv() por uma chamada à API do Google Sheets
(gspread + service account, também gratuito).
"""
import csv
import os
import sys
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from config import (
    TICKERS_B3, MOEDAS, NCM_LIST, MARGEM_MINIMA_PCT, OUTPUT_DIR,
)
from collectors.b3_quotes import get_quotes, BrapiQuoteError
from collectors.currency import get_rates
from collectors.comex_trade import get_trade_by_ncm


def save_csv(filename: str, rows: list[dict]):
    if not rows:
        return
    path = os.path.join(OUTPUT_DIR, filename)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_exists = os.path.isfile(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)
    print(f"[ok] {len(rows)} linhas gravadas em {path}")


def calcular_alerta_margem(preco_venda_brl: float, custo_pousado_brl: float) -> dict:
    """Alerta simples: compara preço de venda contra custo + margem mínima."""
    margem_atual_pct = ((preco_venda_brl - custo_pousado_brl) / preco_venda_brl) * 100
    risco = margem_atual_pct < MARGEM_MINIMA_PCT
    return {
        "margem_atual_pct": round(margem_atual_pct, 2),
        "margem_minima_pct": MARGEM_MINIMA_PCT,
        "risco_margem": risco,
    }


def periodo_ultimo_mes_fechado() -> tuple[str, str]:
    hoje = date.today()
    primeiro_dia_mes_atual = hoje.replace(day=1)
    ultimo_dia_mes_anterior = primeiro_dia_mes_atual - timedelta(days=1)
    periodo = ultimo_dia_mes_anterior.strftime("%Y-%m")
    return periodo, periodo


def main():
    print(f"=== Coleta iniciada em {datetime.now().isoformat()} ===")

    # Garante que a pasta exista mesmo se todas as coletas abaixo falharem,
    # senão o `git add data/` do workflow quebra por falta da pasta.
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    gitkeep_path = os.path.join(OUTPUT_DIR, ".gitkeep")
    if not os.path.isfile(gitkeep_path):
        open(gitkeep_path, "a").close()

    # 1) Ações do setor na B3
    try:
        b3_rows = get_quotes(TICKERS_B3)
        save_csv("b3_quotes.csv", b3_rows)
    except BrapiQuoteError as e:
        print(f"[erro] B3 (brapi.dev): {e}")
    except Exception as e:
        print(f"[erro] B3: {e}")

    # 2) Câmbio
    try:
        fx_rows = get_rates(MOEDAS)
        save_csv("currency.csv", fx_rows)
    except Exception as e:
        print(f"[erro] Câmbio: {e}")

    # 3) Comércio exterior (import/export) — último mês fechado
    try:
        start, end = periodo_ultimo_mes_fechado()
        imp_rows = get_trade_by_ncm(NCM_LIST, start, end, flow="import")
        save_csv("comex_import.csv", imp_rows)
        exp_rows = get_trade_by_ncm(NCM_LIST, start, end, flow="export")
        save_csv("comex_export.csv", exp_rows)
    except Exception as e:
        print(f"[erro] Comex Stat: {e}")

    print("=== Coleta finalizada ===")
    print(
        "\nPróximo passo: preencher preços de concorrentes (scraping) em "
        "collectors/competitor_prices.py e usar calcular_alerta_margem() "
        "para cruzar com seu custo real."
    )


if __name__ == "__main__":
    main()
