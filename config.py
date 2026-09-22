"""
Configurações centrais do sistema de monitoramento de aço.
Ajuste os valores abaixo para refletir sua operação real.
"""

# --- Ações de siderúrgicas na B3 (proxy de sentimento de mercado) ---
TICKERS_B3 = [
    "GGBR4",  # Gerdau
    "CSNA3",  # CSN
    "USIM5",  # Usiminas
    "VALE3",  # Vale (minério de ferro, insumo)
]

# --- Câmbio relevante para aço importado/exportado ---
MOEDAS = ["USD-BRL", "EUR-BRL"]

# --- NCMs de produtos de aço (ajuste para o(s) produto(s) que você compra/vende) ---
# Exemplos comuns:
#   7208 - Produtos laminados planos de ferro/aço, não ligado, largura >= 600mm
#   7213 - Fio-máquina de ferro ou aço não ligado
#   7214 - Barras de ferro/aço não ligado, não trabalhadas além de forjadas/laminadas
#   7216 - Perfis de ferro/aço não ligado
NCM_LIST = ["7208", "7213", "7214", "7216"]

# --- Países de interesse para comparação de fornecimento (Comex Stat) ---
PAISES_REFERENCIA = ["China", "Estados Unidos", "Argentina", "Turquia", "Ucrânia"]

# --- Parâmetros de negócio (margem) ---
MARGEM_MINIMA_PCT = 15.0  # margem mínima aceitável, em %
CUSTO_FIXO_TONELADA_BRL = 0.0  # frete/seguro/taxas fixas por tonelada, se quiser embutir

# --- Onde salvar os dados coletados ---
OUTPUT_DIR = "data"
