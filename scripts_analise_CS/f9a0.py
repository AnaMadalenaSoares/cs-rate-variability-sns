import pandas as pd, numpy as np, pickle
U='dados/'
MAP=pickle.load(open('w/map.pkl','rb'))[0]
d=pd.read_excel(U+'Munic_pio-sa_de-recursos_humanos-total.xlsx',sheet_name='Quadro',header=None)
for r in []: print(r,[(c,str(d.iat[r,c])[:50]) for c in range(0,40) if str(d.iat[r,c])!='nan'])
def blk(df,c0,n=12,yrs=None):
    yrs=yrs or list(range(2013,2013+n))
    x=df.iloc[12:,[0,1]+list(range(c0,c0+n))]; x.columns=['tipo','nome']+yrs
    mun=x[x.tipo=='Município'].set_index('nome')[yrs].apply(pd.to_numeric,errors='coerce')
    cont=x[x.nome=='Continente'].iloc[0][yrs].apply(pd.to_numeric,errors='coerce')
    return mun.loc[MAP.mun],cont
for nm,c0,n in []:
    mun,cont=blk(d,c0,n)
    print('==',nm,'zeros/yr',{y:int((mun[y]==0).sum()) for y in mun.columns},'\n sum vs cont',{y:(int(mun[y].sum()),int(cont[y])) for y in mun.columns})
    print(' n mun with any>0',int((mun.sum(axis=1)>0).sum()))
m1=pd.read_excel(U+'Munic_pio-Popula__o-Esperan_a_de_vida_e_mortes-total.xlsx',sheet_name='Quadro',header=None)
for nm,c0 in [('neo',2),('peri',14),('tmi',26)]:
    x=m1.iloc[12:,[0,1]+list(range(c0,c0+12))]; x.columns=['tipo','nome']+list(range(2013,2025))
    raw=x[x.tipo=='Município'].set_index('nome').drop(columns='tipo')
    print('==',nm,'n mun',len(raw),'nonnum',set(v for v in raw.values.ravel() if isinstance(v,str)))
    mun=raw.apply(pd.to_numeric,errors='coerce')
    miss=set(MAP.mun)-set(mun.index); print(' missing',miss)
    mc=mun.loc[MAP.mun]; cont=x[x.nome=='Continente'].iloc[0][list(range(2013,2025))].apply(pd.to_numeric,errors='coerce')
    print(' zeros/yr',{y:int((mc[y]==0).sum()) for y in mc.columns},'nan',int(mc.isna().sum().sum()))
    if nm!='tmi': print(' sum vs cont',{y:(int(mc[y].sum()),int(cont[y])) for y in mc.columns})
    else: print(' cont',cont.to_dict())
mm=pd.read_excel(U+'Munic_pio-Popula__o-Esperan_a_de_vida_e_mortes-total.xlsx',sheet_name='Metainformação',header=None)
for i in range(len(mm)):
    v=[str(x) for x in mm.iloc[i] if str(x)!='nan']
    if v: print(i,' | '.join(v)[:500])
