import pickle, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
W='w/'
U='dados/'
S,S2,T,P_,R2,flag,um,COH,C2=pickle.load(open(W+'s.pkl','rb'))
LV=pickle.load(open(W+'s2.pkl','rb'))[0]; RG=pickle.load(open(W+'s4.pkl','rb'))[0]
MAP,shared,nopart=pickle.load(open(W+'map.pkl','rb'))
cand,seat,_=pickle.load(open(W+'seat.pkl','rb'))
out=open(W+'out9a.md','w')
def P(*a): print(*a,file=out)
def f(x,d=1):
    if x is None or (isinstance(x,float) and np.isnan(x)): return 'n.a.'
    return f'{round(float(x),d)+0.0:.{d}f}'.replace('.',',')
def md(df):
    cols=[str(c) for c in df.columns]; s='| '+' | '.join(cols)+' |\n|'+'|'.join(['---']*len(cols))+'|\n'
    for _,r in df.iterrows(): s+='| '+' | '.join(str(v) for v in r.values)+' |\n'
    return s
def blk(path,c0,yrs):
    d=pd.read_excel(path,sheet_name='Quadro',header=None)
    x=d.iloc[12:,[0,1]+list(range(c0,c0+len(yrs)))]; x.columns=['tipo','nome']+yrs
    mun=x[x.tipo=='Município'].set_index('nome')[yrs].apply(pd.to_numeric,errors='coerce')
    cont=x[x.nome=='Continente'].iloc[0][yrs].apply(pd.to_numeric,errors='coerce')
    return mun.loc[MAP.mun],cont
def ulsof(r,year):
    if r.x=='depois 2024': return [r.y] if year>=2024 else [r.c]
    if isinstance(r.x,str) and r.x.startswith('A'): return [r.c,r.x]+([r.y] if isinstance(r.y,str) and r.y.startswith('A') else [])
    return [r.c]
def agg(mun,version):
    yrs=list(mun.columns); res=pd.DataFrame(np.nan,index=T.index,columns=yrs)
    for y in yrs:
        acc={}
        for _,r in MAP.iterrows():
            if version=='ii' and r.mun in shared: continue
            for u in ulsof(r,y):
                if u in nopart: continue
                acc[u]=acc.get(u,0)+mun.at[r.mun,y]
        for u,v in acc.items(): res.at[u,y]=v
    if version=='ii': res.loc[['A16','A24','A25']]=np.nan
    return res
Y12=list(range(2013,2025)); Y13=list(range(2013,2026))
M1=U+'Munic_pio-Popula__o-Esperan_a_de_vida_e_mortes-total.xlsx'; M2=U+'Munic_pio-Popula__o-Popula__o_residente-total.xlsx'; M3=U+'Munic_pio-sa_de-recursos_humanos-total.xlsx'
neo,neoC=blk(M1,2,Y12); peri,periC=blk(M1,14,Y12); tmi,tmiC=blk(M1,26,Y12)
fem=None; femC=None
for c0 in range(54,145,13):
    m,c=blk(M2,c0,Y13); fem=m if fem is None else fem+m; femC=c if femC is None else femC+c
femtot,femtotC=blk(M2,2,Y13); dens,densC=blk(M2,249,Y13)
naoesp,naoespC=blk(M3,2,Y12); ped,pedC=blk(M3,26,Y13)
hosp,hospC=blk(M3,63,Y12)
P('fem sum vs cont',{y:(int(fem[y].sum()),int(femC[y])) for y in Y13})
P('dens cont',densC.to_dict()); P('neoC',neoC.to_dict()); P('periC',periC.to_dict()); P('tmiC',tmiC.to_dict())
P('naoespC',naoespC.to_dict()); P('pedC',pedC.to_dict()); P('femC',femC.to_dict()); P('femtotC',femtotC.to_dict())
P('hosp coverage %',{y:f(100*hosp[y].sum()/hospC[y]) if hospC[y]>0 else 'n.d.' for y in Y12})
# women 15-49 by ULS
Fi=agg(fem,'i'); Fii=agg(fem,'ii')
t=pd.DataFrame({'Código':T.index,'Nível':[LV[c] for c in T.index],'Região':[RG[c] for c in T.index]})
for y in [2013,2018,2020,2021,2024,2025]: t[f'(i) {y}'+(' ┴' if y==2021 else '')]=Fi[y].map(lambda v:f(v,0)).values
t['Var. 2013–2020 (%)']=(100*(Fi[2020]/Fi[2013]-1)).map(f).values; t['Var. 2021–2025 (%)']=(100*(Fi[2025]/Fi[2021]-1)).map(f).values
t['(ii) 2013']=Fii[2013].map(lambda v:f(v,0)).values; t['(ii) 2025']=Fii[2025].map(lambda v:f(v,0)).values
t['Partos/1000 mulheres 15–49 (i), média 2013–2020']=(P_[list(range(2013,2021))]/Fi[list(range(2013,2021))]*1000).mean(axis=1).map(f).values
t['Partos/1000 mulheres 15–49 (i), média 2021–2025']=(P_[list(range(2021,2026))]/Fi[list(range(2021,2026))]*1000).mean(axis=1).map(f).values
P('## fem'); P(md(t))
v=(Fi[2020]/Fi[2013]-1)*100; P('fem var13-20 median',f(v.median()),'neg',int((v<0).sum())); v=(Fi[2025]/Fi[2021]-1)*100; P('fem var21-25 median',f(v.median()),'pos',int((v>0).sum()))
P('cont fem var 13-20',f(100*(femC[2020]/femC[2013]-1)),'21-25',f(100*(femC[2025]/femC[2021]-1)))
# neonatal & perinatal
rows=[]
SP=[('2013–2018',list(range(2013,2019))),('2019–2024',list(range(2019,2025)))]
for nm,mun in [('neo',neo),('peri',peri)]:
    Ci=agg(mun,'i'); Cii=agg(mun,'ii'); globals()[nm+'i']=Ci; globals()[nm+'ii']=Cii
for c in T.index:
    r={'Código':c,'Nível':LV[c]}
    for lbl,ys in SP:
        fy=Fi.loc[c,ys].sum()
        r[f'Neonatais {lbl} (n.º)']=f(neoi.loc[c,ys].sum(),0); r[f'Perinatais {lbl} (n.º)']=f(perii.loc[c,ys].sum(),0)
        r[f'Neonatais /100 000 mulheres-ano {lbl}']=f(neoi.loc[c,ys].sum()/fy*1e5,1); r[f'Perinatais /100 000 mulheres-ano {lbl}']=f(perii.loc[c,ys].sum()/fy*1e5,1)
    rows.append(r)
NT=pd.DataFrame(rows); P('## neo/peri (i)'); P(md(NT))
for lbl,ys in SP:
    for nm,Ci in [('neo',neoi),('peri',perii)]:
        rr=Ci[ys].sum(axis=1)/Fi[ys].sum(axis=1)*1e5; P(nm,lbl,'median',f(rr.median()),'min',f(rr.min()),rr.idxmin(),'max',f(rr.max()),rr.idxmax(),'IIQ',f(rr.quantile(.75)-rr.quantile(.25)),'sum counts',int(Ci[ys].sum().sum()),
          'units with <5 events',int((Ci[ys].sum(axis=1)<5).sum()))
        rr2=(globals()[nm+'ii'][ys].sum(axis=1)/Fii[ys].sum(axis=1)*1e5).dropna(); P(' (ii)',nm,lbl,'median',f(rr2.median()),'n',len(rr2))
P('cont neo per 1e5 women',{lbl:f(neoC[ys].sum()/femC[ys].sum()*1e5) for lbl,ys in SP},'peri',{lbl:f(periC[ys].sum()/femC[ys].sum()*1e5) for lbl,ys in SP})
P('neo annual ULS zero count',{y:int((neoi[y]==0).sum()) for y in Y12})
# TMI municipal distribution
for y in [2013,2018,2024]:
    x=tmi[y]; P('tmi',y,'munis 0:',int((x==0).sum()),'p90',f(x.quantile(.9)),'max',f(x.max()),x.idxmax())
# density: municipal distribution by ULS (i)
dr=[]
for c in T.index:
    ms=[r.mun for _,r in MAP.iterrows() if c in ulsof(r,2013)]
    ms25=[r.mun for _,r in MAP.iterrows() if c in ulsof(r,2025)]
    sd=seat[(c,2023)] if (c,2023) in seat else []
    dr.append({'Código':c,'N.º municípios (2013→2025)':f'{len(ms)}→{len(ms25)}','Mediana 2013':f(dens.loc[ms,2013].median()),'Mín.–máx. 2013':f'{f(dens.loc[ms,2013].min())}–{f(dens.loc[ms,2013].max())}','Mediana 2025':f(dens.loc[ms25,2025].median()),
               'Mín.–máx. 2025':f'{f(dens.loc[ms25,2025].min())}–{f(dens.loc[ms25,2025].max())}','Sede (2023)':' + '.join(sd),'Densidade da sede 2023':' / '.join(f(dens.at[m,2023]) for m in sd)})
DR=pd.DataFrame(dr); P('## density'); P(md(DR))
# medicos nao esp & pediatras (residence, Ordens family) per 1000 births
SP2=[('2013–2018',list(range(2013,2019))),('2019–2024',list(range(2019,2025)))]
res={}
for nm,mun,yrs in [('naoesp',naoesp,Y12),('ped',ped,Y13)]:
    Ci=agg(mun,'i'); Cii=agg(mun,'ii'); Ri=Ci/P_[Ci.columns]*1000; Rii=Cii/P_[Cii.columns]*1000; res[nm]=(Ci,Cii,Ri,Rii)
rows=[]
for c in T.index:
    r={'Código':c,'Nível':LV[c]}
    for nm,lab in [('naoesp','Não esp.'),('ped','Pediatras')]:
        Ci,Cii,Ri,Rii=res[nm]
        r[f'{lab} n.º 2013 (i)']=f(Ci.at[c,2013],0); r[f'{lab} n.º 2024 (i)']=f(Ci.at[c,2024],0)
        for lbl,ys in SP2: r[f'{lab}/1000 partos {lbl} (i)']=f(Ri.loc[c,ys].mean())
        r[f'{lab}/1000 partos 2013–2024 (ii)']=f(Rii.loc[c,Y12].mean()) if c not in ('A16','A24','A25') else 'n.a.'
    rows.append(r)
ST=pd.DataFrame(rows); P('## staff'); P(md(ST))
for nm in res:
    Ci,Cii,Ri,Rii=res[nm]
    for lbl,ys in SP2:
        x=Ri.loc[:,ys].mean(axis=1); x2=Rii.loc[:,ys].mean(axis=1).dropna()
        P(nm,lbl,'(i) median',f(x.median()),'min',f(x.min()),x.idxmin(),'max',f(x.max()),x.idxmax(),'CV',f(100*x.std(ddof=0)/x.mean()),'| (ii) median',f(x2.median()),'min',f(x2.min()),x2.idxmin(),'max',f(x2.max()),x2.idxmax(),'CV',f(100*x2.std(ddof=0)/x2.mean()))
    P(nm,'ULS with 0 count (i) 2013/2024',int((Ci[2013]==0).sum()),int((Ci[2024]==0).sum()),[c for c in T.index if Ci.at[c,2013]==0])
    P(nm,'cont growth 2013-2024 %',f(100*(Ci.columns.size and (naoespC if nm=='naoesp' else pedC)[2024]/(naoespC if nm=='naoesp' else pedC)[2013]-100)))
# by level / region medians (context)
for nm in res:
    Ri=res[nm][2]; x=Ri[Y12].mean(axis=1)
    P(nm,'median by level',{l:f(x[[c for c in T.index if LV[c]==l]].median()) for l in ['I','II','III','I/II']},'by region',{g:f(x[[c for c in T.index if RG[c]==g]].median()) for g in sorted(set(RG.values()))})
x=(neoi[Y12].sum(axis=1)/Fi[Y12].sum(axis=1)*1e5); P('neo by region',{g:f(x[[c for c in T.index if RG[c]==g]].median()) for g in sorted(set(RG.values()))})
x=(perii[Y12].sum(axis=1)/Fi[Y12].sum(axis=1)*1e5); P('peri by region',{g:f(x[[c for c in T.index if RG[c]==g]].median()) for g in sorted(set(RG.values()))})
pickle.dump(dict(Fi=Fi,Fii=Fii,neoi=neoi,perii=perii,res=res,femC=femC,neoC=neoC,periC=periC,tmiC=tmiC,naoespC=naoespC,pedC=pedC,hospC=hospC,densC=densC),open(W+'s9a.pkl','wb'))
out.close()
