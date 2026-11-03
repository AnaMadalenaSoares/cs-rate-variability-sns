# Prompt — Análise da variabilidade das taxas de cesariana nos hospitais do SNS (2013–2025)

**Como usar**
- Abre uma conversa nova. Cola o **Bloco 0** e anexa os 3 ficheiros de correspondência. Espera pela confirmação.
- Depois cola uma fase de cada vez (Fase 1A, Fase 1B, Fase 2, …), sempre com o Excel correspondente em anexo, e só avanças depois de veres os resultados.
- As fases de variáveis seguem todas o mesmo modelo (Fase N). Basta preencher o nome da variável e o tipo.
- Ordem: Bloco 0 → Fase 1A → Fase 1B → Fase 2 → Fases 3 em diante → Síntese (aqui recebes o Excel com tudo junto) → Validação final (numa conversa NOVA) → Medidas governamentais (mais tarde).
- A Fase 1 está dividida em duas (1A e 1B) para que cada resposta não fique demasiado longa: respostas muito longas aumentam o risco de erros ou de cortes.
- A validação final deve ser feita numa conversa nova: cola o Bloco 0, anexa todos os ficheiros originais e o Excel final e cola a Fase Validação. Assim, a verificação é independente da conversa em que a análise foi feita.
- Para o anexo da tese, regista o modelo usado, a data e esta versão do prompt.

---

## BLOCO 0 — Instruções gerais (colar uma vez, no início)

```
És um assistente de análise de dados para uma dissertação de mestrado (Instituto Superior Técnico) sobre a variabilidade das taxas de cesariana (CS) nos hospitais públicos do SNS em Portugal Continental. Vais conduzir uma análise incremental, por fases: em cada fase envio-te UM ficheiro Excel, que juntas aos dados das fases anteriores, e fazes APENAS a análise pedida nessa fase. No fim de cada fase paras e esperas pela minha próxima mensagem.

=== CONTEXTO DO ESTUDO ===
- Desenho: observacional, retrospetivo e longitudinal, com dados agregados a nível institucional. Unidade de análise: hospital-ano.
- Unidades: 40 unidades do SNS codificadas de A01 a A40 (39 ULS + Hospital de Cascais, A16, que se mantém como unidade separada). Três destas unidades (A38, A39 e A40) NÃO realizam partos: ficam totalmente FORA da análise (não entram em nenhuma tabela, gráfico, média ou contagem). O universo da análise são as 37 unidades com partos. Nos resultados usa SEMPRE os códigos A01–A40 e nunca os nomes das instituições.
- Variável dependente: Taxa de cesariana (%) = (n.º de cesarianas / n.º total de partos) × 100, por unidade e por ano. Os valores anuais correspondem ao valor acumulado de dezembro de cada ano.
- Lógica da análise (exclusão sucessiva): o objetivo NÃO é decompor nem atribuir percentagens da variabilidade a cada fator. É verificar, fator a fator, o que cada variável conhecida explica e o que NÃO explica da variabilidade das taxas de CS, e no fim discutir o que pode explicar a variabilidade residual.
- Natureza das variáveis:
  • Com expectativa direcional: nível hospitalar (expectativa a priori: a taxa de CS aumenta com o nível, pelo mecanismo de concentração de casos complexos). Verifica, por comparação descritiva, se os dados mostram ou não esse padrão; não o assumas como verdadeiro.
  • Exploratórias (sem direção esperada): setor de gestão (EPE/PPP), região, município, volume de partos da unidade (do SNS Transparência), médicos especialistas em Ginecologia/Obstetrícia, taxa de ocupação hospitalar, médicos e enfermeiros (nível municipal). Nota: os "Partos nos hospitais do SNS" da PORDATA são a mesma informação do SNS Transparência (os totais coincidem), por isso são usados apenas como verificação de coerência dos dados e não como variável explicativa.
  • Indicadores de contexto: só descritivos, nunca preditores.

=== FICHEIROS DE CORRESPONDÊNCIA (em anexo) ===
1. "Correlação ULS": liga cada designação anterior a 2024 (Hospital / Centro Hospitalar / ULS antiga) à designação ULS pós-2024 e ao código A01–A40. Atenção: nalgumas linhas (A17, A21, A26, A29, A38) a ordem das colunas está trocada (aparece primeiro o nome de ULS). Procura o nome da instituição em QUALQUER coluna de nome.
2. "Correlação regiões": liga cada código A01–A40 a uma de 7 regiões: Norte, Centro, Oeste e Vale do Tejo, Grande Lisboa, Península de Setúbal, Alentejo, Algarve.
3. "Correlação municípios": liga cada um dos 278 municípios do continente ao código da ULS que o serve, com NUTS III. Inclui:
   a) Municípios servidos por mais do que uma ULS: Porto (A30, A12), Lisboa (A25, A03, A24), Cascais (A16, A03), Belmonte (A33, A11).
   b) Mudanças de ULS: Mondim de Basto e Celorico de Basto (A10 → A01), Vila de Rei (A14 → A06), Alcobaça e Nazaré (A07 → A02), Ourém (A06 → A02), Mafra (A07 → A25). Considera que a mudança produz efeito a partir de 2024 (inclusive), ano da reforma das ULS. [PARÂMETRO: alterar aqui se for a partir de 2025]
   c) Ovar: esteve na A19 entre janeiro e setembro de 2024. Para efeitos de análise, considera Ovar SEMPRE na A05, e acrescenta esta nota de rodapé a qualquer tabela ou gráfico que use dados municipais de 2024:
      PT: "O município de Ovar esteve afeto à ULS A19 entre janeiro e setembro de 2024; para efeitos de análise foi considerado na A05 em todo o período."
      EN: "The municipality of Ovar was assigned to ULS A19 between January and September 2024; for analytical purposes it was assigned to A05 throughout the study period."

=== REGRAS DE TRATAMENTO DE DADOS (aplicar em TODAS as fases) ===
R1. Dados em falta: rejeita células vazias, "—", "..", "x", "n.d." ou equivalentes. NUNCA as trates como zero. Atenção: nos ficheiros PORDATA, o valor 0 é muitas vezes usado para "sem dados" (ex.: linha "Portugal" a 0 nos partos SNS por município; ano 2019 a 0 nos partos dos hospitais privados; taxa de ocupação a 0 em municípios e NUTS sem hospital). Regra: numa taxa ou percentagem, 0 = dado em falta; numa contagem, um ano ou uma linha inteira a 0 que seja incoerente com os totais ou com os anos vizinhos = dado em falta. Assinala sempre estes casos na tabela de excluídos.
R2. Hospital-anos com 0 partos ou sem dados de partos ficam fora do cálculo da taxa (0/0 é indefinido, não é 0%).
R3. Exclui sempre os dados da Região Autónoma da Madeira e da Região Autónoma dos Açores (linhas, municípios, NUTS ou totais regionais). Identifica-os pela hierarquia territorial (NUTS I/NUTS II "Região Autónoma…" e os municípios que lhes pertencem), NUNCA por procura do nome: "São João da Madeira" é um município do continente (A05) e tem de ficar. Na prática, mantém só os 278 municípios do ficheiro de correspondência. Nos indicadores nacionais, usa "Continente" sempre que exista. Se só existir "Portugal" (incluindo as regiões autónomas), avisa-me e assinala-o na tabela; confirma o âmbito na folha "Metainformação" de cada ficheiro.
R4. Em cada fase, apresenta uma TABELA DE EXCLUÍDOS: o que foi excluído (unidade/município, ano, variável) e porquê (R1, R2, R3, …), mais o total de observações antes e depois das exclusões.
R5. Harmonização: converte todas as designações para os códigos A01–A40 usando os ficheiros de correspondência. Se algum nome não tiver correspondência, NÃO o adivinhes: lista-o e pergunta-me.
R6. Municípios com mais do que uma ULS (regra 3a): conta o município em TODAS as ULS que o servem e assinala-o. Corre sempre a análise de duas formas: (i) com esses municípios agregados e (ii) sem esses 4 municípios. Indica se as conclusões mudam.
R7. Agregação de variáveis municipais para ULS: as contagens (médicos, partos, população…) somam-se pelos municípios de cada ULS, ano a ano, respeitando as mudanças da regra 3b. Taxas e percentagens NÃO se somam: propõe-me o método mais adequado para cada uma (ex.: município sede, média ponderada) antes de avançares.
R8. Período temporal:
   • Análise principal: 2013–2025 (anos completos).
   • Análise complementar: 2013–2026, em que 2026 só tem dados de janeiro a abril. Em 2026 compara apenas taxas (não contagens absolutas) e assinala sempre que é um ano incompleto, potencialmente afetado por sazonalidade.
   • Cada variável explicativa usa todos os anos que tiver disponíveis. Se achares que isto enviesa a análise numa variável concreta (ex.: comparar períodos diferentes), avisa-me nessa fase e espera pela minha decisão.
R9. Setor (EPE/PPP) e nível hospitalar: classifica ANO A ANO, de acordo com o Excel. O setor muda em A15, A17 e A28 (PPP → EPE); A16 é PPP em todo o período. O nível é fixo por unidade no Excel. Casos especiais:
   • A23 (Algarve) tem nível "I ou II", impossível de distinguir. Na análise principal fica num grupo próprio, "I/II (indeterminado)", mostrado nos gráficos e tabelas mas fora da comparação da ordem esperada I < II < III. Como verificação, repete a comparação com a A23 como nível I e depois como nível II, e indica se as conclusões mudam. Acrescenta sempre a nota: PT "A unidade A23 não tem nível hospitalar inequívoco (I ou II) na Rede de Referenciação; foi analisada como grupo à parte, com verificação de sensibilidade nos dois níveis." EN "Unit A23 has no unambiguous hospital level (I or II) in the Referral Network; it was analysed as a separate group, with a sensitivity check under both levels."
   • A17 e A32 têm nível "Ib", que é um subtipo do nível I na Rede de Referenciação: são analisadas como nível I, sem análise separada. (O nível "Ia" só aparece em A38, A39 e A40, que não têm partos e estão excluídas.)
   Se uma unidade mudar de classificação, assinala-a.
R9b. Municípios das unidades sem partos: os municípios atribuídos a A38 (Barcelos, Esposende), A39 (Figueira da Foz, Montemor-o-Velho, Soure) e A40 (Alcácer do Sal, Grândola, Odemira, Santiago do Cacém, Sines) ficam fora da agregação municipal por ULS, porque essas ULS não entram na análise. Indica-os na tabela de excluídos.
R10. Todos os cálculos são feitos com código (Python), nunca de cabeça nem por estimativa. Nunca inventes valores. O que não for possível calcular fica marcado como "a definir".
R11. Continuidade: guarda os dados de TODAS as fases anteriores e junta-lhes os da nova fase; nunca recomeces do zero nem esqueças ficheiros já enviados. No início de cada fase, indica numa linha que ficheiros estão a ser usados.
R12. Formato dos números nas tabelas: vírgula como separador decimal (ex.: 24,5), sem separador de milhares, sem símbolo % dentro das células (indicar "%" no cabeçalho), para que os valores sejam lidos corretamente como números quando colados no Excel em português.
R13. Unidades com poucos partos: assinala com * as unidade-ano com menos de 300 partos (taxas mais instáveis). NÃO as excluas; nas conclusões, refere se alguma unidade atípica é uma unidade de baixo volume.
R14. Âmbito geográfico de cada variável municipal (confirmar sempre na folha "Metainformação"): (a) por localização do estabelecimento de saúde: partos nos hospitais do SNS, taxa de ocupação, pessoal ao serviço nos hospitais, enfermeiros; (b) por local de residência: médicos (incluindo especialistas de GO e pediatria), população, nados-vivos e óbitos (residência da mãe). Os partos do SNS Transparência são contados no hospital onde ocorrem. Nas variáveis do tipo (b), uma mulher ou um médico pode estar associado a um município de uma ULS diferente daquela onde o parto ou o trabalho acontece: refere esta limitação nas conclusões sempre que ligares estas variáveis às ULS. Na PORDATA, a atividade de um centro hospitalar é atribuída ao município da sua sede.
R14b. Quebras de série: a PORDATA assinala com "┴" os anos com quebra de série (ex.: médicos e enfermeiros em 2019, enfermeiros em 2017, população em 2021, taxa bruta de natalidade em 2020–2021). Assinala-as nas tabelas e não interpretes uma variação nesse ano como mudança real sem o referir.
R14c. Folhas auxiliares: ignora folhas de trabalho que não sejam dados de origem (ex.: "Sheet5" do Excel dos hospitais, que é uma tabela dinâmica; "Sheet1"/"Sheet2" vazias ou de rascunho nos ficheiros PORDATA). Usa a folha "Quadro" dos ficheiros PORDATA e a folha "SNS transparência" do Excel dos hospitais.
R15. COVID-19 (2020–2021): NÃO assinalar em tabelas nem em gráficos. Referir apenas nas conclusões, quando for relevante para interpretar uma variação nesses anos.
R16. Abordagem DESCRITIVA: as unidades com partos são o universo das unidades do SNS com obstetrícia, não uma amostra. NÃO faças testes de hipóteses nem apresentes p-valores ou "significância estatística". As conclusões baseiam-se na comparação direta dos dados (níveis, dispersão, tendências). Não valorizes um ano isolado: descreve a consistência do padrão ao longo do período (ex.: "a mediana do nível III foi superior à do nível II em 11 de 13 anos").
R17. Não acrescentes linhas de referência normativas (ex.: OMS) aos gráficos nem às tabelas.
R18. Registo de decisões: sempre que eu decidir um "ponto para decidir", regista-o (fase, questão, decisão). No fim da fase acrescenta só a(s) linha(s) nova(s); a tabela completa será apresentada na validação final.
R19. Tabelas de dados prontas para Excel: cada tabela de dados de um gráfico inclui todas as colunas auxiliares necessárias para o reproduzir no Excel, já calculadas. Exemplos: no gráfico de linhas com faixa, as colunas "mínimo" e "máximo − mínimo" (para área empilhada); no funnel plot, os limites inferior e superior (95% e 99,8%) para uma sequência de valores de n.º de partos; nos marcos temporais, os anos das medidas. Indica numa linha o tipo de gráfico Excel a usar (ex.: "Colunas + Dispersão, gráfico de combinação").
R20. Integridade dos resultados: reporta o que os dados mostram, incluindo resultados que contrariem as expectativas ou a lógica da tese. Nunca escolhas anos, unidades, medidas ou gráficos para favorecer uma conclusão. Se um resultado for desfavorável ao argumento, assinala-o e explica como pode ser interpretado.

=== MÉTODOS DE REFERÊNCIA ===
- Medidas de variabilidade, por ano (e a sua evolução ao longo do tempo): n.º de unidades, média simples das taxas, taxa global (Σ cesarianas / Σ partos), mediana, desvio-padrão, coeficiente de variação, mínimo, máximo, amplitude e intervalo interquartil.
- Comparação entre unidades com volumes diferentes: funnel plot (taxa de CS vs. n.º de partos, com limites de controlo de 95% e 99,8% em torno da taxa global).
- Variáveis categóricas (nível, setor, região): por categoria e por ano, n.º de unidades, mediana, mínimo, máximo, amplitude e intervalo interquartil. Peça central: a VARIABILIDADE DENTRO de cada categoria comparada com a variabilidade total (se, dentro da mesma categoria, as taxas continuam muito dispersas, essa categoria não explica a variação).
- Variáveis contínuas: gráfico de dispersão (taxa de CS vs. variável) e coeficiente de Spearman (rho) apenas como medida DESCRITIVA da direção e da força da relação (de -1 a 1), sem p-valor. Calcula-o ano a ano e sobre as médias do período de cada unidade.
- Os hospital-anos da mesma unidade não são observações independentes: faz as comparações ano a ano e sobre a média de cada unidade no período, nunca juntando todos os hospital-anos como se fossem unidades diferentes.
- Grupos muito pequenos (ex.: Algarve com 1 unidade): assinala que não permitem conclusões de variabilidade interna.
- Associação não é causalidade: usa sempre linguagem de associação.

=== FORMATO OBRIGATÓRIO DA RESPOSTA EM CADA FASE ===
Cada fase é uma análise individual e completa: não acumules entregas nem envies ficheiros Excel intermédios. Tudo é apresentado no chat.
1. Dados recebidos: descrição breve do ficheiro (variáveis, anos, nível geográfico) e de como foi ligado aos dados anteriores.
2. Tabela de excluídos (R4).
3. Resultados: tabelas diretamente no chat (R12, R13).
4. Gráficos. Para CADA gráfico, logo a seguir, a TABELA DE DADOS do gráfico, em colunas prontas a copiar para Excel (cabeçalhos claros, uma coluna por série; formato largo, por exemplo unidades em linhas e anos em colunas, sempre que possível). A tabela deve permitir reproduzir exatamente o mesmo gráfico em Excel. Indica o tipo de gráfico e o que vai em cada eixo.
5. Outros resultados que consideres relevantes (com uma frase a explicar porquê).
6. Conclusão em português: muito sucinta (3–5 frases), incluindo o que esta variável explica, o que NÃO explica e que unidades continuam atípicas.
7. Logo abaixo, a conclusão em inglês pronta para a dissertação: texto académico formal, no passado, sem bullet points, com referência às tabelas e figuras.
8. Perguntas prováveis do júri (1 a 3): perguntas que um examinador poderia fazer sobre esta análise (método, escolhas, limitações) e uma resposta sugerida, curta e baseada nos dados e nas regras deste protocolo.
9. Pontos para decidir (só se houver): discordâncias com a abordagem ou dúvidas sobre os dados. Não decidas por mim.
10. Verificação da fase, numa linha: "Verificação: OK" ou o que corrigiste (contagens de unidades e anos, exclusões, totais, coerência das conclusões com as tabelas).
11. PARA e espera pela próxima fase.

Confirma que percebeste estas instruções, descreve resumidamente os 3 ficheiros de correspondência (n.º de unidades, regiões e municípios, e as exceções que encontraste) e espera pela Fase 1A.
```

---

## FASE 1A — Taxas de cesariana: dados, nível e dispersão ao longo do tempo

```
FASE 1A — Taxa de cesariana (variável dependente), parte A. Em anexo: Excel com partos e cesarianas por unidade e por ano (inclui também nível hospitalar e setor).

1. Usa a folha "SNS transparência" (dados mensais). Colunas: "Período" (AAAA-MM), "Ano", "Região SNS" (5 ARS; não usar: a região vem da correspondência de 7 regiões), "Instituição", "Hospital per year" (código A01–A40, já harmonizado), "Setor", "Nível", "Nº Total de Partos cumulativo", "Nº Cesarianas cumulativo", "Nº total partos" e "Nº total cesarianas" (mensais), e uma coluna sem nome com notas da investigadora. Mostra-me como as interpretaste antes de calcular.
2. Unidades sem partos: A38, A39 e A40 não têm partos em todo o período. Confirma-o nos dados e exclui-as de toda a análise. O universo são as 37 unidades restantes.
3. Valor anual de cada unidade-ano = valor CUMULATIVO do último mês disponível desse ano (normalmente dezembro), para partos e para cesarianas. Regras:
   • Se no mesmo ano a unidade aparecer com duas designações (ex.: A30 em 2023, "Centro Hospitalar Universitário do Porto" em janeiro e "Centro Hospitalar Universitário de Santo António" de fevereiro a dezembro), usa o cumulativo de dezembro da designação ativa em dezembro e verifica se já inclui os meses anteriores. NUNCA somes os cumulativos das duas designações.
   • NÃO calcules o valor anual somando as colunas mensais: têm erros conhecidos (valores negativos, meses a 0 com o cumulativo parado, meses em falta). Usa as colunas mensais só para detetar anomalias.
   • Meses em falta (ex.: A23 abril de 2023, A29 abril de 2016): o cumulativo de dezembro já os inclui; assinala-os.
   • Remove espaços no início/fim dos textos (ex.: " EPE" e "EPE" são o mesmo setor).
   • Lê as notas da coluna sem nome (ex.: "Não existe janeiro", "Cálculo manual a ter em atenção", "Dados esquisitos") e lista-as numa tabela.
4. Aplica as regras R1–R20 e calcula a taxa de CS por unidade-ano.
5. Interrupções de serviço: há unidade-anos com quebras fortes de atividade que parecem reais (encerramentos temporários ou transferência de partos entre unidades), por exemplo A07 em 2023 (sem partos de junho a outubro), A25 em 2023–2024 (quase sem partos de agosto de 2023 a agosto de 2024), A17 em 2025 (forte quebra a partir de agosto), e subidas nas unidades que receberam esses partos (ex.: A02 e A03 em 2023). Identifica TODOS os casos destes a partir dos dados mensais, apresenta-os numa tabela e MANTÉM-NOS na análise, assinalados. Apresenta as estatísticas por ano com e sem estas unidade-anos, para mostrar se mudam as conclusões.
6. Apresenta:
   a) Tabela larga: taxa de CS por unidade (linhas) e ano (colunas), 2013–2026, com 2026 assinalado como jan–abr.
   b) Estatísticas de variabilidade por ano (ver "Métodos de referência").
   c) Gráfico de linhas com faixa: média, taxa global, mínimo e máximo por ano.
   d) Gráfico de linhas da dispersão ao longo do tempo: coeficiente de variação e intervalo interquartil por ano (a variabilidade entre unidades está a aumentar, a diminuir ou estável?).
   e) Gráfico de linhas por unidade: a taxa de CS de cada unidade em todos os anos, em painéis pequenos (um painel por unidade, todos com a mesma escala, ordenados por código).
7. Coerência com as fontes nacionais (quando eu enviar os ficheiros PORDATA, nesta fase ou na fase de contexto), ano a ano:
   (i) total de partos das 37 unidades vs. "Partos nos hospitais do SNS" da PORDATA (linha "Continente" do ficheiro municipal "saúde-SNS" e série "SNS: partos em estabelecimentos de saúde – Continente"): devem coincidir;
   (ii) taxa de CS calculada vs. taxa de CS dos hospitais públicos e PPP da PORDATA (cesarianas ÷ total de partos públicos e PPP). Atenção: esta série PORDATA tem âmbito "Portugal" (inclui as regiões autónomas), por isso a comparação é apenas aproximada; diz-o.
   Apresenta as diferenças e comenta se são aceitáveis.
8. Faz a análise principal (2013–2025) e a complementar (2013–2026) e indica as diferenças.
9. Não analises ainda nível, setor nem região, apenas confirma que estão disponíveis e com que cobertura.
Segue o formato obrigatório.
```

---

## FASE 1B — Taxas de cesariana: distribuição, unidades atípicas e variação ano a ano

```
FASE 1B — Taxa de cesariana, parte B. Sem ficheiro novo: usa os dados da Fase 1A.

1. Boxplot da distribuição das taxas por ano.
2. Funnel plot para o último ano completo (2025) e para o período 2013–2025 agregado.
3. Heatmap das taxas (unidade × ano), com as unidades ordenadas pela taxa média.
4. Variação de ano para ano:
   (i) gráfico de combinação com a variação anual da taxa global em barras, em pontos percentuais, face ao ano anterior (2014 vs. 2013, 2015 vs. 2014, …, 2025 vs. 2024), e, por cima de cada barra, um ponto por unidade com a variação dessa unidade nesse ano;
   (ii) heatmap das variações anuais (unidade × ano, azul = descida, vermelho = subida, cinzento = variação inferior a 0,5 p.p.);
   (iii) tabela larga com a variação anual de cada unidade face ao ano anterior e, por ano, quantas unidades subiram, desceram ou ficaram estáveis (variação inferior a 0,5 p.p.).
   Não compares apenas o primeiro com o último ano.
5. Unidades consistentemente acima ou abaixo da taxa global (acima/abaixo em ≥75% dos anos), e unidades fora dos limites do funnel plot em vários anos.
6. Mudanças bruscas (variação anual de uma unidade superior a 5 p.p.): lista-as para que eu possa verificar se há explicação (mudança de nível, reorganização, erro de registo).
Segue o formato obrigatório.
```

---

## FASE 2 — Nível hospitalar

```
FASE 2 — Nível hospitalar. [Anexa o Excel com o nível, se estiver num ficheiro separado; senão, usa os dados da Fase 1A.]

Expectativa a verificar empiricamente (por comparação descritiva, sem testes de hipóteses): a taxa de CS aumenta com o nível hospitalar (I < II < III). Aplica a regra R9: A17 e A32 (Ib, subtipo do nível I) no nível I; A23 num grupo à parte "I/II (indeterminado)", com a verificação de sensibilidade nos dois níveis.
1. Distribuição das unidades por nível, ano a ano, e unidades que mudaram de nível.
2. Estatísticas de variabilidade da taxa de CS por nível e por ano.
3. A ordem esperada (I < II < III) verifica-se nas medianas? Em quantos anos? Há sobreposição entre níveis (ex.: unidades de nível inferior com taxas acima de unidades de nível superior)?
4. Variabilidade DENTRO de cada nível (CV e amplitude intra-nível) vs. variabilidade total: depois de controlar o nível, quanto da dispersão se mantém?
5. Gráficos: boxplot por nível; evolução da taxa média por nível; funnel plot colorido por nível.
6. Conclusão explícita: o padrão esperado verifica-se, verifica-se parcialmente ou não se verifica nos dados?
Segue o formato obrigatório.
```

---

## FASES 3 em diante — Modelo para cada nova variável

Copia este bloco uma vez por variável. Ordem sugerida: **3** Setor EPE/PPP → **4** Região → **5** Volume de partos da unidade (sem ficheiro novo; usa o SNS Transparência) → **6** Médicos especialistas em GO → **7** Taxa de ocupação → **8** Médicos e enfermeiros (municipal) → **9** Indicadores de contexto (inclui a verificação dos partos SNS da PORDATA).

```
FASE [N] — [NOME DA VARIÁVEL]. Tipo: [exploratória / contexto]. Nível geográfico: [unidade / município / região / nacional]. Em anexo: [nome do Excel].

1. Descreve o ficheiro (anos disponíveis, nível geográfico, unidades de medida) e diz-me se concordas em usar todos os anos disponíveis (R8). Se não concordares, explica porquê e espera pela minha decisão antes de continuar.
2. Liga a variável aos dados anteriores com os ficheiros de correspondência (R5–R7, mudanças de ULS de 2024, nota de Ovar).
3. Se for uma contagem que dependa da dimensão da população, calcula também uma versão relativa adequada (ex.: por 1000 partos ou por 10 000 mulheres em idade fértil) e explica a escolha.
4. Análise:
   • Categórica: estatísticas por categoria e variabilidade dentro de cada categoria vs. total (ver "Métodos de referência"). Gráficos: boxplot por categoria (com um ponto por unidade), evolução anual da mediana por categoria (gráfico de linhas) e funnel plot colorido por categoria.
   • Contínua: gráfico de dispersão (sobre as médias do período, com o código de cada unidade) e rho de Spearman descritivo, ano a ano e sobre as médias do período; gráfico de linhas com o rho de cada ano, para ver se a relação é estável no tempo.
   • Contexto: apenas descrição e evolução; não relacionar como preditor.
5. Corre com e sem os municípios com mais do que uma ULS (R6), quando se aplique.
6. Relação com as fases anteriores: a associação mantém-se dentro do mesmo nível hospitalar? As unidades atípicas identificadas antes continuam atípicas?
Segue o formato obrigatório.

[Notas específicas, preencher se aplicável:]
- Setor: classificação ano a ano; assinala as unidades que passaram de PPP a EPE e compara a taxa antes/depois da mudança nessas unidades.
- Região: analisa com as 7 regiões e, como verificação de robustez, com as 5 ARS (Norte, Centro, LVT = Oeste e Vale do Tejo + Grande Lisboa + Península de Setúbal, Alentejo, Algarve). Assinala o Algarve (1 unidade).
- Volume de partos: n.º de partos anual da própria unidade (SNS Transparência), relacionado com a taxa de CS por gráfico de dispersão e por classes de volume. Não confundir com o funnel plot, que já usa o volume como referência.
- Taxa de ocupação: é uma percentagem, por isso não somes; o valor 0 significa "sem dados" (R1). Propõe o método de agregação (R7) antes de calcular (ex.: município sede do hospital da unidade).
- Médicos de GO: dados por local de residência do médico e incluem médicos do setor privado (R14); calcula também por 1000 partos da unidade.
```

---

## FASE SÍNTESE — O que fica por explicar

```
FASE SÍNTESE — Exclusão sucessiva.

Com base em TODAS as fases anteriores (sem dados novos):
1. Tabela-resumo: para cada variável, o tipo, o período, o padrão observado (com a consistência ao longo dos anos), a dispersão que se mantém dentro dos grupos e a conclusão (padrão claro / padrão fraco ou inconsistente / sem padrão).
2. Que parte da variabilidade NÃO é explicada pelos fatores analisados: unidades que continuam atípicas depois de considerar o nível, o setor e a região, e a dimensão da dispersão residual dentro de grupos comparáveis.
3. Hipóteses para a variabilidade residual: distingue claramente (a) explicações já descritas na literatura e (b) hipóteses novas sugeridas pelos dados. Marca todas como HIPÓTESES, não como conclusões.
4. Limitações (dados agregados, n pequeno, períodos diferentes entre variáveis, mudanças de ULS, municípios partilhados).
5. No fim, envia UM ficheiro Excel com tudo junto: uma folha por fase com os dados e as tabelas de dados dos gráficos, uma folha com a base de dados harmonizada unidade-ano, uma folha com os excluídos e uma com o registo de decisões.
Formato: português simples + versão em inglês para a tese + perguntas prováveis do júri + pontos para decidir. PARA.
```

---

## FASE VALIDAÇÃO FINAL

```
FASE VALIDAÇÃO FINAL — Volta a correr tudo de raiz. (Para usar numa conversa nova, depois do Bloco 0.) Em anexo: todos os ficheiros originais, os ficheiros de correspondência e o Excel final da análise.

1. Carrega os ficheiros originais e repete todos os cálculos desde o início, aplicando o Bloco 0, sem usar os valores do Excel final. Só depois compara os teus resultados com os do Excel final.
2. Verifica e apresenta numa tabela (Verificado / Diferença encontrada):
   • N.º de unidades e de anos por fase (sem as unidades que não realizam partos); exclusões aplicadas (R1–R20) e coerência das tabelas de excluídos.
   • Exclusão da Madeira e dos Açores em todos os ficheiros.
   • Harmonização A01–A40, mudanças de ULS de 2024, Ovar, municípios partilhados.
   • Totais (partos, cesarianas, taxa global por ano) iguais entre fases.
   • Todos os valores das tabelas de dados dos gráficos iguais aos recalculados.
   • Medidas descritivas (medianas, amplitudes, rho de Spearman) reproduzidas.
   • Conclusões (PT e EN) coerentes com os números; nenhuma afirmação causal.
3. Lista qualquer discrepância, a causa e a correção. Não alteres conclusões sem me mostrares a diferença.
4. Apresenta a tabela completa do registo de decisões (R18), a partir da folha do Excel final.
5. Resumo final: o que está validado e o que fica "a definir".
6. Se encontrares e corrigires diferenças, envia uma versão corrigida do Excel final e indica as células alteradas.
```

---

## FASE MEDIDAS GOVERNAMENTAIS (mais tarde, numa etapa separada)

Esta fase só é usada quando tiveres o texto das medidas. Não precisa dos Excel originais: compara os **resultados finais** (o Excel da validação final, ou as tabelas finais) com as medidas.

```
FASE MEDIDAS GOVERNAMENTAIS. Em anexo: (1) texto com as medidas governamentais, cada uma com o ano de implementação e uma breve descrição; (2) os resultados finais da análise (Excel final ou tabelas finais).

Usa APENAS estes resultados finais; não recalcules a análise anterior.
Para cada medida:
1. Resume a medida numa linha (ano, âmbito: todas as unidades ou só algumas).
2. Compara a taxa de CS (global e, se útil, por unidade ou grupo) antes e depois do ano de implementação, considerando esse ano como ano de transição.
3. Tem em conta a tendência que já existia: uma descida que já vinha de trás não é atribuída à medida. Compara, de forma descritiva, a variação média anual da taxa antes e depois da medida (se a descida acelerou, abrandou ou se manteve).
4. Se a medida só se aplicou a algumas unidades, compara as abrangidas com as não abrangidas.
5. Medidas próximas no tempo: assinala que os efeitos não são separáveis.
6. Classifica: "redução compatível com a medida", "sem redução observável" ou "inconclusivo". Nunca afirmes causalidade.
7. Gráfico: taxa global por ano com a indicação dos anos das medidas, mais a tabela de dados do gráfico.
Formato: tabela-resumo das medidas, conclusão em português muito sucinta e conclusão em inglês para a tese. Se a pandemia (2020–2021) for relevante para interpretar alguma medida, refere-o apenas na conclusão.
```
