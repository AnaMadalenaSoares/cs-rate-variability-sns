import pickle, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
W='w/'
U='dados/'
S,S2,T,P_,R2,flag,um,COH,C2=pickle.load(open(W+'s.pkl','rb')); flag=pickle.load(open(W+'flag2.pkl','rb'))
D,chk,sec,m=pickle.load(open(W+'d.pkl','rb'))
LV,SL,OC,PR,WV,pm=pickle.load(open(W+'s2.pkl','rb'))
C=D.pivot(index='cod',columns='ano',values='ces')
r=pd.read_excel(U+'Correla__o_regi_es_final.xlsx',header=None).iloc[2:42,1:3]; RG=dict(zip(r[1],r[2]))
RG={c:RG[c] for c in T.index}
ARS={c:('LVT' if RG[c] in ['Oeste e Vale do Tejo','Grande Lisboa','Península de Setúbal'] else RG[c]) for c in T.index}
R7=['Norte','Centro','Oeste e Vale do Tejo','Grande Lisboa','Península de Setúbal','Alentejo','Algarve']
A5=['Norte','Centro','LVT','Alentejo','Algarve']
ab={'Norte':'Norte','Centro':'Centro','Oeste e Vale do Tejo':'OVT','Grande Lisboa':'GL','Península de Setúbal':'PS','Alentejo':'Alentejo','Algarve':'Algarve','LVT':'LVT','Total':'Total'}
yrs=list(range(2013,2026)); yall=yrs+[2026]
lowv=['A11','A14','A22','A33','A37']
atyp={'A10':'Atípica ↑','A37':'Atípica ↑','A15':'Atípica ↓','A09':'Atípica ↓','A04':'Quase ↑','A21':'Quase ↑','A27':'Quase ↑','A11':'Quase ↑','A25':'Quase ↓'}
out=open(W+'out4.md','w')
def P(*a): print(*a,file=out)
def f(x,d=1):
    if x is None or (isinstance(x,float) and np.isnan(x)): return '—'
    x=round(float(x),d)+0.0
    return f'{x:.{d}f}'.replace('.',',')
def md(df):
    cols=[str(c) for c in df.columns]
    s='| '+' | '.join(cols)+' |\n|'+'|'.join(['---']*len(cols))+'|\n'
    for _,r in df.iterrows(): s+='| '+' | '.join(str(v) for v in r.values)+' |\n'
    return s
lab=lambda y: str(y) if y<2026 else '2026 (jan–abr)'
def st(t,ces,par):
    n=len(t); q1,q3=t.quantile(.25),t.quantile(.75)
    return dict(n=n,media=t.mean(),glob=ces.sum()/par.sum()*100,mediana=t.median(),dp=t.std(ddof=0) if n>1 else np.nan,cv=t.std(ddof=0)/t.mean()*100 if n>1 else np.nan,mn=t.min(),mx=t.max(),amp=t.max()-t.min() if n>1 else np.nan,q1=q1 if n>2 else np.nan,q3=q3 if n>2 else np.nan,iiq=q3-q1 if n>2 else np.nan)
# distribution
dist=[]
for g in R7:
    cs=[c for c in T.index if RG[c]==g]
    dist.append({'Região':g,'ARS':ARS[cs[0]],'N.º unidades':len(cs),'Códigos (nível)':', '.join(f'{c} ({LV[c]})' for c in cs),'N.º por nível I/II/III/I-II':f"{sum(LV[c]=='I' for c in cs)}/{sum(LV[c]=='II' for c in cs)}/{sum(LV[c]=='III' for c in cs)}/{sum(LV[c]=='I/II' for c in cs)}",'PPP (2013–2019)':', '.join(c for c in cs if c in ['A15','A16','A17','A28']) or '—','Baixo volume':', '.join(c for c in cs if c in lowv) or '—','% partos 2013–2025':f(P_.loc[cs,yrs].values.sum()/P_[yrs].values.sum()*100),'Nota':'1 unidade: sem variabilidade interna' if len(cs)==1 else ('3 unidades: sem conclusões de variabilidade interna' if len(cs)==3 else '')})
P('## dist'); P(md(pd.DataFrame(dist)))
# annual stats long
rows=[]
for grpname,mp,gl in [('R7',RG,R7),('ARS',ARS,A5)]:
    for y in yall:
        for g in gl+['Total']:
            cs=list(T.index) if g=='Total' else [c for c in T.index if mp[c]==g]
            d=st(T.loc[cs,y],C.loc[cs,y],P_.loc[cs,y]); d.update(ano=y,g=g,tipo=grpname); rows.append(d)
RS=pd.DataFrame(rows)
def tabreg(g,tipo='R7'):
    x=RS[(RS.g==g)&(RS.tipo==tipo)]
    return pd.DataFrame({'Ano':[lab(y) for y in x.ano],'N.º':x.n.astype(int),'Média (%)':x.media.map(f),'Taxa global (%)':x.glob.map(f),'Mediana (%)':x.mediana.map(f),'DP (p.p.)':x.dp.map(lambda v:f(v,2)),'CV (%)':x.cv.map(f),'Mín. (%)':x.mn.map(f),'Máx. (%)':x.mx.map(f),'Amplitude (p.p.)':x.amp.map(f),'Q1 (%)':x.q1.map(f),'Q3 (%)':x.q3.map(f),'IIQ (p.p.)':x.iiq.map(f)})
for g in ['Norte','Centro','Grande Lisboa']: P(f'## {g}'); P(md(tabreg(g)))
P('## LVT'); P(md(tabreg('LVT','ARS')))
# small regions compact
sm=pd.DataFrame({'Ano':[lab(y) for y in yall]})
for g in ['Oeste e Vale do Tejo','Península de Setúbal','Alentejo']:
    x=RS[(RS.g==g)&(RS.tipo=='R7')].set_index('ano')
    sm[f'{ab[g]} mediana (%)']=[f(x.at[y,'mediana']) for y in yall]; sm[f'{ab[g]} mín.–máx. (%)']=[f'{f(x.at[y,"mn"])}–{f(x.at[y,"mx"])}' for y in yall]; sm[f'{ab[g]} taxa global (%)']=[f(x.at[y,'glob']) for y in yall]
sm['Algarve (A23, %)']=[f(T.at['A23',y]) for y in yall]
P('## small'); P(md(sm))
# medians per region per year + ranking
med=pd.DataFrame({g:[RS[(RS.g==g)&(RS.tipo=='R7')&(RS.ano==y)].mediana.iloc[0] for y in yall] for g in R7+['Total']},index=yall)
mt=med.copy(); mt.insert(0,'Ano',[lab(y) for y in yall])
for c in R7+['Total']: mt[c]=med[c].map(f)
mt['Região com mediana mais alta']=[med.loc[y,R7].idxmax() for y in yall]; mt['Região com mediana mais baixa']=[med.loc[y,R7].idxmin() for y in yall]
P('## medians'); P(md(mt.rename(columns={g:f'{ab[g]} (%)' for g in R7+['Total']})))
P('highest counts', med.loc[yrs,R7].idxmax(axis=1).value_counts().to_dict(),'lowest',med.loc[yrs,R7].idxmin(axis=1).value_counts().to_dict())
P('years above total median', {g:int((med.loc[yrs,g]>med.loc[yrs,'Total']).sum()) for g in R7})
# ranking stability of region medians: rank each year
rk=med.loc[yrs,R7].rank(axis=1,ascending=False); P('mean rank', rk.mean().round(1).to_dict(), 'rank range', {g:(int(rk[g].min()),int(rk[g].max())) for g in R7})
medA=pd.DataFrame({g:[RS[(RS.g==g)&(RS.tipo=='ARS')&(RS.ano==y)].mediana.iloc[0] for y in yall] for g in A5+['Total']},index=yall)
P('## ARS medians'); P(md(pd.DataFrame({'Ano':[lab(y) for y in yall],**{f'{g} (%)':medA[g].map(f).values for g in A5+['Total']},'Mais alta':[medA.loc[y,A5].idxmax() for y in yall],'Mais baixa':[medA.loc[y,A5].idxmin() for y in yall]})))
P('ARS highest counts', medA.loc[yrs,A5].idxmax(axis=1).value_counts().to_dict(),'lowest',medA.loc[yrs,A5].idxmin(axis=1).value_counts().to_dict(), 'above total', {g:int((medA.loc[yrs,g]>medA.loc[yrs,'Total']).sum()) for g in A5})
# period means by region and ARS
def per(mp,gl):
    rr=[]
    for g in gl+['Total']:
        cs=list(T.index) if g=='Total' else [c for c in T.index if mp[c]==g]
        t=um[cs]; d=st(t,C.loc[cs,yrs].sum(axis=1),P_.loc[cs,yrs].sum(axis=1)); d['g']=g; d['cods']=', '.join(f'{c} ({f(um[c])})' for c in t.sort_values(ascending=False).index) if g!='Total' else ''; rr.append(d)
    x=pd.DataFrame(rr)
    return pd.DataFrame({'Região':x.g,'N.º':x.n.astype(int),'Média das médias (%)':x.media.map(f),'Taxa agregada 2013–2025 (%)':x.glob.map(f),'Mediana (%)':x.mediana.map(f),'DP (p.p.)':x.dp.map(lambda v:f(v,2)),'CV (%)':x.cv.map(f),'Mín. (%)':x.mn.map(f),'Máx. (%)':x.mx.map(f),'Amplitude (p.p.)':x.amp.map(f),'IIQ (p.p.)':x.iiq.map(f),'Unidades (média 2013–2025, %)':x.cods})
P('## period R7'); P(md(per(RG,R7))); P('## period ARS'); P(md(per(ARS,A5)))
# within vs total annual for regions with >=7 units and LVT
wv=[]
for y in yrs:
    t=RS[(RS.ano==y)&(RS.g=='Total')&(RS.tipo=='R7')].iloc[0]; r_={'Ano':y}
    for g,tp in [('Norte','R7'),('Centro','R7'),('Grande Lisboa','R7'),('LVT','ARS')]:
        x=RS[(RS.ano==y)&(RS.g==g)&(RS.tipo==tp)].iloc[0]
        r_[f'Amplitude {ab[g]} (p.p.)']=f(x.amp); r_[f'CV {ab[g]} (%)']=f(x.cv); r_[f'Amp. {ab[g]} / Total (%)']=f(x.amp/t.amp*100)
    r_['Amplitude Total (p.p.)']=f(t.amp); r_['CV Total (%)']=f(t.cv); wv.append(r_)
WVr=pd.DataFrame(wv); P('## within'); P(md(WVr))
for g in ['Norte','Centro','Grande Lisboa','LVT']:
    col=f'Amp. {ab[g]} / Total (%)'; v=WVr[col].str.replace(',','.').astype(float); P(g,'mean amp ratio',f(v.mean()),'min',f(v.min()),'max',f(v.max()))
# between-region spread of medians vs within
spread=[med.loc[y,R7].max()-med.loc[y,R7].min() for y in yrs]; spread5=[med.loc[y,[g for g in R7 if g!='Algarve']].max()-med.loc[y,[g for g in R7 if g!='Algarve']].min() for y in yrs]
P('range of region medians per year', [f(v) for v in spread],'mean',f(np.mean(spread)),'excl Algarve mean',f(np.mean(spread5)))
spA=[medA.loc[y,A5].max()-medA.loc[y,A5].min() for y in yrs]; P('ARS medians range mean',f(np.mean(spA)), [f(v) for v in spA])
# within level
for lvl in ['I','II']:
    rows=[]
    for g in R7:
        cs=[c for c in T.index if RG[c]==g and LV[c]==lvl]
        if not cs: continue
        rows.append({'Região':g,'N.º':len(cs),'Unidades (média 2013–2025, %)':', '.join(f'{c} ({f(um[c])})' for c in um[cs].sort_values(ascending=False).index),'Mediana das médias (%)':f(um[cs].median()),'Mín.–máx. (%)':f'{f(um[cs].min())}–{f(um[cs].max())}'})
    cs=[c for c in T.index if LV[c]==lvl]
    rows.append({'Região':f'Total nível {lvl}','N.º':len(cs),'Unidades (média 2013–2025, %)':'','Mediana das médias (%)':f(um[cs].median()),'Mín.–máx. (%)':f'{f(um[cs].min())}–{f(um[cs].max())}'})
    P(f'## level {lvl}'); P(md(pd.DataFrame(rows)))
cs=[c for c in T.index if LV[c]=='III']; P('III', [(c,RG[c],f(um[c])) for c in cs])
# region ranking within level II by period median vs overall
def regmed(lvl=None):
    return {g:um[[c for c in T.index if RG[c]==g and (lvl is None or LV[c]==lvl)]].median() for g in R7 if any(RG[c]==g and (lvl is None or LV[c]==lvl) for c in T.index)}
for l in [None,'I','II']:
    d=regmed(l); P('order', l, ' > '.join(f'{ab[k]} {f(v)}' for k,v in sorted(d.items(),key=lambda kv:-kv[1])))
# annual within level II: Norte vs GL vs Centro medians
for lvl in ['I','II']:
    rr=[]
    for y in yrs:
        d={g:T.loc[[c for c in T.index if RG[c]==g and LV[c]==lvl],y].median() for g in R7 if any(RG[c]==g and LV[c]==lvl for c in T.index)}
        rr.append({'Ano':y,**{f'{ab[g]} (n={sum(RG[c]==g and LV[c]==lvl for c in T.index)})':f(v) for g,v in d.items()},'Mais alta':ab[max(d,key=d.get)],'Mais baixa':ab[min(d,key=d.get)]})
    P(f'## annual level {lvl}'); P(md(pd.DataFrame(rr)))
# atypical by region
P('atyp by region', {g:[f'{c} {atyp[c]}' for c in T.index if RG[c]==g and c in atyp] for g in R7})
# share of units above total median per year by region
P('units above global each year by region (mean share)', {g:f(np.mean([(T.loc[[c for c in T.index if RG[c]==g],y]>S.at[y,'glob']).mean()*100 for y in yrs])) for g in R7})
# ---------- charts
cols={'Norte':'#2a78d6','Centro':'#eb6834','Oeste e Vale do Tejo':'#1baf7a','Grande Lisboa':'#eda100','Península de Setúbal':'#e87ba4','Alentejo':'#008300','Algarve':'#6250d6','LVT':'#e34948'}
mk={'Norte':'o','Centro':'s','Oeste e Vale do Tejo':'^','Grande Lisboa':'D','Península de Setúbal':'v','Alentejo':'P','Algarve':'X','LVT':'D'}
INK,MUT='#0b0b0b','#52514e'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#bbb','xtick.color':MUT,'ytick.color':MUT,'figure.facecolor':'#fcfcfb','axes.facecolor':'#fcfcfb'})
ff=matplotlib.ticker.FuncFormatter(lambda v,q:(f'{v:.0f}' if abs(v-round(v))<1e-9 else f'{v:.1f}').replace('.',','))
rng=np.random.default_rng(7)
fig,axs=plt.subplots(1,2,figsize=(14,6),gridspec_kw={'width_ratios':[7,5]},sharey=True)
for ax,mp,gl,ttl in [(axs[0],RG,R7,'7 regiões'),(axs[1],ARS,A5,'5 ARS (verificação de robustez)')]:
    data=[um[[c for c in T.index if mp[c]==g]].values for g in gl]
    big=[i for i,d in enumerate(data) if len(d)>=7]
    bp=ax.boxplot([data[i] for i in big],positions=big,widths=.55,patch_artist=True,showfliers=False,medianprops=dict(color=INK,lw=2))
    for b,i in zip(bp['boxes'],big): b.set(facecolor=cols[gl[i]]+'33',edgecolor=cols[gl[i]],lw=1.3)
    for i,g in enumerate(gl):
        v=um[[c for c in T.index if mp[c]==g]].sort_values(); xs=i+rng.uniform(-.13,.13,len(v))
        ax.scatter(xs,v,s=34,color=cols[g],marker=mk[g],edgecolor='white',lw=.7,zorder=3)
        if len(v)<7: ax.hlines(v.median(),i-.25,i+.25,color=INK,lw=2)
        ys=[]
        for k,(c,val) in enumerate(v.items()):
            if not (c in atyp or len(v)<7 or k in (0,len(v)-1)): ys.append(val); continue
            yy=val if not ys or val-ys[-1]>=.55 else ys[-1]+.55; ys.append(yy)
            ax.annotate(c,(xs[k],val),xytext=(i+.3,yy),fontsize=6.8,va='center',color=INK,arrowprops=dict(arrowstyle='-',color='#bbb',lw=.5))
    ax.set_xticks(range(len(gl))); ax.set_xticklabels([f"{ab[g] if g not in ('Norte','Centro','Alentejo','Algarve') else g}\n(n = {sum(mp[c]==g for c in T.index)})" for g in gl],fontsize=8)
    ax.set_title(ttl,loc='left',fontsize=10,color=INK); ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(2)); ax.yaxis.set_major_formatter(ff)
    ax.axhline(um.median(),color=MUT,lw=.7,ls=':')
axs[0].set_ylabel('Taxa de cesariana média 2013–2025 (%)')
fig.suptitle('Taxa de cesariana média 2013–2025 por região (um ponto por unidade)',x=.01,ha='left',fontsize=11,color=INK)
fig.text(.01,.01,'Caixas só para grupos com ≥ 7 unidades; nos restantes, linha = mediana. OVT, PS e Alentejo: 3 unidades; Algarve: 1 (A23). Pontilhado: mediana total. Identificadas: unidades atípicas/quase atípicas e extremos de cada grupo.',fontsize=7.2,color=MUT)
fig.tight_layout(rect=(0,.03,1,.95)); fig.savefig(W+'Fig4_1_boxplot_regiao.png',dpi=150); plt.close()
bx=[]
for tipo,mp,gl in [('Região',RG,R7),('ARS',ARS,A5)]:
    for g in gl:
        t=um[[c for c in T.index if mp[c]==g]]; n=len(t)
        if n>=3:
            q1,q3=t.quantile(.25),t.quantile(.75); iq=q3-q1; lw_=min(t[t>=q1-1.5*iq].min(),q1); hw=max(t[t<=q3+1.5*iq].max(),q3)
        else: q1=q3=lw_=hw=t.iloc[0]
        bx.append({'Agrupamento':tipo,'Grupo':g,'N.º':n,'Mínimo (%)':f(t.min()),'Bigode inf. (%)':f(lw_),'Q1 (%)':f(q1),'Mediana (%)':f(t.median()),'Q3 (%)':f(q3),'Bigode sup. (%)':f(hw),'Máximo (%)':f(t.max()),'Q1 − bigode inf.':f(q1-lw_),'Mediana − Q1':f(t.median()-q1),'Q3 − mediana':f(q3-t.median()),'Bigode sup. − Q3':f(hw-q3)})
P('## box'); P(md(pd.DataFrame(bx)))
pts=pd.DataFrame({'Código':T.index,'Região':[RG[c] for c in T.index],'ARS':[ARS[c] for c in T.index],'Nível':[LV[c] for c in T.index],'Média 2013–2025 (%)':um.map(f).values})
for g in R7: pts[ab[g]]=[f(um[c]) if RG[c]==g else '' for c in T.index]
pts['LVT (ARS)']=[f(um[c]) if ARS[c]=='LVT' else '' for c in T.index]
pts['o']=pts.Região.map({g:i for i,g in enumerate(R7)}); pts=pts.sort_values(['o','Código']).drop(columns='o')
P('## box pts'); P(md(pts))
# median evolution
fig,axs=plt.subplots(1,2,figsize=(14,5.4),sharey=True,gridspec_kw={'width_ratios':[1,1]})
for ax,gl,tt,mm_ in [(axs[0],['Norte','Centro','Grande Lisboa'],'Regiões com ≥ 7 unidades',med),(axs[1],['Oeste e Vale do Tejo','Península de Setúbal','Alentejo','Algarve'],'Regiões com 1 a 3 unidades',med)]:
    ax.plot(yrs,mm_.loc[yrs,'Total'],color=MUT,lw=1.2,ls=':',label='Mediana total (37)')
    for g in gl:
        lbl=(ab[g] if g not in ('Norte','Centro','Alentejo','Algarve') else g)+(f' (n={sum(RG[c]==g for c in T.index)})')+(' – A23' if g=='Algarve' else '')
        ax.plot(yrs,mm_.loc[yrs,g],color=cols[g],lw=2 if g in ('Norte','Centro','Grande Lisboa') else 1.5,marker=mk[g],ms=5,label=lbl)
        ax.plot([2025,2026],mm_.loc[[2025,2026],g],color=cols[g],lw=1.5,ls='--'); ax.plot([2026],[mm_.at[2026,g]],marker=mk[g],ms=6,mfc='white',mec=cols[g])
    ax.set_xticks(yall); ax.set_xticklabels([str(y)[2:] if y<2026 else "26*" for y in yall],fontsize=8)
    ax.set_title(tt,loc='left',fontsize=10,color=INK); ax.legend(frameon=False,fontsize=7.5,loc='upper left')
    ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(2)); ax.yaxis.set_major_formatter(ff); ax.set_ylim(22,42)
axs[0].set_ylabel('Mediana da taxa de cesariana (%)')
fig.suptitle('Mediana da taxa de cesariana por região, 2013–2026',x=.01,ha='left',fontsize=11,color=INK)
fig.text(.01,.01,'Eixo X: anos (13 = 2013). *2026: janeiro–abril (tracejado, marcador vazio). Grupos de 1 a 3 unidades: mediana muito sensível a cada unidade.',fontsize=7.5,color=MUT)
fig.tight_layout(rect=(0,.03,1,.95)); fig.savefig(W+'Fig4_2_mediana_regiao.png',dpi=150); plt.close()
P('## med evol'); P(md(mt.drop(columns=['Região com mediana mais alta','Região com mediana mais baixa']).rename(columns={g:f'{ab[g]} (%)' for g in R7+['Total']})))
# funnel 2025 by region
y=2025; p=C[y].sum()/P_[y].sum(); n=P_[y].astype(float); rr=C[y]/P_[y]*100; se=lambda k: np.sqrt(p*(1-p)/k)*100
fig,ax=plt.subplots(figsize=(12.5,6.2)); nn=np.linspace(350,5600,400)
for z,ls,l in [(1.96,'--','Limites 95%'),(3.09,'-','Limites 99,8%')]:
    ax.plot(nn,p*100+z*se(nn),color=MUT,ls=ls,lw=1.1,label=l); ax.plot(nn,p*100-z*se(nn),color=MUT,ls=ls,lw=1.1)
ax.axhline(p*100,color=INK,lw=1,label=f'Taxa global 2025 ({f(p*100)}%)')
for g in R7:
    cs=[c for c in T.index if RG[c]==g]; ax.scatter(n[cs],rr[cs],s=52,marker=mk[g],color=cols[g],edgecolor='white',lw=.8,zorder=3,label=f'{g} (n={len(cs)})')
for c in T.index: ax.annotate(c,(n[c],rr[c]),xytext=(4,3),textcoords='offset points',fontsize=7,color=INK)
ax.set_xlabel('N.º de partos (2025)'); ax.set_ylabel('Taxa de cesariana (%)'); ax.yaxis.set_major_formatter(ff)
ax.legend(frameon=False,fontsize=8,loc='upper left',bbox_to_anchor=(1.01,1))
ax.set_title('Funnel plot de 2025 por região (limites binomiais em torno da taxa global)',loc='left',fontsize=11,color=INK)
fig.tight_layout(); fig.savefig(W+'Fig4_3_funnel_regiao.png',dpi=150); plt.close()
fz=pd.DataFrame({'Código':T.index,'Região':[RG[c] for c in T.index],'N.º partos':n.astype(int).values,'Taxa CS (%)':rr.map(f).values})
for g in R7: fz[ab[g]]=[f(rr[c]) if RG[c]==g else '' for c in T.index]
fz['Posição']=['Acima 99,8%' if rr[c]>p*100+3.09*se(n[c]) else ('Abaixo 99,8%' if rr[c]<p*100-3.09*se(n[c]) else ('Acima 95%' if rr[c]>p*100+1.96*se(n[c]) else ('Abaixo 95%' if rr[c]<p*100-1.96*se(n[c]) else 'Dentro'))) for c in T.index]
fz['o']=fz.Região.map({g:i for i,g in enumerate(R7)}); fz=fz.sort_values(['o','Código']).drop(columns='o')
P('## funnel'); P(md(fz))
P('funnel by region', {g:{'acima':list(fz[(fz.Região==g)&(fz.Posição=='Acima 99,8%')].Código),'abaixo':list(fz[(fz.Região==g)&(fz.Posição=='Abaixo 99,8%')].Código)} for g in R7})
pickle.dump((RG,ARS,RS,med,medA),open(W+'s4.pkl','wb'))
out.close()
