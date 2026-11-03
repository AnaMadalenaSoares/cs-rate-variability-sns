# Scripts da análise da variabilidade da taxa de cesariana (SNS, 2013–2025/26)

Scripts Python usados em todas as fases da análise (1A a 9D e Síntese) e na construção do Excel final.

## Estrutura

```
scripts_analise_CS/
├── LEIA-ME.md
├── correr_tudo.py          corre todos os scripts pela ordem certa
├── f0_auxiliares.py … fxl.py
├── dados/                  colocar aqui os ficheiros de origem (ver lista abaixo)
├── dados_intermedios/      conteúdos de 4 ficheiros auxiliares (ver f0_auxiliares.py)
└── w/                      saídas: ficheiros .pkl intermédios, saídas de cálculo out*.md e figuras .png
```

## Requisitos

Python 3 com `pandas`, `numpy`, `scipy`, `matplotlib` e `openpyxl`.

## Como correr

1. Copiar os ficheiros de origem para `dados/` com os nomes da lista abaixo (os nomes não têm acentos).
2. Na pasta `scripts_analise_CS`, executar `python correr_tudo.py`.
   Também se pode correr cada script isoladamente, desde que os scripts anteriores já tenham sido corridos.

Todos os caminhos são relativos à pasta `scripts_analise_CS`.

## Ordem e conteúdo dos scripts

| Fase | Script | Conteúdo | Saídas principais |
|---|---|---|---|
| 0 | f0_auxiliares.py | Reconstrói 4 ficheiros auxiliares a partir de `dados_intermedios/` | w/flag2.pkl, seat.pkl, m4.pkl, m5mun.pkl |
| 1A | f1a.py | Leitura do Excel 1 – hospitais (Sheet5 e folha mensal); base unidade-ano | w/d.pkl |
| 1A | f1b.py | Taxa por unidade e ano, estatísticas anuais, R2b, coerência [M5]/[N5], atípicas | w/out.md, s.pkl |
| 1A | f1c.py | Figuras da Fase 1A | w/Fig1A_*.png |
| 1B | f1d.py | Diagramas de caixa, funnel plots, sobredispersão, variações anuais e bruscas | w/out1b.md, s1b.pkl, figuras |
| 1B | f1e.py | Verificação do valor da A13 em 2019 | w/out1c.md |
| 2 | f2.py | Nível hospitalar | w/out2.md, s2.pkl, figuras |
| 3 | f3.py | Setor (EPE/PPP) | w/out3.md, figuras |
| 4 | f4.py | Região (7 regiões e ARS) | w/out4.md, s4.pkl, figuras |
| 5 | f5.py | Volume de partos | w/out5.md, figuras |
| 6 | f6a.py | Mapa município → ULS e médicos de GO por município | w/map.pkl, m3go.pkl |
| 6 | f6.py | Médicos de GO por 1000 partos, versões (i) e (ii) | w/out6.md, s6.pkl, figuras |
| 7 | f7.py | Taxa de ocupação do município sede (Tabela 6) | w/out7.md, s7.pkl, figuras |
| 8 | f8a.py | Médicos e enfermeiros inscritos por município (Ordens) | w/m3me.pkl |
| 8 | f8.py | Medida secundária (Ordens) | w/out8.md, s8.pkl |
| 8 | f8b0.py, f8b.py | Inspeção e extração do pessoal dos hospitais do SNS por município | w/s8b.pkl |
| 8 | f8c.py, f8d.py, f8e.py | Exploração: só sede vs. unidade completa e verificações | w/out8b.md |
| 8 | f8f.py | Versão "unidade completa" (Tabela 8.C) | w/s8f.pkl |
| 8 | f8g.py | Fase 8 final: medida principal (pessoal SNS) e comparação com a secundária | w/out8g.md, s8g.pkl, figuras |
| 9A | f9a0.py | Inspeção dos ficheiros municipais [M1], [M3] | — |
| 9A | f9a.py | Contexto municipal: mulheres 15–49, óbitos, médicos não especialistas e pediatras, densidade | w/out9a.md, s9a.pkl |
| 9A | f9b.py | Figuras da Fase 9A | w/Fig9A_*.png |
| 9B | f9c.py | Contexto regional ([R1]) | w/out9b.md, s9b.pkl, figuras |
| 9C | insp9c.py, f9d.py | Contexto nacional, população ([N1]–[N3]) | w/out9c.md, s9c.pkl, figuras |
| 9D | insp9d.py, f9e.py | Contexto nacional, saúde ([N4]–[N6]) | w/out9d.md, s9d.pkl, figuras |
| Síntese | f10.py | Exclusão sucessiva e resíduos face ao grupo comparável | w/out10.md, s10.pkl |
| Síntese | f11.py | Matriz de robustez (5 referências), núcleo e classificação final | w/s11.pkl |
| Síntese | f12.py | Verificação da A25 sem os anos R2b | — |
| Excel | fxl.py | Constrói "Resultados finais - análise CS.xlsx" | Excel na pasta principal |

Os scripts f8b0, f8c, f8d, f8e, f9a0, insp9c e insp9d são de inspeção ou exploração. Ficaram incluídos para que o percurso seja rastreável; os resultados finais vêm dos outros.

## Ficheiros de origem (pasta `dados/`)

| Nome esperado | Fonte | Usado em |
|---|---|---|
| Excel_1_-_hospitais.xlsx | [H] base dos hospitais | f1a |
| Correla__o_munic_pios_final.xlsx | [C1] correspondência município → ULS | f6a |
| Correla__o_regi_es_final.xlsx | correspondência das regiões | f4 |
| Munic_pio-sa_de-SNS-total.xlsx | [M5] PORDATA | f1b |
| Munic_pio-sa_de-recursos_humanos-total.xlsx | [M3] PORDATA | f6a, f8a, f8b, f8b0, f9a, f9a0 |
| Munic_pio-Popula__o-Esperan_a_de_vida_e_mortes-total.xlsx | [M1] PORDATA | f9a, f9a0 |
| Munic_pio-Popula__o-Popula__o_residente-total.xlsx | [M2] PORDATA | f9a |
| Regi_o-popula__o-nascimentos_e_fecundidade-total.xlsx | [R1] PORDATA | f9c |
| Portugal-Popula__o-Esperan_a_de_vida_e_mortes-total.xlsx | [N1] PORDATA | f9d, insp9c |
| Portugal-Popula__o-Nascimentos_e_fecundidade-total.xlsx | [N2] PORDATA | f9d, insp9c |
| Portugal-Popula__o-Popula__o_residente-total.xlsx | [N3] PORDATA | f9d, insp9c |
| Portugal-sa_de-recursos_humanos-total.xlsx | [N4] PORDATA | f9e, insp9d |
| Portugal-Sa_de-Servi_os_e_utiliza__o-total.xlsx | [N5] PORDATA | f1b, f9e, insp9d |
| Portugal-Sa_de-SNS-total.xlsx | [N6] PORDATA | f9e, insp9d |

## Notas

1. **Ficheiros auxiliares (f0_auxiliares.py).** Quatro ficheiros intermédios foram criados durante a análise com comandos executados diretamente e não ficaram guardados como script:
   - a lista das 10 unidades-ano R2b, incluindo a marcação manual da A02 2023;
   - a Tabela 6 (município sede por unidade e ano);
   - a taxa de ocupação por município ([M4], extraída de "Município – Saúde – Serviços e utilização");
   - os partos SNS por município ([M5]).

   Os seus conteúdos estão em `dados_intermedios/` (CSV e JSON legíveis), e o `f0_auxiliares.py` reconstrói-os. Por isso, o ficheiro [M4] não é lido diretamente por nenhum script.
2. **Validação.** O `fxl.py` produz o Excel antes da validação. As correções da versão validada ("Resultados finais - análise CS (validado).xlsx") foram feitas depois, célula a célula, e estão listadas na folha "Validação – alterações" desse ficheiro. Entre elas estão as estatísticas sem R2b de 2023 e as taxas de crescimento da Fase 9A.
3. **Fórmulas.** As fórmulas do Excel (taxa de CS na base unidade-ano) são calculadas quando o ficheiro é aberto no Excel ou no LibreOffice.
4. **Reprodutibilidade.** Corridos de raiz numa pasta limpa, os scripts reproduziram as mesmas saídas de cálculo (out*.md). A única diferença foi a ordem de apresentação de uma linha de verificação da Fase 6, com os mesmos valores.
