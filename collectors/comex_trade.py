"""
Coleta dados oficiais de exportação/importação brasileira de produtos de aço
via API do Comex Stat (MDIC/SECEX) — gratuita, sem necessidade de chave.

Usa a lib comexpy (wrapper Python não-oficial, mas ativo, sobre a API oficial
https://api-comexstat.mdic.gov.br). Instale com: pip install comexpy

A API tem rate limit agressivo — se receber erro 429, aumente o retry_time.
"""
from datetime import datetime, timezone

import comexpy

comexpy.set_verbose(False)
comexpy.set_options(retry_time=20, max_tries=5, timeout_post=120)


def get_trade_by_ncm(ncm_list: list[str], start_period: str, end_period: str,
                      flow: str = "import") -> list[dict]:
    """
    flow: 'import' ou 'export'
    start_period/end_period: 'YYYY-MM'
    Retorna valor FOB (US$) e peso (kg) agregados por país, para os NCMs dados.
    """
    func = comexpy.comex_import if flow == "import" else comexpy.comex_export

    df = func(
        start_period=start_period,
        end_period=end_period,
        details=["country", "ncm"],
        filters={"ncm": ncm_list},
    )

    now = datetime.now(timezone.utc).isoformat()
    results = []
    for _, row in df.iterrows():
        results.append({
            "fonte": "comexstat_mdic",
            "fluxo": flow,
            "ncm": row.get("ncm") or row.get("co_ncm"),
            "pais": row.get("country") or row.get("no_pais"),
            "valor_fob_usd": row.get("metric_fob") or row.get("vl_fob"),
            "peso_kg": row.get("metric_kg") or row.get("kg_liquido"),
            "periodo": f"{start_period}_a_{end_period}",
            "coletado_em": now,
        })
    return results


if __name__ == "__main__":
    from config import NCM_LIST
    # Exemplo: importações do último mês fechado
    dados = get_trade_by_ncm(NCM_LIST, "2026-08", "2026-08", flow="import")
    for row in dados[:10]:
        print(row)
