import pickle, numpy as np, pandas as pd, matplotlib
from scipy.stats import spearmanr
matplotlib.use('Agg'); import matplotlib.pyplot as plt
W='w/'
S,S2,T,P_,R2,flag,um,COH,C2=pickle.load(open(W+'s.pkl','rb')); flag=pickle.load(open(W+'flag2.pkl','rb'))
D,chk,sec,m=pickle.load(open(W+'d.pkl','rb'))
LV,SL,OC,PR,WV,pm=pickle.load(open(W+'s2.pkl','rb'))
RG,ARS,RS,med,medA=pickle.load(open(W+'s4.pkl','rb'))
C=D.pivot(index='cod',columns='ano',values='ces')
yrs=list(range(2013,2026)); yall=yrs+[2026]
lowv=['A11','A14','A22','A33','A37']
atyp={'A10':'Atípica ↑','A37':'Atípica ↑','A15':'Atípica ↓','A09':'Atípica ↓','A04':'Quase ↑','A21':'Quase ↑','A27':'Quase ↑','A11':'Quase ↑','A25':'Quase ↓'}
out=open(W+'out5.md','w')
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
rho=lambda a,b: spearmanr(a,b).correlation
vm=P_[yrs].mean(axis=1)
# descriptive volume table per year
dv=[]
for y in yall:
    v=P_[y]; dv.append({'Ano':lab(y),'N.º unidades':37,'Média (partos)':int(round(v.mean())),'Mediana':int(round(v.median())),'Mínimo':int(v.min()),'Unidade mín.':v.idxmin(),'Máximo':int(v.max()),'Unidade máx.':v.idxmax(),'Q1':int(round(v.quantile(.25))),'Q3':int(round(v.quantile(.75))),'N.º < 600':int((v<600).sum()),'N.º < 300 (R13)':int((v<300).sum())})
P('## vol desc'); P(md(pd.DataFrame(dv)))
# rho per year all / without R2b / within levels
rr=[]
for y in yall:
    r_all=rho(P_[y],T[y]); keep=[c for c in T.index if (c,y) not in flag]; r_nf=rho(P_.loc[keep,y],T.loc[keep,y])
    d={'Ano':lab(y),'N.º':37,'rho (todas)':f(r_all,2),'N.º sem R2b':len(keep),'rho sem R2b':f(r_nf,2)}
    for l in ['I','II','III']:
        cs=[c for c in T.index if LV[c]==l]; d[f'rho nível {l} (n={len(cs)})']=f(rho(P_.loc[cs,y],T.loc[cs,y]),2)
    lv2=[c for c in T.index if c not in lowv]; d['rho sem baixo volume (n=32)']=f(rho(P_.loc[lv2,y],T.loc[lv2,y]),2)
    rr.append(d)
RR=pd.DataFrame(rr); P('## rho annual'); P(md(RR))
fl=lambda s: s.str.replace(',','.').astype(float)
x=RR[RR.Ano.isin([str(y) for y in yrs])]
P('rho all: neg years',int((fl(x['rho (todas)'])<0).sum()),'range',x['rho (todas)'].min(),x['rho (todas)'].max(),'median',f(fl(x['rho (todas)']).median(),2))
for c in ['rho nível I (n=14)','rho nível II (n=17)','rho nível III (n=5)','rho sem baixo volume (n=32)','rho sem R2b']:
    v=fl(x[c]); P(c,'neg',int((v<0).sum()),'min',f(v.min(),2),'max',f(v.max(),2),'median',f(v.median(),2))
# period means
rp={'Todas (37)':rho(vm,um)}
for l in ['I','II','III']:
    cs=[c for c in T.index if LV[c]==l]; rp[f'Nível {l} ({len(cs)})']=rho(vm[cs],um[cs])
cs=[c for c in T.index if c not in lowv]; rp['Sem baixo volume (32)']=rho(vm[cs],um[cs])
cs=[c for c in T.index if c not in atyp or not atyp[c].startswith('Atípica')]; rp['Sem atípicas (33)']=rho(vm[cs],um[cs])
cs=[c for c in T.index if c!='A23']; rp['Sem A23 (36)']=rho(vm[cs],um[cs])
# with means excluding R2b years
um_nf=pd.Series({c:np.mean([T.at[c,y] for y in yrs if (c,y) not in flag]) for c in T.index}); vm_nf=pd.Series({c:np.mean([P_.at[c,y] for y in yrs if (c,y) not in flag]) for c in T.index})
rp['Médias sem anos R2b (37)']=rho(vm_nf,um_nf)
# 2013-2019 and 2020-2025 subperiods
rp['Médias 2013–2019 (37)']=rho(P_[range(2013,2020)].mean(axis=1),T[range(2013,2020)].mean(axis=1)); rp['Médias 2020–2025 (37)']=rho(P_[range(2020,2026)].mean(axis=1),T[range(2020,2026)].mean(axis=1))
P('## rho period'); P(md(pd.DataFrame({'Conjunto':list(rp.keys()),'rho de Spearman (médias do período)':[f(v,2) for v in rp.values()]})))
# classes
bins=[0,600,1500,2500,1e9]; labs=['< 600','600–1499','1500–2499','≥ 2500']
cls=pd.cut(vm,bins,right=False,labels=labs)
bins2=[0,600,1000,2000,3000,1e9]; labs2=['< 600','600–999','1000–1999','2000–2999','≥ 3000']
cls2=pd.cut(vm,bins2,right=False,labels=labs2)
P('## classes'); P(md(pd.DataFrame({'Classe (média de partos/ano 2013–2025)':labs,'N.º unidades':[int((cls==l).sum()) for l in labs],'Unidades (partos médios/ano; nível)':[', '.join(f'{c} ({int(round(vm[c]))}; {LV[c]})' for c in vm[cls==l].sort_values().index) for l in labs]})))
def clsstats(clmap,labs_,years=yall):
    rows=[]
    for y in years:
        for l in labs_:
            cs=[c for c in T.index if clmap[c]==l]
            if not cs: continue
            t=T.loc[cs,y]; q1,q3=t.quantile(.25),t.quantile(.75); n=len(t)
            rows.append(dict(ano=y,cl=l,n=n,media=t.mean(),glob=C.loc[cs,y].sum()/P_.loc[cs,y].sum()*100,mediana=t.median(),dp=t.std(ddof=0) if n>1 else np.nan,cv=t.std(ddof=0)/t.mean()*100 if n>1 else np.nan,mn=t.min(),mx=t.max(),amp=t.max()-t.min() if n>1 else np.nan,iiq=q3-q1 if n>2 else np.nan))
    return pd.DataFrame(rows)
CS=clsstats(cls,labs)
for l in labs:
    x=CS[CS.cl==l]
    P(f'## class {l}'); P(md(pd.DataFrame({'Ano':[lab(y) for y in x.ano],'N.º':x.n,'Média (%)':x.media.map(f),'Taxa global (%)':x.glob.map(f),'Mediana (%)':x.mediana.map(f),'DP (p.p.)':x.dp.map(lambda v:f(v,2)),'CV (%)':x.cv.map(f),'Mín. (%)':x.mn.map(f),'Máx. (%)':x.mx.map(f),'Amplitude (p.p.)':x.amp.map(f),'IIQ (p.p.)':x.iiq.map(f)})))
medc=CS.pivot(index='ano',columns='cl',values='mediana')[labs]
mt=pd.DataFrame({'Ano':[lab(y) for y in yall],**{f'Mediana {l} (%)':medc[l].map(f).values for l in labs},'Mediana total (%)':[f(T[y].median()) for y in yall],'Classe com mediana mais alta':[medc.loc[y].astype(float).idxmax() for y in yall],'Classe com mediana mais baixa':[medc.loc[y].astype(float).idxmin() for y in yall]})
P('## class medians'); P(md(mt))
P('highest', medc.loc[yrs].astype(float).idxmax(axis=1).value_counts().to_dict(),'lowest',medc.loc[yrs].astype(float).idxmin(axis=1).value_counts().to_dict())
P('monotonic decreasing years', sum(all(medc.loc[y,labs[i]]>medc.loc[y,labs[i+1]] for i in range(3)) for y in yrs),'increasing',sum(all(medc.loc[y,labs[i]]<medc.loc[y,labs[i+1]] for i in range(3)) for y in yrs))
P('<600 above others years', sum(medc.loc[y,'< 600']>max(medc.loc[y,l] for l in labs[1:]) for y in yrs))
P('<600 vs ≥2500 higher years', sum(medc.loc[y,'< 600']>medc.loc[y,'≥ 2500'] for y in yrs))
# within vs total
wt=[]
for y in yrs:
    t=S.loc[y]; r_={'Ano':y}
    for l in labs:
        x=CS[(CS.ano==y)&(CS.cl==l)].iloc[0]; r_[f'Amplitude {l} (p.p.)']=f(x.amp); r_[f'CV {l} (%)']=f(x.cv)
    r_['Amplitude total (p.p.)']=f(t.amp); r_['CV total (%)']=f(t.cv); wt.append(r_)
WT=pd.DataFrame(wt); P('## within'); P(md(WT))
for l in labs:
    a=fl(WT[f'Amplitude {l} (p.p.)'])/fl(WT['Amplitude total (p.p.)'])*100; P(l,'amp ratio mean',f(a.mean()),'min',f(a.min()),'max',f(a.max()))
# period-level by class
pr=[]
for l in labs+['Total']:
    cs=list(T.index) if l=='Total' else [c for c in T.index if cls[c]==l]; t=um[cs]; q1,q3=t.quantile(.25),t.quantile(.75)
    pr.append({'Classe':l,'N.º':len(cs),'Mediana das médias (%)':f(t.median()),'Média das médias (%)':f(t.mean()),'Taxa agregada 2013–2025 (%)':f(C.loc[cs,yrs].values.sum()/P_.loc[cs,yrs].values.sum()*100),'CV (%)':f(t.std(ddof=0)/t.mean()*100),'Mín. (%)':f(t.min()),'Máx. (%)':f(t.max()),'Amplitude (p.p.)':f(t.max()-t.min()),'IIQ (p.p.)':f(q3-q1) if len(cs)>2 else '—'})
P('## period class'); P(md(pd.DataFrame(pr)))
# sensitivity: suggested classes and annual classification
CS2=clsstats(cls2,labs2,yrs); m2=CS2.pivot(index='ano',columns='cl',values='mediana')[labs2]
P('## sens classes 5'); P(md(pd.DataFrame({'Ano':yrs,**{f'{l} (n={int((cls2==l).sum())})':m2[l].map(f).values for l in labs2},'Mais alta':[m2.loc[y].astype(float).idxmax() for y in yrs],'Mais baixa':[m2.loc[y].astype(float).idxmin() for y in yrs]})))
P('sens5 highest', m2.astype(float).idxmax(axis=1).value_counts().to_dict(),'lowest',m2.astype(float).idxmin(axis=1).value_counts().to_dict())
# annual classification (unit-year)
ann=[]
for y in yrs:
    cl_y=pd.cut(P_[y],bins,right=False,labels=labs); d={'Ano':y}
    for l in labs:
        cs=cl_y.index[cl_y==l]; d[f'{l}: n']=len(cs); d[f'{l}: mediana (%)']=f(T.loc[cs,y].median()) if len(cs) else '—'
    ann.append(d)
P('## annual class'); P(md(pd.DataFrame(ann)))
# class x level crosstab
ct=pd.crosstab(pd.Series([LV[c] for c in T.index],index=T.index,name='Nível'),cls.rename('Classe'))
P('## crosstab'); P(md(ct.reset_index()))
# within level by class (period means)
for l in ['I','II','III']:
    cs=[c for c in T.index if LV[c]==l]
    P(f'level {l}', {k:(int((cls[cs]==k).sum()), f(um[[c for c in cs if cls[c]==k]].median()) if (cls[cs]==k).any() else '—') for k in labs})
# level I without low-volume vs low-volume
I=[c for c in T.index if LV[c]=='I']; Ilow=[c for c in I if c in lowv]; Ioth=[c for c in I if c not in lowv]
P('level I lowvol period median', f(um[Ilow].median()), [ (c,f(um[c])) for c in Ilow], 'other I', f(um[Ioth].median()))
P('level I: years median lowvol > median other I', sum(T.loc[Ilow,y].median()>T.loc[Ioth,y].median() for y in yrs))
# low volume units individually vs total median
P('lowvol units years above total median', {c:int(sum(T.at[c,y]>T[y].median() for y in yrs)) for c in lowv})
# within-unit temporal association
wu=pd.Series({c:rho(P_.loc[c,yrs],T.loc[c,yrs]) for c in T.index})
P('within-unit rho over time: median',f(wu.median(),2),'neg',int((wu<0).sum()),'of 37', 'range',f(wu.min(),2),f(wu.max(),2))
# trend: births vs time per unit and total
P('total births 2013,2025', int(P_[2013].sum()), int(P_[2025].sum()))
# R2b unit-years details
r2t=[]
for c,y in sorted(flag):
    r2t.append({'Código':c,'Ano':y,'Partos':int(P_.at[c,y]),'Partos médios 2013–2025':int(round(vm[c])),'Partos / média (%)':f(P_.at[c,y]/vm[c]*100),'Taxa (%)':f(T.at[c,y]),'Taxa média 2013–2025 (%)':f(um[c]),'Tipo':'Manual (recetora)' if (c,y)==('A02',2023) else ('Subida' if P_.at[c,y]>(P_.at[c,y-1]+P_.at[c,y-2])/2 else 'Descida')})
P('## r2b'); P(md(pd.DataFrame(r2t)))
# ---------- charts
cols={'I':'#2a78d6','II':'#eb6834','III':'#1baf7a','I/II':'#6250d6'}; mk={'I':'o','II':'s','III':'^','I/II':'D'}
INK,MUT='#0b0b0b','#52514e'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#bbb','xtick.color':MUT,'ytick.color':MUT,'figure.facecolor':'#fcfcfb','axes.facecolor':'#fcfcfb'})
ff=matplotlib.ticker.FuncFormatter(lambda v,q:(f'{v:.0f}' if abs(v-round(v))<1e-9 else f'{v:.1f}').replace('.',','))
fig,ax=plt.subplots(figsize=(11,6.2))
for l in ['I','II','III','I/II']:
    cs=[c for c in T.index if LV[c]==l]; ax.scatter(vm[cs],um[cs],s=55,marker=mk[l],color=cols[l],edgecolor='white',lw=.8,zorder=3,label=f'Nível {l}' if l!='I/II' else 'I/II (A23)')
for c in T.index: ax.annotate(c,(vm[c],um[c]),xytext=(4,3),textcoords='offset points',fontsize=7,color=INK)
for b in [600,1500,2500]: ax.axvline(b,color='#ccc',lw=.8,ls='--')
for xx,t in zip([300,1050,2000,3600],labs): ax.text(xx,23.2,t,fontsize=8,color=MUT,ha='center')
ax.set_xlabel('Partos por ano (média 2013–2025)'); ax.set_ylabel('Taxa de cesariana média 2013–2025 (%)'); ax.yaxis.set_major_formatter(ff); ax.set_ylim(22.5,43)
ax.legend(frameon=False,fontsize=8,loc='upper right')
ax.set_title(f'Taxa de cesariana vs. volume de partos (médias 2013–2025): rho de Spearman = {f(rp["Todas (37)"],2)}',loc='left',fontsize=11,color=INK)
fig.text(.01,.01,'Linhas verticais: limites das classes de volume (< 600; 600–1499; 1500–2499; ≥ 2500). rho descritivo, sem p-valor.',fontsize=7.5,color=MUT)
fig.tight_layout(rect=(0,.03,1,1)); fig.savefig(W+'Fig5_1_dispersao_volume.png',dpi=160); plt.close()
sc=pd.DataFrame({'Código':T.index,'Nível':[LV[c] for c in T.index],'Classe de volume':cls.astype(str).values,'Partos médios/ano 2013–2025':vm.round(0).astype(int).values,'Taxa média 2013–2025 (%)':um.map(f).values})
for l in ['I','II','III','I/II']: sc[f'Taxa nível {l} (%)']=[f(um[c]) if LV[c]==l else '' for c in T.index]
sc=sc.sort_values('Partos médios/ano 2013–2025')
P('## scatter'); P(md(sc))
# rho per year chart
fig,ax=plt.subplots(figsize=(10.5,5))
x_=yrs
series=[('rho (todas)','Todas (37)','#0b0b0b','o',2.2),('rho sem R2b','Sem unidade-anos R2b','#888','o',1.2),('rho nível I (n=14)','Nível I (14)',cols['I'],'o',1.5),('rho nível II (n=17)','Nível II (17)',cols['II'],'s',1.5),('rho nível III (n=5)','Nível III (5)',cols['III'],'^',1.2)]
RRi=RR.set_index('Ano')
for col,lb,cc,mm,lw in series:
    v=fl(RRi.loc[[str(y) for y in yrs],col]); ax.plot(x_,v,color=cc,marker=mm,lw=lw,ms=5,label=lb,ls=':' if 'III' in lb else ('--' if 'R2b' in lb else '-'))
ax.axhline(0,color=INK,lw=.8); ax.set_ylim(-1,1); ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.2)); ax.set_xticks(yrs); ax.set_xticklabels([str(y) for y in yrs],fontsize=8)
ax.set_ylabel('rho de Spearman (taxa vs. partos)'); ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,q:f'{v:.1f}'.replace('.',',')))
ax.legend(frameon=False,fontsize=8,loc='lower left',ncol=3)
ax.set_title('rho de Spearman entre a taxa de cesariana e o n.º de partos, por ano, 2013–2025',loc='left',fontsize=11,color=INK)
fig.text(.01,.01,'Medida descritiva da direção e força da associação (sem p-valor). Nível III: 5 unidades, valor muito instável.',fontsize=7.5,color=MUT)
fig.tight_layout(rect=(0,.03,1,1)); fig.savefig(W+'Fig5_2_rho_anual.png',dpi=160); plt.close()
# class boxplot + median evolution (two panels)
fig,axs=plt.subplots(1,2,figsize=(14,5.6),gridspec_kw={'width_ratios':[1,1.3]})
ax=axs[0]; rng=np.random.default_rng(9); ccol=['#2a78d6','#eb6834','#1baf7a','#6250d6']
data=[um[[c for c in T.index if cls[c]==l]].values for l in labs]
bp=ax.boxplot(data,positions=range(4),widths=.5,patch_artist=True,showfliers=False,medianprops=dict(color=INK,lw=2))
for b,cc in zip(bp['boxes'],ccol): b.set(facecolor=cc+'33',edgecolor=cc,lw=1.3)
for i,l in enumerate(labs):
    v=um[[c for c in T.index if cls[c]==l]].sort_values(); xs=i+rng.uniform(-.13,.13,len(v)); ax.scatter(xs,v,s=32,color=ccol[i],edgecolor='white',lw=.7,zorder=3)
    ys=[]
    for k,(c,val) in enumerate(v.items()):
        if not (c in atyp or len(v)<=5 or k in (0,len(v)-1)): continue
        yy=val if not ys or val-ys[-1]>=.55 else ys[-1]+.55; ys.append(yy)
        ax.annotate(c,(xs[k],val),xytext=(i+.28,yy),fontsize=6.8,va='center',color=INK,arrowprops=dict(arrowstyle='-',color='#bbb',lw=.5))
ax.set_xticks(range(4)); ax.set_xticklabels([f'{l}\n(n = {int((cls==l).sum())})' for l in labs],fontsize=8.5); ax.set_xlabel('Classe de volume (partos/ano, média 2013–2025)')
ax.set_ylabel('Taxa de cesariana média 2013–2025 (%)'); ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(2)); ax.yaxis.set_major_formatter(ff)
ax.set_title('Taxa média por classe de volume (um ponto por unidade)',loc='left',fontsize=10,color=INK)
ax=axs[1]
ax.plot(yrs,[T[y].median() for y in yrs],color=MUT,ls=':',lw=1.2,label='Mediana total (37)')
for i,l in enumerate(labs):
    ax.plot(yrs,medc.loc[yrs,l].astype(float),color=ccol[i],lw=2,marker='o',ms=5,label=f'{l} (n={int((cls==l).sum())})')
    ax.plot([2025,2026],medc.loc[[2025,2026],l].astype(float),color=ccol[i],lw=1.5,ls='--'); ax.plot([2026],[medc.at[2026,l]],marker='o',ms=6,mfc='white',mec=ccol[i])
ax.set_xticks(yall); ax.set_xticklabels([str(y)[2:] if y<2026 else '26*' for y in yall],fontsize=8)
ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(2)); ax.yaxis.set_major_formatter(ff); ax.set_ylabel('Mediana da taxa de cesariana (%)')
ax.legend(frameon=False,fontsize=8,loc='upper left'); ax.set_title('Evolução anual da mediana por classe de volume',loc='left',fontsize=10,color=INK)
fig.text(.01,.01,'Classe atribuída pela média de partos/ano 2013–2025 (fixa por unidade). Eixo X à direita: 13 = 2013; *2026: jan–abr.',fontsize=7.5,color=MUT)
fig.tight_layout(rect=(0,.03,1,1)); fig.savefig(W+'Fig5_3_classes_volume.png',dpi=150); plt.close()
bx=[]
for l in labs:
    t=um[[c for c in T.index if cls[c]==l]]; q1,q3=t.quantile(.25),t.quantile(.75); iq=q3-q1; lw_=min(t[t>=q1-1.5*iq].min(),q1); hw=max(t[t<=q3+1.5*iq].max(),q3)
    bx.append({'Classe':l,'N.º':len(t),'Mínimo (%)':f(t.min()),'Bigode inf. (%)':f(lw_),'Q1 (%)':f(q1),'Mediana (%)':f(t.median()),'Q3 (%)':f(q3),'Bigode sup. (%)':f(hw),'Máximo (%)':f(t.max()),'Q1 − bigode inf.':f(q1-lw_),'Mediana − Q1':f(t.median()-q1),'Q3 − mediana':f(q3-t.median()),'Bigode sup. − Q3':f(hw-q3),'Fora dos bigodes':', '.join(f'{c} ({f(v)})' for c,v in t.items() if v>q3+1.5*iq or v<q1-1.5*iq) or '—'})
P('## box'); P(md(pd.DataFrame(bx)))
# funnel 2025 colored by class
y=2025; p=C[y].sum()/P_[y].sum(); n=P_[y].astype(float); rr_=C[y]/P_[y]*100; se=lambda k: np.sqrt(p*(1-p)/k)*100
fig,ax=plt.subplots(figsize=(12.5,6.2)); nn=np.linspace(350,5600,400)
for z,ls,l in [(1.96,'--','Limites 95%'),(3.09,'-','Limites 99,8%')]:
    ax.plot(nn,p*100+z*se(nn),color=MUT,ls=ls,lw=1.1,label=l); ax.plot(nn,p*100-z*se(nn),color=MUT,ls=ls,lw=1.1)
ax.axhline(p*100,color=INK,lw=1,label=f'Taxa global 2025 ({f(p*100)}%)')
for i,l in enumerate(labs):
    cs=[c for c in T.index if cls[c]==l]; ax.scatter(n[cs],rr_[cs],s=52,color=ccol[i],edgecolor='white',lw=.8,zorder=3,label=f'Classe {l} (n={len(cs)})')
for c in T.index: ax.annotate(c+('†' if (c,y) in flag else ''),(n[c],rr_[c]),xytext=(4,3),textcoords='offset points',fontsize=7,color=INK)
ax.set_xlabel('N.º de partos (2025)'); ax.set_ylabel('Taxa de cesariana (%)'); ax.yaxis.set_major_formatter(ff)
ax.legend(frameon=False,fontsize=8,loc='upper left',bbox_to_anchor=(1.01,1))
ax.set_title('Funnel plot de 2025 por classe de volume (classe pela média 2013–2025)',loc='left',fontsize=11,color=INK)
fig.text(.01,.01,'† Unidade-ano com interrupção/transferência de partos (R2b): volume de 2025 atípico (A17: 828 partos; A25: 2700; A07: 1166).',fontsize=7.5,color=MUT)
fig.tight_layout(rect=(0,.03,1,1)); fig.savefig(W+'Fig5_4_funnel_volume.png',dpi=150); plt.close()
fz=pd.DataFrame({'Código':T.index,'Classe':cls.astype(str).values,'N.º partos 2025':n.astype(int).values,'Taxa CS (%)':rr_.map(f).values})
for l in labs: fz[f'Taxa classe {l} (%)']=[f(rr_[c]) if cls[c]==l else '' for c in T.index]
fz['R2b 2025']=['†' if (c,2025) in flag else '' for c in T.index]
P('## funnel'); P(md(fz.sort_values('N.º partos 2025')))
P('2025 funnel by class', {l:{'acima':[c for c in T.index if cls[c]==l and rr_[c]>p*100+3.09*se(n[c])],'abaixo':[c for c in T.index if cls[c]==l and rr_[c]<p*100-3.09*se(n[c])]} for l in labs})
out.close()
