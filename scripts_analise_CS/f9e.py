import pickle, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
W='w/'
U='dados/'
D=pickle.load(open(W+'d.pkl','rb'))[0]
g=D[D.ano<=2025].groupby('ano')[['partos','ces']].sum(); CSH=g.ces/g.partos*100
def q(fn,r0,r1):
    d=pd.read_excel(U+fn,sheet_name='Quadro',header=None); x=d.iloc[r0:r1].copy(); x.index=x[0].astype(int); return x.drop(columns=0).apply(pd.to_numeric,errors='coerce')
N4=q('Portugal-sa_de-recursos_humanos-total.xlsx',9,22); N6=q('Portugal-Sa_de-SNS-total.xlsx',8,19); N5=q('Portugal-Sa_de-Servi_os_e_utiliza__o-total.xlsx',9,21)
A=pd.DataFrame({'Médicos (total)':N4[1],'Não especialistas':N4[2],'GO':N4[3],'Pediatria':N4[4],'Enfermeiros':N4[6],'Médicos/100 mil hab.':N4[7],'Enfermeiros/100 mil hab.':N4[8]})
B=pd.DataFrame({'Pessoal total':N6[1],'Médicos':N6[2],'Enfermeiros':N6[3]})
B['Médicos/1000 partos SNS [H]']=B['Médicos']/g.partos.reindex(B.index)*1000; B['Enfermeiros/1000 partos SNS [H]']=B['Enfermeiros']/g.partos.reindex(B.index)*1000
C=pd.DataFrame({'Total':N5[1],'Eutócicos':N5[2],'Distócicos':N5[3],'Cesarianas':N5[4],'Outros distócicos':N5[5]})
C['% cesarianas']=C.Cesarianas/C.Total*100; C['% eutócicos']=C.Eutócicos/C.Total*100; C['% outros distócicos']=C['Outros distócicos']/C.Total*100
C['Partos [H]']=g.partos.reindex(C.index); C['Taxa CS [H] (%)']=CSH.reindex(C.index); C['Dif. partos N5−H']=C.Total-C['Partos [H]']; C['Dif. taxa H−N5 (p.p.)']=C['Taxa CS [H] (%)']-C['% cesarianas']
out=open(W+'out9d.md','w')
def P(*a): print(*a,file=out)
f=lambda x,d=1:'n.d.' if x!=x else f'{round(float(x),d)+0.0:.{d}f}'.replace('.',',')
def md(df,dd):
    t=df.copy(); t.insert(0,'Ano',df.index)
    for c,d in dd.items(): t[c]=df[c].map(lambda v:f(v,d))
    cols=[str(c) for c in t.columns]; s='| '+' | '.join(cols)+' |\n|'+'|'.join(['---']*len(cols))+'|\n'
    for _,r in t.iterrows(): s+='| '+' | '.join(str(v) for v in r.values)+' |\n'
    return s
P('check col1==col5',(N4[1]==N4[5]).all(),'nonesp+... ')
P('## A'); P(md(A,{'Médicos (total)':0,'Não especialistas':0,'GO':0,'Pediatria':0,'Enfermeiros':0,'Médicos/100 mil hab.':1,'Enfermeiros/100 mil hab.':1}))
for c in A.columns: P(c,'Δ% 2013-2025',f(100*(A.loc[2025,c]/A.loc[2013,c]-1)),'Δ% 2013-2024',f(100*(A.loc[2024,c]/A.loc[2013,c]-1)))
P('GO share of médicos',{y:f(100*A.loc[y,'GO']/A.loc[y,'Médicos (total)'],2) for y in A.index})
P('## B'); P(md(B,{'Pessoal total':0,'Médicos':0,'Enfermeiros':0,'Médicos/1000 partos SNS [H]':1,'Enfermeiros/1000 partos SNS [H]':1}))
for c in B.columns: P(c,'Δ% 13-18',f(100*(B.loc[2018,c]/B.loc[2013,c]-1)),'Δ% 19-23',f(100*(B.loc[2023,c]/B.loc[2019,c]-1)),'Δ 18-19 %',f(100*(B.loc[2019,c]/B.loc[2018,c]-1)))
P('## C'); P(md(C,{'Total':0,'Eutócicos':0,'Distócicos':0,'Cesarianas':0,'Outros distócicos':0,'% cesarianas':1,'% eutócicos':1,'% outros distócicos':1,'Partos [H]':0,'Taxa CS [H] (%)':1,'Dif. partos N5−H':0,'Dif. taxa H−N5 (p.p.)':2}))
P('check dist=ces+out',((C.Distócicos-C.Cesarianas-C['Outros distócicos']).abs().max()),'tot=eu+dist',((C.Total-C.Eutócicos-C.Distócicos).abs().max()))
pickle.dump(dict(A=A,B=B,C=C),open(W+'s9d.pkl','wb'))
INK,MUT='#0b0b0b','#52514e'; CC=['#2a78d6','#eb6834','#1baf7a','#6250d6','#c23b5a','#9a6b2f']
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#bbb','xtick.color':MUT,'ytick.color':MUT,'figure.facecolor':'#fcfcfb','axes.facecolor':'#fcfcfb'})
cf=matplotlib.ticker.FuncFormatter(lambda x,q:(f'{x:,.0f}'.replace(',',' ') if abs(x-round(x))<1e-9 else f'{x:.1f}').replace('.',','))
def fin(ax,ttl,Y):
    ax.set_title(ttl,loc='left',fontsize=10,color=INK); ax.set_xticks(Y); ax.tick_params(axis='x',labelsize=7.5); ax.yaxis.set_major_formatter(cf)
Y=list(A.index)
fig,axs=plt.subplots(1,2,figsize=(14,4.8))
for i,c in enumerate(['Médicos (total)','Não especialistas','GO','Pediatria','Enfermeiros']): axs[0].plot(Y,A[c]/A.loc[2013,c]*100,marker='o',ms=3.5,lw=1.8,color=CC[i],label=c)
axs[0].axhline(100,color=MUT,lw=.8); fin(axs[0],'Inscritos nas Ordens, índice 2013 = 100',Y); axs[0].legend(frameon=False,fontsize=8,loc='upper left')
axs[1].plot(Y,A['Médicos/100 mil hab.'],marker='o',color=CC[0],lw=1.8,label='Médicos'); axs[1].plot(Y,A['Enfermeiros/100 mil hab.'],marker='o',color=CC[4],lw=1.8,label='Enfermeiros'); axs[1].set_ylim(0,850)
for b in (2019,2020,2021): axs[1].axvline(b-.5,color=MUT,lw=.8,ls=':')
axs[1].text(2018.6,820,'┴ 2019–2021',fontsize=7.5,color=MUT); fin(axs[1],'Por 100 mil habitantes',Y); axs[1].legend(frameon=False,fontsize=8,loc='lower right')
fig.text(.01,.01,'Âmbito: Portugal [N4]; inscritos nas Ordens dos Médicos e dos Enfermeiros (inclui setor privado). ┴ por 100 mil hab.: quebras de 2019–2021 (dentistas, farmacêuticos e população), assinaladas na fonte.',fontsize=7.2,color=MUT)
fig.tight_layout(rect=(0,.04,1,1)); fig.savefig(W+'Fig9D_1_ordens.png',dpi=150); plt.close()
Yb=list(B.index)
fig,axs=plt.subplots(1,2,figsize=(14,4.8))
for i,c in enumerate(['Pessoal total','Enfermeiros','Médicos']): axs[0].plot(Yb,B[c],marker='o',ms=3.5,lw=1.8,color=CC[i],label=c)
axs[0].set_ylim(0,125000); fin(axs[0],'Pessoal ao serviço nos hospitais do SNS, Continente (n.º)',Yb); axs[0].legend(frameon=False,fontsize=8,loc='center left')
axs[1].plot(Yb,B['Enfermeiros/1000 partos SNS [H]'],marker='o',color=CC[1],lw=1.8,label='Enfermeiros'); axs[1].plot(Yb,B['Médicos/1000 partos SNS [H]'],marker='o',color=CC[2],lw=1.8,label='Médicos'); axs[1].set_ylim(0,720)
fin(axs[1],'Por 1000 partos SNS do Continente [H]',Yb); axs[1].legend(frameon=False,fontsize=8,loc='lower right')
for a in axs: a.axvline(2018.5,color=MUT,lw=1,ls=':'); a.text(2018.6,a.get_ylim()[1]*.97,'┴ 2019 (IHPARA)',fontsize=7.5,color=MUT,va='top')
fig.text(.01,.01,'Âmbito: Portugal Continental [N6] (INE, Inquérito aos Hospitais); todo o pessoal dos hospitais do SNS, não só da obstetrícia. 2024–2025 sem dados.',fontsize=7.2,color=MUT)
fig.tight_layout(rect=(0,.04,1,1)); fig.savefig(W+'Fig9D_2_SNS_pessoal.png',dpi=150); plt.close()
Yc=list(C.index)
fig,axs=plt.subplots(1,2,figsize=(14,4.8))
axs[0].bar(Yc,C['Eutócicos'],color='#bcd3ee',label='Eutócicos'); axs[0].bar(Yc,C['Outros distócicos'],bottom=C['Eutócicos'],color=CC[2],label='Distócicos – outros'); axs[0].bar(Yc,C['Cesarianas'],bottom=C['Eutócicos']+C['Outros distócicos'],color=CC[1],label='Distócicos – cesarianas')
fin(axs[0],'Partos nos hospitais públicos e PPP, por tipo (n.º)',Yc); axs[0].set_ylim(0,84000); axs[0].legend(frameon=False,fontsize=8,loc='upper left',ncol=3)
axs[1].plot(Yc,C['% cesarianas'],marker='o',color=CC[1],lw=2,label='Cesarianas – públicos e PPP, Portugal [N5]'); axs[1].plot(Yc,C['Taxa CS [H] (%)'],marker='s',color=INK,lw=1.6,ls='--',label='Taxa global de CS – 37 unidades SNS, Continente [H]')
axs[1].plot(Yc,C['% outros distócicos'],marker='o',color=CC[2],lw=1.8,label='Outros distócicos – [N5]')
axs[1].set_ylim(0,40); fin(axs[1],'Percentagem dos partos (%)',Yc); axs[1].legend(frameon=False,fontsize=8,loc='lower left')
fig.text(.01,.01,'Âmbito [N5]: Portugal (inclui hospitais públicos das regiões autónomas); 2013–2024. Só hospitais públicos e PPP; os privados não são analisados nesta fase.',fontsize=7.2,color=MUT)
fig.tight_layout(rect=(0,.04,1,1)); fig.savefig(W+'Fig9D_3_partos_publicos.png',dpi=150); plt.close()
out.close()
