"""
Coleta cotações das ações de siderúrgicas na B3 via brapi.dev (API v2).
Serve como termômetro do humor do mercado/setor no Brasil.

Doc: https://brapi.dev/docs.mdx
Requer token (gratuito) em TODOS os tickers desde a migração para v2 —
crie uma conta em brapi.dev e defina a variável de ambiente BRAPI_TOKEN.
O token nunca é lido de código nem de arquivo versionado, só de env var,
e este módulo roda apenas no backend/CI (nunca no navegador/frontend).
"""
import os
from datetime import datetime, timezone
from typing import TypedDict

import requests

BASE_URL = "https://brapi.dev/api/v2/stocks/quote"


class StockQuoteData(TypedDict, total=False):
    shortName: str
    currency: str
    regularMarketPrice: float
    regularMarketChangePercent: float
    regularMarketVolume: int
    marketCap: float


class BrapiQuoteError(Exception):
    """Erro ao consultar a API de cotações da brapi.dev."""


def _auth_headers() -> dict[str, str]:
    token = os.getenv("BRAPI_TOKEN")
    if not token:
        raise BrapiQuoteError(
            "BRAPI_TOKEN não definido. Configure a variável de ambiente "
            "(no GitHub, como Secret do repositório) — nunca cole o token "
            "direto no código ou no .env versionado."
        )
    return {"Authorization": f"Bearer {token}"}


def fetch_quote(symbol: str) -> StockQuoteData:
    """
    Busca a cotação de um único ticker (ex: 'B3SA3').
    Lança BrapiQuoteError em qualquer resposta não-2xx, falha de rede,
    ou payload sem resultados.
    """
    try:
        resp = requests.get(
            BASE_URL,
            headers=_auth_headers(),
            params={"symbols": symbol},
            timeout=15,
        )
    except requests.exceptions.RequestException as e:
        raise BrapiQuoteError(f"Falha de rede ao consultar '{symbol}': {e}") from e

    if not resp.ok:
        raise BrapiQuoteError(
            f"brapi.dev retornou {resp.status_code} para '{symbol}': "
            f"{resp.text[:200]}"
        )

    payload = resp.json()
    results = payload.get("results") or []
    if not results:
        raise BrapiQuoteError(f"Nenhum resultado retornado para '{symbol}'.")

    return results[0]["data"]


def get_quotes(tickers: list[str]) -> list[dict]:
    """
    Busca vários tickers em uma única requisição (mais eficiente — a brapi
    cobra por chamada, não por ticker). Usado pelo main.py para popular o CSV.
    """
    symbols_str = ",".join(tickers)

    try:
        resp = requests.get(
            BASE_URL,
            headers=_auth_headers(),
            params={"symbols": symbols_str},
            timeout=15,
        )
    except requests.exceptions.RequestException as e:
        raise BrapiQuoteError(f"Falha de rede ao consultar {tickers}: {e}") from e

    if not resp.ok:
        raise BrapiQuoteError(
            f"brapi.dev retornou {resp.status_code} para {tickers}: "
            f"{resp.text[:200]}"
        )

    payload = resp.json()
    now = datetime.now(timezone.utc).isoformat()
    rows = []
    for item in payload.get("results", []):
        data = item.get("data", {})
        rows.append({
            "fonte": "brapi.dev",
            "ticker": item.get("symbol"),
            "nome": data.get("shortName"),
            "preco": data.get("regularMarketPrice"),
            "variacao_pct": data.get("regularMarketChangePercent"),
            "volume": data.get("regularMarketVolume"),
            "coletado_em": now,
        })
    return rows


if __name__ == "__main__":
    from config import TICKERS_B3
    for row in get_quotes(TICKERS_B3):
        print(row)
