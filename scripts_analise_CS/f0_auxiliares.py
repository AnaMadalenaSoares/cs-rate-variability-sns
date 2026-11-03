# Fase 0 – ficheiros auxiliares.
# Estes quatro ficheiros intermédios foram criados durante a conversa com comandos
# executados diretamente (não ficaram guardados como script). Os seus conteúdos
# foram exportados para a pasta dados_intermedios/ e este script reconstrói-os
# em w/, no formato que os scripts seguintes esperam.
#   - r2b_unidades_ano.csv          -> w/flag2.pkl  (10 unidades-ano R2b, incl. A02 2023 manual)
#   - tabela6_municipios_sede.json  -> w/seat.pkl   (Tabela 6: município sede por unidade e ano)
#   - m4_ocupacao_por_municipio.csv -> w/m4.pkl     (taxa de ocupação por município, [M4])
#   - m5_partos_SNS_por_municipio.csv -> w/m5mun.pkl (partos SNS por município, [M5])
import os, json, pickle, pandas as pd

I = 'dados_intermedios/'
W = 'w/'
os.makedirs(W, exist_ok=True)

r = pd.read_csv(I + 'r2b_unidades_ano.csv')
pickle.dump({(c, int(y)) for c, y in zip(r.codigo, r.ano)}, open(W + 'flag2.pkl', 'wb'))

j = json.load(open(I + 'tabela6_municipios_sede.json', encoding='utf-8'))
sede_ano = {(k.split('|')[0], int(k.split('|')[1])): v for k, v in j['sede_por_unidade_ano'].items()}
pickle.dump((j['sede_por_unidade'], sede_ano, j['unidades_por_municipio']), open(W + 'seat.pkl', 'wb'))

for csv, pkl in [('m4_ocupacao_por_municipio.csv', 'm4.pkl'), ('m5_partos_SNS_por_municipio.csv', 'm5mun.pkl')]:
    d = pd.read_csv(I + csv, index_col='mun')
    d.columns = pd.Index([int(c) for c in d.columns], dtype=object)
    pickle.dump(d, open(W + pkl, 'wb'))

print('Ficheiros auxiliares criados em', W)
