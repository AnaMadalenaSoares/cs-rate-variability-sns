import pickle, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
W='w/'
S,S2,T,P_,*_=pickle.load(open(W+'s.pkl','rb')); LV=pickle.load(open(W+'s2.pkl','rb'))[0]
Z=pickle.load(open(W+'s9a.pkl','rb')); Fi=Z['Fi']; Fii=Z['Fii']; neoi=Z['neoi']; perii=Z['perii']; res=Z['res']
f=lambda x,d=1:'n.a.' if x!=x else f'{round(float(x),d)+0.0:.{d}f}'.replace('.',',')
v=(Fi[2023]/Fi[2021]-1)*100; print('var21-23 median',f(v.median()),'pos',int((v>0).sum()),{c:f(v[c]) for c in T.index})
print('var23-24 >5%',{c:f(100*(Fi.at[c,2024]/Fi.at[c,2023]-1)) for c in T.index if abs(Fi.at[c,2024]/Fi.at[c,2023]-1)>0.05})
print('cont 21-23',f(100*(Z['femC'][2023]/Z['femC'][2021]-1)),'naoesp',f(100*(Z['naoespC'][2024]/Z['naoespC'][2013]-1)),'ped',f(100*(Z['pedC'][2024]/Z['pedC'][2013]-1)))
CV=lambda x:100*x.std(ddof=0)/x.mean()
print('fem CV 2013',f(CV(Fi[2013])),'2023',f(CV(Fi[2023])))
INK,MUT='#0b0b0b','#52514e'; C1c,C2c='#2a78d6','#eb6834'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#bbb','xtick.color':MUT,'ytick.color':MUT,'figure.facecolor':'#fcfcfb','axes.facecolor':'#fcfcfb'})
cf=matplotlib.ticker.FuncFormatter(lambda x,q:(f'{x:,.0f}'.replace(',',' ') if abs(x-round(x))<1e-9 else f'{x:.1f}').replace('.',','))
OV='O município de Ovar esteve afeto à ULS A19 entre janeiro e setembro de 2024; para efeitos de análise foi considerado na A05 em todo o período.'
A23='A23: grupo I/II (indeterminado).'
# Fig 1 continent
Y=list(range(2013,2025)); fig,axs=plt.subplots(1,2,figsize=(13,4.6))
axs[0].plot(Y,[Z['periC'][y] for y in Y],marker='o',color=C2c,lw=1.8,label='Óbitos perinatais'); axs[0].plot(Y,[Z['neoC'][y] for y in Y],marker='o',color=C1c,lw=1.8,label='Óbitos neonatais')
axs[0].set_ylim(0,400); axs[0].legend(frameon=False,fontsize=8.5); axs[0].set_title('Óbitos neonatais e perinatais (n.º), Continente',loc='left',fontsize=10,color=INK)
axs[1].plot(Y,[Z['tmiC'][y] for y in Y],marker='o',color=INK,lw=1.8); axs[1].set_ylim(0,4); axs[1].set_title('Taxa de mortalidade infantil (‰), Continente',loc='left',fontsize=10,color=INK)
for ax in axs: ax.set_xticks(Y); ax.tick_params(axis='x',labelsize=8); ax.yaxis.set_major_formatter(cf)
fig.text(.01,.01,'Fonte: [M1] (INE), por residência da mãe. Óbitos perinatais: fetos de 28 ou mais semanas e nados-vivos com menos de 7 dias.',fontsize=7.5,color=MUT)
fig.tight_layout(rect=(0,.04,1,1)); fig.savefig(W+'Fig9A_1_continente_mortalidade.png',dpi=150); plt.close()
# Fig 2 women 15-49 (i) 2013 vs 2020 vs 2023 (same boundaries)
o=Fi[2023].sort_values().index
fig,ax=plt.subplots(figsize=(10,10))
yy=np.arange(len(o))
ax.hlines(yy,Fi.loc[o,2013],Fi.loc[o,2023],color='#ccc',lw=2,zorder=1)
ax.scatter(Fi.loc[o,2013],yy,color='#888',s=28,zorder=3,label='2013'); ax.scatter(Fi.loc[o,2020],yy,color=C1c,s=28,zorder=3,label='2020'); ax.scatter(Fi.loc[o,2023],yy,color=C2c,s=28,zorder=3,label='2023 (após ┴ 2021)')
ax.set_yticks(yy); ax.set_yticklabels([c+('ᴸ' if c in ('A03','A24','A25','A12','A30') else '') for c in o],fontsize=8)
ax.set_xscale('log'); ax.xaxis.set_major_formatter(cf); ax.set_xticks([20000,50000,100000,200000]); ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
ax.set_xlabel('Mulheres residentes 15–49 anos na área da ULS, versão (i) (escala log)'); ax.legend(frameon=False,fontsize=8.5,loc='lower right')
ax.set_title('População feminina em idade fértil (15–49 anos) por ULS: 2013, 2020 e 2023',loc='left',fontsize=10.5,color=INK)
fig.text(.01,.01,'Versão (i): municípios partilhados contados em todas as ULS que servem (ᴸ: inclui Lisboa ou Porto, contados por inteiro em cada ULS que servem). 2024–2025 omitidos no gráfico: nova delimitação das ULS. ┴ 2021: quebra de série (Censos). '+A23,fontsize=7,color=MUT,wrap=True)
fig.tight_layout(rect=(0,.03,1,1)); fig.savefig(W+'Fig9A_2_mulheres_15_49.png',dpi=140); plt.close()
# Fig 3 neo & peri per 100000 women-years, two subperiods
SP=[('2013–2018',list(range(2013,2019))),('2019–2024',list(range(2019,2025)))]
fig,axs=plt.subplots(1,2,figsize=(13,9),sharey=True)
rN={l:neoi[ys].sum(axis=1) for l,ys in SP}; rP={l:perii[ys].sum(axis=1) for l,ys in SP}
o=rP['2013–2018'].sort_values().index; yy=np.arange(len(o))
for ax,R,ttl in [(axs[0],rN,'Óbitos neonatais'),(axs[1],rP,'Óbitos perinatais')]:
    ax.hlines(yy,R['2013–2018'][o],R['2019–2024'][o],color='#ccc',lw=2)
    ax.scatter(R['2013–2018'][o],yy,color=C1c,s=28,label='2013–2018',zorder=3); ax.scatter(R['2019–2024'][o],yy,color=C2c,s=28,label='2019–2024',zorder=3)
    ax.set_title(f'{ttl} (n.º, soma do subperíodo)',loc='left',fontsize=10,color=INK); ax.set_xscale('symlog',linthresh=10); ax.set_xticks([0,5,10,20,50,100,200]); ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter()); ax.xaxis.set_major_formatter(cf)
axs[0].set_yticks(yy); axs[0].set_yticklabels(o,fontsize=8); axs[0].legend(frameon=False,fontsize=8.5,loc='lower right')
fig.suptitle('Óbitos neonatais e perinatais por ULS (versão i), por subperíodo – contexto',x=.01,ha='left',fontsize=11,color=INK)
fig.text(.01,.01,'Contagens (soma dos municípios, por residência da mãe), sem taxa: números pequenos e instáveis; diferenças entre ULS refletem sobretudo a dimensão da população. Eixo X: escala log simétrica (linear até 10). Taxas padronizadas só a nível nacional (Fase 9C). '+A23+' '+OV,fontsize=7,color=MUT,wrap=True)
fig.tight_layout(rect=(0,.04,1,.96)); fig.savefig(W+'Fig9A_3_neo_peri_ULS.png',dpi=140); plt.close()
# Fig 4 staff (ii)
fig,axs=plt.subplots(1,2,figsize=(13,9),sharey=True)
Rn=res['naoesp'][3]; Rp=res['ped'][3]
R1={'n':{l:Rn[ys].mean(axis=1) for l,ys in SP},'p':{l:Rp[ys].mean(axis=1) for l,ys in SP}}
o=R1['n']['2019–2024'].dropna().sort_values().index; yy=np.arange(len(o))
for ax,k,ttl in [(axs[0],'n','Médicos não especialistas'),(axs[1],'p','Pediatras')]:
    a=R1[k]['2013–2018'][o]; b=R1[k]['2019–2024'][o]
    ax.hlines(yy,a,b,color='#ccc',lw=2); ax.scatter(a,yy,color=C1c,s=28,label='2013–2018',zorder=3); ax.scatter(b,yy,color=C2c,s=28,label='2019–2024 ┴',zorder=3)
    ax.set_title(f'{ttl} inscritos (residência) por 1000 partos',loc='left',fontsize=10,color=INK); ax.xaxis.set_major_formatter(cf)
axs[0].set_yticks(yy); axs[0].set_yticklabels(o,fontsize=8); axs[0].legend(frameon=False,fontsize=8.5,loc='lower right')
fig.suptitle('Médicos não especialistas e pediatras por ULS, versão (ii) (34 unidades) – contexto',x=.01,ha='left',fontsize=11,color=INK)
fig.text(.01,.01,'Família "residência" (Ordens). Versão (ii): sem Porto, Lisboa, Cascais e Belmonte; A16, A24 e A25: n.a. – sem municípios próprios. '+A23+' '+OV,fontsize=7,color=MUT,wrap=True)
fig.tight_layout(rect=(0,.04,1,.96)); fig.savefig(W+'Fig9A_4_naoesp_pediatras.png',dpi=140); plt.close()
for k in ['n','p']:
    for l in R1[k]: x=R1[k][l].dropna(); print(k,l,'(ii) median',f(x.median()),'CV',f(CV(x)))
print('neo cv',{l:f(CV(rN[l])) for l in rN},'peri cv',{l:f(CV(rP[l])) for l in rP})
