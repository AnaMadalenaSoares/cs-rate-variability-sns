import pickle, numpy as np, pandas as pd
W='w/'; U='dados/'
MAP,shared,nopart=pickle.load(open(W+'map.pkl','rb'))
d=pd.read_excel(U+'Munic_pio-sa_de-recursos_humanos-total.xlsx',sheet_name='Quadro',header=None)
yrs=list(range(2013,2025)); R={}
for nm,c0 in [('med',39),('enf',51)]:
    x=d.iloc[12:,[0,1]+list(range(c0,c0+12))]; x.columns=['tipo','nome']+yrs
    mun=x[x.tipo=='Município'].set_index('nome')[yrs].astype(float)
    cont=x[x.nome=='Continente'].iloc[0][yrs].astype(float)
    mc=mun.loc[MAP.mun]
    print(nm,'missing names',set(MAP.mun)-set(mun.index))
    print(nm,'sum278 vs cont',{y:(int(mc[y].sum()),int(cont[y])) for y in yrs})
    print(nm,'zeros by year',{y:int((mc[y]==0).sum()) for y in yrs})
    ch=mc.pct_change(axis=1)*100
    print(nm,'munis with |chg|>30% (and base>=20)',{y:int(((ch[y].abs()>30)&(mc[y-1]>=20)).sum()) for y in yrs[1:]})
    for y in [2017,2019,2024]:
        z=pd.DataFrame({'prev':mc[y-1],'cur':mc[y],'nxt':mc[y+1] if y<2024 else np.nan,'chg':ch[y]})
        z=z[(z.prev>=100)&(z.chg.abs()>25)].sort_values('chg')
        print(nm,y,'large munis >25%:\n',z.to_string())
    R[nm]=(mc,cont)
pickle.dump(R,open(W+'m3me.pkl','wb'))
