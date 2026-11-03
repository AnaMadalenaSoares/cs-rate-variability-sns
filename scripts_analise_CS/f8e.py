import pandas as pd, pickle, numpy as np
W='w/'
C,R,om,X=pickle.load(open(W+'s8b.pkl','rb'))
cand,seat,_=pickle.load(open(W+'seat.pkl','rb'))
def sv(nm,u,y):
    if u=='L': return X[nm].at['Lisboa',y]
    if u=='P': return X[nm].at['Porto',y]
    return sum(X[nm].at[m,y] for m in seat[(u,y)])
tests=[('A02',['Pombal'],2019),('A02',['Pombal','Alcobaça'],2019),('A07',['Torres Vedras','Peniche'],2019),('A07',['Torres Vedras','Peniche','Alcobaça'],2019),
('A08',['Vila do Conde'],2019),('A09',['Amarante'],2019),('A10',['Chaves','Lamego'],2019),('A11',['Fundão'],2019),('A19',['Águeda','Estarreja'],2019),
('A20',['Tondela'],2019),('A22',['Elvas'],2019),('A32',['Montijo'],2019),('A33',['Seia'],2019),('A36',['Ponte de Lima'],2019),('A37',['Mirandela','Macedo de Cavaleiros'],2019),
('L',['Oeiras'],2019),('P',['Valongo'],2019),('A19',['Anadia'],2015),('A34',['Serpa'],2015),('A01',['Fafe'],2016),('A10',['Peso da Régua'],2016)]
rows=[]
for u,ms,y in tests:
    r={'Unidade':u,'Municípios':' + '.join(ms),'Ano abs.':y}
    for nm in ['enf','med']:
        if u=='A07' and y==2019: base=X[nm].at['Caldas da Rainha',y-1]  # seat 2018 Caldas only
        else: base=sv(nm,u,y-1)
        r[f'{nm} subida sede']=int(sv(nm,u,y)-base); r[f'{nm} valor mun. ano ant.']=int(sum(X[nm].at[m,y-1] for m in ms))
    rows.append(r)
print(pd.DataFrame(rows).to_string())
# A06 check 2017: Tomar 2017 vs Abrantes+Tomar+TN 2016
for nm in ['enf','med']:
    print(nm,'A06 2016 sum',sum(X[nm].at[m,2016] for m in ['Abrantes','Tomar','Torres Novas']),'2017 Tomar',X[nm].at['Tomar',2017],'2018 TN',X[nm].at['Torres Novas',2018],'2019 Tomar',X[nm].at['Tomar',2019])
print('seats A07',[seat[('A07',y)] for y in range(2013,2020)])
print('seats A06',[seat[('A06',y)] for y in range(2013,2020)])
for nm in ['enf','med']: print(nm,'Ovar,Cantanhede,Olhão',{m:[int(X[nm].at[m,y]) for y in range(2013,2024)] for m in ['Ovar','Cantanhede','Olhão']})
for nm in ['enf','med']: print(nm,'Braga',[int(X[nm].at['Braga',y]) for y in range(2013,2024)])
