import pickle, numpy as np, pandas as pd, matplotlib
from scipy.stats import spearmanr
matplotlib.use('Agg'); import matplotlib.pyplot as plt
W='w/'
S,S2,T,P_,R2,flag,um,COH,C2=pickle.load(open(W+'s.pkl','rb')); flag=pickle.load(open(W+'flag2.pkl','rb'))
D,chk,sec,m=pickle.load(open(W+'d.pkl','rb'))
LV,SL,OC,PR,WV,pm=pickle.load(open(W+'s2.pkl','rb'))
RG,ARS,RS,med,medA=pickle.load(open(W+'s4.pkl','rb'))
MAP,shared,nopart=pickle.load(open(W+'map.pkl','rb'))
mun,cont=pickle.load(open(W+'m3go.pkl','rb'))
yrs=list(range(2013,2025))
lowv=['A11','A14','A22','A33','A37']
atyp={'A10':'Atípica ↑','A37':'Atípica ↑','A15':'Atípica ↓','A09':'Atípica ↓','A04':'Quase ↑','A21':'Quase ↑','A27':'Quase ↑','A11':'Quase ↑','A25':'Quase ↓'}
vbins=[0,600,1500,2500,1e9]; vlabs=['< 600','600–1499','1500–2499','≥ 2500']
vm=P_[list(range(2013,2026))].mean(axis=1); VC=pd.cut(vm,vbins,right=False,labels=vlabs)
out=open(W+'out6.md','w')
def P(*a): print(*a,file=out)
def f(x,d=1):
    if x is None or (isinstance(x,float) and np.isnan(x)): return 'a definir'
    x=round(float(x),d)+0.0
    return f'{x:.{d}f}'.replace('.',',')
def md(df):
    cols=[str(c) for c in df.columns]
    s='| '+' | '.join(cols)+' |\n|'+'|'.join(['---']*len(cols))+'|\n'
    for _,r in df.iterrows(): s+='| '+' | '.join(str(v) for v in r.values)+' |\n'
    return s
rho=lambda a,b: spearmanr(a,b).correlation
def ulsof(r,year):
    if r.x=='depois 2024': return [r.y] if year>=2024 else [r.c]
    if isinstance(r.x,str) and r.x.startswith('A'): return [r.c,r.x]+([r.y] if isinstance(r.y,str) and r.y.startswith('A') else [])
    return [r.c]
def agg(version):
    res=pd.DataFrame(np.nan,index=T.index,columns=yrs); nm=pd.DataFrame(0,index=T.index,columns=yrs)
    for y in yrs:
        acc={}
        for _,r in MAP.iterrows():
            if version=='ii' and r.mun in shared: continue
            for u in ulsof(r,y):
                if u in nopart: continue
                acc[u]=acc.get(u,0)+mun.at[r.mun,y]; nm.at[u,y]+=1
        for u,v in acc.items(): res.at[u,y]=v
    return res,nm
GOi,NMi=agg('i'); GOii,NMii=agg('ii'); GOii.loc['A25']=np.nan  # A25 em (ii): só Mafra em 2024 (ano R2b) -> a definir
Ri=GOi/P_[yrs]*1000; Rii=GOii/P_[yrs]*1000
P('units without data ii', {c:[y for y in yrs if np.isnan(GOii.at[c,y])] for c in T.index if GOii.loc[c].isna().any()})
P('n municipalities per ULS 2013/2024 (i)', {c:(int(NMi.at[c,2013]),int(NMi.at[c,2024])) for c in T.index})
P('ULS with 0 GO in some year (i)', {c:[y for y in yrs if GOi.at[c,y]==0] for c in T.index if (GOi.loc[c]==0).any()})
# municipalities share check: total counted (i) vs continent excl R9b
excl_mun=MAP[MAP.c.isin(nopart)].mun.tolist()
P('R9b municipalities GO total per year', {y:int(mun.loc[excl_mun,y].sum()) for y in yrs})
P('sum ULS (i) vs continent', {y:(int(GOi[y].sum()),int(cont[y])) for y in yrs})
P('shared munis GO', {k:[int(mun.at[k,y]) for y in (2013,2024)] for k in shared})
# per-ULS table (period means)
def tabU(GO,R,tag):
    rows=[]
    for c in T.index:
        g=GO.loc[c]; r=R.loc[c]
        rows.append({'Código':c,'Nível':LV[c],'Classe de volume':str(VC[c]),'N.º municípios (2013→2024)':f'{int((NMi if tag=="i" else NMii).at[c,2013])}→{int((NMi if tag=="i" else NMii).at[c,2024])}',
          'Médicos GO 2013':f(g[2013],0),'Médicos GO 2024':f(g[2024],0),'Médicos GO, média 2013–2024':f(g.mean()),'Partos médios 2013–2024':int(round(P_.loc[c,yrs].mean())),
          'GO por 1000 partos, média 2013–2024':f(r.mean()),'GO por 1000 partos 2013':f(r[2013]),'GO por 1000 partos 2024':f(r[2024]),'Taxa CS média 2013–2024 (%)':f(T.loc[c,yrs].mean())})
    return pd.DataFrame(rows)
TUi=tabU(GOi,Ri,'i'); TUii=tabU(GOii,Rii,'ii')
P('## ULS i'); P(md(TUi)); P('## ULS ii'); P(md(TUii))
# yearly descriptive of ratio (i)
dd=[]
for y in yrs:
    for tag,R in [('i',Ri),('ii',Rii)]:
        v=R[y].dropna(); dd.append({'Ano':y,'Versão':tag,'N.º unidades':len(v),'Média':f(v.mean()),'Mediana':f(v.median()),'Mín.':f(v.min()),'Unid. mín.':v.idxmin(),'Máx.':f(v.max()),'Unid. máx.':v.idxmax(),'IIQ':f(v.quantile(.75)-v.quantile(.25)),'N.º com 0':int((v==0).sum())})
P('## ratio desc'); P(md(pd.DataFrame(dd)))
# rho annual
rr=[]
for y in yrs:
    d={'Ano':y}
    for tag,R,GO in [('i',Ri,GOi),('ii',Rii,GOii)]:
        ok=R[y].dropna().index
        d[f'rho GO/1000 partos ({tag})']=f(rho(R.loc[ok,y],T.loc[ok,y]),2)
        d[f'rho n.º GO absoluto ({tag})']=f(rho(GO.loc[ok,y],T.loc[ok,y]),2)
    for l in ['I','II']:
        cs=[c for c in T.index if LV[c]==l]; d[f'rho GO/1000 nível {l} (i; n={len(cs)})']=f(rho(Ri.loc[cs,y],T.loc[cs,y]),2)
    cs=[c for c in T.index if c not in lowv]; d['rho GO/1000 sem baixo volume (i; n=32)']=f(rho(Ri.loc[cs,y],T.loc[cs,y]),2)
    ok=[c for c in T.index if (c,y) not in flag]; d['rho GO/1000 sem R2b (i)']=f(rho(Ri.loc[ok,y],T.loc[ok,y]),2)
    d['rho GO/1000 vs partos (i)']=f(rho(Ri[y],P_[y]),2)
    rr.append(d)
RR=pd.DataFrame(rr); P('## rho annual'); P(md(RR))
fl=lambda s: s.str.replace(',','.').astype(float)
for c in RR.columns[1:]:
    v=fl(RR[c]); P(c,'neg',int((v<0).sum()),'pos',int((v>0).sum()),'min',f(v.min(),2),'max',f(v.max(),2),'median',f(v.median(),2))
# period means
mrate=T[yrs].mean(axis=1)
rp={}
for tag,R,GO in [('i',Ri,GOi),('ii',Rii,GOii)]:
    mr=R.mean(axis=1); ok=mr.dropna().index
    rp[f'GO por 1000 partos ({tag}; n={len(ok)})']=rho(mr[ok],mrate[ok]); rp[f'N.º GO absoluto ({tag}; n={len(ok)})']=rho(GO.mean(axis=1)[ok],mrate[ok])
    for l in ['I','II']:
        cs=[c for c in ok if LV[c]==l]; rp[f'GO por 1000 partos, nível {l} ({tag}; n={len(cs)})']=rho(mr[cs],mrate[cs])
    cs=[c for c in ok if c not in lowv]; rp[f'GO por 1000 partos, sem baixo volume ({tag}; n={len(cs)})']=rho(mr[cs],mrate[cs])
    for vl in vlabs:
        cs=[c for c in ok if VC[c]==vl]
        if len(cs)>=5: rp[f'GO por 1000 partos, classe {vl} ({tag}; n={len(cs)})']=rho(mr[cs],mrate[cs])
    rp[f'GO por 1000 partos vs partos médios ({tag}; n={len(ok)})']=rho(mr[ok],P_.loc[ok,yrs].mean(axis=1))
P('## rho period'); P(md(pd.DataFrame({'Conjunto (médias 2013–2024)':list(rp.keys()),'rho de Spearman':[f(v,2) for v in rp.values()]})))
# terciles of ratio (i) vs rate
mr=Ri.mean(axis=1); tc=pd.qcut(mr,3,labels=['Tercil inferior','Tercil médio','Tercil superior'])
P('## terciles i'); P(md(pd.DataFrame([{'Tercil GO/1000 partos (i)':t,'N.º':int((tc==t).sum()),'Intervalo GO/1000':f'{f(mr[tc==t].min())}–{f(mr[tc==t].max())}','Mediana taxa CS 2013–2024 (%)':f(mrate[tc==t].median()),'Mín.–máx. taxa (%)':f'{f(mrate[tc==t].min())}–{f(mrate[tc==t].max())}','Unidades':', '.join(mr[tc==t].sort_values().index)} for t in ['Tercil inferior','Tercil médio','Tercil superior']])))
mr2=Rii.mean(axis=1).dropna(); tc2=pd.qcut(mr2,3,labels=['Tercil inferior','Tercil médio','Tercil superior'])
P('## terciles ii'); P(md(pd.DataFrame([{'Tercil GO/1000 partos (ii)':t,'N.º':int((tc2==t).sum()),'Intervalo GO/1000':f'{f(mr2[tc2==t].min())}–{f(mr2[tc2==t].max())}','Mediana taxa CS 2013–2024 (%)':f(mrate[tc2[tc2==t].index].median()),'Mín.–máx. taxa (%)':f'{f(mrate[tc2[tc2==t].index].min())}–{f(mrate[tc2[tc2==t].index].max())}','Unidades':', '.join(mr2[tc2==t].sort_values().index)} for t in ['Tercil inferior','Tercil médio','Tercil superior']])))
P('atypical GO/1000 (i) rank (1=highest of 37) and tercile', {c:(f(mr[c]),int(mr.rank(ascending=False)[c]),str(tc[c])) for c in atyp})
# changes over time in GO count
P('GO total ULS(i excl shared double) change', int(cont[2013]),int(cont[2024]))
# within-unit temporal rho (ratio vs rate)
wu=pd.Series({c:rho(Ri.loc[c,yrs],T.loc[c,yrs]) for c in T.index if Ri.loc[c,yrs].nunique()>1})
P('within-unit rho median',f(wu.median(),2),'pos',int((wu>0).sum()),'of',len(wu))
# ---------- charts
cols={'I':'#2a78d6','II':'#eb6834','III':'#1baf7a','I/II':'#6250d6'}; mk={'I':'o','II':'s','III':'^','I/II':'D'}
INK,MUT='#0b0b0b','#52514e'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#bbb','xtick.color':MUT,'ytick.color':MUT,'figure.facecolor':'#fcfcfb','axes.facecolor':'#fcfcfb'})
ff=matplotlib.ticker.FuncFormatter(lambda v,q:(f'{v:.0f}' if abs(v-round(v))<1e-9 else f'{v:.1f}').replace('.',','))
fig,axs=plt.subplots(1,2,figsize=(15,6.3),sharey=True)
for ax,R,tag,ttl in [(axs[0],Ri,'i','(i) Com os municípios partilhados (37 unidades)'),(axs[1],Rii,'ii','(ii) Sem Porto, Lisboa, Cascais e Belmonte')]:
    mrr=R.mean(axis=1).dropna()
    for l in ['I','II','III','I/II']:
        cs=[c for c in mrr.index if LV[c]==l]; ax.scatter(mrr[cs],mrate[cs],s=50,marker=mk[l],color=cols[l],edgecolor='white',lw=.8,zorder=3,label=f'Nível {l}' if l!='I/II' else 'I/II (A23)')
    for c in mrr.index: ax.annotate(c,(mrr[c],mrate[c]),xytext=(4,3),textcoords='offset points',fontsize=6.8,color=INK)
    ax.set_xscale('symlog',linthresh=10); ax.xaxis.set_major_formatter(ff); ax.set_xticks([0,2,5,10,20,50,100,200])
    ax.set_xlabel('Médicos de GO residentes por 1000 partos da unidade (média 2013–2024; escala log)')
    ax.set_title(f'{ttl}: rho = {f(rho(mrr,mrate[mrr.index]),2)} (n = {len(mrr)})',loc='left',fontsize=9.5,color=INK)
    ax.yaxis.set_major_formatter(ff)
axs[0].set_ylabel('Taxa de cesariana média 2013–2024 (%)'); axs[0].legend(frameon=False,fontsize=8,loc='upper right')
fig.suptitle('Taxa de cesariana vs. médicos de Ginecologia/Obstetrícia (residência) por 1000 partos, médias 2013–2024',x=.01,ha='left',fontsize=11,color=INK)
fig.text(.01,.01,'Médicos por local de residência, inscritos na Ordem dos Médicos (inclui setor privado). Eixo X em escala logarítmica simétrica (linear até 10). Em (ii), A16, A24 e A25: n.a. – sem municípios próprios (conclusões de (ii) sobre 34 unidades). O município de Ovar esteve afeto à ULS A19 entre janeiro e setembro de 2024; para efeitos de análise foi considerado na A05 em todo o período.',fontsize=7,color=MUT,wrap=True)
fig.tight_layout(rect=(0,.05,1,.95)); fig.savefig(W+'Fig6_1_dispersao_GO.png',dpi=150); plt.close()
sc=pd.DataFrame({'Código':T.index,'Nível':[LV[c] for c in T.index],'Classe de volume':VC.astype(str).values,'GO por 1000 partos (i), média 2013–2024':Ri.mean(axis=1).map(f).values,'GO por 1000 partos (ii), média 2013–2024':Rii.mean(axis=1).map(f).values,'Taxa CS média 2013–2024 (%)':mrate.map(f).values})
for l in ['I','II','III','I/II']: sc[f'Taxa nível {l} (%)']=[f(mrate[c]) if LV[c]==l else '' for c in T.index]
sc=sc.assign(o=Ri.mean(axis=1).values).sort_values('o').drop(columns='o')
P('## scatter'); P(md(sc))
fig,ax=plt.subplots(figsize=(10.5,5))
ser=[('rho GO/1000 partos (i)','GO/1000 partos (i), 37','#0b0b0b','-'),('rho GO/1000 partos (ii)','GO/1000 partos (ii), 34','#888','--'),('rho GO/1000 nível I (i; n=14)','Nível I (i), 14',cols['I'],'-'),('rho GO/1000 nível II (i; n=17)','Nível II (i), 17',cols['II'],'-'),('rho n.º GO absoluto (i)','N.º absoluto GO (i)','#6250d6',':')]
for c,lb,cc,ls in ser:
    ax.plot(yrs,fl(RR[c]),color=cc,ls=ls,marker='o',ms=4,lw=1.8,label=lb)
ax.axhline(0,color=INK,lw=.8); ax.set_ylim(-1,1); ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.2)); ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,q:f'{v:.1f}'.replace('.',',')))
ax.set_xticks(yrs); ax.set_ylabel('rho de Spearman (taxa vs. médicos GO)'); ax.legend(frameon=False,fontsize=8,loc='lower left',ncol=3)
ax.set_title('rho de Spearman entre a taxa de cesariana e os médicos de GO (residência), por ano, 2013–2024',loc='left',fontsize=10.5,color=INK)
fig.text(.01,.01,'Descritivo, sem p-valor. (i) com e (ii) sem os 4 municípios partilhados por mais do que uma ULS.',fontsize=7.5,color=MUT)
fig.tight_layout(rect=(0,.03,1,1)); fig.savefig(W+'Fig6_2_rho_GO.png',dpi=160); plt.close()
pickle.dump((GOi,GOii,Ri,Rii,NMi,NMii),open(W+'s6.pkl','wb'))
out.close()
