import pandas as pd, pickle, numpy as np
W='w/'
d=pd.read_excel('dados/Munic_pio-sa_de-recursos_humanos-total.xlsx',sheet_name='Quadro',header=None)
S,S2,T,P_,R2,flag,um,COH,C2=pickle.load(open(W+'s.pkl','rb')); flag=pickle.load(open(W+'flag2.pkl','rb'))
LV=pickle.load(open(W+'s2.pkl','rb'))[0]
cand,seat,mun_units=pickle.load(open(W+'seat.pkl','rb')); B=pickle.load(open(W+'m5mun.pkl','rb'))
MAP,shared,nopart=pickle.load(open(W+'map.pkl','rb'))
yrs=list(range(2013,2024)); LP={'A03':'Lisboa','A24':'Lisboa','A25':'Lisboa','A12':'Porto','A30':'Porto'}
X={}
for nm,c0 in [('med',123),('enf',135)]:
    x=d.iloc[12:,[0,1]+list(range(c0,c0+12))]; x.columns=['tipo','nome']+list(range(2013,2025))
    X[nm]=x[x.tipo=='Município'].set_index('nome')[list(range(2013,2025))].astype(float)
    print(nm,'2024 nonzero',int((X[nm][2024]>0).sum()))
C={};R={};FL={}
for nm in X:
    cnt=pd.DataFrame(np.nan,index=T.index,columns=yrs); rat=cnt.copy()
    for u in T.index:
        for y in yrs:
            ms=seat[(u,y)]
            if u in LP:
                m=LP[u]; v=X[nm].at[m,y]
                if v>0: cnt.at[u,y]=v; rat.at[u,y]=v/B.at[m,y]*1000
                continue
            vals=[X[nm].at[m,y] for m in ms]
            if all(v>0 for v in vals): cnt.at[u,y]=sum(vals); rat.at[u,y]=sum(vals)/P_.at[u,y]*1000
            else: print('missing',nm,u,y,ms,vals)
    C[nm]=cnt;R[nm]=rat
# omitted staff: municipalities with SNS staff >0 not used as seat, mapped by C1 to unit
om={}
for nm in X:
    rows=[]
    used={(m,y) for (u,y),ms in seat.items() for m in ms if y in yrs}|{(m,y) for m in ('Lisboa','Porto') for y in yrs}
    for _,r in MAP.iterrows():
        for y in yrs:
            v=X[nm].at[r.mun,y]
            if v>0 and (r.mun,y) not in used:
                rows.append((r.mun,y,v,r.c,r.x))
    om[nm]=pd.DataFrame(rows,columns=['mun','ano','v','uls','x'])
    z=om[nm].pivot_table(index=['mun','uls'],columns='ano',values='v',aggfunc='sum')
    print('== omitted',nm); print(z.to_string())
pickle.dump((C,R,om,X),open(W+'s8b.pkl','wb'))
