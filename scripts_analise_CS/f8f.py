import pandas as pd, pickle, numpy as np
W='w/'
S,S2,T,P_,R2,flag,um,COH,C2=pickle.load(open(W+'s.pkl','rb'))
C,R,om,X=pickle.load(open(W+'s8b.pkl','rb')); B=pickle.load(open(W+'m5mun.pkl','rb'))
yrs=list(range(2013,2024))
ADD={'A01':['Fafe'],'A02':['Pombal'],'A06':['Tomar','Torres Novas'],'A07':['Torres Vedras','Peniche'],'A08':['Vila do Conde'],'A09':['Amarante'],
'A10':['Chaves','Lamego','Peso da Régua'],'A11':['Fundão'],'A19':['Águeda','Estarreja','Anadia'],'A20':['Tondela'],'A22':['Elvas'],'A32':['Montijo'],
'A33':['Seia'],'A34':['Serpa'],'A36':['Ponte de Lima'],'A37':['Mirandela','Macedo de Cavaleiros'],'L':['Oeiras'],'P':['Valongo']}
cand,seat,_=pickle.load(open(W+'seat.pkl','rb'))
LP={'A03':'L','A24':'L','A25':'L','A12':'P','A30':'P'}
CB={};RB={};USED={}
for nm in ['enf','med']:
    cb=C[nm].copy(); rb=R[nm].copy()
    for k,ms in ADD.items():
        for y in range(2013,2019):
            add=[m for m in ms if X[nm].at[m,y]>0 and m not in seat.get((k,y),[])]
            if not add: continue
            v=sum(X[nm].at[m,y] for m in add)
            USED.setdefault((k,y),set()).update(add)
            if k in ('L','P'):
                us=[u for u,l in LP.items() if l==k]; mm='Lisboa' if k=='L' else 'Porto'
                for u in us: cb.at[u,y]=X[nm].at[mm,y]+v; rb.at[u,y]=cb.at[u,y]/B.at[mm,y]*1000
            else:
                cb.at[k,y]+=v; rb.at[k,y]=cb.at[k,y]/P_.at[k,y]*1000
    for u in ['A15','A16']: cb.at[u,2019]=np.nan; rb.at[u,2019]=np.nan
    CB[nm]=cb; RB[nm]=rb
pickle.dump((CB,RB,ADD,USED),open(W+'s8f.pkl','wb'))
f=lambda x:'n.d.' if x!=x else f'{x:.0f}'
for nm in ['enf','med']:
    print('##',nm)
    for k in list(ADD)+['A12','A03']:
        u=k if k not in('L','P') else ('A03' if k=='L' else 'A12')
        print(u, 'b:',' '.join(f(RB[nm].at[u,y]) for y in range(2013,2024)),'| sede:',' '.join(f(R[nm].at[u,y]) for y in range(2013,2020)))
for k,ms in ADD.items(): print(k,{y:sorted(USED.get((k,y),[])) for y in range(2013,2019)})
