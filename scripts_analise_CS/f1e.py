import pickle, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
W='w/'
S,S2,T,P_,R2,flag,um,COH,C2=pickle.load(open(W+'s.pkl','rb')); flag=pickle.load(open(W+'flag2.pkl','rb'))
D,chk,sec,m=pickle.load(open(W+'d.pkl','rb'))
C=D.pivot(index='cod',columns='ano',values='ces')
yrs=list(range(2013,2026))
out=open(W+'out1c.md','w')
def P(*a): print(*a,file=out)
def f(x,d=1):
    x=round(float(x),d)+0.0
    return f'{x:.{d}f}'.replace('.',',')
def md(df):
    cols=[str(c) for c in df.columns]
    s='| '+' | '.join(cols)+' |\n|'+'|'.join(['---']*len(cols))+'|\n'
    for _,r in df.iterrows(): s+='| '+' | '.join(str(v) for v in r.values)+' |\n'
    return s
def od(n,ces):
    """Spiegelhalter 2005 additive random-effects, 10% winsorised z-scores"""
    p=ces.sum()/n.sum(); r=ces/n; s2=p*(1-p)/n; z=(r-p)/np.sqrt(s2)
    lo,hi=np.quantile(z,[.1,.9]); zw=z.clip(lo,hi)
    I=len(n); phi=(zw**2).sum()/I; w=1/s2
    tau2=max(0,(I*phi-(I-1))/(w.sum()-(w**2).sum()/w.sum()))
    return p,phi,tau2,z
# annual
rows=[];hb=pd.Series(0,index=T.index);lb=hb.copy();ho=hb.copy();lo_=hb.copy();ho95=hb.copy();lo95=hb.copy()
for y in yrs:
    n=P_[y].astype(float); c=C[y].astype(float); p,phi,tau2,z=od(n,c); r=c/n
    s2=p*(1-p)/n
    hb+=(r>p+3.09*np.sqrt(s2)); lb+=(r<p-3.09*np.sqrt(s2))
    ho+=(r>p+3.09*np.sqrt(s2+tau2)); lo_+=(r<p-3.09*np.sqrt(s2+tau2))
    ho95+=(r>p+1.96*np.sqrt(s2+tau2)); lo95+=(r<p-1.96*np.sqrt(s2+tau2))
    rows.append({'Ano':y,'Taxa global (%)':f(p*100,2),'φ (winsorizado 10%)':f(phi,2),'τ (p.p.)':f(np.sqrt(tau2)*100,2),
      'Fora 99,8% binomial':int(((r>p+3.09*np.sqrt(s2))|(r<p-3.09*np.sqrt(s2))).sum()),
      'Fora 99,8% ajustado':int(((r>p+3.09*np.sqrt(s2+tau2))|(r<p-3.09*np.sqrt(s2+tau2))).sum()),
      'Fora 95% ajustado':int(((r>p+1.96*np.sqrt(s2+tau2))|(r<p-1.96*np.sqrt(s2+tau2))).sum()),
      'Acima 99,8% ajustado':', '.join(T.index[(r>p+3.09*np.sqrt(s2+tau2)).values]) or '—',
      'Abaixo 99,8% ajustado':', '.join(T.index[(r<p-3.09*np.sqrt(s2+tau2)).values]) or '—'})
    if y==2025: P25=(p,phi,tau2)
P('## OD annual'); P(md(pd.DataFrame(rows)))
def cls(h,l):
    mx=max(h,l); d='Acima' if h>l else 'Abaixo'
    if min(h,l)>0 and mx>=7: return f'misto'
    return (f'Atípica ({d.lower()})' if mx>=10 else (f'Quase atípica ({d.lower()})' if mx>=7 else '—'))
lowv=['A11','A14','A22','A33','A37']
tb=pd.DataFrame({'Código':T.index,'Acima 99,8% binomial':hb.values,'Abaixo 99,8% binomial':lb.values,'Classificação binomial (principal)':[cls(a,b) for a,b in zip(hb,lb)],
   'Acima 99,8% ajustado':ho.values,'Abaixo 99,8% ajustado':lo_.values,'Classificação ajustada (sensibilidade)':[cls(a,b) for a,b in zip(ho,lo_)],
   'Acima 95% ajustado':ho95.values,'Abaixo 95% ajustado':lo95.values,'Baixo volume':['Sim' if c in lowv else '' for c in T.index]})
P('## class'); P(md(tb[(tb['Classificação binomial (principal)']!='—')|(tb['Classificação ajustada (sensibilidade)']!='—')|(tb['Acima 99,8% ajustado']+tb['Abaixo 99,8% ajustado']>0)]))
P('full', md(tb))
# 2025 funnel adjusted + chart
p,phi,tau2=P25; n=P_[2025].astype(float); c=C[2025].astype(float); r=c/n*100
B,O,G,INK,MUT='#2a78d6','#eb6834','#1baf7a','#0b0b0b','#52514e'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#bbb','xtick.color':MUT,'ytick.color':MUT,'figure.facecolor':'#fcfcfb','axes.facecolor':'#fcfcfb'})
ff=matplotlib.ticker.FuncFormatter(lambda v,q:f'{v:.0f}'.replace('.',','))
nn=np.linspace(350,5600,400)
fig,ax=plt.subplots(figsize=(12,6))
lim=lambda k,z,t: (p+z*np.sqrt(p*(1-p)/k+t))*100
lim_=lambda k,z,t: (p-z*np.sqrt(p*(1-p)/k+t))*100
ax.plot(nn,lim(nn,3.09,0),color='#bbb',lw=1); ax.plot(nn,lim_(nn,3.09,0),color='#bbb',lw=1,label='Limites 99,8% binomiais (principais)')
ax.plot(nn,lim(nn,1.96,tau2),color=MUT,ls='--',lw=1.2,label='Limites 95% ajustados'); ax.plot(nn,lim_(nn,1.96,tau2),color=MUT,ls='--',lw=1.2)
ax.plot(nn,lim(nn,3.09,tau2),color=INK,lw=1.4,label='Limites 99,8% ajustados'); ax.plot(nn,lim_(nn,3.09,tau2),color=INK,lw=1.4)
ax.axhline(p*100,color=INK,lw=.8,alpha=.6,label=f'Taxa global ({f(p*100)}%)')
hi=r>lim(n,3.09,tau2); lo=r<lim_(n,3.09,tau2); mid=~(hi|lo)
ax.scatter(n[mid],r[mid],s=40,color=B,edgecolor='white',lw=1,zorder=3,label='Dentro dos limites 99,8% ajustados')
if hi.any(): ax.scatter(n[hi],r[hi],s=48,color=O,edgecolor='white',lw=1,zorder=3,label='Acima (ajustado)')
if lo.any(): ax.scatter(n[lo],r[lo],s=48,color=G,edgecolor='white',lw=1,zorder=3,label='Abaixo (ajustado)')
for cc in T.index: ax.annotate(cc,(n[cc],r[cc]),xytext=(4,3),textcoords='offset points',fontsize=7,color=INK)
ax.set_xlabel('N.º de partos'); ax.set_ylabel('Taxa de cesariana (%)'); ax.yaxis.set_major_formatter(ff)
ax.set_title('Funnel plot de 2025 com limites ajustados à sobredispersão (Spiegelhalter, 2005)',loc='left',fontsize=11,color=INK)
ax.legend(frameon=False,fontsize=8,loc='upper left',bbox_to_anchor=(1.01,1))
fig.text(.01,.01,f'Efeitos aleatórios aditivos, z-scores winsorizados a 10%: φ = {f(phi,2)}; τ = {f(np.sqrt(tau2)*100,2)} p.p.',fontsize=8,color=MUT)
fig.tight_layout(rect=(0,.03,1,1)); fig.savefig(W+'Fig1B_2c_funnel2025_ajustado.png',dpi=160); plt.close()
pts=pd.DataFrame({'Código':T.index,'N.º partos':n.astype(int).values,'Taxa CS (%)':r.map(f).values,'LI 99,8% ajustado (%)':lim_(n,3.09,tau2).map(f).values,'LS 99,8% ajustado (%)':lim(n,3.09,tau2).map(f).values,
   'Posição (ajustado)':np.where(hi,'Acima 99,8%',np.where(lo,'Abaixo 99,8%',np.where(r>lim(n,1.96,tau2),'Acima 95%',np.where(r<lim_(n,1.96,tau2),'Abaixo 95%','Dentro'))))})
P('## pts25'); P(md(pts))
seq=[300,400,500,750,1000,1500,2000,2500,3000,4000,5000]
P(md(pd.DataFrame({'N.º partos (sequência)':seq,'Taxa global (%)':f(p*100),'LI 99,8% aj. (%)':[f(lim_(k,3.09,tau2)) for k in seq],'LI 95% aj. (%)':[f(lim_(k,1.96,tau2)) for k in seq],'LS 95% aj. (%)':[f(lim(k,1.96,tau2)) for k in seq],'LS 99,8% aj. (%)':[f(lim(k,3.09,tau2)) for k in seq]})))
# period aggregated adjusted
n=P_[yrs].sum(axis=1).astype(float); c=C[yrs].sum(axis=1).astype(float); pp,phiP,tauP,_=od(n,c); r=c/n
hiP=r>pp+3.09*np.sqrt(pp*(1-pp)/n+tauP); loP=r<pp-3.09*np.sqrt(pp*(1-pp)/n+tauP)
P('## period adj phi',f(phiP,2),'tau',f(np.sqrt(tauP)*100,2),'above',list(T.index[hiP]),'below',list(T.index[loP]))
# ---------- A13 2019 sensitivity
Dx=D[~((D.cod=='A13')&(D.ano==2019))].copy(); Dx['taxa']=Dx.ces/Dx.partos*100
g=Dx[Dx.ano==2019]; t=g.taxa; q1,q3=t.quantile(.25),t.quantile(.75)
s19=dict(n=len(t),media=t.mean(),glob=g.ces.sum()/g.partos.sum()*100,mediana=t.median(),dp=t.std(ddof=0),cv=t.std(ddof=0)/t.mean()*100,mn=t.min(),mx=t.max(),amp=t.max()-t.min(),q1=q1,q3=q3,iiq=q3-q1)
cmp=pd.DataFrame({'Medida':['N.º unidades','Média simples (%)','Taxa global (%)','Mediana (%)','Desvio-padrão (p.p.)','CV (%)','Mínimo (%)','Máximo (%)','Amplitude (p.p.)','Q1 (%)','Q3 (%)','IIQ (p.p.)'],
  'Com A13 2019':[37]+[f(S.at[2019,k],2 if k=='dp' else 1) for k in ['media','glob','mediana','dp','cv','mn','mx','amp','q1','q3','iiq']],
  'Sem A13 2019':[36]+[f(s19[k],2 if k=='dp' else 1) for k in ['media','glob','mediana','dp','cv','mn','mx','amp','q1','q3','iiq']]})
cmp['Diferença']=['-1']+[f(s19[k]-S.at[2019,k],2) for k in ['media','glob','mediana','dp','cv','mn','mx','amp','q1','q3','iiq']]
P('## A13 stats 2019'); P(md(cmp))
P('max unit 2019 without A13', g.loc[t.idxmax(),'cod'], f(t.max()))
# A13 conclusions
y12=[y for y in yrs if y!=2019]
G_=S['glob'].astype(float)
a13=T.loc['A13']
P('A13 mean 13y',f(a13[yrs].mean()),'mean 12y',f(a13[y12].mean()))
P('A13 pooled with/without', f(C.loc['A13',yrs].sum()/P_.loc['A13',yrs].sum()*100), f(C.loc['A13',y12].sum()/P_.loc['A13',y12].sum()*100))
P('A13 above global years with', int((a13[yrs]>G_[yrs]).sum()),'of 13; without 2019', int((a13[y12]>G_[y12]).sum()),'of 12')
# funnel years A13
det=[]
for y in yrs:
    p=G_[y]/100; nn_=P_.at['A13',y]; se=np.sqrt(p*(1-p)/nn_); rr=a13[y]/100
    det.append((y,f(a13[y]),f(G_[y]),'acima' if rr>p+3.09*se else ('abaixo' if rr<p-3.09*se else ('acima95' if rr>p+1.96*se else ('abaixo95' if rr<p-1.96*se else 'dentro')))))
P('A13 funnel by year',det)
# rank of A13 mean among units with 12-year mean
um2=um.copy(); um2['A13']=a13[y12].mean(); P('A13 rank with', int(um.rank(ascending=False)['A13']),'without',int(um2.rank(ascending=False)['A13']))
# pooled funnel period without A13 2019: global p changes slightly; A13 position
n=P_[yrs].sum(axis=1).astype(float); c=C[yrs].sum(axis=1).astype(float)
n['A13']-=2016; c['A13']-=829; pp2=c.sum()/n.sum(); r=c/n
se=np.sqrt(pp2*(1-pp2)/n['A13']); P('A13 period pooled w/o 2019 rate',f(r['A13']*100,2),'p',f(pp2*100,2),'LS99.8',f((pp2+3.09*se)*100,2),'LS95',f((pp2+1.96*se)*100,2))
# variation 2020 vs 2018
P('A13 2020 vs 2018', f(a13[2020]-a13[2018],2), 'abs var mean excluding 2019 transitions', f(pd.Series([a13[2014]-a13[2013],a13[2015]-a13[2014],a13[2016]-a13[2015],a13[2017]-a13[2016],a13[2018]-a13[2017],a13[2020]-a13[2018]]+[a13[y]-a13[y-1] for y in range(2021,2026)]).abs().mean(),2))
P('Jan-Nov rate from user figures', f((829-386)/(2016-612)*100,2), (829-386),(2016-612))
# 2019 with/without: number of abrupt changes etc; boxplot outliers 2019 without A13
tq=t; iq=q3-q1; P('2019 outliers w/o A13', tq[(tq>q3+1.5*iq)|(tq<q1-1.5*iq)].round(1).to_dict(), 'whisk', f(tq[tq<=q3+1.5*iq].max()))
# 2019 funnel binomial without A13: global p
p=s19['glob']/100; cnt=0
P('2019 global w/o',f(p*100,2))
# change in counts of 2019 vs 2018 up/down:
P('2019 vs 2018 global change without A13', f(s19['glob']-S.at[2018,'glob'],2),'2020 vs 2019',f(S.at[2020,'glob']-s19['glob'],2))
out.close()
