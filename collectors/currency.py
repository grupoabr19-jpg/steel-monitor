"""
Coleta câmbio em tempo real. Fonte principal: AwesomeAPI. Como o GitHub Actions
roda em servidores compartilhados por milhares de usuários, é comum a
AwesomeAPI bloquear por excesso de uso (HTTP 429) vindo desses IPs — nesse
caso, cai automaticamente para a frankfurter.app (fonte do Banco Central
Europeu, sem limite de uso e sem necessidade de chave).

Doc AwesomeAPI: https://docs.awesomeapi.com.br/api-de-moedas
Doc Frankfurter: https://www.frankfurter.app/docs
"""
import requests
from datetime import datetime, timezone

AWESOME_URL = "https://economia.awesomeapi.com.br/json/last"
FRANKFURTER_URL = "https://api.frankfurter.app/latest"


def _via_awesomeapi(pares: list[str]) -> list[dict]:
    codigos = ",".join(pares)
    resp = requests.get(f"{AWESOME_URL}/{codigos}", timeout=15)
    resp.raise_for_status()
    payload = resp.json()

    now = datetime.now(timezone.utc).isoformat()
    results = []
    for par, dados in payload.items():
        results.append({
            "fonte": "awesomeapi",
            "par": f"{dados.get('code')}-{dados.get('codein')}",
            "preco_compra": float(dados.get("bid", 0)),
            "preco_venda": float(dados.get("ask", 0)),
            "variacao_pct": float(dados.get("pctChange", 0)),
            "coletado_em": now,
        })
    return results


def _via_frankfurter(pares: list[str]) -> list[dict]:
    """Fallback sem limite de uso. Não tem compra/venda separadas, só uma taxa."""
    now = datetime.now(timezone.utc).isoformat()
    results = []
    for par in pares:
        moeda_origem, moeda_destino = par.split("-")
        resp = requests.get(
            FRANKFURTER_URL,
            params={"from": moeda_origem, "to": moeda_destino},
            timeout=15,
        )
        resp.raise_for_status()
        payload = resp.json()
        taxa = payload.get("rates", {}).get(moeda_destino)
        results.append({
            "fonte": "frankfurter",
            "par": par,
            "preco_compra": taxa,
            "preco_venda": taxa,
            "variacao_pct": None,
            "coletado_em": now,
        })
    return results


def get_rates(pares: list[str]) -> list[dict]:
    """pares no formato ['USD-BRL', 'EUR-BRL']"""
    try:
        return _via_awesomeapi(pares)
    except requests.exceptions.HTTPError as e:
        print(f"[aviso] AwesomeAPI falhou ({e}), tentando frankfurter.app...")
        return _via_frankfurter(pares)


if __name__ == "__main__":
    from config import MOEDAS
    for row in get_rates(MOEDAS):
        print(row)
