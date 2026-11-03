import pandas as pd, pickle, numpy as np
d=pd.read_excel('dados/Munic_pio-sa_de-recursos_humanos-total.xlsx',sheet_name='Quadro',header=None)
yrs=list(range(2013,2025))
cand,seat,mun_units=pickle.load(open('w/seat.pkl','rb'))
seats=sorted({m for v in seat.values() for m in v})
for nm,c0 in [('med',123),('enf',135),('tot',111),('hmed',75),('henf',87)]:
    x=d.iloc[12:,[0,1]+list(range(c0,c0+12))]; x.columns=['tipo','nome']+yrs
    print('==',nm)
    print(x[x.tipo.isin(['NUTS 2024','NUTS I','NUTS II'])].to_string())
    mun=x[x.tipo=='Município'].set_index('nome')[yrs].astype(float)
    print('munis with any >0:',int((mun.sum(axis=1)>0).sum()))
    if nm in('med','enf','hmed','henf'): print(mun.loc[[s for s in seats if s in mun.index]].to_string())
