import pickle, numpy as np, pandas as pd
W='w/'
U='dados/'
# municipal mapping from C1
m=pd.read_excel(U+'Correla__o_munic_pios_final.xlsx',header=None)
n2='Norte';n3=None;rows=[]
for _,x in m.iterrows():
    if x[6]=='NUTS II': n2=x[7]
    if x[6]=='NUTS III': n3=x[7]
    if x[6]=='Município': rows.append((n2,n3,x[7],x[8],x[9],x[10]))
MAP=pd.DataFrame(rows,columns=['n2','n3','mun','c','x','y'])
def ulsof(r,year):
    if r.x=='depois 2024': return [r.y] if year>=2024 else [r.c]
    if isinstance(r.x,str) and r.x.startswith('A'): return [r.c,r.x]+([r.y] if isinstance(r.y,str) and r.y.startswith('A') else [])
    return [r.c]   # Ovar: 'jan-set 2024 foi' -> always A05 (c)
shared={'Porto','Lisboa','Cascais','Belmonte'}
nopart={'A38','A39','A40'}
pickle.dump((MAP,shared,nopart),open(W+'map.pkl','wb'))
print(MAP[MAP.x.notna()][['mun','c','x','y']].to_string())
# M3 GO
d=pd.read_excel(U+'Munic_pio-sa_de-recursos_humanos-total.xlsx',sheet_name='Quadro',header=None)
go=d.iloc[12:,[0,1]+list(range(14,26))]; go.columns=['tipo','nome']+list(range(2013,2025)); go=go[go.tipo.isin(['Município','NUTS I','NUTS II','NUTS III','NUTS 2024'])]
mun=go[go.tipo=='Município'].set_index('nome')[list(range(2013,2025))].astype(float)
cont=go[go.nome=='Continente'].iloc[0][list(range(2013,2025))].astype(float)
print('names not in C1', sorted(set(mun.index)-set(MAP.mun)), 'C1 not in M3', sorted(set(MAP.mun)-set(mun.index)))
print('sum mun vs continente', (mun.sum()-cont).to_dict())
# NUTS III check vs sum
pickle.dump((mun,cont),open(W+'m3go.pkl','wb'))
