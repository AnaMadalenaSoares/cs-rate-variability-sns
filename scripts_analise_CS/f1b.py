import pandas as pd, numpy as np, pickle
W='w/'
U='dados/'
D,chk,sec,m=pickle.load(open(W+'d.pkl','rb'))
def f(x,d=1):
    if x is None or (isinstance(x,float) and np.isnan(x)): return 'a definir'
    return f'{x:.{d}f}'.replace('.',',')
def md(df):
    cols=[str(c) for c in df.columns]
    s='| '+' | '.join(cols)+' |\n|'+'|'.join(['---']*len(cols))+'|\n'
    for _,r in df.iterrows(): s+='| '+' | '.join(str(v) for v in r.values)+' |\n'
    return s
out=open(W+'out.md','w')
def P(*a): print(*a,file=out)

P_=D.pivot(index='cod',columns='ano',values='partos')
T=D.pivot(index='cod',columns='ano',values='taxa')
C=D.pivot(index='cod',columns='ano',values='ces')
# --- R2b
r2=[]
for c in P_.index:
    for y in range(2015,2026):
        base=(P_.at[c,y-1]+P_.at[c,y-2])/2
        v=(P_.at[c,y]-base)/base*100
        if abs(v)>30: r2.append((c,y,P_.at[c,y-2],P_.at[c,y-1],base,P_.at[c,y],v))
R2=pd.DataFrame(r2,columns=['cod','ano','p_y2','p_y1','base','partos','vr'])
P('## R2b'); P(md(pd.DataFrame({'Código':R2.cod,'Ano':R2.ano,'Partos ano−2':R2.p_y2,'Partos ano−1':R2.p_y1,'Média 2 anos anteriores':R2.base.map(lambda x:f(x,1)),'Partos no ano':R2.partos,'Variação (%)':R2.vr.map(f),'Taxa CS (%)':[f(T.at[c,y]) for c,y in zip(R2.cod,R2.ano)]})))
# 2014 check vs 2013 only (info)
v14=((P_[2014]-P_[2013])/P_[2013]*100); P('2014 vs 2013 >30%:',v14[v14.abs()>30].to_dict())
flag=set(zip(R2.cod,R2.ano))
# --- low volume
low=D[D.partos<300]; P('## <300', md(low[['cod','ano','partos']]))
# --- table a
yrs=list(range(2013,2027))
ta=pd.DataFrame(index=T.index)
for y in yrs:
    ta[str(y) if y<2026 else '2026 (jan–abr)']=[f(T.at[c,y])+('*' if P_.at[c,y]<300 else '')+('†' if (c,y) in flag else '') for c in T.index]
# period mean 2013-2025 (simple mean of annual rates) and pooled
ta['Média 2013–2025']=T[list(range(2013,2026))].mean(axis=1).map(f)
ta['Taxa agregada 2013–2025']=(C[list(range(2013,2026))].sum(axis=1)/P_[list(range(2013,2026))].sum(axis=1)*100).map(f)
ta.insert(0,'Código',ta.index)
P('## Tabela a'); P(md(ta))
# --- stats
def stats(sub):
    r={}
    for y,g in sub.groupby('ano'):
        t=g.taxa
        q1,q3=t.quantile(.25),t.quantile(.75)
        r[y]=dict(n=len(t),media=t.mean(),glob=g.ces.sum()/g.partos.sum()*100,mediana=t.median(),dp=t.std(ddof=0),dps=t.std(ddof=1),
                  cv=t.std(ddof=0)/t.mean()*100,mn=t.min(),mx=t.max(),amp=t.max()-t.min(),q1=q1,q3=q3,iiq=q3-q1,
                  cmin=g.loc[t.idxmin(),'cod'],cmax=g.loc[t.idxmax(),'cod'])
    return pd.DataFrame(r).T
S=stats(D); S2=stats(D[[ (c,y) not in flag for c,y in zip(D.cod,D.ano)]])
def stab(S):
    return pd.DataFrame({'Ano':[str(y) if y<2026 else '2026 (jan–abr)' for y in S.index],'N.º unidades':S.n.astype(int),'Média simples (%)':S.media.map(f),'Taxa global (%)':S.glob.map(f),'Mediana (%)':S.mediana.map(f),
      'Desvio-padrão (p.p.)':S.dp.map(lambda x:f(x,2)),'CV (%)':S.cv.map(f),'Mínimo (%)':S.mn.map(f),'Unidade mín.':S.cmin,'Máximo (%)':S.mx.map(f),'Unidade máx.':S.cmax,'Amplitude (p.p.)':S.amp.map(f),'Q1 (%)':S.q1.map(f),'Q3 (%)':S.q3.map(f),'IIQ (p.p.)':S.iiq.map(f)})
P('## Stats all'); P(md(stab(S)))
P('## Stats sem R2b'); P(md(stab(S2)))
dd=pd.DataFrame({'Ano':S.index,'n com':S.n.astype(int),'n sem':S2.n.astype(int),'Δ média':(S2.media-S.media).map(lambda x:f(x,2)),'Δ global':(S2.glob-S.glob).map(lambda x:f(x,2)),'Δ mediana':(S2.mediana-S.mediana).map(lambda x:f(x,2)),'Δ DP':(S2.dp-S.dp).map(lambda x:f(x,2)),'Δ CV':(S2.cv-S.cv).map(lambda x:f(x,2)),'Δ amplitude':(S2.amp-S.amp).map(lambda x:f(x,2)),'Δ IIQ':(S2.iiq-S.iiq).map(lambda x:f(x,2))})
P('## Diferenças sem-com'); P(md(dd[dd['n com']!=dd['n sem']]))
P('sample sd for reference', S.dps.round(2).to_dict())
# period-level (unit means) dispersion
um=T[list(range(2013,2026))].mean(axis=1)
P('unit means 2013-2025: n',len(um),'mean',f(um.mean()),'median',f(um.median()),'sd',f(um.std(ddof=0),2),'cv',f(um.std(ddof=0)/um.mean()*100),'min',f(um.min()),um.idxmin(),'max',f(um.max()),um.idxmax(),'IQR',f(um.quantile(.75)-um.quantile(.25)))
P('sorted unit means', um.sort_values().round(1).to_dict())
# trends
main=S.loc[2013:2025]
P('years median increased vs prev', sum(main.mediana.diff()>0),'of 12')
P('CV first/last', f(main.cv.iloc[0]),f(main.cv.iloc[-1]), 'min cv year', main.cv.astype(float).idxmin(), 'max', main.cv.astype(float).idxmax())
P('IIQ range', f(main.iiq.min()),f(main.iiq.max()))
# per unit trend: 2013-15 mean vs 2023-25 mean
early=T[[2013,2014,2015]].mean(axis=1); late=T[[2023,2024,2025]].mean(axis=1)
P('units increased early->late', (late>early).sum(), 'decreased', (late<early).sum(), (late-early).round(1).sort_values().to_dict())
# rank stability: Spearman between 2013 and 2025 ranks (descriptive)
P('rank corr 2013 vs 2025', round(T[2013].rank().corr(T[2025].rank()),2), '2013-2015 mean vs 2023-2025 mean', round(early.rank().corr(late.rank()),2))
# quartile persistence
qtop=pd.DataFrame({y:T[y]>=T[y].quantile(.75) for y in range(2013,2026)}).sum(axis=1)
qbot=pd.DataFrame({y:T[y]<=T[y].quantile(.25) for y in range(2013,2026)}).sum(axis=1)
# funnel outliers per year 99.8 / 95
out_hi99=pd.Series(0,index=T.index); out_lo99=out_hi99.copy(); out_hi95=out_hi99.copy(); out_lo95=out_hi99.copy()
for y in range(2013,2026):
    p=S.at[y,'glob']/100
    for c in T.index:
        n=P_.at[c,y]; se=np.sqrt(p*(1-p)/n); r=T.at[c,y]/100
        if r>p+3.09*se: out_hi99[c]+=1
        if r<p-3.09*se: out_lo99[c]+=1
        if r>p+1.96*se: out_hi95[c]+=1
        if r<p-1.96*se: out_lo95[c]+=1
A=pd.DataFrame({'Código':T.index,'Média 2013–2025 (%)':um.map(f),'Anos no quartil superior (de 13)':qtop.values,'Anos no quartil inferior (de 13)':qbot.values,
   'Anos acima do limite 99,8%':out_hi99.values,'Anos abaixo do limite 99,8%':out_lo99.values,'Anos acima 95%':out_hi95.values,'Anos abaixo 95%':out_lo95.values,
   'Partos médios/ano 2013–2025':P_[list(range(2013,2026))].mean(axis=1).round(0).astype(int).values})
P('## Atípicas'); P(md(A))
# 2026 vs 2025 per unit
d26=(T[2026]-T[2025]); P('2026-2025 units up',(d26>0).sum(),'down',(d26<0).sum(), 'median diff', f(d26.median(),2))
# --- chart data tables
yl=[str(y) if y<2026 else '2026 (jan–abr)' for y in S.index]
cdat=pd.DataFrame({'Ano':yl,'Média simples (%)':S.media.map(f),'Taxa global (%)':S.glob.map(f),'Mínimo (%)':S.mn.map(f),'Máximo − mínimo (p.p.)':S.amp.map(f),'Máximo (%)':S.mx.map(f)})
P('## Chart c'); P(md(cdat))
ddat=pd.DataFrame({'Ano':yl,'CV (%)':S.cv.map(f),'IIQ (p.p.)':S.iiq.map(f),'Q1 (%)':S.q1.map(f),'Q3 (%)':S.q3.map(f)})
P('## Chart d'); P(md(ddat))
edat=pd.DataFrame(index=T.index)
for y in yrs: edat[str(y) if y<2026 else '2026 (jan–abr)']=T[y].map(f)
edat.insert(0,'Código',edat.index)
P('## Chart e'); P(md(edat))
# --- sector/level table
lv=D.groupby('cod').nivel_orig.first()
nivel_an={'Ib':'I','I ou II':'I/II (indeterminado)'}
st=sec.idxmax(axis=1).unstack()
trans={('A28',2019):'PPP (jan–ago) → EPE (set–dez)',('A17',2021):'PPP (jan–mai) → EPE (jun–dez)'}
rowsS=[]
for c in T.index:
    r={'Código':c,'Nível (folha mensal)':lv[c],'Nível na análise':nivel_an.get(lv[c],lv[c])}
    for y in yrs:
        v=st.at[c,y];
        if (c,y) in trans: v+='‡'
        if c=='A15' and y==2022: v+='§'
        r[str(y) if y<2026 else '2026 (jan–abr)']=v
    rowsS.append(r)
P('## Setor nivel'); P(md(pd.DataFrame(rowsS)))
P('level counts', pd.Series([nivel_an.get(lv[c],lv[c]) for c in T.index]).value_counts().to_dict())
P('sector counts by year', {y:D[D.ano==y].setor.value_counts().to_dict() for y in yrs})
# --- coherence M5
m5=pd.read_excel(U+'Munic_pio-sa_de-SNS-total.xlsx',sheet_name='Quadro',header=None)
yrow=m5.iloc[11]; cont=m5[m5[1]=='Continente'].iloc[0]; port=m5[m5[1]=='Portugal'].iloc[0]
m5c={int(yrow[c]):cont[c] for c in range(2,m5.shape[1]) if pd.notna(yrow[c]) and str(yrow[c]).isdigit()}
P('M5 portugal row', [port[c] for c in range(2,14)])
P('M5 symbols ┴ present:', m5.astype(str).apply(lambda s:s.str.contains('┴')).any().any())
coh=[]
for y in range(2013,2025):
    h=chk.at[y,'partos']; p=m5c[y]
    coh.append((y,h,p,h-p,(h-p)/p*100))
COH=pd.DataFrame(coh,columns=['ano','h','m5','dif','pct'])
P('## Coerencia i'); P(md(pd.DataFrame({'Ano':COH.ano,'Partos 37 unidades [H]':COH.h,'Partos hospitais SNS Continente [M5]':COH.m5,'Diferença (n.º)':COH.dif,'Diferença (%)':COH.pct.map(lambda x:f(x,2)),'≤ 0,5%':np.where(COH.pct.abs()<=0.5,'Sim','Não')})))
n5=pd.read_excel(U+'Portugal-Sa_de-Servi_os_e_utiliza__o-total.xlsx',sheet_name='Quadro',header=None).iloc[9:21]
n5=n5.set_index(0)
c2=[]
for y in range(2013,2025):
    tp,ce=n5.at[y,1],n5.at[y,4]; r=ce/tp*100; h=chk.at[y,'glob']
    c2.append((y,chk.at[y,'partos'],chk.at[y,'ces'],h,tp,ce,r,h-r,chk.at[y,'partos']-tp))
C2=pd.DataFrame(c2,columns=['ano','hp','hc','h','tp','ce','r','d','dp'])
P('## Coerencia ii'); P(md(pd.DataFrame({'Ano':C2.ano,'Partos [H]':C2.hp,'Cesarianas [H]':C2.hc,'Taxa global [H] (%)':C2.h.map(lambda x:f(x,2)),'Partos públicos e PPP [N5] (Portugal)':C2.tp,'Cesarianas públicos e PPP [N5]':C2.ce,'Taxa [N5] (%)':C2.r.map(lambda x:f(x,2)),'Diferença taxa (p.p.)':C2.d.map(lambda x:f(x,2)),'Diferença partos [H] − [N5]':C2.dp})))
P('N5 private 2019 / total 2019 / % 2019:', n5.loc[2019,[6,11,16]].tolist())
P('N5 % cesarianas total hospitais', n5[16].to_dict())
pickle.dump((S,S2,T,P_,R2,flag,um,COH,C2),open(W+'s.pkl','wb'))
out.close()
