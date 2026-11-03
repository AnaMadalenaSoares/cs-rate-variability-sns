import pickle, numpy as np, pandas as pd
from scipy.stats import spearmanr
W='w/'
S,S2,T,P_,*_=pickle.load(open(W+'s.pkl','rb'))
LV=pickle.load(open(W+'s2.pkl','rb'))[0]; RG=pickle.load(open(W+'s4.pkl','rb'))[0]
RES10,tab10,steps10,ref10,CT10=pickle.load(open(W+'s10.pkl','rb'))
GOi,GOii,Rgi,Rgii,_,_=pickle.load(open(W+'s6.pkl','rb'))
Y=list(range(2013,2026)); lv={c:LV[c] for c in T.index}
vm=P_[Y].mean(axis=1); VC=pd.cut(vm,[0,600,1500,2500,1e9],right=False,labels=['<600','600–1499','1500–2499','≥2500']).astype(str)
def resid(keyf):
    R=pd.DataFrame(index=T.index,columns=Y,dtype=float)
    for y in Y:
        for c in T.index:
            grp=[k for k in T.index if keyf(k)==keyf(c) and k!=c]
            if len(grp)==0: grp=[k for k in T.index if lv[k]=='I']  # only A23 under 'Nível'
            R.at[c,y]=T.at[c,y]-T.loc[grp,y].median()
    return R
refs={'Ref. global':resid(lambda k:'all'),'Ref. nível':resid(lambda k:lv[k]),'Ref. volume':resid(lambda k:VC[k]),'Ref. região':resid(lambda k:RG[k]),'Ref. nível × volume':RES10}
rows=[]
for c in T.index:
    r={'Código':c,'Nível da unidade':lv[c],'Classe de volume':VC[c],'Região da unidade':RG[c]}; nA=0; dirs=[]
    for n,R in refs.items():
        u=int((R.loc[c]>=3).sum()); d=int((R.loc[c]<=-3).sum())
        lab='A↑' if u>=10 else 'A↓' if d>=10 else 'Q↑' if u>=7 else 'Q↓' if d>=7 else '—'
        r[n]=f'{lab} ({u}↑/{d}↓)'
        if lab!='—': nA+=1; dirs.append(lab[1])
    r['N.º de referências (de 5)']=nA
    sdir='↑' if dirs and all(x=='↑' for x in dirs) else '↓' if dirs and all(x=='↓' for x in dirs) else ('misto' if dirs else '')
    miss=[n.replace('Ref. ','') for n in refs if r[n].startswith('—')]
    if nA==5: r['Classificação final']='Robusta – núcleo '+sdir
    elif nA==4: r['Classificação final']='Robusta '+sdir+' (4/5; não atípica na referência: '+', '.join(miss)+')'
    else: r['Classificação final']=('Não robusta (só em '+str(nA)+' referência(s))' if nA>0 else '')
    if c=='A25': r['Classificação final']+=' – FRÁGIL. Anos ≤ −3 p.p. com 13 anos (2013–2025): global 9, nível 7, volume 4, região 7, nível × volume 7 → 4/5. Sem os anos R2b (2023–2025), em 10 anos: global 7, nível 6, volume 3, região 6, nível × volume 6 → com limiares proporcionais (atípica ≥ 8/10; quase ≥ 6/10) mantém-se robusta (4/5); com limiares absolutos (quase ≥ 7) ficaria só na referência global (1/5) e deixaria de ser robusta.'
    if c=='A36': r['Classificação final']+=' – artefacto do grupo pequeno (II × 600–1499: A10, A27, A36)'
    rows.append(r)
MX=pd.DataFrame(rows); print(MX[MX['N.º de referências (de 5)']>0].to_string())
# GO subperiods
f=lambda x:f'{x:.2f}'.replace('.',',')
for tag,R in [('i',Rgi),('ii',Rgii)]:
    for lab,ys in [('2013–2018',list(range(2013,2019))),('2019–2024',list(range(2019,2025))),('2013–2024',list(range(2013,2025)))]:
        mm=R[ys].mean(axis=1).dropna(); mr=T.loc[mm.index,ys].mean(axis=1)
        print('GO',tag,lab,len(mm),f(spearmanr(mm,mr).correlation))
pickle.dump(MX,open(W+'s11.pkl','wb'))
