import pandas as pd, glob
U='dados/'
fs=['Portugal-sa_de-recursos_humanos-total.xlsx','Portugal-Sa_de-SNS-total.xlsx','Portugal-Sa_de-Servi_os_e_utiliza__o-total.xlsx']
for fn in fs:
    x=pd.ExcelFile(U+fn); print('#####',fn,x.sheet_names)
    d=pd.read_excel(U+fn,sheet_name='Quadro',header=None); print(d.shape)
    for r in range(0,len(d)):
        v=[(c,str(d.iat[r,c])[:55]) for c in range(d.shape[1]) if str(d.iat[r,c]).strip() not in ('nan','')]
        if v: print(r,v[:40])
    m=pd.read_excel(U+fn,sheet_name='Metainformação',header=None)
    for i in range(len(m)):
        v=[str(x) for x in m.iloc[i] if str(x)!='nan']
        if not v: continue
        s=' | '.join(v)
        if (len(v)==1 and len(s)<140 and not s.startswith(('Conceitos','Séries','Notas','Fontes','Dados'))) or any(k in s for k in ['Âmbito geográfico','Notas:','Quebra de série','U. Medida','Unidade de Medida']) or s[:4].isdigit(): print('M',i,s[:400])
