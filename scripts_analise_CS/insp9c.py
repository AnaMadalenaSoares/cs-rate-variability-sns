import pandas as pd, sys
U='dados/'
for fn in ['Portugal-Popula__o-Esperan_a_de_vida_e_mortes-total.xlsx','Portugal-Popula__o-Nascimentos_e_fecundidade-total.xlsx','Portugal-Popula__o-Popula__o_residente-total.xlsx']:
    x=pd.ExcelFile(U+fn); print('#####',fn,x.sheet_names)
    d=pd.read_excel(U+fn,sheet_name='Quadro',header=None); print(d.shape)
    for r in range(0,min(25,len(d))):
        v=[(c,str(d.iat[r,c])[:40]) for c in range(d.shape[1]) if str(d.iat[r,c])!='nan']
        if v: print(r,v[:60])
