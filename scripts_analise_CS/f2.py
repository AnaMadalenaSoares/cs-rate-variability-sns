import pickle, numpy as np, pandas as pd, matplotlib, itertools
matplotlib.use('Agg'); import matplotlib.pyplot as plt
W='w/'
S,S2,T,P_,R2,flag,um,COH,C2=pickle.load(open(W+'s.pkl','rb')); flag=pickle.load(open(W+'flag2.pkl','rb'))
D,chk,sec,m=pickle.load(open(W+'d.pkl','rb'))
C=D.pivot(index='cod',columns='ano',values='ces')
yrs=list(range(2013,2026)); yall=yrs+[2026]
lvraw=D.groupby('cod').nivel_orig.first()
LV={c:{'Ib':'I','I ou II':'I/II'}.get(v,v) for c,v in lvraw.items()}
lowv=['A11','A14','A22','A33','A37']
out=open(W+'out2.md','w')
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
# 1 distribution
dist=[]
for l in ['I','II','III','I/II']:
    cs=[c for c in T.index if LV[c]==l]
    dist.append({'Nível':l if l!='I/II' else 'I/II (indeterminado)','N.º unidades':len(cs),'Códigos':', '.join(cs),
      'Partos médios/ano por unidade 2013–2025':int(round(P_.loc[cs,yrs].mean(axis=1).mean())),'Mín.–máx. partos médios/ano':f'{int(P_.loc[cs,yrs].mean(axis=1).min())}–{int(P_.loc[cs,yrs].mean(axis=1).max())}',
      '% dos partos 2013–2025':f(P_.loc[cs,yrs].values.sum()/P_[yrs].values.sum()*100),'Unidades de baixo volume':', '.join([c for c in cs if c in lowv]) or '—'})
P('## dist'); P(md(pd.DataFrame(dist)))
# 2 stats by level and year
def st(t,ces=None,par=None):
    q1,q3=t.quantile(.25),t.quantile(.75)
    return dict(n=len(t),media=t.mean(),glob=(ces.sum()/par.sum()*100) if ces is not None else np.nan,mediana=t.median(),dp=t.std(ddof=0),cv=t.std(ddof=0)/t.mean()*100,mn=t.min(),mx=t.max(),amp=t.max()-t.min(),q1=q1,q3=q3,iiq=q3-q1)
def levelmap(a23):
    d=dict(LV); d['A23']=a23; return d
rows=[]
for y in yall:
    for l in ['I','II','III','I/II','Total']:
        cs=list(T.index) if l=='Total' else [c for c in T.index if LV[c]==l]
        s=st(T.loc[cs,y],C.loc[cs,y],P_.loc[cs,y]); s.update(ano=y,nivel=l); rows.append(s)
SL=pd.DataFrame(rows)
def tab(SL,lv):
    x=SL[SL.nivel==lv]
    return pd.DataFrame({'Ano':[lab(y) for y in x.ano],'N.º unidades':x.n.astype(int),'Média simples (%)':x.media.map(f),'Taxa global (%)':x.glob.map(f),'Mediana (%)':x.mediana.map(f),'Desvio-padrão (p.p.)':x.dp.map(lambda v:f(v,2)),'CV (%)':x.cv.map(f),'Mínimo (%)':x.mn.map(f),'Máximo (%)':x.mx.map(f),'Amplitude (p.p.)':x.amp.map(f),'Q1 (%)':x.q1.map(f),'Q3 (%)':x.q3.map(f),'IIQ (p.p.)':x.iiq.map(f)})
for l in ['I','II','III']: P(f'## stats {l}'); P(md(tab(SL,l)))
x=SL[SL.nivel=='I/II']; P('## A23', md(pd.DataFrame({'Ano':[lab(y) for y in x.ano],'Taxa A23 (%)':x.media.map(f)})))
# 3 order
def order_counts(lmap,years,excl=set()):
    res=[]
    for y in years:
        med={}
        for l in ['I','II','III']:
            cs=[c for c in T.index if lmap[c]==l and (c,y) not in excl]
            med[l]=T.loc[cs,y].median()
        res.append(dict(ano=y,I=med['I'],II=med['II'],III=med['III'],full=med['I']<med['II']<med['III'],i_ii=med['I']<med['II'],ii_iii=med['II']<med['III'],i_iii=med['I']<med['III']))
    return pd.DataFrame(res)
OC=order_counts(LV,yall)
P('## order'); P(md(pd.DataFrame({'Ano':[lab(y) for y in OC.ano],'Mediana I (%)':OC.I.map(f),'Mediana II (%)':OC.II.map(f),'Mediana III (%)':OC.III.map(f),'A23 I/II (%)':[f(T.at['A23',y]) for y in OC.ano],'I < II':np.where(OC.i_ii,'Sim','Não'),'II < III':np.where(OC.ii_iii,'Sim','Não'),'I < III':np.where(OC.i_iii,'Sim','Não'),'I < II < III':np.where(OC.full,'Sim','Não'),'Ordem observada':[ ' < '.join(sorted(['I','II','III'],key=lambda k:r[k])) for _,r in OC.iterrows()]})))
def summ(oc):
    o=oc[oc.ano<=2025]; return dict(full=int(o.full.sum()),i_ii=int(o.i_ii.sum()),ii_iii=int(o.ii_iii.sum()),i_iii=int(o.i_iii.sum()))
P('main counts', summ(OC))
sens={}
for nm,mp in [('A23 fora (principal)',LV),('A23 como I',levelmap('I')),('A23 como II',levelmap('II'))]:
    sens[nm]=summ(order_counts(mp,yrs))
sens['Sem unidade-anos R2b']=summ(order_counts(LV,yrs,excl=flag))
sens['Sem A13 2019 (◊)']=summ(order_counts(LV,yrs,excl={('A13',2019)}))
P('## sens', sens)
# also medians with A23 as I/II per year, for table
for nm,mp in [('I',levelmap('I')),('II',levelmap('II'))]:
    oc=order_counts(mp,yrs); P(f'A23 as {nm} medians', {int(r.ano):(f(r.I),f(r.II),f(r.III)) for _,r in oc.iterrows()})
# mean-based order too
mo=[]
for y in yrs:
    mm={l:SL[(SL.ano==y)&(SL.nivel==l)].media.iloc[0] for l in ['I','II','III']}; gg={l:SL[(SL.ano==y)&(SL.nivel==l)].glob.iloc[0] for l in ['I','II','III']}
    mo.append((mm['I']<mm['II']<mm['III'], gg['I']<gg['II']<gg['III'], ' < '.join(sorted(mm,key=mm.get)), ' < '.join(sorted(gg,key=gg.get))))
P('order by mean full', sum(a for a,_,_,_ in mo),'by global full', sum(b for _,b,_,_ in mo), [c for _,_,c,_ in mo], [d for *_,d in mo])
# period means by level
pm=pd.DataFrame({'cod':T.index,'nivel':[LV[c] for c in T.index],'media':um.values,'agreg':(C[yrs].sum(axis=1)/P_[yrs].sum(axis=1)*100).values})
pr=[]
for l in ['I','II','III','I/II']:
    t=pm[pm.nivel==l].media; s=st(t); s['nivel']=l; s['agreg']=C.loc[pm[pm.nivel==l].cod,yrs].values.sum()/P_.loc[pm[pm.nivel==l].cod,yrs].values.sum()*100; pr.append(s)
s=st(pm.media); s['nivel']='Total'; s['agreg']=C[yrs].values.sum()/P_[yrs].values.sum()*100; pr.append(s)
PR=pd.DataFrame(pr)
P('## period by level'); P(md(pd.DataFrame({'Nível':PR.nivel,'N.º unidades':PR.n.astype(int),'Média das médias (%)':PR.media.map(f),'Taxa agregada 2013–2025 (%)':PR.agreg.map(f),'Mediana (%)':PR.mediana.map(f),'Desvio-padrão (p.p.)':PR.dp.map(lambda v:f(v,2)),'CV (%)':PR.cv.map(f),'Mínimo (%)':PR.mn.map(f),'Máximo (%)':PR.mx.map(f),'Amplitude (p.p.)':PR.amp.map(f),'Q1 (%)':PR.q1.map(f),'Q3 (%)':PR.q3.map(f),'IIQ (p.p.)':PR.iiq.map(f)})))
# sorted units by mean with level
P('units by mean', [(c,LV[c],f(um[c])) for c in um.sort_values(ascending=False).index])
# overlap
ov=[]
for y in yrs:
    I=T.loc[[c for c in T.index if LV[c]=='I'],y]; II=T.loc[[c for c in T.index if LV[c]=='II'],y]; III=T.loc[[c for c in T.index if LV[c]=='III'],y]
    pij=lambda a,b: np.mean([u>v for u in a for v in b])*100
    ov.append({'Ano':y,'I acima do máximo do III (n.º)':int((I>III.max()).sum()),'I acima da mediana do III (n.º de '+str(len(I))+')':int((I>III.median()).sum()),'II acima do máximo do III (n.º)':int((II>III.max()).sum()),
       'III abaixo do mínimo do I (n.º)':int((III<I.min()).sum()),'III abaixo da mediana do I (n.º)':int((III<I.median()).sum()),
       '% pares I > III':f(pij(I,III)),'% pares I > II':f(pij(I,II)),'% pares II > III':f(pij(II,III))})
OV=pd.DataFrame(ov); P('## overlap'); P(md(OV))
# period-mean overlap
Im=pm[pm.nivel=='I'].set_index('cod').media; IIm=pm[pm.nivel=='II'].set_index('cod').media; IIIm=pm[pm.nivel=='III'].set_index('cod').media
P('period: I above max III', list(Im[Im>IIIm.max()].index), 'III max', f(IIIm.max()), IIIm.idxmax(),'I below min III', list(Im[Im<IIIm.min()].index),'III min',f(IIIm.min()))
P('period pairs I>III', f(np.mean([u>v for u in Im for v in IIIm])*100),'I>II',f(np.mean([u>v for u in Im for v in IIm])*100),'II>III',f(np.mean([u>v for u in IIm for v in IIIm])*100))
# 4 within vs total
wv=[]
for y in yrs:
    r={'Ano':y}
    for l in ['I','II','III','Total']:
        x=SL[(SL.ano==y)&(SL.nivel==l)].iloc[0]; r[f'CV {l} (%)']=x.cv; r[f'Amplitude {l} (p.p.)']=x.amp; r[f'IIQ {l} (p.p.)']=x.iiq
    wv.append(r)
WV=pd.DataFrame(wv)
P('## within'); P(md(WV.assign(**{c:WV[c].map(f) for c in WV.columns if c!='Ano'})))
for l in ['I','II','III']:
    P(l,'years amp>=50% of total', int((WV[f'Amplitude {l} (p.p.)']>=0.5*WV['Amplitude Total (p.p.)']).sum()),
      'years CV>= total', int((WV[f'CV {l} (%)']>=WV['CV Total (%)']).sum()),'years IIQ>=total',int((WV[f'IIQ {l} (p.p.)']>=WV['IIQ Total (p.p.)']).sum()),
      'mean ratio amp',f(np.mean(WV[f'Amplitude {l} (p.p.)']/WV['Amplitude Total (p.p.)'])*100),'mean ratio cv',f(np.mean(WV[f'CV {l} (%)']/WV['CV Total (%)'])*100),'mean ratio iiq',f(np.mean(WV[f'IIQ {l} (p.p.)']/WV['IIQ Total (p.p.)'])*100))
# medians range across levels vs amp within: difference of medians max-min per year
WV['dif_med']=[OC.set_index('ano').loc[y,['I','II','III']].astype(float).max()-OC.set_index('ano').loc[y,['I','II','III']].astype(float).min() for y in yrs]
P('diff between level medians per year', WV.dif_med.round(1).tolist(), 'mean',f(WV.dif_med.mean()), 'vs mean within-level amp I/II/III', [f(WV[f'Amplitude {l} (p.p.)'].mean()) for l in ['I','II','III']])
# atypical by level
atyp={'A10':'Atípica (acima)','A37':'Atípica (acima)','A15':'Atípica (abaixo)','A09':'Atípica (abaixo)','A04':'Quase atípica (acima)','A21':'Quase atípica (acima)','A27':'Quase atípica (acima)','A11':'Quase atípica (acima)','A25':'Quase atípica (abaixo)'}
P('atyp by level', {c:(LV[c],v) for c,v in atyp.items()})
# within-level funnel: per level, units above/below level-specific pooled rate? (descriptive) — position relative to level median in years
pos=[]
for c in T.index:
    l=LV[c]
    if l=='I/II': continue
    cs=[k for k in T.index if LV[k]==l]
    ab=sum(T.at[c,y]>T.loc[cs,y].median() for y in yrs); pos.append((c,l,ab))
P('years above own level median', pos)
# 2025 funnel by level chart + table
p=C[2025].sum()/P_[2025].sum(); n=P_[2025].astype(float); r=C[2025]/P_[2025]*100
cols={'I':'#2a78d6','II':'#eb6834','III':'#1baf7a','I/II':'#6250d6'}
mk={'I':'o','II':'s','III':'^','I/II':'D'}
INK,MUT='#0b0b0b','#52514e'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#bbb','xtick.color':MUT,'ytick.color':MUT,'figure.facecolor':'#fcfcfb','axes.facecolor':'#fcfcfb'})
ff=matplotlib.ticker.FuncFormatter(lambda v,q:(f'{v:.0f}' if abs(v-round(v))<1e-9 else f'{v:.1f}').replace('.',','))
fig,ax=plt.subplots(figsize=(12,6.2)); nn=np.linspace(350,5600,400); se=lambda k: np.sqrt(p*(1-p)/k)*100
for z,ls,l in [(1.96,'--','Limites 95%'),(3.09,'-','Limites 99,8%')]:
    ax.plot(nn,p*100+z*se(nn),color=MUT,ls=ls,lw=1.1,label=l); ax.plot(nn,p*100-z*se(nn),color=MUT,ls=ls,lw=1.1)
ax.axhline(p*100,color=INK,lw=1,label=f'Taxa global 2025 ({f(p*100)}%)')
for l in ['I','II','III','I/II']:
    cs=[c for c in T.index if LV[c]==l]
    ax.scatter(n[cs],r[cs],s=55,marker=mk[l],color=cols[l],edgecolor='white',lw=1,zorder=3,label=f'Nível {l}' if l!='I/II' else 'I/II (indeterminado)')
for c in T.index: ax.annotate(c,(n[c],r[c]),xytext=(4,3),textcoords='offset points',fontsize=7,color=INK)
ax.set_xlabel('N.º de partos (2025)'); ax.set_ylabel('Taxa de cesariana (%)'); ax.yaxis.set_major_formatter(ff)
ax.legend(frameon=False,fontsize=8,loc='upper left',bbox_to_anchor=(1.01,1))
ax.set_title('Funnel plot de 2025 por nível hospitalar (limites binomiais em torno da taxa global)',loc='left',fontsize=11,color=INK)
fig.tight_layout(); fig.savefig(W+'Fig2_3_funnel_nivel.png',dpi=160); plt.close()
fz=pd.DataFrame({'Código':T.index,'Nível':[LV[c] for c in T.index],'N.º partos':n.astype(int).values,'Taxa CS (%)':r.map(f).values,
  'Taxa nível I (%)':[f(r[c]) if LV[c]=='I' else '' for c in T.index],'Taxa nível II (%)':[f(r[c]) if LV[c]=='II' else '' for c in T.index],'Taxa nível III (%)':[f(r[c]) if LV[c]=='III' else '' for c in T.index],'Taxa I/II (%)':[f(r[c]) if LV[c]=='I/II' else '' for c in T.index]})
fz=fz.sort_values(['Nível','Código'],key=lambda s: s.map({'I':0,'II':1,'III':2,'I/II':3}) if s.name=='Nível' else s)
P('## funnel level'); P(md(fz))
P('2025 funnel position by level', {l:{'acima':[c for c in T.index if LV[c]==l and r[c]>p*100+3.09*se(n[c])],'abaixo':[c for c in T.index if LV[c]==l and r[c]<p*100-3.09*se(n[c])]} for l in ['I','II','III','I/II']})
# boxplot period means by level
fig,ax=plt.subplots(figsize=(8.5,5.5)); rng=np.random.default_rng(3)
levels=['I','II','III','I/II']
data=[pm[pm.nivel==l].media.values for l in levels[:3]]
bp=ax.boxplot(data,positions=[0,1,2],widths=.5,patch_artist=True,showfliers=False,whis=1.5,medianprops=dict(color=INK,lw=2))
for i,b in enumerate(bp['boxes']): b.set(facecolor=cols[levels[i]]+'33',edgecolor=cols[levels[i]],lw=1.3)
for i,l in enumerate(levels):
    sub=pm[pm.nivel==l]; xs=i+rng.uniform(-.15,.15,len(sub)) if l!='I/II' else [3]*len(sub)
    ax.scatter(xs,sub.media,s=38,marker=mk[l],color=cols[l],edgecolor='white',lw=.8,zorder=3)
    order_=np.argsort(sub.media.values); ys=[]
    for k in order_:
        v=sub.media.values[k]; yy=v if not ys or v-ys[-1]>=0.45 else ys[-1]+0.45; ys.append(yy)
        ax.annotate(sub.cod.values[k],(list(xs)[k],v),xytext=(i+0.3,yy),fontsize=7,va='center',color=INK,arrowprops=dict(arrowstyle='-',color='#bbb',lw=.5))
ax.axhline(um.median(),color=MUT,lw=.8,ls=':'); ax.text(3.45,um.median(),'Mediana total',fontsize=7,color=MUT,va='bottom',ha='right')
ax.set_xticks(range(4)); ax.set_xticklabels([f'Nível I\n(n = {sum(pm.nivel=="I")})',f'Nível II\n(n = {sum(pm.nivel=="II")})',f'Nível III\n(n = {sum(pm.nivel=="III")})','I/II (indet.)\n(n = 1)'])
ax.set_ylabel('Taxa de cesariana média 2013–2025 (%)'); ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(2)); ax.yaxis.set_major_formatter(ff)
ax.set_title('Taxa de cesariana média 2013–2025 por nível hospitalar (um ponto por unidade)',loc='left',fontsize=10.5,color=INK)
fig.text(.01,.01,'Caixa: Q1–Q3 (quartis inclusivos); linha: mediana; bigodes: até 1,5 × IIQ. A23 (I/II) fora da comparação da ordem esperada.',fontsize=7.5,color=MUT)
fig.tight_layout(rect=(0,.03,1,1)); fig.savefig(W+'Fig2_1_boxplot_nivel.png',dpi=160); plt.close()
bx=[]
for l in levels:
    t=pm[pm.nivel==l].media; q1,q3=t.quantile(.25),t.quantile(.75); iq=q3-q1
    lw_=t[t>=q1-1.5*iq].min(); hw=t[t<=q3+1.5*iq].max()
    bx.append({'Nível':l,'Mínimo (%)':f(t.min()),'Bigode inf. (%)':f(lw_),'Q1 (%)':f(q1),'Mediana (%)':f(t.median()),'Q3 (%)':f(q3),'Bigode sup. (%)':f(hw),'Máximo (%)':f(t.max()),'Q1 − bigode inf.':f(q1-lw_),'Mediana − Q1':f(t.median()-q1),'Q3 − mediana':f(q3-t.median()),'Bigode sup. − Q3':f(hw-q3),'Fora dos bigodes':', '.join(f'{c} ({f(v)})' for c,v in zip(pm[pm.nivel==l].cod,t) if v>q3+1.5*iq or v<q1-1.5*iq) or '—'})
P('## box summary'); P(md(pd.DataFrame(bx)))
pts=pm.copy(); pts['ord']=pts.nivel.map({'I':0,'II':1,'III':2,'I/II':3}); pts=pts.sort_values(['ord','media'],ascending=[True,False])
P('## box points'); P(md(pd.DataFrame({'Código':pts.cod,'Nível':pts.nivel,'Média 2013–2025 (%)':pts.media.map(f),'Nível I':[f(v) if l=='I' else '' for l,v in zip(pts.nivel,pts.media)],'Nível II':[f(v) if l=='II' else '' for l,v in zip(pts.nivel,pts.media)],'Nível III':[f(v) if l=='III' else '' for l,v in zip(pts.nivel,pts.media)],'I/II':[f(v) if l=='I/II' else '' for l,v in zip(pts.nivel,pts.media)]})))
# median evolution chart
fig,ax=plt.subplots(figsize=(10,5.2))
for l in ['I','II','III']:
    ax.plot(yrs,OC.set_index('ano').loc[yrs,l],color=cols[l],lw=2,marker=mk[l],ms=6,label=f'Nível {l}')
    ax.plot([2025,2026],OC.set_index('ano').loc[[2025,2026],l],color=cols[l],lw=2,ls='--'); ax.plot([2026],[OC.set_index('ano').at[2026,l]],marker=mk[l],ms=7,mfc='white',mec=cols[l],mew=2)
ax.plot(yrs,T.loc['A23',yrs],color=cols['I/II'],lw=1.2,ls=':',marker='D',ms=4,label='A23 (I/II indeterminado)')
ax.plot([2026],[T.at['A23',2026]],marker='D',ms=5,mfc='white',mec=cols['I/II'])
ax.set_xticks(yall); ax.set_xticklabels([str(y) if y<2026 else '2026\n(jan–abr)' for y in yall],fontsize=8)
ax.set_ylabel('Mediana da taxa de cesariana (%)'); ax.set_ylim(20,40); ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(2)); ax.yaxis.set_major_formatter(ff)
ax.legend(frameon=False,fontsize=8,loc='upper left',ncol=2)
ax.set_title('Mediana da taxa de cesariana por nível hospitalar, 2013–2026',loc='left',fontsize=11,color=INK)
fig.text(.01,.01,'Nível I inclui A17 e A32 (Ib). Tracejado e marcador vazio: 2026, janeiro–abril. A23: valor da própria unidade.',fontsize=7.5,color=MUT)
fig.tight_layout(rect=(0,.03,1,1)); fig.savefig(W+'Fig2_2_mediana_nivel.png',dpi=160); plt.close()
P('## med evol'); P(md(pd.DataFrame({'Ano':[lab(y) for y in OC.ano],'Mediana nível I (%)':OC.I.map(f),'Mediana nível II (%)':OC.II.map(f),'Mediana nível III (%)':OC.III.map(f),'A23 I/II (%)':[f(T.at['A23',y]) for y in OC.ano]})))
pickle.dump((LV,SL,OC,PR,WV,pm),open(W+'s2.pkl','wb'))
out.close()
