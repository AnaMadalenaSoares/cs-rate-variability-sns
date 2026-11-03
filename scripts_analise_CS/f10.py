import pickle, numpy as np, pandas as pd
W='w/'
S,S2,T,P_,R2,flag,um,COH,C2=pickle.load(open(W+'s.pkl','rb')); flag=pickle.load(open(W+'flag2.pkl','rb'))
LV=pickle.load(open(W+'s2.pkl','rb'))[0]; RG=pickle.load(open(W+'s4.pkl','rb'))[0]
D=pickle.load(open(W+'d.pkl','rb'))[0]
Y=list(range(2013,2026))
vm=P_[Y].mean(axis=1); VC=pd.cut(vm,[0,600,1500,2500,1e9],right=False,labels=['<600','600–1499','1500–2499','≥2500']).astype(str)
PPP={(r.cod,r.ano) for r in D.itertuples() if r.setor=='PPP'}
f=lambda x,d=1:'n.d.' if x!=x else f'{round(float(x),d)+0.0:.{d}f}'.replace('.',',')
out=open(W+'out10.md','w')
def P(*a): print(*a,file=out)
m=T[Y].mean(axis=1)
def decomp(groups,label):
    # pooled within-group SD across units (unit means) and per year
    g=pd.Series(groups,index=T.index)
    tot=((m-m.mean())**2).sum(); within=sum(((m[g==k]-m[g==k].mean())**2).sum() for k in g.unique())
    ys=[]
    for y in Y:
        x=T[y]; tt=((x-x.mean())**2).sum(); ww=sum(((x[g==k]-x[g==k].mean())**2).sum() for k in g.unique()); ys.append(ww/tt)
    sizes=g.value_counts()
    P(f'{label}: groups {len(sizes)}, sizes {sizes.to_dict()}, within share unit means {f(100*within/tot)}%, pooled within SD {f(np.sqrt(within/len(m)),2)} vs total SD {f(np.sqrt(tot/len(m)),2)}; per-year within share median {f(100*np.median(ys))}% min {f(100*min(ys))} max {f(100*max(ys))}')
    return 100*within/tot,np.sqrt(within/len(m)),100*np.median(ys)
lv={c:('I/II' if LV[c]=='I/II' else LV[c]) for c in T.index}
steps=[('Nenhum (37 unidades)',{c:'all' for c in T.index}),('Nível',lv),('Região (7)',{c:RG[c] for c in T.index}),('Classe de volume',{c:VC[c] for c in T.index}),
       ('Nível × volume',{c:lv[c]+'|'+VC[c] for c in T.index}),('Nível × volume × região',{c:lv[c]+'|'+VC[c]+'|'+RG[c] for c in T.index})]
res=[]
for lab,gr in steps: res.append((lab,)+decomp(gr,lab))
# residuals vs level×volume cell median per year (cells <3 -> level median)
cell={c:lv[c]+'|'+VC[c] for c in T.index}
csize=pd.Series(cell).value_counts()
ref={c:(cell[c] if csize[cell[c]]>=3 else ('I (sens. A23)' if c=='A23' else 'nível '+lv[c])) for c in T.index}
P('cell sizes',csize.to_dict()); P('ref used',{c:ref[c] for c in T.index if ref[c]!=cell[c]})
RES=pd.DataFrame(index=T.index,columns=Y,dtype=float)
for y in Y:
    for c in T.index:
        if ref[c]==cell[c]: grp=[k for k in T.index if cell[k]==cell[c] and k!=c]
        elif c=='A23': grp=[k for k in T.index if lv[k]=='I']
        else: grp=[k for k in T.index if lv[k]==lv[c] and k!=c]
        RES.at[c,y]=T.at[c,y]-T.loc[grp,y].median()
up=(RES>=3).sum(axis=1); dn=(RES<=-3).sum(axis=1)
tab=pd.DataFrame({'Código':T.index,'Nível':[lv[c] for c in T.index],'Volume':[VC[c] for c in T.index],'Região':[RG[c] for c in T.index],'Grupo de referência':[ref[c] for c in T.index],
 'Taxa média 2013–2025':m.map(f).values,'Resíduo médio (p.p.)':RES.mean(axis=1).map(f).values,'Anos ≥ +3 p.p.':up.values,'Anos ≤ −3 p.p.':dn.values})
tab['Classificação']=['Atípica ↑' if u>=10 else 'Atípica ↓' if d>=10 else 'Quase ↑' if u>=7 else 'Quase ↓' if d>=7 else '' for u,d in zip(up,dn)]
RA=pd.Series({y:T.at['A23',y]-T.loc[[k for k in T.index if lv[k]=='II'],y].median() for y in Y})
P('A23 vs II: mean',f(RA.mean()),'up',int((RA>=3).sum()),'dn',int((RA<=-3).sum()))
P('## residual'); P(tab.to_string())
pickle.dump((RES,tab,res,ref),open(W+'s10.pkl','wb'))
# region pattern of residuals
P('res by region median',{g:f(RES.loc[[c for c in T.index if RG[c]==g]].mean(axis=1).median()) for g in sorted(set(RG.values()))})
# PPP residuals 2013-2019
pp=[RES.at[c,y] for (c,y) in PPP if y<=2019 and c in T.index]; P('PPP residual mean 2013-19',f(np.mean(pp)),'n',len(pp),{c:f(RES.loc[c,[y for y in range(2013,2020)]].mean()) for c in ['A15','A16','A17','A28']})
# residual SD within groups per year
P('residual SD per year',{y:f(RES[y].std(ddof=0),2) for y in Y},'IQR',{y:f(RES[y].quantile(.75)-RES[y].quantile(.25),2) for y in Y})
P('residual range per year',{y:(f(RES[y].min()),RES[y].idxmin(),f(RES[y].max()),RES[y].idxmax()) for y in Y})
P('n units |mean res|>=3',int((RES.mean(axis=1).abs()>=3).sum()),[c for c in T.index if abs(RES.loc[c].mean())>=3])
out.close()
# robustness: alternative references
out=open(W+'out10.md','a')
def cls(keyf):
    R=pd.DataFrame(index=T.index,columns=Y,dtype=float)
    for y in Y:
        for c in T.index:
            grp=[k for k in T.index if keyf(k)==keyf(c) and k!=c]
            if c=='A23' and keyf is not None and len(grp)==0: grp=[k for k in T.index if lv[k]=='I']
            R.at[c,y]=T.at[c,y]-T.loc[grp,y].median()
    u=(R>=3).sum(axis=1); d=(R<=-3).sum(axis=1)
    return {c:('A↑' if u[c]>=10 else 'A↓' if d[c]>=10 else 'Q↑' if u[c]>=7 else 'Q↓' if d[c]>=7 else '') for c in T.index}, R
alts={'Global':lambda k:'all','Nível':lambda k:lv[k],'Volume':lambda k:VC[k],'Região':lambda k:RG[k],'Nível×volume':lambda k:ref[k] if True else None}
C={}
for n,kf in alts.items():
    if n=='Nível×volume':
        C[n]={c:{'Atípica ↑':'A↑','Atípica ↓':'A↓','Quase ↑':'Q↑','Quase ↓':'Q↓','':''}[t] for c,t in zip(tab['Código'],tab['Classificação'])}
    else: C[n]=cls(kf)[0]
CT=pd.DataFrame(C); CT=CT[(CT!='').any(axis=1)]
print('## robustness',file=out); print(CT.to_string(),file=out)
# group composition for small cells
for k in ['II|600–1499','I|<600','III|≥2500','II|≥2500']: print(k,[c for c in T.index if cell[c]==k],{c:f(m[c]) for c in T.index if cell[c]==k},file=out)
pickle.dump((RES,tab,res,ref,CT),open(W+'s10.pkl','wb'))
out.close()
