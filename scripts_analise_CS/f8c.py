import pandas as pd, pickle, numpy as np
W='w/'
S,S2,T,P_,R2,flag,um,COH,C2=pickle.load(open(W+'s.pkl','rb')); flag=pickle.load(open(W+'flag2.pkl','rb'))
LV=pickle.load(open(W+'s2.pkl','rb'))[0]
cand,seat,mun_units=pickle.load(open(W+'seat.pkl','rb')); B=pickle.load(open(W+'m5mun.pkl','rb'))
C,R,om,X=pickle.load(open(W+'s8b.pkl','rb'))
yrs=list(range(2013,2024)); LP=['A03','A24','A25','A12','A30']
chg={('A06',2017),('A06',2018),('A06',2019),('A04',2019)}
def f(x,d=0):
    if x is None or (isinstance(x,float) and np.isnan(x)): return 'n.d.'
    return f'{round(float(x),d)+0.0:.{d}f}'.replace('.',',')
def md(df):
    cols=[str(c) for c in df.columns]; s='| '+' | '.join(cols)+' |\n|'+'|'.join(['---']*len(cols))+'|\n'
    for _,r in df.iterrows(): s+='| '+' | '.join(str(v) for v in r.values)+' |\n'
    return s
out=open(W+'out8b.md','w')
for nm in ['enf','med']:
    t=pd.DataFrame({'Código':T.index,'Nível':[LV[c] for c in T.index]})
    for y in yrs:
        t[str(y) if y!=2019 else '2019 ┴']=[f(R[nm].at[c,y])+('ᴸ' if c in LP else '')+('§' if (c,y) in chg else '')+('†' if (c,y) in flag else '') for c in T.index]
    t['2024']='n.d.'
    print('##',nm,file=out); print(md(t),file=out)
    d=[]
    for y in yrs:
        x=R[nm][y]; x2=x.drop(LP)
        d.append((y,f(x.median()),f(x2.median()),f(x2.min()),x2.idxmin(),f(x2.max()),x2.idxmax()))
    print(nm,'desc',d,file=out)
    # omitted share by unit, 2013-2018 vs seat count
    o=om[nm]; o=o[~o.uls.isin(['A38','A39','A40'])]
    sh={}
    for u in sorted(o.uls.unique()):
        r=[]
        for y in range(2013,2019):
            ov=o[(o.uls==u)&(o.ano==y)].v.sum(); base=C[nm].at[u,y]
            r.append(100*ov/(ov+base) if base==base else np.nan)
        r2=[]
        for y in range(2019,2024):
            ov=o[(o.uls==u)&(o.ano==y)].v.sum(); base=C[nm].at[u,y]; r2.append(100*ov/(ov+base))
        sh[u]=(f(np.nanmean(r),1),f(max(r),1),f(np.mean(r2),1),', '.join(sorted(o[o.uls==u].mun.unique())))
    print(nm,'omitted',sh,file=out)
    # 2018->2019 change in count per unit
    ch=(C[nm][2019]/C[nm][2018]-1)*100
    print(nm,'chg18-19',{c:f(ch[c],1) for c in T.index},file=out)
    print(nm,'counts',{c:(f(C[nm].at[c,2013]),f(C[nm].at[c,2018]),f(C[nm].at[c,2019]),f(C[nm].at[c,2023])) for c in T.index},file=out)
print('Lisboa births',{y:int(B.at['Lisboa',y]) for y in yrs},'Porto',{y:int(B.at['Porto',y]) for y in yrs},file=out)
print('LP unit births sum Lisboa', {y:int(P_.loc[['A03','A24','A25'],y].sum()) for y in yrs},'Porto',{y:int(P_.loc[['A12','A30'],y].sum()) for y in yrs},file=out)
out.close()
