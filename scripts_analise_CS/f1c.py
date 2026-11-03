import pickle, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
W='w/'
S,S2,T,P_,R2,flag,um,COH,C2=pickle.load(open(W+'s.pkl','rb')); flag=pickle.load(open(W+'flag2.pkl','rb'))
B,O,G,INK,MUT='#2a78d6','#eb6834','#1baf7a','#0b0b0b','#52514e'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#bbb','axes.labelcolor':INK,'xtick.color':MUT,'ytick.color':MUT,'figure.facecolor':'#fcfcfb','axes.facecolor':'#fcfcfb'})
fmt=lambda ax: ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,p:f'{v:.0f}'.replace('.',',')))
yrs=list(range(2013,2026)); x26=[2025,2026]
xt=[str(y) for y in yrs]+['2026\n(jan–abr)']
# chart c
fig,ax=plt.subplots(figsize=(9,5))
ax.fill_between(yrs,S.loc[yrs,'mn'].astype(float),S.loc[yrs,'mx'].astype(float),color=B,alpha=.15,lw=0,label='Mínimo–máximo')
ax.fill_between(x26,S.loc[x26,'mn'].astype(float),S.loc[x26,'mx'].astype(float),color=B,alpha=.07,lw=0)
for k,c,l in [('media',B,'Média simples'),('glob',O,'Taxa global')]:
    ax.plot(yrs,S.loc[yrs,k],color=c,lw=2,marker='o',ms=5,label=l)
    ax.plot(x26,S.loc[x26,k],color=c,lw=2,ls='--')
    ax.plot([2026],[S.at[2026,k]],marker='o',ms=6,mfc='white',mec=c,mew=2)
for k in ['mn','mx']:
    ax.plot(range(2013,2027),S[k],color=B,lw=1,alpha=.6)
ax.set_xticks(range(2013,2027)); ax.set_xticklabels(xt,fontsize=8); ax.set_ylabel('Taxa de cesariana (%)'); fmt(ax)
ax.set_ylim(15,55); ax.legend(frameon=False,loc='upper left',ncol=3)
ax.set_title('Taxa de cesariana nas 37 unidades: média, taxa global e amplitude, 2013–2026',loc='left',fontsize=11,color=INK)
fig.text(0.01,0.01,'2026: janeiro–abril (ano incompleto), linha tracejada e marcador vazio.',fontsize=8,color=MUT)
fig.tight_layout(rect=(0,0.03,1,1)); fig.savefig(W+'Fig1A_c_faixa.png',dpi=160)
# chart d
fig,axs=plt.subplots(1,2,figsize=(10,4.2))
for ax,k,c,lab in [(axs[0],'cv',B,'Coeficiente de variação (%)'),(axs[1],'iiq',O,'Intervalo interquartil (p.p.)')]:
    ax.plot(yrs,S.loc[yrs,k],color=c,lw=2,marker='o',ms=5)
    ax.plot(x26,S.loc[x26,k],color=c,lw=2,ls='--'); ax.plot([2026],[S.at[2026,k]],marker='o',ms=6,mfc='white',mec=c,mew=2)
    ax.set_xticks(range(2013,2027,2)); ax.set_xticklabels([str(y) if y<2026 else '2026*' for y in range(2013,2027,2)],fontsize=8)
    ax.set_title(lab,loc='left',fontsize=10,color=INK); ax.set_ylim(0,20 if k=='cv' else 8); ax.set_yticks(range(0,21,4) if k=='cv' else range(0,9,2)); fmt(ax)
fig.suptitle('Dispersão das taxas de cesariana entre unidades, 2013–2026',x=0.01,ha='left',fontsize=11,color=INK)
fig.text(0.01,0.01,'Tracejado e marcador vazio: 2026, janeiro–abril (ano incompleto).',fontsize=8,color=MUT)
fig.tight_layout(rect=(0,0.04,1,0.95)); fig.savefig(W+'Fig1A_d_dispersao.png',dpi=160)
# chart e
fig,axs=plt.subplots(7,6,figsize=(13,14),sharex=True,sharey=True)
codes=list(T.index)
for i,ax in enumerate(axs.flat):
    if i>=len(codes): ax.axis('off'); continue
    c=codes[i]
    ax.plot(yrs,T.loc[c,yrs],color=B,lw=1.6)
    ax.plot(x26,T.loc[c,x26],color=B,lw=1.6,ls='--'); ax.plot([2026],[T.at[c,2026]],marker='o',ms=4,mfc='white',mec=B,mew=1.5)
    fl=[y for y in yrs if (c,y) in flag]
    if fl: ax.plot(fl,T.loc[c,fl],ls='none',marker='D',ms=5,color=O)
    ax.set_title(c,fontsize=9,loc='left',color=INK,pad=2); ax.set_ylim(15,55); ax.set_yticks([20,30,40,50])
    ax.grid(axis='y',color='#e6e6e3',lw=.6); ax.set_xticks([2013,2019,2025]); ax.tick_params(labelsize=7)
fig.suptitle('Taxa de cesariana (%) por unidade, 2013–2026 (mesma escala)',x=0.01,ha='left',fontsize=12,color=INK)
fig.text(0.01,0.005,'Losango laranja: unidade-ano com interrupção/transferência de partos (R2b). Tracejado e marcador vazio: 2026, janeiro–abril.',fontsize=8,color=MUT)
fig.tight_layout(rect=(0,0.015,1,0.97)); fig.savefig(W+'Fig1A_e_paineis.png',dpi=140)
