import pandas as pd, numpy as np, pickle, sys
U='dados/'
OUT='w/'
H=U+'Excel_1_-_hospitais.xlsx'
s=pd.read_excel(H,sheet_name='Sheet5',header=None)
years=[int(s.iat[3,c]) for c in range(1,43,3)]
rows=[]
for r in range(5,45):
    code=s.iat[r,0]
    for i,y in enumerate(years):
        c=1+3*i
        rows.append((code,y,s.iat[r,c],s.iat[r,c+1],s.iat[r,c+2]))
L=pd.DataFrame(rows,columns=['cod','ano','partos','ces','taxa_f'])
gt={y:(s.iat[45,1+3*i],s.iat[45,2+3*i],s.iat[45,3+3*i]) for i,y in enumerate(years)}
tot=s.iloc[5:45,[0,43,44,45]]; tot.columns=['cod','tp','tc','tt']
print('raw rows',len(L))
excl=L[L.cod.isin(['A38','A39','A40'])]
print('A38-40 values:',excl[['partos','ces']].stack().value_counts(dropna=False).to_dict(), 'nan count', excl.partos.isna().sum())
D=L[~L.cod.isin(['A38','A39','A40'])].copy()
print('rows',len(D),'units',D.cod.nunique(),'missing',D[['partos','ces','taxa_f']].isna().sum().sum(), 'zeros', (D.partos==0).sum())
D[['partos','ces']]=D[['partos','ces']].astype(int)
D['taxa']=D.ces/D.partos*100
print('max |taxa-Sum of Taxa|',(D.taxa-D.taxa_f.astype(float)).abs().max())
# yearly totals vs grand total
chk=D.groupby('ano')[['partos','ces']].sum()
chk['gt_p']=[gt[y][0] for y in chk.index]; chk['gt_c']=[gt[y][1] for y in chk.index]; chk['gt_t']=[gt[y][2] for y in chk.index]
chk['glob']=chk.ces/chk.partos*100
print(chk.assign(dp=chk.partos-chk.gt_p,dc=chk.ces-chk.gt_c,dt=(chk.glob-chk.gt_t).abs()))
# unit totals
ut=D[D.ano<=2026].groupby('cod')[['partos','ces']].sum().join(tot.set_index('cod'))
print('unit total diffs', (ut.partos-ut.tp).abs().max(), (ut.ces-ut.tc).abs().max(), ((ut.ces/ut.partos*100)-ut.tt.astype(float)).abs().max())
print('grand total period', s.iat[45,43], s.iat[45,44], D.partos.sum(), D.ces.sum())

# monthly sheet
m=pd.read_excel(H,sheet_name='SNS transparência')
m=m[m['Período'].notna()].copy()
for c in ['Setor','Nível','Hospital per year']: m[c]=m[c].astype(str).str.strip()
m['Ano']=m['Ano'].astype(int)
m['mes']=m['Período'].astype(str).str[5:7]
print('periods', m['Período'].min(), m['Período'].max(), 'months 2026', sorted(m[m.Ano==2026].mes.unique()))
print('setores', m.Setor.unique(), 'niveis', m['Nível'].unique())
lv=m.groupby('Hospital per year')['Nível'].unique()
print(lv.to_string())
sec=m.groupby(['Hospital per year','Ano','Setor']).mes.nunique().unstack(fill_value=0)
print(sec[(sec>0).sum(axis=1)>1])
sec_maj=sec.idxmax(axis=1)
# transitions detail months
for k in sec[(sec>0).sum(axis=1)>1].index:
    sub=m[(m['Hospital per year']==k[0])&(m.Ano==k[1])].groupby('Setor').mes.unique()
    print(k, sub.to_dict())
D['setor']=[sec_maj.get((c,y),np.nan) for c,y in zip(D.cod,D.ano)]
D['nivel_orig']=D.cod.map(lambda c: ','.join(lv[c]))
print('missing setor', D.setor.isna().sum())
# months per code-year coverage
mc=m.groupby(['Hospital per year','Ano']).mes.nunique()
print('code-years with <12 months (excl 2026):', mc[(mc<12)&(mc.index.get_level_values(1)<2026)].to_dict())
# institutions per code
print(m.groupby('Hospital per year')['Instituição'].nunique().to_dict())
pickle.dump((D,chk,sec,m[['Hospital per year','Ano','Setor','mes','Instituição']]),open(OUT+'d.pkl','wb'))
