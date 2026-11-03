import pickle, numpy as np, pandas as pd, matplotlib
from scipy.stats import spearmanr
matplotlib.use('Agg'); import matplotlib.pyplot as plt
W='w/'
S,S2,T,P_,R2,flag,um,COH,C2=pickle.load(open(W+'s.pkl','rb')); flag=pickle.load(open(W+'flag2.pkl','rb'))
LV=pickle.load(open(W+'s2.pkl','rb'))[0]
D=pickle.load(open(W+'d.pkl','rb'))[0]
cand,seat,_=pickle.load(open(W+'seat.pkl','rb')); B=pickle.load(open(W+'m5mun.pkl','rb'))
C0,R0,om,X=pickle.load(open(W+'s8b.pkl','rb'))   # só sede
RES=pickle.load(open(W+'s8.pkl','rb'))            # Ordens: (Ci,Cii,Ri,Rii)
OCC=pickle.load(open(W+'s7.pkl','rb'))[0]
yrs=list(range(2013,2024)); P1=list(range(2013,2019)); P2=list(range(2019,2024))
LPm={'A03':'Lisboa','A24':'Lisboa','A25':'Lisboa','A12':'Porto','A30':'Porto'}; LP=list(LPm)
lowv=['A11','A14','A22','A33','A37']; at4=['A10','A37','A09','A15']
atyp={'A10':'Atípica ↑','A37':'Atípica ↑','A15':'Atípica ↓','A09':'Atípica ↓','A04':'Quase ↑','A21':'Quase ↑','A27':'Quase ↑','A11':'Quase ↑','A25':'Quase ↓'}
PPP={(r.cod,r.ano) for r in D.itertuples() if r.setor=='PPP'}
ADD={'A01':['Fafe'],'A02':['Pombal','Alcobaça'],'A06':['Tomar','Torres Novas'],'A07':['Torres Vedras','Peniche'],'A08':['Vila do Conde'],'A09':['Amarante'],
'A10':['Chaves','Lamego','Peso da Régua'],'A11':['Fundão'],'A19':['Águeda','Estarreja','Anadia'],'A20':['Tondela'],'A22':['Elvas'],'A32':['Montijo'],
'A33':['Seia'],'A34':['Serpa'],'A36':['Ponte de Lima'],'A37':['Mirandela','Macedo de Cavaleiros'],'Lisboa':['Oeiras'],'Porto':['Valongo']}
partial={u for u in ADD if u.startswith('A')}
out=open(W+'out8g.md','w')
def P(*a): print(*a,file=out)
def f(x,d=1):
    if x is None or (isinstance(x,float) and np.isnan(x)): return 'n.d.'
    return f'{round(float(x),d)+0.0:.{d}f}'.replace('.',',')
def md(df):
    cols=[str(c) for c in df.columns]; s='| '+' | '.join(cols)+' |\n|'+'|'.join(['---']*len(cols))+'|\n'
    for _,r in df.iterrows(): s+='| '+' | '.join(str(v) for v in r.values)+' |\n'
    return s
def rho(a,b):
    ok=a.notna()&b.notna(); return spearmanr(a[ok],b[ok]).correlation if ok.sum()>=5 else np.nan
# ---- main measure (b)
CB={};RB={}
for nm in ['enf','med']:
    cb=pd.DataFrame(np.nan,index=T.index,columns=yrs); rb=cb.copy()
    for u in T.index:
        for y in yrs:
            if u in LPm:
                m=LPm[u]; v=X[nm].at[m,y]+(sum(X[nm].at[a,y] for a in ADD[m]) if y<=2018 else 0)
                cb.at[u,y]=v; rb.at[u,y]=v/B.at[m,y]*1000; continue
            v=sum(X[nm].at[m,y] for m in seat[(u,y)])
            if y<=2018 and u in ADD: v+=sum(X[nm].at[m,y] for m in ADD[u] if m not in seat[(u,y)])
            cb.at[u,y]=v; rb.at[u,y]=v/P_.at[u,y]*1000
    for u in ['A15','A16']: cb.at[u,2019]=rb.at[u,2019]=np.nan
    if nm=='med':
        for y in range(2015,2019): cb.at['A28',y]=rb.at['A28',y]=np.nan
    CB[nm]=cb; RB[nm]=rb
# só sede sensitivity with same n.d.
RS={}
for nm in ['enf','med']:
    r=R0[nm].copy()
    for u in ['A15','A16']: r.at[u,2019]=np.nan
    if nm=='med':
        for y in range(2015,2019): r.at['A28',y]=np.nan
    RS[nm]=r
NAME={'enf':'Enfermeiros','med':'Médicos'}
def sub(Rm,ys,minn=4):
    m=Rm[ys].mean(axis=1); m[Rm[ys].notna().sum(axis=1)<minn]=np.nan; return m
# ---- attribution tables
for nm in ['enf','med']:
    t=pd.DataFrame({'Código':T.index,'Nível':[LV[c] for c in T.index]})
    for y in yrs:
        t[str(y)+(' ┴' if y==2019 else '')]=[f(RB[nm].at[c,y],0)+('ᴸ' if c in LP else '')+('ᵃ' if (c in partial and y<=2018 and (c!='A01' or y<=2015) and (c!='A34' or y<=2014) and (c!='A06' or y<=2016)) else '')+('§' if (c,y) in {('A06',2017),('A06',2018),('A06',2019),('A04',2019)} else '')+('ᴾ' if (c,y) in PPP else '')+('†' if (c,y) in flag else '') if not np.isnan(RB[nm].at[c,y]) else 'n.d.' for c in T.index]
    t['Média 2013–2018']=sub(RB[nm],P1).map(lambda x:f(x,0)).values; t['Média 2019–2023']=sub(RB[nm],P2).map(lambda x:f(x,0)).values
    P(f'## attrib {nm}'); P(md(t))
# ---- yearly desc
dd=[]
for y in yrs:
    r={'Ano':str(y)+(' ┴' if y==2019 else '')}
    for nm in ['enf','med']:
        x=RB[nm][y].dropna(); x2=x.drop([c for c in LP if c in x.index])
        r[f'{nm} n']=len(x); r[f'{nm} mediana']=f(x.median(),0); r[f'{nm} mediana sem L/P']=f(x2.median(),0); r[f'{nm} mín (unid)']=f'{f(x2.min(),0)} ({x2.idxmin()})'; r[f'{nm} máx (unid)']=f'{f(x2.max(),0)} ({x2.idxmax()})'; r[f'{nm} IIQ sem L/P']=f(x2.quantile(.75)-x2.quantile(.25),0)
    dd.append(r)
P('## desc'); P(md(pd.DataFrame(dd)))
# ---- annual rho
RRs={}
for nm in ['enf','med']:
    rr=[]
    for y in yrs:
        R=RB[nm]; ok=R[y].dropna().index
        okx=[c for c in ok if c not in LP]; I=[c for c in ok if LV[c]=='I']; II=[c for c in ok if LV[c]=='II']
        np_=[c for c in ok if (c,y) not in PPP]; nr=[c for c in ok if (c,y) not in flag]; nl=[c for c in ok if c not in lowv]
        sd=RS[nm][y].dropna().index
        rr.append({'Ano':str(y)+(' ┴' if y==2019 else ''),'n':len(ok),'rho':f(rho(R.loc[ok,y],T.loc[ok,y]),2),'n sem L/P':len(okx),'rho sem L/P':f(rho(R.loc[okx,y],T.loc[okx,y]),2),
          'n I':len(I),'rho I':f(rho(R.loc[I,y],T.loc[I,y]),2),'rho I+A23':f(rho(R.loc[I+['A23'],y],T.loc[I+['A23'],y]),2),'n II':len(II),'rho II':f(rho(R.loc[II,y],T.loc[II,y]),2),'rho II+A23':f(rho(R.loc[II+['A23'],y],T.loc[II+['A23'],y]),2),
          'n sem PPP':len(np_),'rho sem PPP':f(rho(R.loc[np_,y],T.loc[np_,y]),2),'rho sem R2b':f(rho(R.loc[nr,y],T.loc[nr,y]),2),'rho sem baixo vol.':f(rho(R.loc[nl,y],T.loc[nl,y]),2),
          'rho só sede':f(rho(RS[nm].loc[sd,y],T.loc[sd,y]),2),'rho absoluto':f(rho(CB[nm].loc[ok,y],T.loc[ok,y]),2),'rho vs partos':f(rho(R.loc[ok,y],P_.loc[ok,y]),2)})
    RR=pd.DataFrame(rr); RRs[nm]=RR; P(f'## rho annual {nm}'); P(md(RR))
    fl=lambda s: pd.to_numeric(s.str.replace(',','.'),errors='coerce')
    for c in [k for k in RR.columns if k.startswith('rho')]:
        v=fl(RR[c]); P(c,'pos',int((v>0).sum()),'neg',int((v<0).sum()),'med13-18',f(v[:6].median(),2),'med19-23',f(v[6:].median(),2),'min',f(v.min(),2),'max',f(v.max(),2))
# ---- subperiod rho
SPt=[]
for nm in ['enf','med']:
    for lbl,ys in [('2013–2018',P1),('2019–2023 ┴',P2)]:
        R=RB[nm]; m=sub(R,ys); mr=T[ys].mean(axis=1); ok=m.dropna().index
        okx=[c for c in ok if c not in LP]; I=[c for c in ok if LV[c]=='I']; II=[c for c in ok if LV[c]=='II']
        Rn=R.copy()
        for (u,y) in PPP:
            if u in Rn.index and y in yrs: Rn.at[u,y]=np.nan
        mn=sub(Rn,ys); okn=mn.dropna().index
        ms=sub(RS[nm],ys); oks=ms.dropna().index
        SPt.append({'Variável':NAME[nm],'Subperíodo':lbl,'n':len(ok),'rho':f(rho(m[ok],mr[ok]),2),'n sem L/P':len(okx),'rho sem L/P':f(rho(m[okx],mr[okx]),2),
            'rho nível I (n)':f'{f(rho(m[I],mr[I]),2)} ({len(I)})','rho nível II (n)':f'{f(rho(m[II],mr[II]),2)} ({len(II)})',
            'rho sem PPP (n)':f'{f(rho(mn[okn],mr[okn]),2)} ({len(okn)})','rho sem baixo vol.':f(rho(m[[c for c in ok if c not in lowv]],mr[[c for c in ok if c not in lowv]]),2),
            'rho sem 4 atípicas':f(rho(m[[c for c in ok if c not in at4]],mr[[c for c in ok if c not in at4]]),2),'rho só sede':f(rho(ms[oks],mr[oks]),2),
            'rho absoluto':f(rho(sub(CB[nm],ys)[ok],mr[ok]),2)})
        tc=pd.qcut(m[okx],3,labels=['Inferior','Médio','Superior'])
        P(f'terciles {nm} {lbl} (sem L/P):'); P(md(pd.DataFrame([{'Tercil':t,'n':int((tc==t).sum()),'Intervalo':f'{f(m[okx][tc==t].min(),0)}–{f(m[okx][tc==t].max(),0)}','Mediana taxa CS':f(mr[tc[tc==t].index].median()),'Unidades':', '.join(m[tc[tc==t].index].sort_values().index)} for t in ['Inferior','Médio','Superior']])))
        rk=m[okx].rank(ascending=False)
        P('atyp',{c:(f(m.get(c),0),int(rk[c]) if c in rk else 'L/P/n.d.',str(tc[c]) if c in tc else '-') for c in atyp})
SP=pd.DataFrame(SPt); P('## subperiod'); P(md(SP))
# within-unit
for nm in ['enf','med']:
    for lbl,ys in [('P1',P1),('P2',P2)]:
        wu=pd.Series({c:rho(RB[nm].loc[c,ys],T.loc[c,ys]) for c in T.index}).dropna()
        P('within',nm,lbl,'median',f(wu.median(),2),'pos',int((wu>0).sum()),'of',len(wu))
# cross: enf vs med, vs occupancy
for lbl,ys in [('P1',P1),('P2',P2)]:
    me=sub(RB['enf'],ys); mm=sub(RB['med'],ys); mo=OCC[ys].mean(axis=1); mo[OCC[ys].notna().sum(axis=1)<4]=np.nan
    P('cross',lbl,'enf vs med',f(rho(me,mm),2),'enf vs occ',f(rho(me,mo),2),int((me.notna()&mo.notna()).sum()),'med vs occ',f(rho(mm,mo),2))
# ---- secondary (Ordens)
Ci,Cii,Ri,Rii=RES['enf']; Mi,Mii,MRi,MRii=RES['med']
Ei=Ri.copy(); Eii=Rii.copy(); Ei[[2017,2024]]=np.nan; Eii[[2017,2024]]=np.nan
sec=[]
mrA=T[list(range(2013,2025))].mean(axis=1)
for tag,R in [('i',MRi),('ii',MRii)]:
    m=R.mean(axis=1); ok=m.dropna().index
    sec.append({'Medida':'Médicos inscritos (residência)','Versão':tag,'Período':'2013–2024 (principal)','n':len(ok),'rho':f(rho(m[ok],mrA[ok]),2)})
    for lbl,ys in [('2013–2018 (verif.)',P1),('2019–2024 ┴ (verif.)',list(range(2019,2025)))]:
        mm=R[ys].mean(axis=1); ok=mm.dropna().index; sec.append({'Medida':'Médicos inscritos (residência)','Versão':tag,'Período':lbl,'n':len(ok),'rho':f(rho(mm[ok],T.loc[ok,ys].mean(axis=1)),2)})
for tag,R in [('i',Ei),('ii',Eii)]:
    for lbl,ys in [('2013–2016',list(range(2013,2017))),('2018',[2018]),('2019–2023 ┴',P2)]:
        mm=R[ys].mean(axis=1); ok=mm.dropna().index; sec.append({'Medida':'Enfermeiros inscritos (localização)','Versão':tag,'Período':lbl,'n':len(ok),'rho':f(rho(mm[ok],T.loc[ok,ys].mean(axis=1)),2)})
P('## secondary'); P(md(pd.DataFrame(sec)))
secA=[]
for y in range(2013,2025):
    r={'Ano':y}
    for lab,R in [('Méd (i)',MRi),('Méd (ii)',MRii),('Enf (i)',Ei),('Enf (ii)',Eii)]:
        ok=R[y].dropna().index; r[lab]=f(rho(R.loc[ok,y],T.loc[ok,y]),2) if len(ok) else 'n.d.'
    secA.append(r)
SECA=pd.DataFrame(secA); P('## secondary annual'); P(md(SECA))
# main vs secondary unit-level agreement
for lbl,ys in [('P1',P1),('P2',P2)]:
    P('agree',lbl,'enf SNS vs enf Ordens(i)',f(rho(sub(RB['enf'],ys),Ei[ys].mean(axis=1)),2),'med SNS vs med Ordens(i)',f(rho(sub(RB['med'],ys),MRi[ys].mean(axis=1)),2))
pickle.dump((CB,RB,RS,PPP),open(W+'s8g.pkl','wb'))
# ---- charts
cols={'I':'#2a78d6','II':'#eb6834','III':'#1baf7a','I/II':'#6250d6'}; mk={'I':'o','II':'s','III':'^','I/II':'D'}
INK,MUT='#0b0b0b','#52514e'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#bbb','xtick.color':MUT,'ytick.color':MUT,'figure.facecolor':'#fcfcfb','axes.facecolor':'#fcfcfb'})
ff=matplotlib.ticker.FuncFormatter(lambda v,q:(f'{v:.0f}' if abs(v-round(v))<1e-9 else f'{v:.1f}').replace('.',','))
fig,axs=plt.subplots(2,2,figsize=(15,11),sharey='row',dpi=140)
for i_,nm in enumerate(['enf','med']):
    for j,(lbl,ys) in enumerate([('2013–2018',P1),('2019–2023 (após a quebra de 2019)',P2)]):
        ax=axs[i_,j]; m=sub(RB[nm],ys).dropna(); mr=T[ys].mean(axis=1)
        for l in ['I','II','III','I/II']:
            cs=[c for c in m.index if LV[c]==l]; ax.scatter(m[cs],mr[cs],s=48,marker=mk[l],color=cols[l],edgecolor='white',lw=.8,zorder=3,label=f'Nível {l}' if l!='I/II' else 'I/II (A23)')
        ax.figure.canvas.draw(); placed=[]
        for c in sorted(m.index,key=lambda c:-mr[c]):
            if c in ('A24','A25','A30'): continue
            px,py=ax.transData.transform((m[c],mr[c])); best=(4,3)
            for dx,dy in [(4,3),(4,-9),(-22,3),(-22,-9),(4,10),(4,-16),(-22,10),(-22,-16)]:
                bx,by=px+dx*1.94,py+dy*1.94
                if all(abs(bx-qx)>36 or abs(by-qy)>15 for qx,qy in placed): best=(dx,dy); break
            placed.append((px+best[0]*1.94,py+best[1]*1.94))
            t=c+('ᴾ' if any((c,y) in PPP for y in ys) else '')
            if c=='A03': t='A03/A24/A25ᴸ'
            if c=='A12': t='A12/A30ᴸ'
            ax.annotate(t,(m[c],mr[c]),xytext=best,textcoords='offset points',fontsize=6.6,color=INK)
        okx=[c for c in m.index if c not in LP]
        ax.set_title(f'{NAME[nm]} – {lbl}: rho = {f(rho(m,mr[m.index]),2)} (n = {len(m)}); sem Lisboa/Porto = {f(rho(m[okx],mr[okx]),2)} (n = {len(okx)})',loc='left',fontsize=9.2,color=INK)
        ax.set_xlabel(f'{NAME[nm]} dos hospitais do SNS por 1000 partos (média do subperíodo)',fontsize=9); ax.xaxis.set_major_formatter(ff); ax.yaxis.set_major_formatter(ff)
        if j==0: ax.set_ylabel('Taxa de cesariana média do subperíodo (%)',fontsize=9)
axs[0,0].legend(frameon=False,fontsize=8,loc='upper left')
fig.suptitle('Taxa de cesariana vs. pessoal dos hospitais do SNS por 1000 partos (medida principal), por subperíodo',x=.01,ha='left',fontsize=11.5,color=INK)
fig.text(.01,.008,'Pessoal ao serviço nos hospitais do SNS (INE), todo o hospital e não só a obstetrícia; 2013–2018: sede + outros hospitais da mesma unidade (Tabela 8.C); 2019–2023: sede. ᴸ valor comum do município (Lisboa: A03, A24, A25; Porto: A12, A30), pontos sobrepostos. ᴾ unidade com anos PPP no subperíodo (pessoal possivelmente subcontado). Médicos da A28 em 2015–2018 n.d. (A28 fora de 2013–2018 em médicos). A23: grupo I/II (indeterminado).',fontsize=7,color=MUT,wrap=True)
fig.tight_layout(rect=(0,.045,1,.96)); fig.savefig(W+'Fig8_1_dispersao_SNS.png'); plt.close()
fig,axs=plt.subplots(1,2,figsize=(14,5),sharey=True)
fl=lambda s: pd.to_numeric(s.str.replace(',','.'),errors='coerce')
for ax,nm in zip(axs,['enf','med']):
    RR=RRs[nm]
    for c,lb,cc,ls in [('rho','Com Lisboa/Porto (37)','#0b0b0b','-'),('rho sem L/P','Sem Lisboa/Porto (32)','#888','--'),('rho I','Nível I (14)',cols['I'],'-'),('rho II','Nível II (17)',cols['II'],'-'),('rho sem PPP','Sem unidade-anos PPP','#6250d6',':')]:
        ax.plot(yrs,fl(RR[c]),color=cc,ls=ls,marker='o',ms=3.5,lw=1.7,label=lb)
    ax.axvline(2018.5,color=MUT,lw=1,ls=':'); ax.text(2018.6,.88,'┴ 2019',fontsize=8,color=MUT)
    ax.axhline(0,color=INK,lw=.8); ax.set_ylim(-1,1); ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.2)); ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,q:f'{v:.1f}'.replace('.',',')))
    ax.set_xticks(yrs); ax.tick_params(axis='x',labelsize=8); ax.set_title(f'{NAME[nm]} dos hospitais do SNS por 1000 partos',loc='left',fontsize=10,color=INK)
axs[0].set_ylabel('rho de Spearman (taxa CS vs. pessoal)'); axs[0].legend(frameon=False,fontsize=7.5,loc='lower left',ncol=2)
fig.suptitle('rho de Spearman entre a taxa de cesariana e o pessoal dos hospitais do SNS, por ano, 2013–2023',x=.01,ha='left',fontsize=11,color=INK)
fig.text(.01,.01,'Descritivo, sem p-valor. Médicos: n = 36 em 2015–2018 (A28 n.d.); 2019: n = 35 (A15 e A16 n.d.).',fontsize=7.5,color=MUT)
fig.tight_layout(rect=(0,.03,1,.95)); fig.savefig(W+'Fig8_2_rho_SNS.png',dpi=150); plt.close()
fig,ax=plt.subplots(figsize=(10.5,4.8))
for c,lb,cc,ls in [('Méd (i)','Médicos inscritos (i)','#0b0b0b','-'),('Méd (ii)','Médicos inscritos (ii)','#888','--'),('Enf (i)','Enfermeiros inscritos (i)','#1baf7a','-'),('Enf (ii)','Enfermeiros inscritos (ii)','#1baf7a','--')]:
    ax.plot(list(range(2013,2025)),fl(SECA[c]),color=cc,ls=ls,marker='o',ms=3.5,lw=1.7,label=lb)
ax.axvline(2018.5,color=MUT,lw=1,ls=':'); ax.axvline(2016.5,color=MUT,lw=1,ls=':'); ax.text(2016.55,.88,'┴ 2017 (enf.)',fontsize=8,color=MUT); ax.text(2018.6,.75,'┴ 2019',fontsize=8,color=MUT)
ax.axhline(0,color=INK,lw=.8); ax.set_ylim(-1,1); ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.2)); ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,q:f'{v:.1f}'.replace('.',',')))
ax.set_xticks(list(range(2013,2025))); ax.set_ylabel('rho de Spearman'); ax.legend(frameon=False,fontsize=8,loc='lower right',ncol=2)
ax.set_title('Medida secundária (Ordens): rho entre a taxa de cesariana e os inscritos por 1000 partos, por ano',loc='left',fontsize=10.5,color=INK)
fig.text(.01,.01,'Enfermeiros: 2017 e 2024 n.d. (distribuição municipal não credível). (i) com e (ii) sem os 4 municípios partilhados. O município de Ovar esteve afeto à ULS A19 entre janeiro e setembro de 2024; para efeitos de análise foi considerado na A05 em todo o período.',fontsize=7,color=MUT,wrap=True)
fig.tight_layout(rect=(0,.05,1,1)); fig.savefig(W+'Fig8_3_rho_Ordens.png',dpi=150); plt.close()
out.close()
