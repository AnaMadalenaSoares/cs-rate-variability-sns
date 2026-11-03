# -*- coding: utf-8 -*-
"""
f13_longitudinal.py
Análise longitudinal: associação, DENTRO de cada hospital, entre o volume anual
de partos e a taxa anual de cesarianas (SNS, 2013–2025).

Especificação (definida pelo orientador, não alterar):
    TaxaCS_it = beta * ln(Partos_it) + alpha_i + gamma_t + e_it
    - alpha_i: efeitos fixos de hospital (unidade)
    - gamma_t: efeitos fixos de ano
    - erros-padrão agrupados por hospital
    - sem outras covariáveis

Fonte: Excel 1 – hospitais, folha "SNS transparência" (dados mensais SNS Transparência).

Como correr (na pasta scripts_analise_CS):
    python f13_longitudinal.py
ou indicando o caminho do Excel:
    python f13_longitudinal.py caminho/para/Excel_1_-_hospitais.xlsx

Saídas (pasta w/):
    f13_estrutura_resumo.csv          resumo da estrutura do painel
    f13_completude_mensal.csv         meses por unidade-ano (só os que não têm 12)
    f13_valores_implausiveis.csv      meses com partos/cesarianas em falta, nulos ou negativos
    f13_unidades_excluidas.csv        unidades excluídas e motivo
    f13_designacoes_por_codigo.csv    designações de cada código ao longo do tempo
    f13_variacoes_bruscas.csv         variações anuais de ln(partos) superiores a 0,25 em valor absoluto
    f13_dp_within_por_hospital.csv    desvio-padrão de ln(partos) dentro de cada hospital
    f13_obs_excluidas_sensibilidade.csv  observações excluídas na análise de sensibilidade
    f13_resultados.csv                coeficientes, EP agrupado, IC 95 %, p-value, n, R² within
    f13_painel_anual.csv              base hospital-ano usada nas estimações

Requisitos: pandas, numpy, openpyxl, linearmodels
"""

import os
import sys

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

# ---------------------------------------------------------------------------
# Parâmetros
# ---------------------------------------------------------------------------
FICHEIRO = sys.argv[1] if len(sys.argv) > 1 else os.path.join("dados", "Excel_1_-_hospitais.xlsx")
FOLHA = "SNS transparência"
PASTA_SAIDA = sys.argv[2] if len(sys.argv) > 2 else "w"
ANO_INICIAL, ANO_FINAL = 2013, 2025   # 2026 excluído: só contém janeiro–abril

# Colunas usadas
C_UNI = "Hospital per year"      # código anonimizado da unidade (A01–A40)
C_INST = "Instituição"
C_PER = "Período"                # AAAA-MM
C_ANO = "Ano"
C_PARTOS_M = "Nº total partos"           # partos no mês
C_CS_M = "Nº total cesarianas"           # cesarianas no mês
C_PARTOS_CUM = "Nº Total de Partos cumulativo"   # acumulado no ano
C_CS_CUM = "Nº Cesarianas cumulativo"

# Períodos com interrupções relevantes da atividade obstétrica (análise de sensibilidade)
INTERRUPCOES = [
    ("A07", 2023, "Hospital das Caldas da Rainha: serviço de obstetrícia (internamento, bloco de partos "
                  "e urgência) suspenso para obras de 1 de junho a 13 de novembro de 2023"),
    ("A25", 2023, "Hospital de Santa Maria: bloco de partos e urgência obstétrica encerrados para obras "
                  "a partir de agosto de 2023"),
    ("A25", 2024, "Hospital de Santa Maria: encerramento para obras até à reabertura faseada "
                  "(urgência em agosto de 2024, maternidade a partir de setembro de 2024)"),
    ("A17", 2025, "Hospital de Vila Franca de Xira: encerramentos recorrentes da urgência obstétrica "
                  "a partir do verão de 2025, com forte redução dos partos no 2.º semestre"),
]

os.makedirs(PASTA_SAIDA, exist_ok=True)
saida = lambda nome: os.path.join(PASTA_SAIDA, nome)


# ---------------------------------------------------------------------------
# 1. Leitura dos dados mensais
# ---------------------------------------------------------------------------
m = pd.read_excel(FICHEIRO, sheet_name=FOLHA)
m = m.dropna(subset=[C_UNI])                 # remove linhas vazias no fim da folha
m[C_ANO] = m[C_ANO].astype(int)
m[C_INST] = m[C_INST].str.strip()
m = m[(m[C_ANO] >= ANO_INICIAL) & (m[C_ANO] <= ANO_FINAL)].copy()


# ---------------------------------------------------------------------------
# 2. Verificação da estrutura e da completude
# ---------------------------------------------------------------------------

# 2.1 Meses disponíveis por unidade-ano (registam-se apenas os casos com menos de 12 meses)
meses = m.groupby([C_UNI, C_ANO])[C_PER].nunique().rename("meses").reset_index()
meses[meses["meses"] < 12].to_csv(saida("f13_completude_mensal.csv"), index=False)

# 2.2 Valores mensais em falta, nulos ou negativos
impl = m[
    m[C_PARTOS_M].isna() | m[C_CS_M].isna()
    | (m[C_PARTOS_M] <= 0) | (m[C_CS_M] < 0)
    | (m[C_CS_M] > m[C_PARTOS_M])
][[C_UNI, C_PER, C_PARTOS_M, C_CS_M]]
impl.to_csv(saida("f13_valores_implausiveis.csv"), index=False)

# 2.3 Totais anuais: usa-se o valor acumulado do último mês do ano, que é o total oficial.
#     Verifica-se se coincide com a soma dos valores mensais (os valores mensais negativos
#     são correções e anulam-se no total anual).
m = m.sort_values([C_UNI, C_PER])
g = m.groupby([C_UNI, C_ANO])
anual = pd.DataFrame({
    "partos": g[C_PARTOS_CUM].last(),
    "cesarianas": g[C_CS_CUM].last(),
    "partos_soma_mensal": g[C_PARTOS_M].sum(),
    "cesarianas_soma_mensal": g[C_CS_M].sum(),
}).reset_index().rename(columns={C_UNI: "hospital", C_ANO: "ano"})
anual["coincide_soma_mensal"] = (
    np.isclose(anual["partos"].fillna(-1), anual["partos_soma_mensal"])
    & np.isclose(anual["cesarianas"].fillna(-1), anual["cesarianas_soma_mensal"])
)

# 2.4 Unidades sem partos em todo o período: excluídas (não têm atividade obstétrica)
tot = anual.groupby("hospital")["partos"].sum(min_count=1)
sem_partos = tot[(tot.fillna(0) == 0)].index.tolist()
excl = pd.DataFrame({
    "hospital": sem_partos,
    "motivo": "sem partos registados em todo o período",
    "anos_com_registo": [", ".join(map(str, anual.loc[anual.hospital == h, "ano"])) for h in sem_partos],
})
excl.to_csv(saida("f13_unidades_excluidas.csv"), index=False)
anual = anual[~anual["hospital"].isin(sem_partos)].copy()

# 2.5 Designações de cada código ao longo do tempo (mudanças de nome, fusões, ULS de 2024)
desig = (m[~m[C_UNI].isin(sem_partos)]
         .groupby([C_UNI, C_INST])[C_ANO].agg(["min", "max"]).reset_index()
         .rename(columns={C_UNI: "hospital", C_INST: "designacao", "min": "ano_inicio", "max": "ano_fim"})
         .sort_values(["hospital", "ano_inicio"]))
desig.to_csv(saida("f13_designacoes_por_codigo.csv"), index=False)

# 2.6 Variáveis do modelo
anual["taxa_cs"] = 100 * anual["cesarianas"] / anual["partos"]
anual["ln_partos"] = np.log(anual["partos"])

# 2.7 Variações anuais bruscas de ln(partos) (> 0,25 em valor absoluto, cerca de ±28 %):
#     possíveis indícios de encerramentos, fusões ou mudanças de perímetro
anual = anual.sort_values(["hospital", "ano"])
anual["dif_ln_partos"] = anual.groupby("hospital")["ln_partos"].diff()
anual.loc[anual["dif_ln_partos"].abs() > 0.25,
          ["hospital", "ano", "partos", "dif_ln_partos"]].to_csv(saida("f13_variacoes_bruscas.csv"), index=False)

# 2.8 Variação do volume DENTRO de cada hospital (é desta variação que o modelo depende)
dp = (anual.groupby("hospital")
      .agg(partos_min=("partos", "min"), partos_max=("partos", "max"),
           dp_ln_partos=("ln_partos", "std"))
      .reset_index())
dp.to_csv(saida("f13_dp_within_por_hospital.csv"), index=False)
dp_within_global = (anual["ln_partos"] - anual.groupby("hospital")["ln_partos"].transform("mean")).std()

# 2.9 Resumo da estrutura do painel
n_hosp = anual["hospital"].nunique()
n_anos = anual["ano"].nunique()
obs_por_hosp = anual.groupby("hospital").size()
resumo = pd.DataFrame([
    ("Período", f"{ANO_INICIAL}–{ANO_FINAL}"),
    ("Hospitais incluídos", n_hosp),
    ("Anos", n_anos),
    ("Observações hospital-ano", len(anual)),
    ("Painel equilibrado", "sim" if (obs_por_hosp == n_anos).all() else "não"),
    ("Hospitais com anos em falta", ", ".join(obs_por_hosp[obs_por_hosp < n_anos].index) or "nenhum"),
    ("Unidades excluídas (sem partos)", ", ".join(sem_partos) or "nenhuma"),
    ("Unidade-ano com menos de 12 meses", int((meses.loc[~meses[C_UNI].isin(sem_partos), "meses"] < 12).sum())),
    ("Meses com valores em falta, nulos ou implausíveis", int((~impl[C_UNI].isin(sem_partos)).sum())),
    ("Totais anuais = soma dos meses", "sim" if anual["coincide_soma_mensal"].all() else "não"),
    ("Partos por hospital-ano (mín.–máx.)", f"{int(anual.partos.min())}–{int(anual.partos.max())}"),
    ("Taxa de cesarianas (mín.–máx., %)", f"{anual.taxa_cs.min():.1f}–{anual.taxa_cs.max():.1f}"),
    ("DP de ln(partos) dentro dos hospitais (global)", round(dp_within_global, 3)),
    ("DP de ln(partos) por hospital (mediana; mín.–máx.)",
     f"{dp.dp_ln_partos.median():.3f}; {dp.dp_ln_partos.min():.3f}–{dp.dp_ln_partos.max():.3f}"),
], columns=["indicador", "valor"])
resumo.to_csv(saida("f13_estrutura_resumo.csv"), index=False)
anual.to_csv(saida("f13_painel_anual.csv"), index=False)


# ---------------------------------------------------------------------------
# 3. Estimação: PanelOLS com efeitos fixos de hospital e de ano,
#    erros-padrão agrupados por hospital
# ---------------------------------------------------------------------------
def estimar(dados, etiqueta):
    p = dados.set_index(["hospital", "ano"])
    mod = PanelOLS(p["taxa_cs"], p[["ln_partos"]], entity_effects=True, time_effects=True)
    r = mod.fit(cov_type="clustered", cluster_entity=True)
    b = r.params["ln_partos"]
    ic = r.conf_int().loc["ln_partos"]
    return {
        "especificacao": etiqueta,
        "beta": b,
        "ep_agrupado": r.std_errors["ln_partos"],
        "ic95_inf": ic["lower"],
        "ic95_sup": ic["upper"],
        "p_value": r.pvalues["ln_partos"],
        "n_obs": int(r.nobs),
        "n_hospitais": int(r.entity_info["total"]),
        "r2_within": r.rsquared_within,
        "variacao_pp_aumento_10pct": b * np.log(1.10),
    }

# 3.1 Modelo principal: todas as observações
resultados = [estimar(anual, "Principal: todas as observações")]

# 3.2 Análise de sensibilidade: exclui os períodos com interrupções relevantes
idx_int = pd.MultiIndex.from_tuples([(h, a) for h, a, _ in INTERRUPCOES])
mask = anual.set_index(["hospital", "ano"]).index.isin(idx_int)
pd.DataFrame(INTERRUPCOES, columns=["hospital", "ano", "motivo"]).merge(
    anual[["hospital", "ano", "partos", "taxa_cs"]], on=["hospital", "ano"], how="left"
).to_csv(saida("f13_obs_excluidas_sensibilidade.csv"), index=False)
resultados.append(estimar(anual[~mask], "Sensibilidade: sem períodos com interrupções relevantes"))

res = pd.DataFrame(resultados)
res.to_csv(saida("f13_resultados.csv"), index=False)


# ---------------------------------------------------------------------------
# 4. Impressão no ecrã
# ---------------------------------------------------------------------------
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)
print("\n=== Estrutura do painel ===")
print(resumo.to_string(index=False))
print("\n=== Unidades excluídas ===")
print(excl.to_string(index=False))
print("\n=== Unidade-ano com menos de 12 meses ===")
print(meses[(meses["meses"] < 12) & ~meses[C_UNI].isin(sem_partos)].to_string(index=False))
print("\n=== Meses com valores em falta, nulos ou negativos (excluindo unidades sem partos) ===")
print(impl[~impl[C_UNI].isin(sem_partos)].to_string(index=False))
print("\n=== Códigos com mais de duas designações ===")
k = desig.groupby("hospital").size()
print(desig[desig.hospital.isin(k[k > 2].index)].to_string(index=False))
print("\n=== Variações anuais bruscas de ln(partos) (|dif| > 0,25) ===")
print(pd.read_csv(saida("f13_variacoes_bruscas.csv")).round(3).to_string(index=False))
print("\n=== DP de ln(partos) dentro de cada hospital (5 menores e 5 maiores) ===")
d = dp.sort_values("dp_ln_partos").round(3)
print(pd.concat([d.head(5), d.tail(5)]).to_string(index=False))
print(f"\nObservações excluídas na sensibilidade: {int(mask.sum())}")
print("\n=== Resultados ===")
print(res.round(4).to_string(index=False))
