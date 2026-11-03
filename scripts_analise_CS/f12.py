import pickle, numpy as np, pandas as pd
W='w/'
S,S2,T,P_,*_=pickle.load(open(W+'s.pkl','rb')); flag=pickle.load(open(W+'flag2.pkl','rb'))
LV=pickle.load(open(W+'s2.pkl','rb'))[0]; RG=pickle.load(open(W+'s4.pkl','rb'))[0]
RES10,tab10,steps10,ref10,CT10=pickle.load(open(W+'s10.pkl','rb'))
Y=list(range(2013,2026)); lv={c:LV[c] for c in T.index}
vm=P_[Y].mean(axis=1); VC=pd.cut(vm,[0,600,1500,2500,1e9],right=False,labels=['<600','600–1499','1500–2499','≥2500']).astype(str)
cell={c:lv[c]+'|'+VC[c] for c in T.index}; csize=pd.Series(cell).value_counts()
keys={'Global':lambda k:'all','Nível':lambda k:lv[k],'Volume':lambda k:VC[k],'Região':lambda k:RG[k],'Nível×volume':None}
def grp_nv(c):
    if csize[cell[c]]>=3: return [k for k in T.index if cell[k]==cell[c] and k!=c]
    if c=='A23': return [k for k in T.index if lv[k]=='I']
    return [k for k in T.index if lv[k]==lv[c] and k!=c]
def counts(c,TT,years):
    out={}
    for n,kf in keys.items():
        u=d=0
        for y in years:
            if np.isnan(TT.at[c,y]): continue
            grp=grp_nv(c) if kf is None else [k for k in T.index if kf(k)==kf(c) and k!=c]
            if not grp: grp=[k for k in T.index if lv[k]=='I']
            r=TT.at[c,y]-TT.loc[grp,y].median()
            u+=r>=3; d+=r<=-3
        out[n]=(u,d)
    return out
f=lambda x:f'{x:.1f}'.replace('.',',')
print('A25 flags',[y for (c,y) in flag if c=='A25'])
yrs_ok=[y for y in Y if ('A25',y) not in flag]
print('A25 all years',counts('A25',T,Y))
print('A25 without own R2b',len(yrs_ok),counts('A25',T,yrs_ok))
T2=T.copy()
for (c,y) in flag:
    if y in Y: T2.at[c,y]=np.nan
print('A25 all R2b removed (peers too)',counts('A25',T2,Y))
for c in ['A09','A25','A27']:
    print(c,'cell',cell[c],'peers',grp_nv(c))
    for n,kf in keys.items():
        grp=grp_nv(c) if kf is None else [k for k in T.index if kf(k)==kf(c) and k!=c]
        med=np.mean([T.loc[grp,y].median() for y in Y]); print('  ',n,'n peers',len(grp),'mean peer median',f(med),'unit mean',f(T.loc[c,Y].mean()))
# annual residual A25 vs references
for n,kf in keys.items():
    grp=grp_nv('A25') if kf is None else [k for k in T.index if kf(k)==kf('A25') and k!=c]
