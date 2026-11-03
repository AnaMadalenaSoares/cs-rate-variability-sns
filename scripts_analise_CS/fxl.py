import pickle, re, numpy as np, pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
W='w/'
OUT='Resultados finais - análise CS.xlsx'
S,S2,T,P_,R2,flag,um,COH,C2=pickle.load(open(W+'s.pkl','rb')); flag=pickle.load(open(W+'flag2.pkl','rb'))
D,chk,sec,m=pickle.load(open(W+'d.pkl','rb'))
LV=pickle.load(open(W+'s2.pkl','rb'))[0]; RG,ARS,RS,med,medA=pickle.load(open(W+'s4.pkl','rb'))
GOi,GOii,Rgi,Rgii,_,_=pickle.load(open(W+'s6.pkl','rb'))
OCC,m1,m2=pickle.load(open(W+'s7.pkl','rb'))
CB,RB,RSd,PPP=pickle.load(open(W+'s8g.pkl','rb'))
RES8=pickle.load(open(W+'s8.pkl','rb'))
Z9=pickle.load(open(W+'s9a.pkl','rb'))
RES10,tab10,steps10,ref10,CT10=pickle.load(open(W+'s10.pkl','rb'))
cand,seat,_=pickle.load(open(W+'seat.pkl','rb'))
vm=P_[list(range(2013,2026))].mean(axis=1); VC=pd.cut(vm,[0,600,1500,2500,1e9],right=False,labels=['< 600','600–1499','1500–2499','≥ 2500']).astype(str)
LP=['A03','A24','A25','A12','A30']
F=Font(name='Arial',size=10); FB=Font(name='Arial',size=10,bold=True); FH=Font(name='Arial',size=12,bold=True); FG=Font(name='Arial',size=9,italic=True,color='555555')
HF=PatternFill('solid',fgColor='DCE6F1')
wb=Workbook(); ws0=wb.active; ws0.title='Leia-me'
def num(s):
    if not isinstance(s,str): return s
    t=s.strip()
    if re.fullmatch(r'-?\d+(,\d+)?',t): return float(t.replace(',','.')) if ',' in t else int(t)
    if re.fullmatch(r'-?\d+\.\d+',t): return float(t)
    return t
def fmt(c,v):
    if isinstance(v,float): c.number_format='0.0###'
    elif isinstance(v,int): c.number_format='0'
def put_table(ws,r,title,df,note=None):
    ws.cell(r,1,title).font=FH; r+=1
    if note: ws.cell(r,1,note).font=FG; r+=1
    for j,col in enumerate(df.columns,1):
        c=ws.cell(r,j,str(col)); c.font=FB; c.fill=HF; c.alignment=Alignment(wrap_text=True,vertical='top')
    r+=1
    for row in df.itertuples(index=False):
        for j,v in enumerate(row,1):
            v=num(v) if isinstance(v,str) else (None if (isinstance(v,float) and np.isnan(v)) else v)
            if isinstance(v,(np.integer,)): v=int(v)
            if isinstance(v,(np.floating,)): v=float(v)
            c=ws.cell(r,j,v); c.font=F; fmt(c,v)
        r+=1
    return r+1
def md_to_sheet(ws,path,r,skip_titles=()):
    lines=open(path,encoding='utf-8').read().split('\n'); i=0; title=None
    while i<len(lines):
        L=lines[i]
        if L.startswith('|'):
            block=[]
            while i<len(lines) and lines[i].startswith('|'): block.append(lines[i]); i+=1
            rows=[[x.strip() for x in b.strip().strip('|').split('|')] for b in block if not re.fullmatch(r'\|[-|\s:]+\|',b.strip())]
            if title in skip_titles: title=None; continue
            hdr=rows[0]; data=rows[1:]
            df=pd.DataFrame(data,columns=hdr[:len(data[0])] if data else hdr)
            r=put_table(ws,r,title or 'Tabela',df); title=None; continue
        if L.startswith('#'): title=L.lstrip('#').strip()
        elif L.strip() and not re.match(r'^\s*(\(ii\) )?(neo|peri) |^cont neo per|^neo by region|^peri by region',L):
            if title: ws.cell(r,1,title).font=FB; r+=1; title=None
            ws.cell(r,1,L[:32000]).font=FG; r+=1
        i+=1
    return r
def widths(ws,w=14):
    for j in range(1,40): ws.column_dimensions[get_column_letter(j)].width=w
    ws.column_dimensions['A'].width=18
# ---------- Leia-me
info=[('Resultados finais – análise da variabilidade da taxa de cesariana (CS) nas unidades do SNS, 2013–2025/26',FH),
('Conteúdo: uma folha por fase (tabelas de resultados e tabelas de dados dos gráficos), a base harmonizada unidade-ano, os excluídos e o registo de decisões (R18).',F),
('Convenções: valores numéricos guardados como números (a vírgula decimal depende das definições regionais do Excel); sem "%" nas células (R12); "n.d." = sem dados; "n.a." = não aplicável; marcas de texto mantidas nas células com símbolos.',F),
('Marcas: † unidade-ano R2b; ◊ A13 2019 (valor atípico, possível problema de registo); ‡ ano de transição de setor; * < 300 partos; ┴ quebra de série; ᴸ valor comum Lisboa/Porto; § mudança de município sede; ᵃ sede + outros hospitais da unidade (Fase 8); ᴾ unidade-ano PPP.',F),
('Fontes: [H] Excel 1 – hospitais (Sheet5; folha mensal só para setor e nível); [C1]–[C3] correspondências; PORDATA (folha "Quadro"): [M1]–[M5], [R1], [N1]–[N6].',F),
('Nota A23 (PT): A unidade A23 não tem nível hospitalar inequívoco (I ou II) na Rede de Referenciação; foi analisada como grupo à parte, com verificação de sensibilidade nos dois níveis.',F),
('Note A23 (EN): Unit A23 has no unambiguous hospital level (I or II) in the Referral Network; it was analysed as a separate group, with a sensitivity check under both levels.',F),
('Nota Ovar (PT): O município de Ovar esteve afeto à ULS A19 entre janeiro e setembro de 2024; para efeitos de análise foi considerado na A05 em todo o período.',F),
('Note Ovar (EN): The municipality of Ovar was assigned to ULS A19 between January and September 2024; for analytical purposes it was assigned to A05 throughout the study period.',F),
('As folhas de fase reproduzem as saídas de cálculo de cada fase (tabelas e linhas de verificação em itálico cinzento). Fase 8: medida principal = pessoal dos hospitais do SNS (versão final); a medida secundária (Ordens) está na mesma folha. Fase 9A: óbitos por ULS apenas em contagens (versão final).',F),
('Folhas: '+'; '.join(['Base unidade-ano','F1A','F1B','F2 Nível','F3 Setor','F4 Região','F5 Volume','F6 GO','F7 Ocupação','F8 Pessoal','F9A Contexto mun','F9B Contexto reg','F9C Nacional pop','F9D Nacional saúde','Síntese','Excluídos','Registo de decisões']),F)]
for i,(t,fn) in enumerate(info,1):
    c=ws0.cell(i,1,t); c.font=fn; c.alignment=Alignment(wrap_text=True,vertical='top')
ws0.column_dimensions['A'].width=150
# ---------- Base unidade-ano
ws=wb.create_sheet('Base unidade-ano')
cols=['Código','Ano','Partos','Cesarianas','Taxa CS (%)','Nível','Setor','Região (7)','ARS','Classe de volume','R2b (†)','< 300 partos (*)','A13 2019 (◊)','Lisboa/Porto (ᴸ)',
 'Município(s) sede (Tabela 6)','Taxa de ocupação sede (%)','Enfermeiros SNS /1000 partos (principal)','Médicos SNS /1000 partos (principal)','Enfermeiros SNS /1000 partos (só sede)','Médicos SNS /1000 partos (só sede)',
 'Médicos GO /1000 partos (i)','Médicos GO /1000 partos (ii)','Médicos inscritos /1000 partos (i)','Enfermeiros inscritos /1000 partos (i)','Mulheres 15–49 (i)','Óbitos neonatais (i)','Óbitos perinatais (i)',
 'Médicos não esp. /1000 partos (i)','Pediatras /1000 partos (i)','Resíduo vs. grupo comparável (p.p., Síntese)']
for j,cn in enumerate(cols,1):
    c=ws.cell(1,j,cn); c.font=FB; c.fill=HF; c.alignment=Alignment(wrap_text=True,vertical='top')
ws.row_dimensions[1].height=60
Ri_m=RES8['med'][2]; Ri_e=RES8['enf'][2].copy(); Ri_e[[2017,2024]]=np.nan
naoesp=Z9['res']['naoesp'][2]; ped=Z9['res']['ped'][2]
def g(df,c,y):
    try:
        v=df.at[c,y]; return None if v is None or (isinstance(v,float) and np.isnan(v)) else float(v)
    except KeyError: return None
r=2
for c in T.index:
    for y in range(2013,2027):
        row=D[(D.cod==c)&(D.ano==y)].iloc[0]
        vals=[c,y,int(row.partos),int(row.ces),None,LV[c],row.setor,RG[c],ARS[c],VC[c],'†' if (c,y) in flag else '','*' if row.partos<300 else '','◊' if (c,y)==('A13',2019) else '','ᴸ' if c in LP else '',
              ' + '.join(seat.get((c,y),[])) if y<=2024 else '',g(OCC,c,y),g(RB['enf'],c,y),g(RB['med'],c,y),g(RSd['enf'],c,y),g(RSd['med'],c,y),g(Rgi,c,y),g(Rgii,c,y),g(Ri_m,c,y),g(Ri_e,c,y),
              g(Z9['Fi'],c,y),g(Z9['neoi'],c,y),g(Z9['perii'],c,y),g(naoesp,c,y),g(ped,c,y),g(RES10,c,y)]
        for j,v in enumerate(vals,1):
            cell=ws.cell(r,j,v); cell.font=F
            if isinstance(v,float): cell.number_format='0.0'
        ws.cell(r,5,f'=IF(C{r}>0,D{r}/C{r}*100,"")').number_format='0.0'
        r+=1
ws.cell(r+1,1,'Taxa CS calculada por fórmula (Cesarianas ÷ Partos × 100). 2026 = janeiro–abril (complementar, só taxas). Indicadores municipais: vazio = n.d. ou fora do período da fonte. Médicos/enfermeiros SNS: Fase 8 (A15/A16 2019 e médicos A28 2015–2018 = n.d.). Enfermeiros inscritos: 2017 e 2024 = n.d.').font=FG
ws.freeze_panes='C2'; widths(ws,13)
# ---------- phase sheets
phases=[('F1A',['out.md','out1c.md']),('F1B',['out1b.md']),('F2 Nível',['out2.md']),('F3 Setor',['out3.md']),('F4 Região',['out4.md']),('F5 Volume',['out5.md']),('F6 GO',['out6.md']),('F7 Ocupação',['out7.md']),
        ('F8 Pessoal',['out8g.md']),('F9A Contexto mun',['out9a.md']),('F9B Contexto reg',['out9b.md']),('F9C Nacional pop',['out9c.md']),('F9D Nacional saúde',['out9d.md'])]
for name,files in phases:
    ws=wb.create_sheet(name); r=1
    for fn in files:
        ws.cell(r,1,f'Saídas de cálculo ({fn})').font=FG; r+=1
        r=md_to_sheet(ws,W+fn,r,skip_titles=('neo/peri (i)',))
    if name=='F8 Pessoal':
        ADD={'A01':'Fafe (2013–2015)','A02':'Pombal, Alcobaça','A06':'Tomar, Torres Novas (2013–2016)','A07':'Torres Vedras, Peniche','A08':'Vila do Conde','A09':'Amarante','A10':'Chaves, Lamego; Peso da Régua (2013–2015)','A11':'Fundão','A19':'Águeda, Estarreja; Anadia (2013–2014)','A20':'Tondela','A22':'Elvas','A32':'Montijo','A33':'Seia','A34':'Serpa (2013–2014)','A36':'Ponte de Lima','A37':'Mirandela, Macedo de Cavaleiros','Lisboa (A03, A24, A25)':'Oeiras','Porto (A12, A30)':'Valongo'}
        r=put_table(ws,r,'Tabela 8.C – Municípios somados à sede em 2013–2018 (confirmada)',pd.DataFrame({'Unidade':list(ADD),'Municípios somados':list(ADD.values())}),'Não somados (duvidosos): Ovar (A05), Cantanhede (A31), Olhão (A23). Alcobaça somada à A02 (dados; a [C1] é um mapa de residência).')
    if name=='F9A Contexto mun':
        SP=[('2013–2018',list(range(2013,2019))),('2019–2024',list(range(2019,2025)))]
        dfc=pd.DataFrame({'Código':T.index})
        for lab,ys in SP:
            dfc[f'Óbitos neonatais {lab}']=[int(Z9['neoi'].loc[c,ys].sum()) for c in T.index]; dfc[f'Óbitos perinatais {lab}']=[int(Z9['perii'].loc[c,ys].sum()) for c in T.index]
        r=put_table(ws,r,'Tabela 9A.3 (revista) – Óbitos neonatais e perinatais por ULS, versão (i), contagens',dfc,'Contagens pequenas e instáveis; sem taxas por ULS (decisão R18). A tabela anterior por 100 000 mulheres foi retirada.')
    widths(ws)
# ---------- Síntese
ws=wb.create_sheet('Síntese'); r=1
dec=pd.DataFrame([(a,round(b,1),round(c,2),round(d,1)) for a,b,c,d in steps10],columns=['Agrupamento','% da variância entre unidades (médias 2013–2025) que fica dentro dos grupos','DP agregado dentro dos grupos (p.p.)','Mediana anual da % dentro dos grupos'])
r=put_table(ws,r,'S.2 – Exclusão sucessiva: dispersão que fica dentro dos grupos',dec,'Descritivo (decomposição da soma de quadrados), sem testes. DP total das médias das unidades = 3,75 p.p.')
r=put_table(ws,r,'S.3 – Resíduo de cada unidade face ao grupo comparável (nível × classe de volume; mediana dos pares, por ano)',tab10,'Atípica: ≥ 3 p.p. no mesmo sentido em ≥ 10 de 13 anos; quase: 7–9 anos. Grupos com < 3 unidades: comparação com o nível (A12, A17, A25); A23 com o nível I (sensibilidade com o nível II: resíduo médio −0,3).')
MX=pickle.load(open(W+'s11.pkl','rb'))
r=put_table(ws,r,'S.4 – Matriz de robustez (unidade × referência) e classificação final',MX,'A = atípica (≥ 10/13 anos), Q = quase (7–9 anos), — = não; entre parênteses: n.º de anos ≥ +3 p.p. / ≤ −3 p.p. face à mediana dos pares. Classificação final (R18): atípica ou quase em ≥ 4 das 5 referências. A36: atípica só na referência nível × volume – artefacto do grupo pequeno (A10, A27, A36).')
S1=pd.DataFrame([('Enfermeiros SNS /1000 partos (principal)','Hospital','37 (32 sem L/P)','0,30 (0,38)','0,20 (0,29)','—','+'),
('Médicos SNS /1000 partos (principal)','Hospital','36–37 (31–32)','0,25 (0,37)','0,12 (0,28)','—','+'),
('Médicos inscritos /1000 partos (i) / (ii)','Residência','37 / 34','0,27 / 0,34','0,06 / 0,20 (2019–2024)','0,15 / 0,24 (2013–2024)','+'),
('Enfermeiros inscritos /1000 partos (i) / (ii)','Residência','37 / 34','2013–2016: 0,28 / 0,28; 2018: 0,19 / 0,39','0,19 / 0,34 (2019–2023)','—','+'),
('Médicos GO /1000 partos (i) / (ii)','Residência','37 / 34','-0,03 / 0,00','-0,20 / -0,11 (2019–2024)','-0,14 / -0,10 (2013–2024, principal)','≈ 0 / −'),
('Taxa de ocupação (referência, não é pessoal)','Hospital','19–20 (14–15 sem L/P)','-0,28 (-0,40)','-0,09 (-0,25) (2019–2024)','—','−')],
columns=['Medida','Família','n','rho 2013–2018','rho 2019–2023/24','rho período completo','Sentido'])
r=put_table(ws,r,'S.1 – Medidas de pessoal lado a lado (rho de Spearman nas médias por subperíodo)',S1,'Descritivo, sem p-valor. Entre parênteses: sem Lisboa/Porto.')
HY=pd.DataFrame([('(a)1','Diferenças de prática clínica e cultura institucional','Estudos de variação entre hospitais com ajustamento ao risco (modelos multinível); estudos qualitativos sobre cultura e liderança das equipas','[referência a definir]'),
('(a)2','Case-mix não observado (cesariana anterior, paridade, pélvica, múltipla, prematuridade, idade, IMC)','Análises por grupos de Robson; estudos com dados individuais que comparam taxas brutas e ajustadas','[referência a definir]'),
('(a)3','Fatores organizacionais (cobertura 24 h, carga de trabalho, hora/dia, organização do bloco)','Estudos observacionais da distribuição horária/semanal das cesarianas e de modelos de equipa','[referência a definir]'),
('(a)4','Medicina defensiva e pedido materno','Inquéritos a profissionais; estudos sobre litigância; estudos sobre cesariana a pedido','[referência a definir]'),
('(a)5','Modelos de gestão e financiamento (PPP, incentivos, auditoria e feedback)','Avaliações de políticas de pagamento; ensaios ou estudos de auditoria e feedback; estudos público vs. privado','[referência a definir]')],
columns=['N.º','HIPÓTESE (literatura)','Tipo de evidência que a sustentaria','Referência'])
r=put_table(ws,r,'S.6 – Hipóteses (a) da literatura (HIPÓTESES, não conclusões)',HY)
dfr=RES10.copy(); dfr.insert(0,'Código',dfr.index); dfr.columns=[str(c) for c in dfr.columns]
r=put_table(ws,r,'S.5 – Resíduos anuais (p.p.) – dados do gráfico de resíduos',dfr.round(2))
widths(ws)
# ---------- Excluídos
EX=[('Universo','A38, A39, A40','Todas','Sem partos; municípios dessas ULS excluídos da agregação (R9b)'),
('Universo','Regiões autónomas','Todas','R3; São João da Madeira mantém-se'),
('1A','10 unidades-ano R2b (A02 2023 manual; A02 2024; A03 2023; A07 2023, 2025; A13 2023; A17 2025; A25 2023, 2024, 2025)','Todas','Mantidas e assinaladas (†), com sensibilidade sem elas'),
('1B','A13 2019','Taxa CS','Mantida e assinalada (◊), valor atípico – possível problema de registo; sensibilidade sem ela'),
('1A','2026 (janeiro–abril)','Taxa CS','Complementar: só taxas (R8)'),
('6','A16, A24, A25 na versão (ii)','Variáveis municipais (i)/(ii)','n.a. – sem municípios próprios (A25 também 2024–2025)'),
('7','A02, A07, A08, A15, A18, A19, A20, A23, A27, A29, A33, A35, A36','Ocupação','Sem valor do município sede (0 = n.d.)'),
('7','A01, A21, A31 (médias); A10, A04, A13 (só um subperíodo)','Ocupação','Menos de 4 anos com valor no subperíodo'),
('7','2025','Ocupação','Sem dados no [M4]'),
('8','A15 e A16, 2019','Pessoal SNS','Valor igual ao de 2018 no ano da mudança de método (provável imputação) → n.d.'),
('8','A28, médicos SNS, 2015–2018','Pessoal SNS','Queda de 506 para 361 sem município em falta e recuperação em 2019 → n.d.'),
('8','Todas, 2024','Pessoal SNS','0 em todos os municípios → n.d.'),
('8','Ovar (A05), Cantanhede (A31), Olhão (A23)','Pessoal SNS (Tabela 8.C)','Não somados: valor próprio depois de 2019'),
('8','Unidades-ano PPP (A15 2013–2021, A16 2013–2023, A17 2013–2020, A28 2013–2019)','Pessoal SNS','Assinaladas (ᴾ); análise também sem elas (possível subcontagem)'),
('8','Todas, 2017 e 2024','Enfermeiros inscritos (Ordens)','Distribuição municipal não credível (2017 ≈ 250 e 2024 ≈ 150 municípios com variação > 30%) → n.d.'),
('9A','TMI por ULS','Contexto municipal','Não agregada (Continente + distribuição municipal)'),
('9A','Taxas de óbitos neonatais/perinatais por ULS','Contexto municipal','Só contagens; taxas a nível nacional (9C)'),
('9A','Densidade agregada por ULS','Contexto municipal','Sem área: distribuição dos municípios'),
('9A','Pessoal ao serviço nos hospitais (total) por ULS','Contexto municipal','Cobertura municipal 58–67%: só série do Continente'),
('9B','Idade média da mãe 2013–2020 (Centro, OVT, GL, PS, Alentejo)','Contexto regional','0 no ficheiro → n.d.'),
('9B','Nados-vivos 40–44 em 2024 (todas as regiões); % ≥35 em 2024','Contexto regional','0 incoerente com o total → n.d.; valor derivado só em nota'),
('9C','Óbitos maternos 2023, 2024, 2025; TMM 2025','Contexto nacional','0 no ficheiro → n.d. (R1)'),
('9C','"Óbitos infantis – Com 7 dias ou mais"','Contexto nacional','Apresentada sem interpretação: definição não especificada na metainformação da fonte'),
('9D','[N5] privados, total e % CS dos hospitais (2019 = 0)','Contexto nacional','Não analisados nesta fase (outro prompt); 2019 = dado em falta'),
('9D','[N6] 2024–2025; [N5] público e PPP 2025','Contexto nacional','Sem dados')]
ws=wb.create_sheet('Excluídos'); put_table(ws,1,'Excluídos, n.d. e unidades-ano assinaladas (todas as fases)',pd.DataFrame(EX,columns=['Fase','Unidade / ano / série','Afeta','Motivo e tratamento']))
ws.column_dimensions['A'].width=10; ws.column_dimensions['B'].width=70; ws.column_dimensions['C'].width=30; ws.column_dimensions['D'].width=90
# ---------- R18
R18=[('1A','Limiar absoluto de 300 partos (R13) mantido também em 2026.'),
('1A','A02 2023 assinalada manualmente como R2b: subida coincidente com a interrupção da A07 (junho–outubro de 2023).'),
('1A','Desvio-padrão populacional (DESVPAD.P).'),
('1A','Unidade atípica: fora do limite de 99,8% no mesmo sentido em ≥ 10 de 13 anos (2013–2025); 7–9 anos = quase atípica.'),
('1B','Baixo volume: média < 600 partos/ano em 2013–2025 (classe mais baixa da Fase 5).'),
('1B','Funnel de Spiegelhalter como sensibilidade; limites binomiais como principal; atípicas sob ambos os critérios.'),
('1B','A13 2019 mantida e assinalada "valor atípico – possível problema de registo"; sensibilidade sem ela.'),
('3','Comparação EPE/PPP principal em 2013–2019; 2020–2021 transição; 2022–2025 só descrição da A16; ênfase no antes/depois dentro da unidade; datas da R9 prevalecem.'),
('5','Classes de volume < 600 / 600–1499 / 1500–2499 / ≥ 2500, fixas por unidade pela média 2013–2025; classes do protocolo só como sensibilidade.'),
('6','Versão (ii): A16, A24, A25 = "n.a. – sem municípios próprios" em todos os anos e variáveis municipais (A25 também 2024–2025); conclusões de (ii) sobre 34 unidades; versão (i) principal.'),
('7','Município sede por unidade-ano = município a que o [M5] atribui os partos; repartição → média ponderada pelos partos (só municípios com valor).'),
('7','Valores em falta = "n.d."; sem substituição; análises anuais com as unidades com valor (n indicado); médias por subperíodo com ≥ 4 de 6 anos; conclusões indicativas.'),
('7','rho por ano e médias 2013–2018 e 2019–2024 em separado (quebra de 2019); 0 = sem dados; Lisboa/Porto valor comum, com e sem as 5 unidades; R6 e Ovar não se aplicam.'),
('7','Tabela 6 confirmada; mudanças de sede (A06 2017–2019; A04 2019) assinaladas e não interpretadas; cobertura (≈ 20 unidades/ano; 14–15 sem Lisboa/Porto) indicada.'),
('8','Medida principal: pessoal ao serviço nos hospitais do SNS ([M3], bloco SNS), 2013–2023, por 1000 partos da unidade; atribuição pela sede (Tabela 6); Lisboa/Porto valor comum do município; subperíodos 2013–2018 e 2019–2023.'),
('8','Versão (b) "unidade completa": em 2013–2018 soma-se à sede o pessoal dos outros hospitais SNS da mesma unidade (Tabela 8.C); "só sede" como sensibilidade. Pertença assumida em todos os anos anteriores com valor (confirmado).'),
('8','Ovar, Cantanhede e Olhão não somados; Alcobaça somada à A02 (CH Leiria desde 2013), com nota sobre a [C1]; Oeiras e Valongo somados ao numerador de Lisboa e Porto.'),
('8','A15 e A16 2019 = n.d. (provável imputação); médicos A28 2015–2018 = n.d.; unidades-ano PPP assinaladas e análise sem elas como verificação.'),
('8','Medida secundária (Ordens): enfermeiros 2017 e 2024 = n.d.; subperíodos 2013–2016, 2018, 2019–2023; médicos: média 2013–2024 principal, subperíodos como verificação.'),
('8+','Variáveis municipais em duas famílias: "hospital" (INE, sede: ocupação, pessoal SNS) e "residência" (Ordens: GO, médicos e enfermeiros inscritos). Contagens de pessoal sempre por 1000 partos da unidade. Comparar principal e secundária nas conclusões.'),
('9A','Contexto municipal agregado por ULS com [C1] (i)/(ii); sem relação com a taxa de CS; mulheres 15–49 como referência; comparações 2013–2020 e 2021–2023; 2024–2025 com a nova delimitação das ULS.'),
('9A','TMI não agregada por ULS; óbitos neonatais/perinatais por ULS só em contagens; densidade como distribuição dos municípios; pessoal hospitalar total só no Continente.'),
('9B','[R1] "Quadro"; 7 regiões = [C2]; idade média com 0 = n.d.; % ≥35 = (35–39 + 40–44 + 45–49 + 50+) ÷ soma dos grupos; 40–44 de 2024 = n.d. (valor derivado só em nota).'),
('9B','Taxa de CS regional agregada (Fase 4) como principal e mediana das unidades como verificação; residência vs. localização indicada nas conclusões.'),
('9C','Âmbito "Portugal" em [N1]–[N3]; óbitos infantis = "Óbitos – Menos de 1 ano"; "Com 7 dias ou mais" sem interpretação; óbitos maternos 2023–2025 e TMM 2025 = n.d.; comparação CS vs. idade por variações em subperíodos.'),
('9D','Âmbitos: [N4] Portugal, [N6] Continente, [N5] Portugal; [N5] só público e PPP; [N6] ┴ 2019 com subperíodos; pessoal SNS também por 1000 partos do [H].'),
('Síntese','Classificação final "robusta": atípica ou quase em ≥ 4 das 5 referências (global, nível, volume, região, nível × volume); o método residual nível × volume é uma das 5 referências; matriz completa unidade × referência apresentada.'),
('Síntese','Lista final (opção c): regra ≥ 4/5 → 9 unidades robustas (A04, A09, A10, A14, A15, A21, A25, A27, A37); "núcleo" = atípicas nas 5 referências (A04, A10, A14, A15, A21, A37); para A09, A25 e A27 indica-se a referência em que não são atípicas e porquê; A25 verificada sem os anos R2b. A lista de 6 indicada antes resultava de um erro de contagem e foi corrigida.'),
('Síntese','A25 – sensibilidade sem os anos R2b (2023–2025): limiares proporcionais aos 10 anos restantes (atípica ≥ 8/10; quase ≥ 6/10), porque a regra é uma proporção dos anos; A25 mantém-se robusta com a nota "frágil", indicando as contagens exatas em 13 e em 10 anos e que, com limiares absolutos (quase ≥ 7), deixaria de ser robusta.'),
('Síntese','A36 tratada como artefacto do grupo pequeno (II × 600–1499: A10, A27, A36), mantida visível na matriz com nota (atípica só nesse critério, não robusta).'),
('Síntese','rho dos médicos de GO calculado também para 2013–2018 e 2019–2024 (Tabela S.1); a análise principal dos GO continua a ser 2013–2024 (Fase 6).'),
('Síntese','Hipóteses (a): sem referências citadas; para cada uma indica-se o tipo de evidência e "[referência a definir]" (fontes primárias a acrescentar pela autora).'),
('Síntese','Referência nível × volume: resíduo de cada unidade = taxa − mediana dos pares no mesmo nível × classe de volume (grupos < 3 → nível; A23 → nível I, sensibilidade nível II); residual atípica: ± 3 p.p. no mesmo sentido em ≥ 10/13 anos; robustez com 5 grupos de referência.')]
ws=wb.create_sheet('Registo de decisões'); put_table(ws,1,'Registo de decisões (R18)',pd.DataFrame(R18,columns=['Fase','Decisão']))
ws.column_dimensions['A'].width=10; ws.column_dimensions['B'].width=160
for wsx in wb.worksheets:
    for row in wsx.iter_rows():
        for c in row:
            if c.value is not None and c.font.name!='Arial': c.font=F
wb.save(OUT); print('saved')
