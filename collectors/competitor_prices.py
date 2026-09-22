"""
Template de scraper de preços de concorrentes.

Não existe API pública para preço de concorrente — isso precisa ser raspado
das páginas públicas de cada um (catálogo, tabela de preços, e-commerce).

COMO USAR:
1. Para cada concorrente, adicione uma função `scrape_<nome>()` abaixo,
   seguindo o padrão do exemplo `scrape_exemplo()`.
2. Registre a função no dict COLETORES no final do arquivo.
3. Rode via `python competitor_prices.py` ou integre ao main.py.

BOAS PRÁTICAS:
- Raspe apenas páginas públicas (sem login).
- Respeite o robots.txt do site.
- Não sobrecarregue o servidor: 1 requisição a cada poucos segundos, no máximo.
- Sites com JavaScript pesado (React/Vue) podem precisar de Playwright/Selenium
  em vez de requests+BeautifulSoup puro.
"""
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup


def scrape_exemplo() -> list[dict]:
    """
    EXEMPLO — substitua pela URL e pelos seletores CSS reais do concorrente.
    Inspecione a página (F12 no navegador) para achar a classe/id do preço.
    """
    url = "https://www.exemplo-concorrente.com.br/produtos/vergalhao-ca50"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; SteelMonitorBot/1.0)"}

    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # AJUSTE o seletor abaixo para o site real:
    preco_tag = soup.select_one(".preco-produto")
    preco = None
    if preco_tag:
        texto = preco_tag.get_text(strip=True)
        preco = float(
            texto.replace("R$", "").replace(".", "").replace(",", ".").strip()
        )

    return [{
        "fonte": "scrape_exemplo",
        "concorrente": "Concorrente Exemplo",
        "produto": "Vergalhão CA-50",
        "preco_brl": preco,
        "url": url,
        "coletado_em": datetime.now(timezone.utc).isoformat(),
    }]


# Registre aqui cada concorrente mapeado
COLETORES = {
    "exemplo": scrape_exemplo,
    # "concorrente_a": scrape_concorrente_a,
    # "concorrente_b": scrape_concorrente_b,
}


def coletar_todos() -> list[dict]:
    resultados = []
    for nome, func in COLETORES.items():
        try:
            resultados.extend(func())
        except Exception as e:
            print(f"[erro] scraper '{nome}': {e}")
    return resultados


if __name__ == "__main__":
    for row in coletar_todos():
        print(row)
