import pandas as pd, pickle, numpy as np
W='w/'
S,S2,T,P_,R2,flag,um,COH,C2=pickle.load(open(W+'s.pkl','rb'))
cand,seat,mun_units=pickle.load(open(W+'seat.pkl','rb'))
C,R,om,X=pickle.load(open(W+'s8b.pkl','rb'))
MAP=pickle.load(open(W+'map.pkl','rb'))[0]
yrs=list(range(2013,2024))
seatmun={}
for (u,y),ms in seat.items():
    for m in ms: seatmun.setdefault((m,y),[]).append(u)
for m in ['Lisboa','Porto']:
    for y in yrs: seatmun[(m,y)]=['L/P']
o=om['enf']; o=o[~o.uls.isin(['A38','A39','A40'])]
for m in sorted(o.mun.unique()):
    for nm in ['enf','med']:
        s=X[nm].loc[m,yrs]; nz=[y for y in yrs if s[y]>0]; L=max(nz)
        line=f'{nm} {m:22s} c1={MAP.set_index("mun").at[m,"c"]} years={nz[0]}-{L} lastval={int(s[L])}'
        if L<2023:
            # which seat municipalities rose in L+1
            rises=[]
            for (sm,y),us in seatmun.items():
                if y==L+1 and X[nm].at[sm,L]>0:
                    dv=X[nm].at[sm,L+1]-X[nm].at[sm,L]
                    rises.append((dv,sm,us))
                elif y==L+1 and X[nm].at[sm,L]==0: rises.append((np.nan,sm,us))
            rises=sorted([r for r in rises if r[0]==r[0]],reverse=True)[:4]
            line+=f' | absorbed {L+1}? top seat rises: '+'; '.join(f'{sm}{us}:{int(dv):+d}' for dv,sm,us in rises)
        else: line+=' | still reporting 2023'
        print(line)
