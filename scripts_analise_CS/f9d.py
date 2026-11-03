import pickle, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
W='w/'
U='dados/'
D=pickle.load(open(W+'d.pkl','rb'))[0]
Y=list(range(2013,2026))
def q(fn):
    d=pd.read_excel(U+fn,sheet_name='Quadro',header=None); x=d.iloc[8:21].copy(); x.index=x[0].astype(int); return x.drop(columns=0).apply(pd.to_numeric,errors='coerce')
N1=q('Portugal-Popula__o-Esperan_a_de_vida_e_mortes-total.xlsx'); N2=q('Portugal-Popula__o-Nascimentos_e_fecundidade-total.xlsx'); N3=q('Portugal-Popula__o-Popula__o_residente-total.xlsx')
M=pd.DataFrame({'Infantis (<1 ano)':N1[10],'Infantis ≥7 dias':N1[1],'Perinatais':N1[2],'Neonatais':N1[3],'Óbitos maternos':N1[4],'TMI (‰)':N1[5],'TMM (/100 000)':N1[6],'TM perinatal (‰)':N1[7],'TM neonatal (‰)':N1[8]})
M.loc[[2023,2024,2025],'Óbitos maternos']=np.nan; M.loc[2025,'TMM (/100 000)']=np.nan
F=pd.DataFrame({'Partos SNS (milhares)':N2[1],'Idade média 1 filho':N2[2],'Idade média 1.º filho':N2[3],'ISF':N2[4],'TBR':N2[5],'TBN (‰)':N2[6],'TFG (‰)':N2[7]})
FA=N2[[8,9,10,11,12,13,14]]; FA.columns=['15-19','20-24','25-29','30-34','35-39','40-44','45-49']
POP=N3[list(range(1,20))]; POP.columns=['Total','0-04','05-09','10-14','15-19','20-24','25-29','30-34','35-39','40-44','45-49','50-54','55-59','60-64','65-69','70-74','75-79','80-84','85+']
g=D[D.ano<=2025].groupby('ano')[['partos','ces']].sum(); CS=(g.ces/g.partos*100)
out=open(W+'out9c.md','w')
def P(*a): print(*a,file=out)
f=lambda x,d=1:'n.d.' if x!=x else f'{round(float(x),d)+0.0:.{d}f}'.replace('.',',')
def md(df):
    cols=[str(c) for c in df.columns]; s='| '+' | '.join(cols)+' |\n|'+'|'.join(['---']*len(cols))+'|\n'
    for _,r in df.iterrows(): s+='| '+' | '.join(str(v) for v in r.values)+' |\n'
    return s
def tab(X,dd):
    t=X.copy(); t.insert(0,'Ano',[('┴ ' if y==2021 else '')+str(y) for y in X.index])
    for c,d in dd.items(): t[c]=X[c].map(lambda v:f(v,d))
    return t
P('## M'); P(md(tab(M,{'Infantis (<1 ano)':0,'Infantis ≥7 dias':0,'Perinatais':0,'Neonatais':0,'Óbitos maternos':0,'TMI (‰)':1,'TMM (/100 000)':1,'TM perinatal (‰)':1,'TM neonatal (‰)':1})))
P('## F'); P(md(tab(F,{'Partos SNS (milhares)':1,'Idade média 1 filho':1,'Idade média 1.º filho':1,'ISF':2,'TBR':2,'TBN (‰)':1,'TFG (‰)':1})))
P('## FA'); P(md(tab(FA,{c:1 for c in FA.columns})))
P15=POP[['15-19','20-24','25-29','30-34','35-39','40-44','45-49']]; P15=P15.assign(**{'15-49':P15.sum(axis=1)})
P('## POP'); P(md(tab(P15.assign(Total=POP.Total),{c:0 for c in list(P15.columns)+['Total']})))
P('sum groups vs total',{y:int(POP.iloc[:,1:].sum(axis=1)[y]-POP.Total[y]) for y in Y})
P('partos SNS vs H',{y:(F.loc[y,'Partos SNS (milhares)'],round(g.partos[y]/1000,1)) for y in Y})
P('ISF check sum FA*5/1000',{y:(F.loc[y,'ISF'],round(FA.loc[y].sum()*5/1000,2)) for y in Y})
P('TBR=ISF*0.488',{y:(F.loc[y,'TBR'],round(F.loc[y,'ISF']*0.488,2)) for y in Y})
P('TMI check infant/NV? n/a')
P('## CS vs age'); t=pd.DataFrame({'Ano':[('┴ ' if y==2021 else '')+str(y) for y in Y],'Taxa CS global [H] (%)':[f(CS[y]) for y in Y],'Idade média mãe (um filho)':[f(F.loc[y,'Idade média 1 filho']) for y in Y],'Idade média mãe (1.º filho)':[f(F.loc[y,'Idade média 1.º filho']) for y in Y],'Fec. 35–39 (‰)':[f(FA.loc[y,'35-39']) for y in Y],'Fec. 40–44 (‰)':[f(FA.loc[y,'40-44']) for y in Y]}); P(md(t))
for a,b in [(2013,2016),(2016,2020),(2021,2025),(2013,2020),(2013,2025)]:
    P('Δ',a,b,'CS',f(CS[b]-CS[a]),'age',f(F.loc[b,'Idade média 1 filho']-F.loc[a,'Idade média 1 filho']),'age1',f(F.loc[b,'Idade média 1.º filho']-F.loc[a,'Idade média 1.º filho']),'f35',f(FA.loc[b,'35-39']-FA.loc[a,'35-39']),'f40',f(FA.loc[b,'40-44']-FA.loc[a,'40-44']))
for c in ['15-19','20-24','25-29','30-34','35-39','40-44','45-49','15-49']: P('pop',c,'13-20 %',f(100*(P15.loc[2020,c]/P15.loc[2013,c]-1)),'21-25 %',f(100*(P15.loc[2025,c]/P15.loc[2021,c]-1)))
for c in FA.columns: P('fa',c,'13-20',f(FA.loc[2020,c]-FA.loc[2013,c]),'21-25',f(FA.loc[2025,c]-FA.loc[2021,c]))
pickle.dump(dict(M=M,F=F,FA=FA,POP=POP,CS=CS),open(W+'s9c.pkl','wb'))
# charts
INK,MUT='#0b0b0b','#52514e'; C=['#2a78d6','#eb6834','#1baf7a','#6250d6','#c23b5a','#9a6b2f','#17a3b8']
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#bbb','xtick.color':MUT,'ytick.color':MUT,'figure.facecolor':'#fcfcfb','axes.facecolor':'#fcfcfb'})
cf=matplotlib.ticker.FuncFormatter(lambda x,q:(f'{x:.0f}' if abs(x-round(x))<1e-9 else (f'{x:.1f}' if abs(x*10-round(x*10))<1e-9 else f'{x:.2f}')).replace('.',','))
def brk(ax):
    ax.axvline(2020.5,color=MUT,lw=1,ls=':'); ax.text(2020.55,ax.get_ylim()[1],'┴ 2021',fontsize=7.5,color=MUT,va='top')
def fin(ax,ttl):
    ax.set_title(ttl,loc='left',fontsize=10,color=INK); ax.set_xticks(Y); ax.tick_params(axis='x',labelsize=7.5); ax.yaxis.set_major_formatter(cf)
fig,axs=plt.subplots(1,2,figsize=(14,4.8))
for i,c in enumerate(['Infantis (<1 ano)','Perinatais','Neonatais']): axs[0].plot(Y,M[c],marker='o',ms=3.5,lw=1.8,color=C[i],label=c)
axs[0].set_ylim(0,420); fin(axs[0],'Óbitos infantis, perinatais e neonatais (n.º)'); axs[0].legend(frameon=False,fontsize=8,loc='lower left')
for i,c in enumerate(['TMI (‰)','TM perinatal (‰)','TM neonatal (‰)']): axs[1].plot(Y,M[c],marker='o',ms=3.5,lw=1.8,color=C[i],label=c)
axs[1].set_ylim(0,5); fin(axs[1],'Taxas de mortalidade infantil, perinatal e neonatal (‰)'); axs[1].legend(frameon=False,fontsize=8,loc='lower left'); brk(axs[1])
fig.text(.01,.01,'Âmbito: Portugal (inclui regiões autónomas), residência da mãe [N1]. Perinatal por 1000 nascimentos (nados-vivos + fetos mortos ≥28 semanas); infantil e neonatal por 1000 nados-vivos. ┴ 2021: TMI (série da população).',fontsize=7.2,color=MUT)
fig.tight_layout(rect=(0,.04,1,1)); fig.savefig(W+'Fig9C_1_mortalidade.png',dpi=150); plt.close()
fig,axs=plt.subplots(1,2,figsize=(13,4.5))
axs[0].bar(Y,M['Óbitos maternos'].fillna(0),color=[C[0] if v==v else '#ddd' for v in M['Óbitos maternos']]); fin(axs[0],'Óbitos maternos (n.º)')
for y in [2023,2024,2025]: axs[0].text(y,0.3,'n.d.',ha='center',fontsize=7.5,color=MUT)
axs[1].plot(Y,M['TMM (/100 000)'],marker='o',color=C[1],lw=1.8); axs[1].set_ylim(0,25); fin(axs[1],'Taxa de mortalidade materna (por 100 000 nados-vivos)')
fig.text(.01,.01,'Âmbito: Portugal [N1]. Óbitos maternos 2023–2025 e TMM 2025: n.d. (0 no ficheiro, incoerente com a taxa; série atualizada em 22/11/2024). Contagens pequenas (5–17 por ano): grande variação anual.',fontsize=7.2,color=MUT)
fig.tight_layout(rect=(0,.05,1,1)); fig.savefig(W+'Fig9C_2_materna.png',dpi=150); plt.close()
fig,axs=plt.subplots(1,3,figsize=(17,4.8))
axs[0].plot(Y,F['ISF'],marker='o',color=C[0],lw=1.8,label='Índice sintético de fecundidade'); axs[0].plot(Y,F['TBR'],marker='o',color=C[1],lw=1.8,label='Taxa bruta de reprodução'); axs[0].set_ylim(0,1.6); fin(axs[0],'ISF e TBR (filhos/filhas por mulher)'); axs[0].legend(frameon=False,fontsize=8,loc='lower left'); brk(axs[0])
axs[1].plot(Y,F['TFG (‰)'],marker='o',color=C[2],lw=1.8,label='Taxa de fecundidade geral (‰)'); axs[1].plot(Y,F['TBN (‰)'],marker='o',color=C[3],lw=1.8,label='Taxa bruta de natalidade (‰)'); axs[1].set_ylim(0,42); fin(axs[1],'TFG e TBN (‰)'); axs[1].legend(frameon=False,fontsize=8,loc='lower left'); brk(axs[1])
for i,c in enumerate(FA.columns): axs[2].plot(Y,FA[c],marker='o',ms=3,lw=1.6,color=C[i],label=c)
fin(axs[2],'Taxa de fecundidade por grupo etário (‰)'); axs[2].legend(frameon=False,fontsize=7.5,ncol=4,loc='upper left',bbox_to_anchor=(0,-.1)); brk(axs[2])
fig.text(.01,.01,'Âmbito: Portugal [N2]. ┴ 2021: denominador (estimativas da população de base administrativa). 15–19 inclui mães de 10–19 anos; 45–49 inclui ≥45.',fontsize=7.2,color=MUT)
fig.tight_layout(rect=(0,.05,1,1)); fig.savefig(W+'Fig9C_3_fecundidade.png',dpi=150); plt.close()
fig,ax=plt.subplots(figsize=(10.5,5))
for i,c in enumerate(['15-19','20-24','25-29','30-34','35-39','40-44','45-49']): ax.plot(Y,P15[c]/1000,marker='o',ms=3,lw=1.7,color=C[i],label=c)
fin(ax,'População feminina média anual por grupo etário, 15–49 anos (milhares)'); ax.set_ylim(0,460); ax.legend(frameon=False,fontsize=8,ncol=7,loc='lower center'); brk(ax)
fig.text(.01,.01,'Âmbito: Portugal [N3]. ┴ 2021: estimativas de base administrativa; a evolução de 2020 para 2021 não é diretamente comparável.',fontsize=7.2,color=MUT)
fig.tight_layout(rect=(0,.04,1,1)); fig.savefig(W+'Fig9C_4_pop_feminina.png',dpi=150); plt.close()
fig,axs=plt.subplots(2,1,figsize=(10.5,7.5),sharex=True)
axs[0].plot(Y,CS[Y],marker='o',color=INK,lw=2); fin(axs[0],'Taxa global de cesariana, 37 unidades SNS do Continente [H] (%)'); axs[0].set_ylim(26,34)
axs[1].plot(Y,F['Idade média 1 filho'],marker='o',color=C[1],lw=2,label='Ao nascimento de um filho'); axs[1].plot(Y,F['Idade média 1.º filho'],marker='o',color=C[0],lw=2,label='Ao nascimento do 1.º filho'); axs[1].set_ylim(29,33); fin(axs[1],'Idade média da mãe, Portugal [N2] (anos)'); axs[1].legend(frameon=False,fontsize=8.5,loc='lower right'); brk(axs[1])
for a in axs: a.axvspan(2012.6,2016.4,color='#f2f2f2',zorder=0)
fig.suptitle('Evolução lado a lado: taxa global de cesariana e idade média da mãe, 2013–2025 (descritivo, sem relação causal)',x=.01,ha='left',fontsize=11,color=INK)
fig.text(.01,.01,'Âmbitos diferentes: taxa de CS = partos SNS por localização, Continente; idade média = todos os nados-vivos, residência, Portugal. Sombreado 2013–2016: idade sobe e taxa de CS desce.',fontsize=7.2,color=MUT)
fig.tight_layout(rect=(0,.03,1,.95)); fig.savefig(W+'Fig9C_5_cs_idade.png',dpi=150); plt.close()
out.close()
