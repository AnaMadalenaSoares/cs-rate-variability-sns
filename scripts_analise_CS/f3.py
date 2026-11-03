import pickle, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
W='w/'
S,S2,T,P_,R2,flag,um,COH,C2=pickle.load(open(W+'s.pkl','rb')); flag=pickle.load(open(W+'flag2.pkl','rb'))
D,chk,sec,m=pickle.load(open(W+'d.pkl','rb'))
LV,SL,OC,PR,WV,pm=pickle.load(open(W+'s2.pkl','rb'))
C=D.pivot(index='cod',columns='ano',values='ces'); SE=D.pivot(index='cod',columns='ano',values='setor')
yrs=list(range(2013,2026)); yall=yrs+[2026]
out=open(W+'out3.md','w')
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
    q1,q3=t.quantile(.25),t.quantile(.75); n=len(t)
    return dict(n=n,media=t.mean(),glob=ces.sum()/par.sum()*100,mediana=t.median(),dp=t.std(ddof=0) if n>1 else np.nan,cv=t.std(ddof=0)/t.mean()*100 if n>1 else np.nan,mn=t.min(),mx=t.max(),amp=t.max()-t.min() if n>1 else np.nan,q1=q1 if n>1 else np.nan,q3=q3 if n>1 else np.nan,iiq=q3-q1 if n>1 else np.nan)
rows=[]
for y in yall:
    for s_ in ['EPE','PPP','Total']:
        cs=list(T.index) if s_=='Total' else list(SE.index[SE[y]==s_])
        d=st(T.loc[cs,y],C.loc[cs,y],P_.loc[cs,y]); d.update(ano=y,setor=s_,cods=', '.join(cs) if s_=='PPP' else ''); rows.append(d)
SS=pd.DataFrame(rows)
# counts
cnt=pd.DataFrame({'Ano':[lab(y) for y in yall],'N.º EPE':[int((SE[y]=='EPE').sum()) for y in yall],'N.º PPP':[int((SE[y]=='PPP').sum()) for y in yall],'Unidades PPP':[', '.join(SE.index[SE[y]=='PPP']) for y in yall],
  'PPP por nível':[', '.join(f'{c} ({LV[c]})' for c in SE.index[SE[y]=='PPP']) for y in yall],'% partos em PPP':[f(P_.loc[SE.index[SE[y]=='PPP'],y].sum()/P_[y].sum()*100) for y in yall]})
P('## counts'); P(md(cnt))
def tab(s_):
    x=SS[SS.setor==s_]
    return pd.DataFrame({'Ano':[lab(y) for y in x.ano],'N.º unidades':x.n.astype(int),'Média simples (%)':x.media.map(f),'Taxa global (%)':x.glob.map(f),'Mediana (%)':x.mediana.map(f),'Desvio-padrão (p.p.)':x.dp.map(lambda v:f(v,2)),'CV (%)':x.cv.map(f),'Mínimo (%)':x.mn.map(f),'Máximo (%)':x.mx.map(f),'Amplitude (p.p.)':x.amp.map(f),'Q1 (%)':x.q1.map(f),'Q3 (%)':x.q3.map(f),'IIQ (p.p.)':x.iiq.map(f)})
P('## EPE'); P(md(tab('EPE'))); P('## PPP'); P(md(tab('PPP')))
# PPP unit rates per year
pr=pd.DataFrame({'Código':['A15','A16','A17','A28'],'Nível':[LV[c] for c in ['A15','A16','A17','A28']]})
for y in yall: pr[lab(y)]=[f(T.at[c,y])+('' if SE.at[c,y]=='PPP' else ' (EPE)') for c in pr.Código]
P('## ppp units'); P(md(pr))
# medians compare + position
cmp=[]
for y in yrs:
    e=SS[(SS.ano==y)&(SS.setor=='EPE')].iloc[0]; p=SS[(SS.ano==y)&(SS.setor=='PPP')].iloc[0]; t=SS[(SS.ano==y)&(SS.setor=='Total')].iloc[0]
    ppp=list(SE.index[SE[y]=='PPP'])
    cmp.append({'Ano':y,'N.º PPP':int(p.n),'Mediana EPE (%)':f(e.mediana),'Mediana PPP (%)':f(p.mediana),'Dif. PPP − EPE (p.p.)':f(p.mediana-e.mediana,2),'Taxa global EPE (%)':f(e.glob),'Taxa global PPP (%)':f(p.glob),
      'PPP abaixo da mediana EPE (n.º)':int((T.loc[ppp,y]<e.mediana).sum()),'PPP dentro do IIQ EPE (n.º)':int(((T.loc[ppp,y]>=e.q1)&(T.loc[ppp,y]<=e.q3)).sum()),'Mín.–máx. EPE (%)':f'{f(e.mn)}–{f(e.mx)}','Mín.–máx. PPP (%)':f'{f(p.mn)}–{f(p.mx)}'})
CM=pd.DataFrame(cmp); P('## compare'); P(md(CM))
P('years PPP median < EPE median', int((CM['Dif. PPP − EPE (p.p.)'].str.replace(',','.').astype(float)<0).sum()))
# within vs total (years with >=2 PPP)
wt=[]
for y in yrs:
    e=SS[(SS.ano==y)&(SS.setor=='EPE')].iloc[0]; p=SS[(SS.ano==y)&(SS.setor=='PPP')].iloc[0]; t=SS[(SS.ano==y)&(SS.setor=='Total')].iloc[0]
    wt.append({'Ano':y,'CV EPE (%)':f(e.cv),'CV PPP (%)':f(p.cv),'CV Total (%)':f(t.cv),'Amplitude EPE (p.p.)':f(e.amp),'Amplitude PPP (p.p.)':f(p.amp),'Amplitude Total (p.p.)':f(t.amp),'IIQ EPE (p.p.)':f(e.iiq),'IIQ PPP (p.p.)':f(p.iiq),'IIQ Total (p.p.)':f(t.iiq),'Amplitude EPE / Total (%)':f(e.amp/t.amp*100)})
P('## within'); P(md(pd.DataFrame(wt)))
# confounding with level: within level II, 2013-2019
lv2=[c for c in T.index if LV[c]=='II']
w2=[]
for y in yrs:
    ppp=[c for c in lv2 if SE.at[c,y]=='PPP']; epe=[c for c in lv2 if SE.at[c,y]=='EPE']
    e=T.loc[epe,y]; p=T.loc[ppp,y]
    w2.append({'Ano':y,'N.º EPE nível II':len(epe),'N.º PPP nível II':len(ppp),'PPP nível II':', '.join(ppp),'Mediana EPE II (%)':f(e.median()),'Mediana PPP II (%)':f(p.median()),'Dif. PPP − EPE (p.p.)':f(p.median()-e.median(),2),
               'Mín.–máx. EPE II (%)':f'{f(e.min())}–{f(e.max())}','Mín.–máx. PPP II (%)':f'{f(p.min())}–{f(p.max())}','Q1–Q3 EPE II (%)':f'{f(e.quantile(.25))}–{f(e.quantile(.75))}','PPP abaixo da mediana EPE II (n.º)':int((p<e.median()).sum())})
W2=pd.DataFrame(w2); P('## level II'); P(md(W2))
P('years PPP II median < EPE II', int((W2['Dif. PPP − EPE (p.p.)'].str.replace(',','.').astype(float)<0).sum()))
lv1=[c for c in T.index if LV[c]=='I']
w1=[]
for y in range(2013,2021):
    e=T.loc[[c for c in lv1 if c!='A17'],y]
    w1.append({'Ano':y,'A17 (PPP, %)':f(T.at['A17',y]),'Mediana EPE nível I (n = 13, %)':f(e.median()),'Dif. A17 − mediana (p.p.)':f(T.at['A17',y]-e.median(),2),'Q1–Q3 EPE I (%)':f'{f(e.quantile(.25))}–{f(e.quantile(.75))}','Posição A17 (n.º EPE I abaixo, de 13)':int((e<T.at['A17',y]).sum())})
P('## level I A17'); P(md(pd.DataFrame(w1)))
# period 2013-2019 means by sector (stable classification), and level II
per=list(range(2013,2020))
mm=T[per].mean(axis=1); ppp4=['A15','A16','A17','A28']
P('2013-2019 means PPP', {c:f(mm[c]) for c in ppp4},'median PPP',f(mm[ppp4].median()),'EPE median',f(mm.drop(ppp4).median()),'EPE II median', f(mm[[c for c in lv2 if c not in ppp4]].median()),'EPE II range',f(mm[[c for c in lv2 if c not in ppp4]].min()),f(mm[[c for c in lv2 if c not in ppp4]].max()),'EPE range',f(mm.drop(ppp4).min()),f(mm.drop(ppp4).max()))
P('ranks 2013-2019 means of PPP among 37 (1=highest)', {c:int(mm.rank(ascending=False)[c]) for c in ppp4})
# before/after
ba=[]
trans={'A28':(2019,'2019 (PPP jan–ago, EPE set–dez → PPP)'),'A17':(2021,'2021 (PPP jan–mai, EPE jun–dez → EPE)'),'A15':(2022,'2022 (EPE desde janeiro)')}
for c,(ty,txt) in trans.items():
    ppp_y=[y for y in yrs if SE.at[c,y]=='PPP']; epe_y=[y for y in yrs if SE.at[c,y]=='EPE']
    last3=ppp_y[-3:]; first3=epe_y[:3]
    oth=[k for k in T.index if k not in ppp4]
    ref_b=np.mean([T.loc[oth,y].median() for y in last3]); ref_a=np.mean([T.loc[oth,y].median() for y in first3])
    gb=np.mean([S.at[y,'glob'] for y in last3]); ga=np.mean([S.at[y,'glob'] for y in first3])
    # relative position: percentile among all 37 per year (share of units below)
    pct=lambda ys: np.mean([(T[y]<T.at[c,y]).sum()/36*100 for y in ys])
    ba.append({'Código':c,'Nível':LV[c],'Ano de transição':txt,'Anos PPP':f'{ppp_y[0]}–{ppp_y[-1]}','Anos EPE':f'{epe_y[0]}–{epe_y[-1]}',
      'Média PPP, todos os anos (%)':f(T.loc[c,ppp_y].mean()),'Média EPE, todos os anos (%)':f(T.loc[c,epe_y].mean()),
      'Média últimos 3 anos PPP (%)':f(T.loc[c,last3].mean()),'Média primeiros 3 anos EPE (%)':f(T.loc[c,first3].mean()),'Variação da unidade (p.p.)':f(T.loc[c,first3].mean()-T.loc[c,last3].mean(),2),
      'Variação da mediana das unidades sempre EPE, mesmos anos (p.p.)':f(ref_a-ref_b,2),'Variação líquida (p.p.)':f((T.loc[c,first3].mean()-T.loc[c,last3].mean())-(ref_a-ref_b),2),
      'Posição relativa antes (% unidades abaixo)':f(pct(last3)),'Posição relativa depois (% unidades abaixo)':f(pct(first3)),'Janelas':f'{last3[0]}–{last3[-1]} vs {first3[0]}–{first3[-1]}'})
P('## before after'); P(md(pd.DataFrame(ba)))
for c in ['A15','A17','A28']: P(c, {y:(f(T.at[c,y]),SE.at[c,y]) for y in yrs}, 'R2b', [y for y in yrs if (c,y) in flag])
# A16 all period PPP: vs EPE II median each year
P('A16 below EPE II median years', sum(T.at['A16',y]<T.loc[[k for k in lv2 if SE.at[k,y]=='EPE'],y].median() for y in yrs))
P('A15 below EPE II median years PPP', sum(T.at['A15',y]<T.loc[[k for k in lv2 if SE.at[k,y]=='EPE'],y].median() for y in range(2013,2022)), 'EPE years', sum(T.at['A15',y]<T.loc[[k for k in lv2 if SE.at[k,y]=='EPE' and k!='A15'],y].median() for y in range(2022,2026)))
P('A28 below EPE II median PPP years', sum(T.at['A28',y]<T.loc[[k for k in lv2 if SE.at[k,y]=='EPE'],y].median() for y in range(2013,2020)),'EPE years',sum(T.at['A28',y]<T.loc[[k for k in lv2 if SE.at[k,y]=='EPE' and k!='A28'],y].median() for y in range(2020,2026)))
# all ex-PPP pooled: rate of 4 units 2013-2019 vs 2022-2025
# ---- charts
B,O,G,INK,MUT='#2a78d6','#eb6834','#1baf7a','#0b0b0b','#52514e'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#bbb','xtick.color':MUT,'ytick.color':MUT,'figure.facecolor':'#fcfcfb','axes.facecolor':'#fcfcfb'})
ff=matplotlib.ticker.FuncFormatter(lambda v,q:(f'{v:.0f}' if abs(v-round(v))<1e-9 else f'{v:.1f}').replace('.',','))
# boxplot 2013-2019 means
fig,ax=plt.subplots(figsize=(8,5.5)); rng=np.random.default_rng(5)
grp={'EPE':[c for c in T.index if c not in ppp4],'PPP':ppp4}
bp=ax.boxplot([mm[grp['EPE']].values,mm[grp['PPP']].values],positions=[0,1],widths=.5,patch_artist=True,showfliers=False,medianprops=dict(color=INK,lw=2))
for b,c in zip(bp['boxes'],[B,O]): b.set(facecolor=c+'33',edgecolor=c,lw=1.3)
for i,(g,col) in enumerate([('EPE',B),('PPP',O)]):
    v=mm[grp[g]]; xs=i+rng.uniform(-.14,.14,len(v)); ax.scatter(xs,v,s=36,color=col,edgecolor='white',lw=.8,zorder=3,marker='o' if g=='EPE' else 's')
    srt=np.argsort(v.values); ys=[]
    if g=='EPE': srt=list(srt[:3])+list(srt[-4:])
    for k in srt:
        yy=v.values[k] if not ys or v.values[k]-ys[-1]>=.45 else ys[-1]+.45; ys.append(yy)
        ax.annotate(v.index[k]+(f' ({LV[v.index[k]]})' if g=='PPP' else ''),(xs[k],v.values[k]),xytext=(i+.3,yy),fontsize=7,va='center',color=INK,arrowprops=dict(arrowstyle='-',color='#bbb',lw=.5))
ax.set_xticks([0,1]); ax.set_xticklabels([f'EPE\n(n = {len(grp["EPE"])})',f'PPP\n(n = 4)']); ax.set_xlim(-.6,1.9)
ax.set_ylabel('Taxa de cesariana média 2013–2019 (%)'); ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(2)); ax.yaxis.set_major_formatter(ff)
ax.set_title('Taxa de cesariana média 2013–2019 por setor de gestão (um ponto por unidade)',loc='left',fontsize=10.5,color=INK)
fig.text(.01,.01,'2013–2019: período com as 4 PPP (A28 em 2019: PPP pela maioria dos meses).\nEntre parênteses: nível das PPP. EPE: identificadas só as 3 mais baixas e as 4 mais altas. Grupo PPP pequeno (4 unidades).',fontsize=7.2,color=MUT)
fig.tight_layout(rect=(0,.06,1,1)); fig.savefig(W+'Fig3_1_boxplot_setor.png',dpi=160); plt.close()
bxt=[]
for g in ['EPE','PPP']:
    t=mm[grp[g]]; q1,q3=t.quantile(.25),t.quantile(.75); iq=q3-q1; lw_=min(t[t>=q1-1.5*iq].min(),q1); hw=max(t[t<=q3+1.5*iq].max(),q3)
    bxt.append({'Setor':g,'N.º':len(t),'Mínimo (%)':f(t.min()),'Bigode inf. (%)':f(lw_),'Q1 (%)':f(q1),'Mediana (%)':f(t.median()),'Q3 (%)':f(q3),'Bigode sup. (%)':f(hw),'Máximo (%)':f(t.max()),'Q1 − bigode inf.':f(q1-lw_),'Mediana − Q1':f(t.median()-q1),'Q3 − mediana':f(q3-t.median()),'Bigode sup. − Q3':f(hw-q3),'Fora dos bigodes':', '.join(f'{c} ({f(v)})' for c,v in t.items() if v>q3+1.5*iq or v<q1-1.5*iq) or '—'})
P('## box'); P(md(pd.DataFrame(bxt)))
bpts=pd.DataFrame({'Código':mm.index,'Setor 2013–2019':['PPP' if c in ppp4 else 'EPE' for c in mm.index],'Nível':[LV[c] for c in mm.index],'Média 2013–2019 (%)':mm.map(f).values}).sort_values(['Setor 2013–2019','Código'])
bpts['EPE']=[v if s_=='EPE' else '' for s_,v in zip(bpts['Setor 2013–2019'],bpts['Média 2013–2019 (%)'])]; bpts['PPP']=[v if s_=='PPP' else '' for s_,v in zip(bpts['Setor 2013–2019'],bpts['Média 2013–2019 (%)'])]
P('## box pts'); P(md(bpts))
# median evolution
fig,ax=plt.subplots(figsize=(10,5.2))
me=SS[SS.setor=='EPE'].set_index('ano').mediana; mp=SS[SS.setor=='PPP'].set_index('ano').mediana; npp=SS[SS.setor=='PPP'].set_index('ano').n
ax.plot(yrs,me[yrs],color=B,lw=2,marker='o',label='Mediana EPE'); ax.plot([2025,2026],me[[2025,2026]],color=B,lw=2,ls='--'); ax.plot([2026],[me[2026]],marker='o',mfc='white',mec=B,mew=2)
ax.plot(yrs,mp[yrs],color=O,lw=2,marker='s',label='Mediana PPP'); ax.plot([2025,2026],mp[[2025,2026]],color=O,lw=2,ls='--'); ax.plot([2026],[mp[2026]],marker='s',mfc='white',mec=O,mew=2)
for y in yrs: ax.annotate(f'n={int(npp[y])}',(y,mp[y]),xytext=(0,-14),textcoords='offset points',fontsize=7,color=O,ha='center')
ax.set_xticks(yall); ax.set_xticklabels([str(y) if y<2026 else '2026\n(jan–abr)' for y in yall],fontsize=8)
ax.set_ylim(20,36); ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(2)); ax.yaxis.set_major_formatter(ff); ax.set_ylabel('Mediana da taxa de cesariana (%)')
ax.legend(frameon=False,fontsize=8,loc='upper left')
ax.set_title('Mediana da taxa de cesariana por setor de gestão, 2013–2026',loc='left',fontsize=11,color=INK)
fig.text(.01,.01,'n = n.º de unidades PPP no ano (4 até 2019; 1 a partir de 2022, só A16). Tracejado e marcador vazio: 2026, jan–abr.',fontsize=7.5,color=MUT)
fig.tight_layout(rect=(0,.03,1,1)); fig.savefig(W+'Fig3_2_mediana_setor.png',dpi=160); plt.close()
P('## med'); P(md(pd.DataFrame({'Ano':[lab(y) for y in yall],'Mediana EPE (%)':[f(me[y]) for y in yall],'Mediana PPP (%)':[f(mp[y]) for y in yall],'N.º PPP':[int(npp[y]) for y in yall]})))
# funnel 2019 by sector (+ level marker)
y=2019; p=C[y].sum()/P_[y].sum(); n=P_[y].astype(float); r=C[y]/P_[y]*100
fig,ax=plt.subplots(figsize=(12,6.2)); nn=np.linspace(350,5200,400); se=lambda k: np.sqrt(p*(1-p)/k)*100
for z,ls,l in [(1.96,'--','Limites 95%'),(3.09,'-','Limites 99,8%')]:
    ax.plot(nn,p*100+z*se(nn),color=MUT,ls=ls,lw=1.1,label=l); ax.plot(nn,p*100-z*se(nn),color=MUT,ls=ls,lw=1.1)
ax.axhline(p*100,color=INK,lw=1,label=f'Taxa global 2019 ({f(p*100)}%)')
for g,col,mk in [('EPE',B,'o'),('PPP',O,'s')]:
    cs=[c for c in T.index if SE.at[c,y]==g]; ax.scatter(n[cs],r[cs],s=60 if g=='PPP' else 42,marker=mk,color=col,edgecolor='white',lw=1,zorder=3,label=g)
for c in T.index: ax.annotate(c+('◊' if c=='A13' else '')+('‡' if c=='A28' else ''),(n[c],r[c]),xytext=(4,3),textcoords='offset points',fontsize=7,color=INK,fontweight='bold' if SE.at[c,y]=='PPP' else 'normal')
ax.set_xlabel('N.º de partos (2019)'); ax.set_ylabel('Taxa de cesariana (%)'); ax.yaxis.set_major_formatter(ff)
ax.legend(frameon=False,fontsize=8,loc='upper left',bbox_to_anchor=(1.01,1))
ax.set_title('Funnel plot de 2019 por setor de gestão (último ano com as 4 PPP)',loc='left',fontsize=11,color=INK)
fig.text(.01,.01,'‡ A28: ano de transição (PPP jan–ago, EPE set–dez; classificada PPP). ◊ A13: valor atípico – possível problema de registo.',fontsize=7.5,color=MUT)
fig.tight_layout(rect=(0,.03,1,1)); fig.savefig(W+'Fig3_3_funnel_setor2019.png',dpi=160); plt.close()
fz=pd.DataFrame({'Código':T.index,'Setor 2019':[SE.at[c,y] for c in T.index],'Nível':[LV[c] for c in T.index],'N.º partos':n.astype(int).values,'Taxa CS (%)':r.map(f).values,'Taxa EPE (%)':[f(r[c]) if SE.at[c,y]=='EPE' else '' for c in T.index],'Taxa PPP (%)':[f(r[c]) if SE.at[c,y]=='PPP' else '' for c in T.index],
   'Posição':['Acima 99,8%' if r[c]>p*100+3.09*se(n[c]) else ('Abaixo 99,8%' if r[c]<p*100-3.09*se(n[c]) else ('Acima 95%' if r[c]>p*100+1.96*se(n[c]) else ('Abaixo 95%' if r[c]<p*100-1.96*se(n[c]) else 'Dentro'))) for c in T.index]})
P('## funnel pts'); P(md(fz.sort_values(['Setor 2019','Código'])))
seq=[300,400,500,750,1000,1500,2000,2500,3000,4000,5000]
P(md(pd.DataFrame({'N.º partos (sequência)':seq,'Taxa global (%)':f(p*100),'LI 99,8% (%)':[f(p*100-3.09*se(k)) for k in seq],'LI 95% (%)':[f(p*100-1.96*se(k)) for k in seq],'LS 95% (%)':[f(p*100+1.96*se(k)) for k in seq],'LS 99,8% (%)':[f(p*100+3.09*se(k)) for k in seq]})))
P('p2019',f(p*100,2))
# 2025 A16 position
p5=C[2025].sum()/P_[2025].sum(); P('A16 2025', f(T.at['A16',2025]), 'LI95', f((p5-1.96*np.sqrt(p5*(1-p5)/P_.at['A16',2025]))*100))
out.close()
