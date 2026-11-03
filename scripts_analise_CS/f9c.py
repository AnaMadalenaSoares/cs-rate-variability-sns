import pickle, numpy as np, pandas as pd, matplotlib
from scipy.stats import spearmanr
matplotlib.use('Agg'); import matplotlib.pyplot as plt
W='w/'
U='dados/Regi_o-popula__o-nascimentos_e_fecundidade-total.xlsx'
RG,ARS,RS,med,medA=pickle.load(open(W+'s4.pkl','rb'))
R7=['Norte','Centro','Oeste e Vale do Tejo','Grande Lisboa','Península de Setúbal','Alentejo','Algarve']
AB={'Norte':'Norte','Centro':'Centro','Oeste e Vale do Tejo':'OVT','Grande Lisboa':'GL','Península de Setúbal':'PS','Alentejo':'Alentejo','Algarve':'Algarve','Continente':'Continente'}
Y=list(range(2013,2026))
d=pd.read_excel(U,sheet_name='Quadro',header=None)
rows=d.iloc[12:21].set_index(1)
def blk(c0):
    x=rows[list(range(c0,c0+13))].apply(pd.to_numeric,errors='coerce'); x.columns=Y; return x.loc[['Continente']+R7]
TBN=blk(2); A1=blk(15); AF=blk(28); NV=blk(41)
G={g:blk(c) for g,c in zip(['10-14','15-19','20-24','25-29','30-34','35-39','40-44','45-49','50+'],range(54,159,13))}
G['40-44'][2024]=np.nan
A1=A1.replace(0,np.nan); AF=AF.replace(0,np.nan)
SG=sum(G.values()); P35=(G['35-39']+G['40-44']+G['45-49']+G['50+'])/SG*100; P40=(G['40-44']+G['45-49']+G['50+'])/SG*100
P20=(G['10-14']+G['15-19'])/SG*100
out=open(W+'out9b.md','w')
def P(*a): print(*a,file=out)
f=lambda x,dd=1:'n.d.' if x!=x else f'{round(float(x),dd)+0.0:.{dd}f}'.replace('.',',')
def md(df):
    cols=[str(c) for c in df.columns]; s='| '+' | '.join(cols)+' |\n|'+'|'.join(['---']*len(cols))+'|\n'
    for _,r in df.iterrows(): s+='| '+' | '.join(str(v) for v in r.values)+' |\n'
    return s
P('total minus sum groups',(NV-SG).to_string())
P('sum regions vs cont NV',{y:int(NV.loc[R7,y].sum()-NV.at['Continente',y]) for y in Y})
def tab(X,dd=1,lab=None):
    t=pd.DataFrame({'Região':[AB[r] for r in X.index]})
    for y in Y: t[(lab(y) if lab else str(y))]=[f(X.at[r,y],dd) for r in X.index]
    return t
P('## TBN'); P(md(tab(TBN,lab=lambda y:('┴ ' if y in (2020,2021) else '')+str(y))))
P('## A1'); P(md(tab(A1,lab=lambda y:('┴ ' if y==2021 else '')+str(y))))
P('## AF'); P(md(tab(AF,lab=lambda y:('┴ ' if y==2021 else '')+str(y))))
P('## NV'); P(md(tab(NV,0)))
P('## P35'); P(md(tab(P35)))
P('## P40'); P(md(tab(P40)))
P('## P20'); P(md(tab(P20)))
# regional CS (Phase 4)
rs=RS[RS.tipo=='R7']; CS=rs.pivot(index='g',columns='ano',values='glob')[Y]; MD=rs.pivot(index='g',columns='ano',values='mediana')[Y]; NN=rs.pivot(index='g',columns='ano',values='n')[Y]
CSC=rs[rs.g=='Total'].set_index('ano').glob[Y]
CS=CS.loc[R7]; MD=MD.loc[R7]
P('## CS glob'); t=tab(CS); t.insert(1,'n unidades',[int(NN.at[r,2013]) for r in R7]); P(md(t))
# change summaries
chg=pd.DataFrame({'Região':[AB[r] for r in ['Continente']+R7],
 '% ≥35 2013':[f(P35.at[r,2013]) for r in ['Continente']+R7],'% ≥35 2025':[f(P35.at[r,2025]) for r in ['Continente']+R7],'Δ % ≥35 (p.p.)':[f(P35.at[r,2025]-P35.at[r,2013]) for r in ['Continente']+R7],
 'Taxa CS 2013':[f(CSC[2013] if r=='Continente' else CS.at[r,2013]) for r in ['Continente']+R7],'Taxa CS 2025':[f(CSC[2025] if r=='Continente' else CS.at[r,2025]) for r in ['Continente']+R7],
 'Δ taxa CS (p.p.)':[f((CSC[2025]-CSC[2013]) if r=='Continente' else CS.at[r,2025]-CS.at[r,2013]) for r in ['Continente']+R7],
 'Média % ≥35 2013–2025':[f(P35.loc[r,Y].mean(skipna=True)) for r in ['Continente']+R7],'Média taxa CS 2013–2025':[f(CSC[Y].mean() if r=='Continente' else CS.loc[r,Y].mean()) for r in ['Continente']+R7]})
P('## change'); P(md(chg))
# rank comparison & rho across 7 regions per year (descriptive)
rr=[]
for y in Y:
    rr.append({'Ano':y,'rho %≥35 vs CS global':f(spearmanr(P35.loc[R7,y],CS[y]).correlation,2) if y!=2024 else 'n.d.','rho %≥35 vs mediana CS':f(spearmanr(P35.loc[R7,y],MD[y]).correlation,2) if y!=2024 else 'n.d.','rho TBN vs CS global':f(spearmanr(TBN.loc[R7,y],CS[y]).correlation,2),
               'Região com maior % ≥35':AB[P35.loc[R7,y].idxmax()] if y!=2024 else 'n.d.','Região com maior CS':AB[CS[y].idxmax()]})
RR=pd.DataFrame(rr); P('## rho 7 regions'); P(md(RR))
for y in [2021,2022,2023,2024,2025]: P('age rho',y,f(spearmanr(AF.loc[R7,y],CS[y]).correlation,2),f(spearmanr(A1.loc[R7,y],CS[y]).correlation,2))
# temporal within region
Yn=[y for y in Y if y!=2024]
for r in R7: P('within',r,'rho %35 vs CS',f(spearmanr(P35.loc[r,Yn],CS.loc[r,Yn]).correlation,2))
P('within cont',f(spearmanr(P35.loc['Continente',Yn],CSC[Yn]).correlation,2))
P('ranks 2013',P35.loc[R7,2013].rank(ascending=False).to_dict(),CS[2013].rank(ascending=False).to_dict())
P('ranks 2025',P35.loc[R7,2025].rank(ascending=False).to_dict(),CS[2025].rank(ascending=False).to_dict())
pickle.dump(dict(TBN=TBN,A1=A1,AF=AF,NV=NV,P35=P35,CS=CS,CSC=CSC,MD=MD),open(W+'s9b.pkl','wb'))
# charts
INK,MUT='#0b0b0b','#52514e'
PAL={'Norte':'#2a78d6','Centro':'#1baf7a','Oeste e Vale do Tejo':'#9a6b2f','Grande Lisboa':'#eb6834','Península de Setúbal':'#6250d6','Alentejo':'#c23b5a','Algarve':'#17a3b8','Continente':'#0b0b0b'}
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#bbb','xtick.color':MUT,'ytick.color':MUT,'figure.facecolor':'#fcfcfb','axes.facecolor':'#fcfcfb'})
cf=matplotlib.ticker.FuncFormatter(lambda x,q:(f'{x:.0f}' if abs(x-round(x))<1e-9 else f'{x:.1f}').replace('.',','))
def lines(ax,X,ttl,brk=()):
    for r in ['Continente']+R7:
        ax.plot(Y,X.loc[r,Y],color=PAL[r],lw=2.4 if r=='Continente' else 1.6,ls='-' ,marker='o',ms=3,label=AB[r])
    for b in brk: ax.axvline(b-.5,color=MUT,lw=1,ls=':'); ax.text(b-.45,ax.get_ylim()[1],f'┴ {b}',fontsize=7.5,color=MUT,va='top')
    ax.set_title(ttl,loc='left',fontsize=10,color=INK); ax.set_xticks(Y); ax.tick_params(axis='x',labelsize=7.5); ax.yaxis.set_major_formatter(cf)
fig,axs=plt.subplots(1,2,figsize=(14,5))
lines(axs[0],P35,'Nados-vivos de mães com 35 ou mais anos (%)');
CSall=pd.concat([CS,CSC.to_frame('Continente').T]); lines(axs[1],CSall,'Taxa de cesariana regional (%, taxa agregada, Fase 4)')
h,l=axs[0].get_legend_handles_labels(); fig.legend(h,l,frameon=False,fontsize=8.5,ncol=8,loc='lower center',bbox_to_anchor=(.5,.045))
fig.suptitle('Idade materna avançada e taxa de cesariana por região, 2013–2025 (comparação descritiva, sem relação causal)',x=.01,ha='left',fontsize=11,color=INK)
fig.text(.01,.01,'% ≥35: 2024 n.d. (grupo 40–44 com 0 no ficheiro). Residência da mãe, todos os nados-vivos (todos os setores) [R1]. Taxa de CS: partos SNS por localização do hospital, 37 unidades [H]. Âmbitos diferentes. Algarve: 1 unidade (A23, grupo I/II indeterminado).',fontsize=7.2,color=MUT)
fig.tight_layout(rect=(0,.1,1,.94)); fig.savefig(W+'Fig9B_1_p35_cs.png',dpi=150); plt.close()
fig,axs=plt.subplots(1,3,figsize=(16,4.8))
lines(axs[0],TBN,'Taxa bruta de natalidade (‰)',brk=(2020,2021))
lines(axs[1],A1,'Idade média da mãe ao 1.º filho (anos)',brk=(2021,))
lines(axs[2],AF,'Idade média da mãe ao nascimento de um filho (anos)',brk=(2021,))
h,l=axs[0].get_legend_handles_labels(); fig.legend(h,l,frameon=False,fontsize=8.5,ncol=8,loc='lower center',bbox_to_anchor=(.5,.045))
for a in axs[1:]: a.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.5))
fig.suptitle('Natalidade e idade materna por região (NUTS II), 2013–2025',x=.01,ha='left',fontsize=11,color=INK)
fig.text(.01,.01,'Idade média: Centro, OVT, GL, PS e Alentejo só têm valores desde 2021 (0 no ficheiro = n.d.). Valores 2021–2024 revistos pelo INE (22/06/2026). Residência da mãe.',fontsize=7.2,color=MUT)
fig.tight_layout(rect=(0,.1,1,.94)); fig.savefig(W+'Fig9B_2_tbn_idade.png',dpi=150); plt.close()
fig,axs=plt.subplots(1,2,figsize=(13,5.2),sharey=True)
for ax,(lbl,ys) in zip(axs,[('2013–2018',list(range(2013,2019))),('2019–2025 (sem 2024)',[2019,2020,2021,2022,2023,2025])]):
    x=P35.loc[R7,ys].mean(axis=1,skipna=True); yv=CS.loc[R7,ys].mean(axis=1)
    for r in R7:
        ax.scatter(x[r],yv[r],s=60,color=PAL[r],zorder=3); ax.annotate(AB[r],(x[r],yv[r]),xytext=(5,4),textcoords='offset points',fontsize=8.5,color=INK)
    ax.set_title(f'{lbl}: rho = {f(spearmanr(x,yv).correlation,2)} (n = 7)',loc='left',fontsize=10,color=INK)
    ax.set_xlabel('Nados-vivos de mães com ≥35 anos (%, média do período)'); ax.xaxis.set_major_formatter(cf); ax.yaxis.set_major_formatter(cf)
axs[0].set_ylabel('Taxa de cesariana regional (%, média do período)')
fig.suptitle('Regiões: % de mães com ≥35 anos vs. taxa de cesariana (descritivo, n = 7, sem p-valor)',x=.01,ha='left',fontsize=11,color=INK)
fig.text(.01,.01,'Comparação descritiva, sem relação causal: âmbitos diferentes (residência, todos os setores vs. localização, SNS). Com 7 regiões, um ponto altera o rho.',fontsize=7.2,color=MUT)
fig.tight_layout(rect=(0,.04,1,.93)); fig.savefig(W+'Fig9B_3_dispersao.png',dpi=150); plt.close()
for lbl,ys in [('A',list(range(2013,2019))),('B',[2019,2020,2021,2022,2023,2025])]:
    P('scatter',lbl,{AB[r]:(f(P35.loc[r,ys].mean()),f(CS.loc[r,ys].mean())) for r in R7})
out.close()
