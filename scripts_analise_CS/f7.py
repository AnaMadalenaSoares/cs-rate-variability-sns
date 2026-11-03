import pickle, numpy as np, pandas as pd, matplotlib
from scipy.stats import spearmanr
matplotlib.use('Agg'); import matplotlib.pyplot as plt
W='w/'
S,S2,T,P_,R2,flag,um,COH,C2=pickle.load(open(W+'s.pkl','rb')); flag=pickle.load(open(W+'flag2.pkl','rb'))
LV,SL,OC_,PR,WV,pm=pickle.load(open(W+'s2.pkl','rb'))
cand,seat,mun_units=pickle.load(open(W+'seat.pkl','rb')); v=pickle.load(open(W+'m4.pkl','rb')); B=pickle.load(open(W+'m5mun.pkl','rb'))
yrs=list(range(2013,2025)); P1=list(range(2013,2019)); P2=list(range(2019,2025))
LP=['A03','A24','A25','A12','A30']
chg={('A06',2017),('A06',2018),('A06',2019),('A04',2019)}
lowv=['A11','A14','A22','A33','A37']
atyp={'A10':'Atípica ↑','A37':'Atípica ↑','A15':'Atípica ↓','A09':'Atípica ↓','A04':'Quase ↑','A21':'Quase ↑','A27':'Quase ↑','A11':'Quase ↑','A25':'Quase ↓'}
out=open(W+'out7.md','w')
def P(*a): print(*a,file=out)
def f(x,d=1):
    if x is None or (isinstance(x,float) and np.isnan(x)): return 'n.d.'
    x=round(float(x),d)+0.0
    return f'{x:.{d}f}'.replace('.',',')
def md(df):
    cols=[str(c) for c in df.columns]
    s='| '+' | '.join(cols)+' |\n|'+'|'.join(['---']*len(cols))+'|\n'
    for _,r in df.iterrows(): s+='| '+' | '.join(str(v) for v in r.values)+' |\n'
    return s
rho=lambda a,b: spearmanr(a,b).correlation
OCC=pd.DataFrame(np.nan,index=T.index,columns=yrs)
for u in T.index:
    for y in yrs:
        ms=[m for m in seat[(u,y)] if v.at[m,y]>0]
        if ms:
            w=np.array([B.at[m,y] for m in ms],float); OCC.at[u,y]=float(np.dot(w,[v.at[m,y] for m in ms])/w.sum())
# wide table
wt=pd.DataFrame({'Código':T.index,'Nível':[LV[c] for c in T.index]})
for y in yrs: wt[str(y)]=[f(OCC.at[c,y])+('§' if (c,y) in chg and not np.isnan(OCC.at[c,y]) else '')+('ᴸ' if c in LP and not np.isnan(OCC.at[c,y]) else '') for c in T.index]
wt['Anos com valor']=OCC.notna().sum(axis=1).values
m1=OCC[P1].where(OCC[P1].notna().sum(axis=1)>=4).mean(axis=1); m1[OCC[P1].notna().sum(axis=1)<4]=np.nan
m2=OCC[P2].mean(axis=1); m2[OCC[P2].notna().sum(axis=1)<4]=np.nan
wt['Média 2013–2018']=m1.map(f).values; wt['Média 2019–2024']=m2.map(f).values
P('## occ wide'); P(md(wt))
# descriptive per year
dd=[]
for y in yrs:
    x=OCC[y].dropna(); x2=x.drop([c for c in LP if c in x.index])
    dd.append({'Ano':y+0 if y!=2019 else '2019 ┴','N.º unidades com valor':len(x),'Das quais Lisboa/Porto':int(sum(c in LP for c in x.index)),'N.º sem Lisboa/Porto':len(x2),'Mediana (%)':f(x.median()),'Mín. (%)':f(x.min()),'Unid. mín.':x.idxmin(),'Máx. (%)':f(x.max()),'Unid. máx.':x.idxmax(),'IIQ (p.p.)':f(x.quantile(.75)-x.quantile(.25)),'Taxa de ocupação Continente (%)':''})
P('## desc'); P(md(pd.DataFrame(dd)))
# rho per year
rr=[]
for y in yrs:
    ok=OCC[y].dropna().index; ok2=[c for c in ok if c not in LP]
    okI=[c for c in ok if LV[c]=='I']; okII=[c for c in ok if LV[c]=='II']
    okn=[c for c in ok if (c,y) not in flag and (c,y) not in chg]
    rr.append({'Ano':str(y)+(' ┴' if y==2019 else ''),'n (com Lisboa/Porto)':len(ok),'rho (com Lisboa/Porto)':f(rho(OCC.loc[ok,y],T.loc[ok,y]),2),'n (sem Lisboa/Porto)':len(ok2),'rho (sem Lisboa/Porto)':f(rho(OCC.loc[ok2,y],T.loc[ok2,y]),2),
               'n nível I':len(okI),'rho nível I':f(rho(OCC.loc[okI,y],T.loc[okI,y]),2) if len(okI)>=5 else '—','n nível II':len(okII),'rho nível II':f(rho(OCC.loc[okII,y],T.loc[okII,y]),2) if len(okII)>=5 else '—',
               'n sem R2b e sem mudança de sede':len(okn),'rho sem R2b/mudança de sede':f(rho(OCC.loc[okn,y],T.loc[okn,y]),2),'rho ocupação vs partos (com L/P)':f(rho(OCC.loc[ok,y],P_.loc[ok,y]),2)})
RR=pd.DataFrame(rr); P('## rho annual'); P(md(RR))
fl=lambda s: s.str.replace(',','.').replace('—',np.nan).astype(float)
for c in [k for k in RR.columns if k.startswith('rho')]:
    vv=fl(RR[c]).dropna(); P(c,'neg',int((vv<0).sum()),'pos',int((vv>0).sum()),'of',len(vv),'min',f(vv.min(),2),'max',f(vv.max(),2),'median',f(vv.median(),2),'2013-18 median',f(fl(RR[c])[:6].median(),2),'2019-24 median',f(fl(RR[c])[6:].median(),2))
# subperiod means
r1=T[P1].mean(axis=1); r2=T[P2].mean(axis=1)
sp=[]
for lbl,mo,mr in [('2013–2018',m1,r1),('2019–2024 ┴',m2,r2)]:
    ok=mo.dropna().index; ok2=[c for c in ok if c not in LP]
    okI=[c for c in ok if LV[c]=='I']; okII=[c for c in ok if LV[c]=='II']; okIIx=[c for c in okII if c not in LP]
    sp+= [{'Subperíodo':lbl,'Conjunto':'Com Lisboa/Porto','n':len(ok),'rho':f(rho(mo[ok],mr[ok]),2)},
          {'Subperíodo':lbl,'Conjunto':'Sem Lisboa/Porto','n':len(ok2),'rho':f(rho(mo[ok2],mr[ok2]),2)},
          {'Subperíodo':lbl,'Conjunto':'Nível I','n':len(okI),'rho':f(rho(mo[okI],mr[okI]),2) if len(okI)>=5 else '—'},
          {'Subperíodo':lbl,'Conjunto':'Nível II','n':len(okII),'rho':f(rho(mo[okII],mr[okII]),2) if len(okII)>=5 else '—'},
          {'Subperíodo':lbl,'Conjunto':'Ocupação vs partos (com L/P)','n':len(ok),'rho':f(rho(mo[ok],P_.loc[ok,P1 if '2013' in lbl else P2].mean(axis=1)),2)}]
P('## rho subperiod'); P(md(pd.DataFrame(sp)))
P('levels in sample P1', {c:LV[c] for c in m1.dropna().index}); P('levels P2',{c:LV[c] for c in m2.dropna().index})
# halves by occupancy (median split) excluding LP to avoid duplication
for lbl,mo,mr in [('2013–2018',m1,r1),('2019–2024',m2,r2)]:
    ok=[c for c in mo.dropna().index if c not in LP]; med=mo[ok].median()
    lo=[c for c in ok if mo[c]<=med]; hi=[c for c in ok if mo[c]>med]
    P(lbl,'median occ',f(med),'low',lo,f(mr[lo].median()),'high',hi,f(mr[hi].median()))
# atypical present
P('atyp', {c:(f(m1.get(c)),f(m2.get(c))) for c in atyp})
# seat-change effects
for c,y in sorted(chg): P('chg',c,y,f(OCC.at[c,y-1]) if y-1 in yrs else '', f(OCC.at[c,y]))
# continent occupancy
P('cont', )
# ---- charts
cols={'I':'#2a78d6','II':'#eb6834','III':'#1baf7a','I/II':'#6250d6'}; mk={'I':'o','II':'s','III':'^','I/II':'D'}
INK,MUT='#0b0b0b','#52514e'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#bbb','xtick.color':MUT,'ytick.color':MUT,'figure.facecolor':'#fcfcfb','axes.facecolor':'#fcfcfb'})
ff=matplotlib.ticker.FuncFormatter(lambda v_,q:(f'{v_:.0f}' if abs(v_-round(v_))<1e-9 else f'{v_:.1f}').replace('.',','))
fig,axs=plt.subplots(1,2,figsize=(14,6),sharey=True)
for ax,mo,mr,lbl in [(axs[0],m1,r1,'2013–2018'),(axs[1],m2,r2,'2019–2024 (após a quebra de 2019)')]:
    ok=mo.dropna().index; ok2=[c for c in ok if c not in LP]
    for l in ['I','II','III']:
        cs=[c for c in ok if LV[c]==l]
        if cs: ax.scatter(mo[cs],mr[cs],s=55,marker=mk[l],color=cols[l],edgecolor='white',lw=.8,zorder=3,label=f'Nível {l}')
    off={'A17':(-26,-12),'A34':(5,-9)} if '2013' in lbl else {'A24':None,'A03':(-62,4),'A34':(5,4),'A12':(5,-9),'A17':(4,3)}
    for c in ok:
        o=off.get(c,(4,3))
        if o is None and '2019' in lbl: continue
        if o is None: o=(4,3)
        t=c+('ᴸ' if c in LP else '')
        if c=='A03' and '2019' in lbl: t='A03ᴸ/A24ᴸ'
        ax.annotate(t,(mo[c],mr[c]),xytext=o,textcoords='offset points',fontsize=7,color=INK)
    ax.set_title(f'{lbl}: rho = {f(rho(mo[ok],mr[ok]),2)} (n = {len(ok)}); sem Lisboa/Porto = {f(rho(mo[ok2],mr[ok2]),2)} (n = {len(ok2)})',loc='left',fontsize=9,color=INK)
    ax.set_xlabel('Taxa de ocupação dos hospitais do município sede (%, média do subperíodo)'); ax.xaxis.set_major_formatter(ff); ax.yaxis.set_major_formatter(ff)
axs[0].set_ylabel('Taxa de cesariana média do subperíodo (%)'); axs[0].legend(frameon=False,fontsize=8,loc='upper right')
fig.suptitle('Taxa de cesariana vs. taxa de ocupação hospitalar (todo o hospital, todas as especialidades; resultado indicativo)',x=.01,ha='left',fontsize=11,color=INK)
fig.text(.01,.01,'Só unidades com valor em ≥ 4 dos 6 anos. ᴸ Lisboa (A03, A24, A25) e Porto (A12, A30): valor comum do município, que não distingue as unidades. Taxa de ocupação por localização, inclui hospitais privados do município.',fontsize=7.2,color=MUT)
fig.tight_layout(rect=(0,.04,1,.95)); fig.savefig(W+'Fig7_1_dispersao_ocupacao.png',dpi=150); plt.close()
sc=pd.DataFrame({'Código':T.index,'Nível':[LV[c] for c in T.index],'Lisboa/Porto':['Sim' if c in LP else '' for c in T.index],'Ocupação média 2013–2018 (%)':m1.map(f).values,'Taxa CS média 2013–2018 (%)':[f(r1[c]) if not np.isnan(m1[c]) else 'n.d.' for c in T.index],'Ocupação média 2019–2024 (%)':m2.map(f).values,'Taxa CS média 2019–2024 (%)':[f(r2[c]) if not np.isnan(m2[c]) else 'n.d.' for c in T.index]})
sc=sc[(sc['Ocupação média 2013–2018 (%)']!='n.d.')|(sc['Ocupação média 2019–2024 (%)']!='n.d.')]
P('## scatter'); P(md(sc))
fig,ax=plt.subplots(figsize=(10.5,5))
ser=[('rho (com Lisboa/Porto)','Com Lisboa/Porto (n ≈ 20)','#0b0b0b','-'),('rho (sem Lisboa/Porto)','Sem Lisboa/Porto (n ≈ 15)','#888','--'),('rho nível II','Nível II','#eb6834','-'),('rho nível I','Nível I','#2a78d6','-')]
for c,lb,cc,ls in ser: ax.plot(yrs,fl(RR[c]),color=cc,ls=ls,marker='o',ms=4,lw=1.8,label=lb)
ax.axvline(2018.5,color=MUT,lw=1,ls=':'); ax.text(2018.6,0.85,'quebra de série (2019)',fontsize=8,color=MUT)
ax.axhline(0,color=INK,lw=.8); ax.set_ylim(-1,1); ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.2)); ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v_,q:f'{v_:.1f}'.replace('.',',')))
ax.set_xticks(yrs); ax.set_ylabel('rho de Spearman (taxa CS vs. ocupação)'); ax.legend(frameon=False,fontsize=8,loc='lower left',ncol=2)
ax.set_title('rho de Spearman entre a taxa de cesariana e a taxa de ocupação hospitalar, por ano (indicativo)',loc='left',fontsize=10.5,color=INK)
fig.text(.01,.01,'Descritivo, sem p-valor. Só unidades com valor no ano (19 a 21; 14 a 16 sem Lisboa/Porto). Nível I: n = 8–9; nível II: n = 7.',fontsize=7.5,color=MUT)
fig.tight_layout(rect=(0,.03,1,1)); fig.savefig(W+'Fig7_2_rho_ocupacao.png',dpi=160); plt.close()
pickle.dump((OCC,m1,m2),open(W+'s7.pkl','wb'))
out.close()
