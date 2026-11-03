import pickle, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, BoundaryNorm
W='w/'
S,S2,T,P_,R2,flag,um,COH,C2=pickle.load(open(W+'s.pkl','rb')); flag=pickle.load(open(W+'flag2.pkl','rb'))
D,chk,sec,m=pickle.load(open(W+'d.pkl','rb'))
C=D.pivot(index='cod',columns='ano',values='ces')
out=open(W+'out1b.md','w')
def P(*a): print(*a,file=out)
def f(x,d=1):
    if pd.isna(x): return 'a definir'
    x=round(float(x),d)+0.0
    if x==0: x=0.0
    return f'{x:.{d}f}'.replace('.',',').replace('-0,'+'0'*d,'0,'+'0'*d)
def md(df):
    cols=[str(c) for c in df.columns]
    s='| '+' | '.join(cols)+' |\n|'+'|'.join(['---']*len(cols))+'|\n'
    for _,r in df.iterrows(): s+='| '+' | '.join(str(v) for v in r.values)+' |\n'
    return s
B,O,G,INK,MUT='#2a78d6','#eb6834','#1baf7a','#0b0b0b','#52514e'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#bbb','xtick.color':MUT,'ytick.color':MUT,'figure.facecolor':'#fcfcfb','axes.facecolor':'#fcfcfb'})
ff=matplotlib.ticker.FuncFormatter(lambda v,p:(f'{v:.0f}' if abs(v-round(v))<1e-9 else f'{v:.1f}').replace('.',','))
yrs=list(range(2013,2026)); yall=yrs+[2026]
lab=lambda y: str(y) if y<2026 else '2026 (jan–abr)'
lowv={c for c in T.index if P_.loc[c,yrs].mean()<600}
# ---------- 1 boxplot
fig,ax=plt.subplots(figsize=(11,5.2))
data=[T[y].values for y in yall]
bp=ax.boxplot(data,positions=range(len(yall)),widths=.55,whis=1.5,patch_artist=True,showfliers=False,medianprops=dict(color=INK,lw=2))
for i,b in enumerate(bp['boxes']):
    b.set(facecolor='#cde2fb' if i<13 else '#ececec',edgecolor=B if i<13 else MUT,lw=1.2)
rng=np.random.default_rng(1)
for i,y in enumerate(yall):
    ax.scatter(i+rng.uniform(-.18,.18,len(T)),T[y],s=12,color=B if i<13 else MUT,alpha=.55,zorder=3,lw=0)
# label extremes outside whiskers
for i,y in enumerate(yall):
    t=T[y]; q1,q3=t.quantile(.25),t.quantile(.75); iq=q3-q1
    o=t[(t>q3+1.5*iq)|(t<q1-1.5*iq)].sort_values()
    ys=[];
    for c,v in o.items():
        yy=v if not ys or v-ys[-1]>=1.3 else ys[-1]+1.3
        ys.append(yy); ax.annotate(c,(i+.08,v),xytext=(i+.24,yy),fontsize=7,color=INK,va='center')
ax.set_xticks(range(len(yall))); ax.set_xticklabels([str(y) if y<2026 else '2026\n(jan–abr)' for y in yall],fontsize=8)
ax.set_ylabel('Taxa de cesariana (%)'); ax.yaxis.set_major_formatter(ff); ax.set_ylim(15,55)
ax.set_title('Distribuição das taxas de cesariana das 37 unidades, por ano',loc='left',fontsize=11,color=INK)
fig.text(.01,.01,'Caixa: Q1–Q3 (quartis inclusivos); linha: mediana; bigodes: até 1,5 × IIQ; pontos: unidades (códigos identificados fora dos bigodes). 2026 a cinzento: jan–abr.',fontsize=7.5,color=MUT)
fig.tight_layout(rect=(0,.03,1,1)); fig.savefig(W+'Fig1B_1_boxplot.png',dpi=160); plt.close()
# outliers table + box data
rows=[]
for y in yall:
    t=T[y]; q1,q3=t.quantile(.25),t.quantile(.75); iq=q3-q1
    lo_w=t[t>=q1-1.5*iq].min(); hi_w=t[t<=q3+1.5*iq].max()
    o=t[(t>q3+1.5*iq)|(t<q1-1.5*iq)]
    rows.append({'Ano':lab(y),'Mínimo (%)':f(t.min()),'Bigode inferior (%)':f(lo_w),'Q1 (%)':f(q1),'Mediana (%)':f(t.median()),'Q3 (%)':f(q3),'Bigode superior (%)':f(hi_w),'Máximo (%)':f(t.max()),'Q1 − bigode inf. (p.p.)':f(q1-lo_w),'Mediana − Q1 (p.p.)':f(t.median()-q1),'Q3 − mediana (p.p.)':f(q3-t.median()),'Bigode sup. − Q3 (p.p.)':f(hi_w-q3),'Valores fora dos bigodes':', '.join(f'{c} ({f(v)})' for c,v in o.sort_values(ascending=False).items()) or '—'})
P('## box'); P(md(pd.DataFrame(rows)))
# ---------- 2 funnel
def funnel(n,ces,codes,title,fn,p):
    r=ces/n*100
    nn=np.linspace(max(50,n.min()*0.8),n.max()*1.1,400)
    se=lambda k: np.sqrt(p*(1-p)/k)*100
    fig,ax=plt.subplots(figsize=(10,6))
    for z,ls,l in [(1.96,'--','95%'),(3.09,'-','99,8%')]:
        ax.plot(nn,p*100+z*se(nn),color=MUT,ls=ls,lw=1.2,label=f'Limites {l}'); ax.plot(nn,p*100-z*se(nn),color=MUT,ls=ls,lw=1.2)
    ax.axhline(p*100,color=INK,lw=1.2,label=f'Taxa global ({f(p*100)}%)')
    hi=r>p*100+3.09*se(n); lo=r<p*100-3.09*se(n); mid=~(hi|lo)
    ax.scatter(n[mid],r[mid],s=40,color=B,edgecolor='white',lw=1,zorder=3,label='Dentro dos limites 99,8%')
    ax.scatter(n[hi],r[hi],s=48,color=O,edgecolor='white',lw=1,zorder=3,label='Acima do limite 99,8%')
    ax.scatter(n[lo],r[lo],s=48,color=G,edgecolor='white',lw=1,zorder=3,label='Abaixo do limite 99,8%')
    for c in codes: ax.annotate(c,(n[c],r[c]),xytext=(4,3),textcoords='offset points',fontsize=7,color=INK)
    ax.set_xlabel('N.º de partos'); ax.set_ylabel('Taxa de cesariana (%)'); ax.yaxis.set_major_formatter(ff)
    ax.set_title(title,loc='left',fontsize=11,color=INK); ax.legend(frameon=False,fontsize=8,loc='upper right')
    fig.tight_layout(); fig.savefig(W+fn,dpi=160); plt.close()
    pts=pd.DataFrame({'Código':codes,'N.º partos':n.astype(int).values,'Cesarianas':ces.astype(int).values,'Taxa CS (%)':r.map(f).values,
        'LI 99,8% no n da unidade (%)':(p*100-3.09*se(n)).map(f).values,'LS 99,8% no n da unidade (%)':(p*100+3.09*se(n)).map(f).values,
        'Posição':np.where(hi,'Acima 99,8%',np.where(lo,'Abaixo 99,8%',np.where(r>p*100+1.96*se(n),'Acima 95%',np.where(r<p*100-1.96*se(n),'Abaixo 95%','Dentro'))))})
    base=[100,200,300,400,500,750,1000,1500,2000,2500,3000,4000,5000,6000,7500,10000,12500,15000,20000,25000,30000,40000,50000,60000,70000]
    seq=np.array([k for k in base if n.min()*0.5<=k<=n.max()*1.1])
    lim=pd.DataFrame({'N.º partos (sequência)':seq,'Taxa global (%)':f(p*100),'LI 99,8% (%)':[f(p*100-3.09*se(k)) for k in seq],'LI 95% (%)':[f(p*100-1.96*se(k)) for k in seq],'LS 95% (%)':[f(p*100+1.96*se(k)) for k in seq],'LS 99,8% (%)':[f(p*100+3.09*se(k)) for k in seq]})
    return pts,lim,hi,lo
p25=C[2025].sum()/P_[2025].sum()
pts25,lim25,hi25,lo25=funnel(P_[2025].astype(float),C[2025].astype(float),T.index,'Funnel plot: taxa de cesariana vs. n.º de partos, 2025','Fig1B_2a_funnel2025.png',p25)
Pp=P_[yrs].sum(axis=1).astype(float); Cp=C[yrs].sum(axis=1).astype(float); pp=Cp.sum()/Pp.sum()
ptsP,limP,hiP,loP=funnel(Pp,Cp,T.index,'Funnel plot: taxa de cesariana vs. n.º de partos, 2013–2025 agregado','Fig1B_2b_funnelperiodo.png',pp)
P('## funnel 2025 p',f(p25*100,2)); P(md(pts25.sort_values('Código'))); P(md(lim25))
P('counts 2025: hi',hi25.sum(),list(T.index[hi25]),'lo',lo25.sum(),list(T.index[lo25]))
P('in95 2025', (pts25['Posição']=='Dentro').sum(), 'acima95',(pts25['Posição']=='Acima 95%').sum(),'abaixo95',(pts25['Posição']=='Abaixo 95%').sum())
P('## funnel periodo p',f(pp*100,2)); P(md(ptsP.sort_values('Código'))); P(md(limP))
P('counts per: hi',hiP.sum(),list(T.index[hiP]),'lo',loP.sum(),list(T.index[loP]))
P('within', (ptsP['Posição']=='Dentro').sum(), ptsP['Posição'].value_counts().to_dict())
# ---------- 3 heatmap rates
order=um.sort_values(ascending=False).index
H=T.loc[order,yall]
cm=LinearSegmentedColormap.from_list('b',['#f2f7fd','#86b6ef','#2a78d6','#104281'])
fig,ax=plt.subplots(figsize=(11,12))
im=ax.imshow(H.values,cmap=cm,vmin=19,vmax=51,aspect='auto')
for i in range(H.shape[0]):
    for j in range(H.shape[1]):
        v=H.iat[i,j]; ax.text(j,i,f(v)+('*' if P_.at[H.index[i],yall[j]]<300 else ''),ha='center',va='center',fontsize=6.8,color='white' if v>37 else INK)
ax.set_xticks(range(len(yall))); ax.set_xticklabels([str(y) if y<2026 else '2026\n(jan–abr)' for y in yall],fontsize=8)
ax.set_yticks(range(len(order))); ax.set_yticklabels([f'{c} ({f(um[c])})' for c in order],fontsize=7.5)
ax.axvline(12.5,color='white',lw=3)
for s in ax.spines.values(): s.set_visible(False)
cb=fig.colorbar(im,ax=ax,fraction=.025,pad=.01); cb.set_label('Taxa de cesariana (%)'); cb.ax.yaxis.set_major_formatter(ff)
ax.set_title('Taxa de cesariana (%) por unidade e ano, unidades ordenadas pela média 2013–2025 (entre parênteses)',loc='left',fontsize=10.5,color=INK)
fig.text(.01,.005,'* < 300 partos. 2026: janeiro–abril (ano incompleto), separado por linha branca.',fontsize=8,color=MUT)
fig.tight_layout(rect=(0,.01,1,1)); fig.savefig(W+'Fig1B_3_heatmap_taxas.png',dpi=150); plt.close()
hm=pd.DataFrame({'Código':order,'Média 2013–2025 (%)':[f(um[c]) for c in order]})
for y in yall: hm[lab(y)]=[f(T.at[c,y]) for c in order]
P('## heatmap'); P(md(hm))
# ---------- 4 variations
V=T.diff(axis=1)[list(range(2014,2027))]
dg=S['glob'].astype(float).diff()
vy=list(range(2014,2026))
# (i)
fig,ax=plt.subplots(figsize=(11,5.5))
ax.bar(range(len(vy)),dg[vy],color=[O if v>0 else B for v in dg[vy]],width=.6,alpha=.85,zorder=2)
for i,y in enumerate(vy):
    ax.scatter(i+rng.uniform(-.2,.2,len(T)),V[y],s=12,color=INK,alpha=.45,zorder=3,lw=0)
    ext=V[y][V[y].abs()>8]
    for c,v in ext.items(): ax.annotate(c,(i+.24,v),fontsize=6.5,color=INK,va='center')
ax.axhline(0,color=INK,lw=.8)
ax.set_xticks(range(len(vy))); ax.set_xticklabels([f'{y}\nvs {y-1}' for y in vy],fontsize=7.5)
ax.set_ylabel('Variação face ao ano anterior (p.p.)'); ax.yaxis.set_major_formatter(ff)
ax.set_title('Variação anual da taxa de cesariana: taxa global (barras) e cada unidade (pontos), 2014–2025',loc='left',fontsize=10.5,color=INK)
from matplotlib.patches import Patch; from matplotlib.lines import Line2D
ax.legend(handles=[Patch(color=O,label='Taxa global: subida'),Patch(color=B,label='Taxa global: descida'),Line2D([],[],ls='none',marker='o',color=INK,alpha=.5,label='Unidade')],frameon=False,fontsize=8,loc='upper left')
fig.text(.01,.01,'Códigos identificados: variações superiores a 8 p.p. em valor absoluto.',fontsize=7.5,color=MUT)
fig.tight_layout(rect=(0,.03,1,1)); fig.savefig(W+'Fig1B_4i_variacao_combo.png',dpi=160); plt.close()
ci=pd.DataFrame({'Ano':[f'{y} vs {y-1}' for y in vy],'Δ taxa global (p.p.)':[f(dg[y],2) for y in vy]})
for c in T.index: ci[c]=[f(V.at[c,y],2) for y in vy]
P('## combo'); P(md(ci))
# (ii)
cmap=ListedColormap(['#104281','#2a78d6','#86b6ef','#d9d9d6','#f4a582','#e34948','#a50f15'])
bnd=[-30,-5,-2,-0.5,0.5,2,5,30]; norm=BoundaryNorm(bnd,cmap.N)
Vo=V.loc[order,vy+[2026]]
fig,ax=plt.subplots(figsize=(11,12))
ax.imshow(Vo.values,cmap=cmap,norm=norm,aspect='auto')
for i in range(Vo.shape[0]):
    for j in range(Vo.shape[1]):
        v=Vo.iat[i,j]; c=Vo.index[i]; y=(vy+[2026])[j]
        mk='†' if (c,y) in flag else ''
        ax.text(j,i,f(v)+mk,ha='center',va='center',fontsize=6.8,color='white' if abs(v)>=5 else INK)
ax.set_xticks(range(Vo.shape[1])); ax.set_xticklabels([f'{y}\nvs {y-1}' if y<2026 else '2026*\nvs 2025' for y in vy+[2026]],fontsize=7.5)
ax.set_yticks(range(len(order))); ax.set_yticklabels(order,fontsize=8); ax.axvline(11.5,color='white',lw=3)
for s in ax.spines.values(): s.set_visible(False)
leg=[Patch(color=cmap(i),label=l) for i,l in enumerate(['≤ −5','−5 a −2','−2 a −0,5','|Δ| < 0,5 (estável)','0,5 a 2','2 a 5','≥ 5'])]
ax.legend(handles=leg,title='Variação (p.p.)',frameon=False,fontsize=7.5,title_fontsize=8,loc='upper left',bbox_to_anchor=(1.01,1))
ax.set_title('Variação anual da taxa de cesariana (p.p.) por unidade, ordenadas pela média 2013–2025',loc='left',fontsize=10.5,color=INK)
fig.text(.01,.005,'Azul = descida; vermelho = subida; cinzento = variação inferior a 0,5 p.p. † ano com interrupção/transferência de partos (R2b). *2026: jan–abr.',fontsize=7.5,color=MUT)
fig.tight_layout(rect=(0,.01,1,1)); fig.savefig(W+'Fig1B_4ii_heatmap_variacoes.png',dpi=150); plt.close()
# (iii)
tv=pd.DataFrame({'Código':T.index})
for y in vy+[2026]: tv[f'{y} vs {y-1}' if y<2026 else '2026 (jan–abr) vs 2025']=[f(V.at[c,y],2)+('†' if (c,y) in flag else '') for c in T.index]
tv['Subidas 2014–2025']=[(V.loc[c,vy]>=0.5).sum() for c in T.index]
tv['Descidas 2014–2025']=[(V.loc[c,vy]<=-0.5).sum() for c in T.index]
tv['Estável 2014–2025']=[(V.loc[c,vy].abs()<0.5).sum() for c in T.index]
tv['Variação absoluta média (p.p.)']=[f(V.loc[c,vy].abs().mean(),2) for c in T.index]
P('## var wide'); P(md(tv))
cnt=pd.DataFrame({'Ano':[f'{y} vs {y-1}' if y<2026 else '2026 (jan–abr) vs 2025' for y in vy+[2026]],
  'Subiram (≥ 0,5 p.p.)':[(V[y]>=0.5).sum() for y in vy+[2026]],'Desceram (≤ −0,5 p.p.)':[(V[y]<=-0.5).sum() for y in vy+[2026]],'Estáveis (|Δ| < 0,5 p.p.)':[(V[y].abs()<0.5).sum() for y in vy+[2026]],
  'Δ taxa global (p.p.)':[f(dg[y],2) for y in vy+[2026]],'Mediana das variações (p.p.)':[f(V[y].median(),2) for y in vy+[2026]],'Variação absoluta média (p.p.)':[f(V[y].abs().mean(),2) for y in vy+[2026]]})
P('## counts'); P(md(cnt))
P('same sign as global per year', {y:int((np.sign(V[y])==np.sign(dg[y])).sum()) for y in vy})
P('mean abs var unit-level overall', f(V[vy].abs().stack().mean(),2), 'median', f(V[vy].abs().stack().median(),2))
# ---------- 5 consistently above/below global
G_=S['glob'].astype(float)
ab=pd.DataFrame({y:T[y]>G_[y] for y in yrs}); be=pd.DataFrame({y:T[y]<G_[y] for y in yrs})
# funnel annual counts
se=lambda p,n: np.sqrt(p*(1-p)/n)
h99=pd.Series(0,index=T.index); l99=h99.copy(); h95=h99.copy(); l95=h99.copy()
for y in yrs:
    p=G_[y]/100; n=P_[y]; r=T[y]/100
    h99+=(r>p+3.09*se(p,n)); l99+=(r<p-3.09*se(p,n)); h95+=(r>p+1.96*se(p,n)); l95+=(r<p-1.96*se(p,n))
cl=lambda c: 'Atípica' if max(h99[c],l99[c])>=10 and min(h99[c],l99[c])==0 else ('Quase atípica' if 7<=max(h99[c],l99[c])<=9 and min(h99[c],l99[c])==0 else '—')
t5=pd.DataFrame({'Código':T.index,'Anos acima da taxa global (de 13)':ab.sum(axis=1).values,'Anos abaixo da taxa global (de 13)':be.sum(axis=1).values,
  'Consistência (≥ 10 de 13)':['Acima' if a>=10 else ('Abaixo' if b>=10 else '—') for a,b in zip(ab.sum(axis=1),be.sum(axis=1))],
  'Anos acima LS 99,8%':h99.values,'Anos abaixo LI 99,8%':l99.values,'Anos acima LS 95%':h95.values,'Anos abaixo LI 95%':l95.values,
  'Classificação (Fase 1A)':[cl(c) for c in T.index],'Funnel 2025':pts25.set_index('Código').loc[T.index,'Posição'].values,'Funnel 2013–2025':ptsP.set_index('Código').loc[T.index,'Posição'].values,
  'Baixo volume (< 600 partos/ano)':['Sim' if c in lowv else '' for c in T.index]})
P('## t5'); P(md(t5))
P('consist above', list(t5[t5['Consistência (≥ 10 de 13)']=='Acima'].Código), 'below', list(t5[t5['Consistência (≥ 10 de 13)']=='Abaixo'].Código))
P('lowv',sorted(lowv))
# ---------- 6 abrupt changes
rows=[]
for c in T.index:
    for y in vy+[2026]:
        v=V.at[c,y]
        if abs(v)>5:
            r2=[]
            if (c,y) in flag: r2.append(f'{y} R2b')
            if (c,y-1) in flag: r2.append(f'{y-1} R2b')
            rows.append({'Código':c,'Ano':f'{y} vs {y-1}' if y<2026 else '2026 (jan–abr) vs 2025','Taxa ano anterior (%)':f(T.at[c,y-1]),'Taxa no ano (%)':f(T.at[c,y])+('*' if P_.at[c,y]<300 else ''),'Variação (p.p.)':f(v,2),'Partos ano anterior':P_.at[c,y-1],'Partos no ano':P_.at[c,y],
                         'Coincide com R2b':'Sim ('+'; '.join(r2)+')' if r2 else 'Não','Baixo volume':'Sim' if c in lowv else '','Reverte no ano seguinte (> 5 p.p. em sentido oposto)':('Sim' if y<2026 and y+1 in V.columns and abs(V.at[c,y+1])>5 and np.sign(V.at[c,y+1])!=np.sign(v) else ('—' if y>=2025 else 'Não'))})
A6=pd.DataFrame(rows)
P('## abrupt'); P(md(A6))
mm=A6[~A6.Ano.str.startswith('2026')]
P('n abrupt 2014-2025',len(mm),'up',(mm['Variação (p.p.)'].str.replace(',','.').astype(float)>0).sum(),'R2b',(mm['Coincide com R2b']!='Não').sum(),'lowvol',(mm['Baixo volume']=='Sim').sum(),'units',mm.Código.nunique(), mm.Código.value_counts().to_dict())
P('per year', mm.Ano.value_counts().sort_index().to_dict())
P('n abrupt 2026',(A6.Ano.str.startswith('2026')).sum())
# share lowvol unit-years
P('low vol unit share of unit-years', len(lowv)*12, 'of', 37*12)
pickle.dump((V,dg,t5,A6,pts25,ptsP,order),open(W+'s1b.pkl','wb'))
out.close()
