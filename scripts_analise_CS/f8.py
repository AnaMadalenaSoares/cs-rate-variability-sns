import pickle, numpy as np, pandas as pd, matplotlib
from scipy.stats import spearmanr
matplotlib.use('Agg'); import matplotlib.pyplot as plt
W='w/'
S,S2,T,P_,R2,flag,um,COH,C2=pickle.load(open(W+'s.pkl','rb')); flag=pickle.load(open(W+'flag2.pkl','rb'))
LV,SL,OC,PR,WV,pm=pickle.load(open(W+'s2.pkl','rb'))
MAP,shared,nopart=pickle.load(open(W+'map.pkl','rb'))
RM=pickle.load(open(W+'m3me.pkl','rb'))
GOi,GOii,Rgi,Rgii,_,_=pickle.load(open(W+'s6.pkl','rb'))
yrs=list(range(2013,2025))
lowv=['A11','A14','A22','A33','A37']
atyp={'A10':'Atípica ↑','A37':'Atípica ↑','A15':'Atípica ↓','A09':'Atípica ↓','A04':'Quase ↑','A21':'Quase ↑','A27':'Quase ↑','A11':'Quase ↑','A25':'Quase ↓'}
vbins=[0,600,1500,2500,1e9]; vlabs=['< 600','600–1499','1500–2499','≥ 2500']
vm=P_[list(range(2013,2026))].mean(axis=1); VC=pd.cut(vm,vbins,right=False,labels=vlabs)
out=open(W+'out8.md','w')
def P(*a): print(*a,file=out)
def f(x,d=1):
    if x is None or (isinstance(x,float) and np.isnan(x)): return 'n.a.'
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
def agg(mun,version):
    res=pd.DataFrame(np.nan,index=T.index,columns=yrs)
    for y in yrs:
        acc={}
        for _,r in MAP.iterrows():
            if version=='ii' and r.mun in shared: continue
            for u in ulsof(r,y):
                if u in nopart: continue
                acc[u]=acc.get(u,0)+mun.at[r.mun,y]
        for u,v in acc.items(): res.at[u,y]=v
    if version=='ii': res.loc['A25']=np.nan
    return res
SUB={'med':[('2013–2018',list(range(2013,2019))),('2019–2024 ┴',list(range(2019,2025)))],
     'enf':[('2013–2016',list(range(2013,2017))),('2017–2018 ┴',[2017,2018]),('2019–2024 ┴',list(range(2019,2025))),('2019–2023 (sem 2024)',list(range(2019,2024))),('2013–2024 sem 2017 e 2024',[y for y in yrs if y not in (2017,2024)])]}
NAME={'med':'Médicos (residência)','enf':'Enfermeiros (localização)'}
RES={}
cols={'I':'#2a78d6','II':'#eb6834','III':'#1baf7a','I/II':'#6250d6'}; mk={'I':'o','II':'s','III':'^','I/II':'D'}
INK,MUT='#0b0b0b','#52514e'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#bbb','xtick.color':MUT,'ytick.color':MUT,'figure.facecolor':'#fcfcfb','axes.facecolor':'#fcfcfb'})
ff=matplotlib.ticker.FuncFormatter(lambda v,q:(f'{v:.0f}' if abs(v-round(v))<1e-9 else f'{v:.1f}').replace('.',','))
OVAR='O município de Ovar esteve afeto à ULS A19 entre janeiro e setembro de 2024; para efeitos de análise foi considerado na A05 em todo o período.'
A23N='A23: grupo I/II (indeterminado); nos rho por nível, sensibilidade com A23 em I e em II.'
for v in ['med','enf']:
    mun,cont=RM[v]
    Ci=agg(mun,'i'); Cii=agg(mun,'ii'); Ri=Ci/P_[yrs]*1000; Rii=Cii/P_[yrs]*1000
    RES[v]=(Ci,Cii,Ri,Rii)
    P(f'# ===== {v}')
    P('continent',{y:int(cont[y]) for y in yrs})
    P('sum ULS (i) (double counts shared)',{y:int(Ci[y].sum()) for y in yrs},'(ii)',{y:int(Cii[y].sum()) for y in yrs})
    ch=(Ci.pct_change(axis=1)*100)
    P('ULS (i) yoy change >20%:',{y:{c:f(ch.at[c,y]) for c in T.index if abs(ch.at[c,y])>20} for y in yrs[1:] if (ch[y].abs()>20).any()})
    # ULS table
    rows=[]
    for c in T.index:
        rows.append({'Código':c,'Nível':LV[c],'N.º 2013 (i)':f(Ci.at[c,2013],0),'N.º 2024 (i)':f(Ci.at[c,2024],0),'Por 1000 partos 2013 (i)':f(Ri.at[c,2013]),'Por 1000 partos 2024 (i)':f(Ri.at[c,2024]),
                     'Por 1000 partos, média 2013–2024 (i)':f(Ri.loc[c].mean()),'Por 1000 partos, média 2013–2024 (ii)':f(Rii.loc[c].mean()) if c not in ('A16','A24','A25') else 'n.a.','Taxa CS média 2013–2024 (%)':f(T.loc[c,yrs].mean())})
    P('## ULS'); P(md(pd.DataFrame(rows)))
    dd=[]
    for y in yrs:
        for tag,R in [('i',Ri),('ii',Rii)]:
            x=R[y].dropna(); dd.append({'Ano':y,'Versão':tag,'n':len(x),'Mediana':f(x.median()),'Mín.':f(x.min()),'Unid. mín.':x.idxmin(),'Máx.':f(x.max()),'Unid. máx.':x.idxmax(),'IIQ':f(x.quantile(.75)-x.quantile(.25)),'Continente (n.º)':int(cont[y])})
    P('## desc'); P(md(pd.DataFrame(dd)))
    rr=[]
    for y in yrs:
        d={'Ano':y}
        for tag,R,C in [('i',Ri,Ci),('ii',Rii,Cii)]:
            ok=R[y].dropna().index
            d[f'rho /1000 ({tag})']=f(rho(R.loc[ok,y],T.loc[ok,y]),2); d[f'rho abs ({tag})']=f(rho(C.loc[ok,y],T.loc[ok,y]),2)
        for l in ['I','II']:
            cs=[c for c in T.index if LV[c]==l]; d[f'rho nível {l} (i)']=f(rho(Ri.loc[cs,y],T.loc[cs,y]),2)
            cs2=cs+['A23']; d[f'rho nível {l}+A23 (i)']=f(rho(Ri.loc[cs2,y],T.loc[cs2,y]),2)
        cs=[c for c in T.index if c not in lowv]; d['rho sem baixo vol (i)']=f(rho(Ri.loc[cs,y],T.loc[cs,y]),2)
        ok=[c for c in T.index if (c,y) not in flag]; d['rho sem R2b (i)']=f(rho(Ri.loc[ok,y],T.loc[ok,y]),2)
        d['rho /1000 vs partos (i)']=f(rho(Ri[y],P_[y]),2)
        d['rho /1000 vs GO/1000 (i)']=f(rho(Ri[y],Rgi[y]),2)
        rr.append(d)
    RR=pd.DataFrame(rr); P('## rho annual'); P(md(RR))
    fl=lambda s: s.str.replace(',','.').astype(float)
    for c in RR.columns[1:]:
        x=fl(RR[c]); P(c,'neg',int((x<0).sum()),'pos',int((x>0).sum()),'min',f(x.min(),2),'max',f(x.max(),2),'median',f(x.median(),2))
    sp=[]
    for lbl,ys in SUB[v]:
        mr=T[ys].mean(axis=1)
        for tag,R,C in [('i',Ri,Ci),('ii',Rii,Cii)]:
            m_=R[ys].mean(axis=1).dropna(); ok=m_.index
            row={'Subperíodo':lbl,'Versão':tag,'n':len(ok),'rho /1000':f(rho(m_,mr[ok]),2),'rho n.º absoluto':f(rho(C.loc[ok,ys].mean(axis=1),mr[ok]),2)}
            for l in ['I','II']:
                cs=[c for c in ok if LV[c]==l]; row[f'n nível {l}']=len(cs); row[f'rho nível {l}']=f(rho(m_[cs],mr[cs]),2)
            cs=[c for c in ok if c not in lowv]; row['rho sem baixo volume']=f(rho(m_[cs],mr[cs]),2)
            cs=[c for c in ok if c not in ('A37','A10','A09','A15')]; row['rho sem as 4 atípicas']=f(rho(m_[cs],mr[cs]),2)
            sp.append(row)
    P('## rho subperiod'); P(md(pd.DataFrame(sp)))
    # terciles on main subperiod (last documented) version i
    lbl,ys=SUB[v][0]; mrA=Ri[ys].mean(axis=1);
    for lbl,ys in [SUB[v][0],SUB[v][2] if v=='enf' else SUB[v][1]]:
        m_=Ri[ys].mean(axis=1); mr=T[ys].mean(axis=1); tc=pd.qcut(m_,3,labels=['Inferior','Médio','Superior'])
        P(f'## terciles {lbl}'); P(md(pd.DataFrame([{'Tercil':t,'n':int((tc==t).sum()),'Intervalo /1000':f'{f(m_[tc==t].min())}–{f(m_[tc==t].max())}','Mediana taxa CS (%)':f(mr[tc==t].median()),'Unidades':', '.join(m_[tc==t].sort_values().index)} for t in ['Inferior','Médio','Superior']])))
        P('atyp rank (1=highest of 37)',{c:(f(m_[c]),int(m_.rank(ascending=False)[c]),str(tc[c])) for c in atyp})
    # within-unit temporal rho (excluding break-affected years for enf)
    ys=[y for y in yrs if not (v=='enf' and y in (2017,2024))]
    wu=pd.Series({c:rho(Ri.loc[c,ys],T.loc[c,ys]) for c in T.index})
    P('within-unit rho median',f(wu.median(),2),'pos',int((wu>0).sum()),'of',len(wu))
    # ---- scatter 2x2
    pans=[SUB[v][0],SUB[v][1]] if v=='med' else [SUB[v][0],SUB[v][2]]
    fig,axs=plt.subplots(2,2,figsize=(15,11),sharey='row',dpi=140)
    tabs=[]
    for j,(lbl,ys) in enumerate(pans):
        mr=T[ys].mean(axis=1)
        for i_,(tag,R) in enumerate([('i',Ri),('ii',Rii)]):
            ax=axs[i_,j]; m_=R[ys].mean(axis=1).dropna()
            for l in ['I','II','III','I/II']:
                cs=[c for c in m_.index if LV[c]==l]; ax.scatter(m_[cs],mr[cs],s=48,marker=mk[l],color=cols[l],edgecolor='white',lw=.8,zorder=3,label=f'Nível {l}' if l!='I/II' else 'I/II (A23)')
            ax.set_xscale('log')
            pts=[(c,m_[c],mr[c]) for c in m_.index]; ax.figure.canvas.draw()
            placed=[]
            for c,x_,y_ in sorted(pts,key=lambda t:-t[2]):
                px,py=ax.transData.transform((x_,y_)); best=None
                for dx,dy in [(4,3),(4,-9),(-22,3),(-22,-9),(4,10),(4,-16),(-22,10),(-22,-16)]:
                    bx,by=px+dx*1.94,py+dy*1.94
                    if all(abs(bx-qx)>36 or abs(by-qy)>15 for qx,qy in placed): best=(dx,dy); break
                best=best or (4,3); placed.append((px+best[0]*1.94,py+best[1]*1.94))
                ax.annotate(c,(x_,y_),xytext=best,textcoords='offset points',fontsize=6.6,color=INK); ax.xaxis.set_major_formatter(ff); ax.yaxis.set_major_formatter(ff)
            ax.xaxis.set_major_locator(matplotlib.ticker.LogLocator(subs=(1,2,5))); ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
            ttl=f"{lbl} – {'(i) com' if tag=='i' else '(ii) sem'} municípios partilhados: rho = {f(rho(m_,mr[m_.index]),2)} (n = {len(m_)})"
            ax.set_title(ttl,loc='left',fontsize=9.3,color=INK)
            ax.set_xlabel(f'{NAME[v]} por 1000 partos da unidade (média do subperíodo; escala log)',fontsize=9)
            if j==0: ax.set_ylabel('Taxa de cesariana média do subperíodo (%)',fontsize=9)
        tabs.append((lbl,ys))
    axs[0,0].legend(frameon=False,fontsize=8,loc='upper right')
    fig.suptitle(f'Taxa de cesariana vs. {NAME[v].lower()} por 1000 partos, por subperíodo entre quebras de série',x=.01,ha='left',fontsize=11.5,color=INK)
    note=('Médicos inscritos na Ordem, por local de residência (inclui setor privado e todas as especialidades). ' if v=='med' else 'Enfermeiros inscritos na Ordem, por localização do estabelecimento (todos os estabelecimentos; residência quando falta o local de trabalho). ')+'Em (ii), A16, A24 e A25: n.a. – sem municípios próprios (34 unidades). '+A23N+' '+OVAR
    fig.text(.01,.008,note,fontsize=7,color=MUT,wrap=True)
    fig.tight_layout(rect=(0,.04,1,.96)); fig.savefig(W+f'Fig8_{1 if v=="med" else 3}_dispersao_{v}.png',dpi=140); plt.close()
    sc=pd.DataFrame({'Código':T.index,'Nível':[LV[c] for c in T.index]})
    for lbl,ys in tabs:
        sc[f'/1000 (i) {lbl}']=Ri[ys].mean(axis=1).map(f).values; sc[f'/1000 (ii) {lbl}']=Rii[ys].mean(axis=1).map(f).values; sc[f'Taxa CS {lbl} (%)']=T[ys].mean(axis=1).map(f).values
    P('## scatter table'); P(md(sc))
    # ---- rho line
    fig,ax=plt.subplots(figsize=(10.5,5))
    ser=[('rho /1000 (i)','(i) 37 unidades','#0b0b0b','-'),('rho /1000 (ii)','(ii) 34 unidades','#888','--'),('rho nível I (i)','Nível I (i), 14',cols['I'],'-'),('rho nível II (i)','Nível II (i), 17',cols['II'],'-')]
    for c,lb,cc,ls in ser: ax.plot(yrs,fl(RR[c]),color=cc,ls=ls,marker='o',ms=4,lw=1.8,label=lb)
    brks=[2019] if v=='med' else [2017,2019]
    for b in brks: ax.axvline(b-.5,color=MUT,lw=1,ls=':'); ax.text(b-.45,.88,f'┴ {b}',fontsize=8,color=MUT)
    if v=='enf':
        for y in (2017,2024): ax.axvspan(y-.3,y+.3,color='#eee',zorder=0)
    ax.axhline(0,color=INK,lw=.8); ax.set_ylim(-1,1); ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.2)); ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x,q:f'{x:.1f}'.replace('.',',')))
    ax.set_xticks(yrs); ax.set_ylabel('rho de Spearman'); ax.legend(frameon=False,fontsize=8,loc='lower left',ncol=2)
    ax.set_title(f'rho de Spearman entre a taxa de cesariana e {NAME[v].lower()} por 1000 partos, por ano',loc='left',fontsize=10.5,color=INK)
    ft='Descritivo, sem p-valor. (i) com e (ii) sem os 4 municípios partilhados.'+(' Sombreado: 2017 e 2024, anos com redistribuição atípica entre municípios.' if v=='enf' else '')
    fig.text(.01,.01,ft,fontsize=7.5,color=MUT)
    fig.tight_layout(rect=(0,.03,1,1)); fig.savefig(W+f'Fig8_{2 if v=="med" else 4}_rho_{v}.png',dpi=150); plt.close()
pickle.dump(RES,open(W+'s8.pkl','wb'))
# cross-variable
Ri_m=RES['med'][2]; Ri_e=RES['enf'][2]
P('rho med/1000 vs enf/1000 per year',{y:f(rho(Ri_m[y],Ri_e[y]),2) for y in yrs})
out.close()
