# Guia Editorial Consolidado — Artigo TCC (E6.3)

**Versão:** 1.0 — 07/11/2026  
**Fonte da auditoria:** `docs/E6_3_AUDITORIA_ARTIGO.md` (subseções 20.1 a 20.7 e seção 21)  
**Artigo original:** `docs/Modelo_Artigo_Tcc_Final 2026.md` (não modificado por este guia)  
**Pacote de referência:** `tcc_final_product.zip` — SHA-256 `F00E5DB7F445F276574CBB0185BC87BCE2D347DB078B5F74091C9060F8BE6378` (315 entradas)

---

## 1. Orientações gerais

### 1.1 O que preservar
- Contexto sobre crescimento da geração distribuída no Brasil/Nordeste e justificativa do dimensionamento fotovoltaico residencial.
- Referência à Lei nº 14.300/2022 e potencial solar do Nordeste.
- João Pessoa como cidade de referência (série mensal de irradiância disponível).
- Uso de Algoritmo Genético implementado manualmente em Python, sem bibliotecas especializadas de computação evolutiva.
- Estrutura geral do artigo em seções (introdução, metodologia, fundamentação, desenvolvimento computacional, resultados e discussões).
- Avaliação de três cenários de consumo (baixo, médio, alto).
- Motivação de desenvolver uma aplicação auxiliar de dimensionamento.

### 1.2 O que NÃO afirmar
- Que o AG "supera" métodos tradicionais/exatos (os experimentos não demonstram superioridade; métodos determinísticos apresentaram tempos menores).
- Que existe otimização multiobjetiva ou função fitness escalar `Eg − Ct`.
- Que existem múltiplas variáveis de decisão (inclinação, orientação, inversor, sombreamento); a única variável de decisão é `N` (quantidade inteira de módulos).
- Que a irradiância é medida real; usar "dados simulados (mock)".
- Que há cálculo de payback/ROI (não implementado).
- Que o produto é um sistema comercial completo de dimensionamento fotovoltaico.
- Que os 7 módulos da Tabela 1 (simulação preliminar) fazem parte dos 180 experimentos oficiais.

### 1.3 Regras de interpretação a manter
- **180 experimentos** são resultados científicos (AG × 3 cenários × 2 configurações × 30 sementes).
- **208/208 testes aprovados** são evidência de validação de software (contexto distinto dos experimentos científicos).
- Não há alegação de superioridade do AG sobre métodos exatos.
- Não há validação com instalações fotovoltaicas reais.
- A única variável de decisão é `N`.
- Parâmetros como irradiação, eficiência, área e orçamento são entradas fixas/restrições, não genes.

---

## 2. Correções por seção

### 2.1 Resumo e Abstract (linhas 9–19 do artigo)
- Substituir o Resumo por versão que contenha, em ordem:
  1. contexto e problema;
  2. objetivo de **minimizar o custo estimado de aquisição e instalação dos módulos**, sujeito à cobertura energética mensal, à área útil e ao orçamento opcional;
  3. **uma única variável de decisão inteira: N**;
  4. declaração de **dados simulados** (série mensal para João Pessoa; médias anuais para as demais cidades);
  5. comparação **AG × analítico × exaustivo**;
  6. **180 execuções** e taxa de ótimo de **100 %**;
  7. ressalva de que **não há demonstração de superioridade** do AG;
  8. arquitetura **FastAPI + React/Vite**, com Streamlit como protótipo legado.
- Traduzir o Resumo corrigido para o Abstract em inglês, mantendo os mesmos fatos e a mesma ressalva.
- **Prioridade:** obrigatória.

### 2.2 Seção 1.1 — Contexto e Justificativa (linhas 23–30)
- Preservar os dois primeiros parágrafos.
- Qualificar a descrição de "alta complexidade": o problema geral envolve muitas variáveis, mas o recorte implementado é unidimensional (apenas `N`).
- Substituir a afirmação de superioridade do AG por descrição de comparação com solução analítica e busca exaustiva.
- Declarar que a irradiância é simulada e que apenas João Pessoa possui série mensal; as demais cidades usam média anual.
- **Prioridade:** obrigatória.

### 2.3 Seção 1.2 — Objetivo Geral (linhas 32–34)
- Substituir o objetivo que menciona "maximizar a diferença entre energia gerada e custo total" (`Eg − Ct`).
- Adotar: "determinar a quantidade de módulos fotovoltaicos que minimiza o custo estimado de aquisição e instalação dos módulos, sujeita ao atendimento do consumo mensal da residência em todos os meses, à área útil do telhado e, quando informado, ao orçamento máximo, avaliando três cenários de consumo residencial (baixo, médio e alto) e comparando o AG com solução analítica e busca exaustiva."
- **Prioridade:** obrigatória.

### 2.4 Seção 1.3 — Objetivos Específicos (linhas 36–42)
- Substituir os cinco objetivos por:
  1. Modelar o problema como minimização do custo estimado, sujeito à cobertura do consumo mensal em todos os meses, área útil do telhado e orçamento opcional, com `N` como variável inteira.
  2. Implementar manualmente o AG em Python, com comparação lexicográfica *feasibility‑first*, sem bibliotecas especializadas.
  3. Organizar e documentar os dados simulados de irradiância (série mensal João Pessoa; médias anuais demais cidades), declarando limitação de generalização.
  4. Simular três cenários (150, 300, 500 kWh/mês) e duas configurações de AG (`pop10/gens20` e `pop20/gens40`), com 30 sementes por configuração.
  5. Comparar AG com solução analítica e busca exaustiva (módulos, custo, cobertura energética, tempo); não há análise de payback.
- **Prioridade:** obrigatória.

### 2.5 Seção 1.4 — Estrutura do artigo (linhas 44–46)
- **Opção recomendada:** criar a Seção 6 — Considerações Finais e manter a afirmação de seis seções.
- **Alternativa:** alterar o texto para "cinco seções" e remover a menção à Seção 6 (menos adequada para um TCC).
- Revisar a descrição da Seção 5 para mencionar os resultados consolidados (180 execuções), não apenas "resultados obtidos".
- **Prioridade:** obrigatória.

### 2.6 Seção 2 — Metodologia (subseções 2.1–2.3)
- Esclarecer que os dados de irradiância são simulados (mock), não medições reais.
- Registrar que payback e ROI não foram calculados.
- Descrever os procedimentos efetivamente executados (180 execuções, 2 configurações × 3 cenários × 30 sementes).
- **Prioridade:** obrigatória.

### 2.7 Seção 3 — Fundamentação Teórica (3.1–3.4)
- **3.1:** Corrigir "irradiância … kWh/m²/dia" para "irradiação solar média diária" ou "horas de sol pleno (HSP)". Reescrever objetivo para minimização de custo sujeita a restrições. Inserir parágrafo sobre simplificação unidimensional.
- **3.2:** Ajustar fórmula com nota de consistência de unidades. Acrescentar parágrafo sobre não inclusão de inversor e layout. Registrar que payback/ROI não foram avaliados. Incluir tabela de parâmetros de entrada (painel 550 Wp, área 2,2 m², eficiência 0,82, custo R$ 1.100 + R$ 250).
- **3.3:** Substituir "função de aptidão" por "regra de seleção baseada em comparação lexicográfica *feasibility‑first*". Esclarecer variável única `N`. Delimitar os 100 % de sucesso aos 180 experimentos realizados. Referenciar `compare_lexicographic` e `EvaluationResult` (`src/simulation/evaluation.py`).
- **3.4:** Conferir e ajustar cada referência (veja seção 6 deste guia). Reescrever conclusão geral para evitar alegação absoluta de superioridade. Corrigir frase sobre base de irradiância para dados simulados.
- **Prioridade:** obrigatória para todas as subseções.

### 2.8 Seção 4 — Desenvolvimento Computacional (4.1–4.5)
- **4.1:** Substituir o objetivo duplo ("maximizar geração e minimizar custo") pela minimização de custo sujeita a restrições. Trocar a Equação 1 por \(E_m(N)=N\cdot\frac{P_{\text{módulo}}}{1000}\cdot HSP_m\cdot30\cdot\eta\). Remover fitness escalar `Eg − Ct`. Explicitar `N` como única variável de decisão.
- **4.2:** Descrever o **AG v2** com comparação lexicográfica. Citar `tournament_selection_lexicographic`, `_select_elites` e `_cmp_lexicographic`. Registrar que a versão v1 (fitness escalar) **não** foi usada nos resultados publicados.
- **4.3:** Explicitar que o cromossomo é **um único gene inteiro N** (quantidade de módulos); demais parâmetros são entradas fixas, não genes.
- **4.4:** Substituir parâmetros 100/200/80 %/5 % pelos valores experimentais: população 10/20, gerações 20/40, crossover 80 %, mutação 20 %, elitismo 2. Registrar que os defaults do `GAConfig` (50/100/0,1) **não** foram usados.
- **4.5:** Atualizar o fluxograma: remover "função fitness"; incluir avaliação por comparação lexicográfica, restrição de área/orçamento, elitismo e reavaliação a cada geração.
- **Prioridade:** obrigatória para todas as subseções.

### 2.9 Seção 5 — Resultados e Discussões (5.1–5.5)
- **5.1:** Substituir "Streamlit" por FastAPI (backend) + React/Vite (frontend). Explicar que a interface envia parâmetros ao backend via API e recebe a solução. Evitar atribuir cálculos à interface. Preservar descrição de entrada de dados, cálculo de área útil e execução da otimização.
- **5.2:** Remover referência a fitness escalar. Descrever AG v2 e avaliação lexicográfica. Esclarecer representação de `N`. Reformular objetivo para minimização de custo com restrições. Mencionar que v1 não foi usada nos resultados.
- **5.3:** Esclarecer que a Tabela 1 refere-se a simulação preliminar, distinta dos experimentos E5.4. Apresentar os três cenários oficiais (150/300/500 kWh → 3/5/8 módulos). Mencionar 180 execuções e taxa 180/180 (100 %). Incluir tabela dos cenários e gráficos comparativos de tempo.
- **5.4:** Atualizar descrição tecnológica para FastAPI + React/Vite. Explicar comunicação frontend-backend. Descrever apenas funcionalidades implementadas (DashboardForm, DashboardPage, MetricCards, AnalysisPage, rotas `/health`, `/cities`, `/panels`, `/optimize`, `/baseline`, `/compare`, `/experiments/*`).
- **5.5:** Atualizar estado de desenvolvimento (produto encerrado na E6.2). Corrigir descrição da função de avaliação (lexicográfica, não fitness escalar). Incorporar resultados oficiais (cenários, 180 execuções, 180/180). Registrar limitações científicas. Atualizar trabalhos futuros. Evitar afirmações de superioridade geral do AG.
- **Prioridade:** obrigatória para todas as subseções.

### 2.10 Seção 6 — Conclusões (a criar)
- Criar a seção no corpo do artigo (não existe atualmente; só é mencionada no sumário).
- Sintetizar: produto tecnicamente encerrado, modelo E5.2, 180 execuções, taxa 180/180, três cenários oficiais, AG v2 com comparação lexicográfica, comparação de tempos sem alegar superioridade.
- Listar limitações científicas (irradiância simulada, única variável `N`, custo simplificado R$ 1.350 por módulo, eficiência 0,82, fator de área 0,85, sem validação real).
- Apresentar contribuições do trabalho e trabalhos futuros.
- Manter distinção entre conclusões do produto técnico e conclusões científicas.
- **Prioridade:** obrigatória.

---

## 3. Seção 6 — Considerações Finais (conteúdo a desenvolver)

O colega deverá redigir uma seção de conclusão que inclua, no mínimo:

1. **Estado do produto:** desenvolvimento computacional encerrado tecnicamente; aplicação composta por backend FastAPI, frontend React/Vite e módulo de otimização AG v2.
2. **Modelo adotado:** E5.2 — minimização de custo sujeita a restrições de cobertura energética mensal, área útil e orçamento opcional; variável única `N`.
3. **Resultados experimentais:** 180 execuções (3 cenários × 2 configurações × 30 sementes); taxa de obtenção do ótimo determinístico de 180/180 (100 %); quantidades ótimas: 3 (150 kWh), 5 (300 kWh) e 8 (500 kWh) módulos; tempos médios do AG (pop10/gen20 ≈ 5–7 ms; pop20/gen40 ≈ 22–24 ms) **maiores** que os dos métodos determinísticos (analítico ≈ 0,04–0,67 ms; exaustiva ≈ 0,4–2,8 ms).
4. **Limitações:** irradiância simulada/mock (série mensal apenas para João Pessoa); única variável de decisão; custo simplificado; eficiência 0,82; fator de aproveitamento 0,85; resultados restritos aos cenários testados; ausência de validação em instalações reais.
5. **Contribuições:** aplicação computacional funcional para dimensionamento residencial simplificado, baseado em AG v2 com comparação lexicográfica *feasibility‑first*.
6. **Trabalhos futuros:** séries históricas reais de irradiação; mais localidades e cenários; modelo de custos mais completo; variáveis adicionais de dimensionamento; outras estratégias de otimização; validação com instalações reais.

---

## 4. Figuras e tabelas recomendadas

| Figura/Tabela | Onde inserir | O que deve demonstrar | Fonte/evidência |
|---|---|---|---|
| Tabela dos três cenários oficiais | Seção 5.3 | Consumo, quantidade ótima (3/5/8), custo estimado | `results/e5_4_6/summary.json` |
| Gráfico de tempos médios | Seção 5.3 | AG pop10/gen20, AG pop20/gen40, analítico, exaustiva | `results/e5_4_6/summary.json` |
| Captura da Tabela 1 (simulação preliminar) | Seção 5.3 (com nota explicativa) | Exemplo inicial, não parte dos 180 experimentos | imagem `image2` do artigo |
| Captura real da interface principal | Seção 5.4 | Tela de configuração com campos de entrada | `frontend/src/components/DashboardForm.tsx` |
| Diagrama de arquitetura | Seção 5.4 | React/Vite ↔ FastAPI ↔ módulo de otimização | `backend/routes.py`, `frontend/src` |
| Captura dos resultados (gráficos) | Seção 5.4 | Evolução das soluções ao longo das gerações (o produto expõe histórico de gerações; verificar o rótulo exibido — não descrever como fitness escalar), geração × consumo, balanço energético, ocupação do telhado | `frontend/src/components/DashboardPage.tsx`, `AnalysisPage.tsx` |
| Tabela de parâmetros do AG | Seção 4.4 | População 10/20, gerações 20/40, crossover 80 %, mutação 20 %, elitismo 2 | `scripts/e5_4_6_consolidacao.py` |
| Fluxograma do AG v2 | Seção 4.5 | Entrada → restrições → população → avaliação lexicográfica → seleção/torneio → operadores → parada | `src/genetic/algorithm.py` |

**Regra geral:** utilizar apenas capturas reais do produto e diagramas próprios; não utilizar imagens ilustrativas de outras aplicações.

---

## 5. Resultados experimentais: dados oficiais, interpretações permitidas e limitações

### 5.1 Dados oficiais (conferir em `results/e5_4_6/summary.json`; tempos mostrados abaixo em **milissegundos**, convertidos dos segundos registrados no JSON)

| Cenário | Consumo | Configuração AG | Módulos ótimos | Taxa de ótimo | Tempo médio AG | Tempo analítico | Tempo exaustivo |
|---|---|---|---|---|---|---|---|
| Baixo | 150 kWh | pop10/gen20 | 3 | 100 % | ~5 ms | ~0,15 ms | ~0,9 ms |
| Baixo | 150 kWh | pop20/gen40 | 3 | 100 % | ~23 ms | ~0,05 ms | ~0,5 ms |
| Médio | 300 kWh | pop10/gen20 | 5 | 100 % | ~6 ms | ~0,04 ms | ~0,4 ms |
| Médio | 300 kWh | pop20/gen40 | 5 | 100 % | ~22 ms | ~0,06 ms | ~0,7 ms |
| Alto | 500 kWh | pop10/gen20 | 8 | 100 % | ~7 ms | ~0,67 ms | ~2,8 ms |
| Alto | 500 kWh | pop20/gen40 | 8 | 100 % | ~24 ms | ~0,11 ms | ~0,7 ms |

### 5.2 Interpretações permitidas
- O AG encontrou o ótimo determinístico em 100 % das execuções nos cenários testados.
- Os métodos determinísticos (analítico e exaustivo) apresentaram tempos de execução menores que o AG.
- O modelo é unidimensional (variável `N`) e usa dados simulados.
- Não há demonstração de superioridade do AG sobre métodos exatos.

### 5.3 Limitações a declarar
- Irradiância simulada/mock; série mensal apenas para João Pessoa, médias anuais para as demais cidades.
- Modelo com uma única variável de decisão inteira (`N`).
- Custo simplificado de R$ 1.350,00 por módulo (R$ 1.100 + R$ 250).
- Eficiência global de 0,82; fator de aproveitamento da área de 0,85.
- Resultados restritos aos cenários e parâmetros testados.
- Ausência de validação em instalações fotovoltaicas reais.

---

## 6. Referências bibliográficas — 11 providências (subseção 20.7.8)

O responsável pela redação deverá executar, na versão final do artigo:

1. Corrigir as citações de Silva, Bezerra, Ramírez-Quiroz, Paixão e Abaide e Pereira, conforme as autorias identificadas:
   - `SILVA et al. (2023)` → `SILVA (2023)` (autora individual: Brenda Andreza Oliveira da Silva; *Meio Ambiente (Brasil)*, v. 5, n. 1, p. 55–66, 2023; DOI `10.66205/mabra.v5i1.295`).
   - `ETENE/BNB (2023)` → `BEZERRA (2023)` (*Infraestrutura: Energia Solar*, Caderno Setorial ETENE, ano 8, n. 295, julho de 2023, Banco do Nordeste).
   - `CAMARILLO-PEÑARANDA et al. (2015)` → `RAMÍREZ-QUIROZ et al. (2015)` (DOI `10.17533/udea.redin.n75a10`).
   - `PAIXÃO et al. (2025)` → `PAIXÃO e ABAIDE (2025)` (capítulo *Algoritmos Genéticos na Engenharia Elétrica*, Aurum Editora, 2025, pp. 16–24; DOI `10.63330/aurumpub.019-002`).
   - `INPE (2017)` → `PEREIRA et al. (2017)` (*Atlas brasileiro de energia solar*, 2ª ed., INPE, São José dos Campos, 2017, 80 p.; DOI `10.34024/978851700089`).
2. Corrigir títulos e dados editoriais de Wamusse (dissertação *Otimização de sistemas isolados para eletrificação rural considerando a probabilidade de perda de carga*, UFPR, 2019; `https://hdl.handle.net/1884/66850`) e Rodrigues et al. (*Matemática Aplicada no Dimensionamento de um Sistema Fotovoltaico Conectado à Rede Elétrica*, Revista FT, v. 28, n. 130, jan. 2024; DOI `10.5281/zenodo.10607610`).
3. Separar a referência à Resolução Normativa ANEEL nº 1.000/2021 da referência à Lei nº 14.300/2022 (`BRASIL, 2022`).
4. Substituir links genéricos ou indiretos (ex.: busca do Google) por endereços oficiais ou identificadores permanentes das fontes.
5. Identificar a edição específica do material da ABSOLAR utilizado.
6. Comprovar documentalmente as referências de Sorknæs (2018) e Gore (2014) antes de mantê-las; caso não localizadas, remover.
7. Decidir sobre a permanência da referência de Oliveira e Lana (2023), conforme uso efetivo no texto.
8. Padronizar as referências de Pinho e Galdino, Villalva (2ª ed., 2015, Érica), Gil (2010), Goldberg (1989), Holland (1975) e Mitchell (1998) segundo uma única norma bibliográfica.
9. Conferir a correspondência entre todas as citações do corpo do artigo e a lista final de referências.
10. Revisar as afirmações sustentadas por trabalhos de escopo diferente (ex.: Ramírez-Quiroz et al. sobre reconfiguração sob sombreamento; Wamusse sobre sistemas isolados), evitando atribuir-lhes conclusões que não demonstram.
11. Corrigir o uso de "irradiância" quando associado à unidade de energia por área por dia (usar "irradiação solar diária" ou "horas de sol pleno (HSP)").

**Cuidados adicionais:** não apresentar referências de contextualização como validação do modelo matemático ou dos resultados experimentais.

---

## 7. Checklist final (antes da entrega do artigo)

- [ ] Resumo reescrito com objetivo, variável `N`, dados mock e resultados de 180 execuções.
- [ ] Abstract em espelho ao Resumo.
- [ ] Seção 1.1 qualificada (simplificação unidimensional, sem afirmação de superioridade).
- [ ] Seção 1.2 substituída (minimização de custo com restrições).
- [ ] Seção 1.3 atualizada (cinco objetivos específicos corrigidos).
- [ ] Seção 1.4 ajustada (Seção 6 criada ou texto corrigido para cinco seções).
- [ ] Seção 2 alinhada aos dados mock e procedimentos executados.
- [ ] Seção 3 corrigida (terminologia HSP/irradiação, comparação lexicográfica, referências verificadas).
- [ ] Seção 4 atualizada (AG v2, parâmetros experimentais, fluxograma alinhado).
- [ ] Seção 5 corrigida (Stack FastAPI/React/Vite, Tabela 1 como preliminar, cenários oficiais, 180/180, interface descrita corretamente).
- [ ] Seção 5.5 atualizada (estado encerrado, limitações, trabalhos futuros, sem alegação de superioridade).
- [ ] Seção 6 criada no corpo do artigo.
- [ ] Referências bibliográficas corrigidas conforme as 11 providências.
- [ ] Verificada a distinção 180 experimentos × 208 testes aprovados.
- [ ] Nenhuma afirmação de superioridade do AG não sustentada pelos experimentos.
- [ ] Verificado que o artigo original não foi modificado diretamente por este guia (robo de edição para o colega).
- [ ] Verificado que o produto computacional permanece encerrado e preservado, sem alterações.

---

## 8. Limites e ressalvas

- Este guia não modifica o artigo original (`docs/Modelo_Artigo_Tcc_Final 2026.md`) nem o produto computacional (`tcc_final_product.zip`). É um roteiro de edição para o colega.
- A redação efetiva do artigo, incluindo a criação da Seção 6, fica sob responsabilidade do colega.
- Todas as orientações são fundamentadas nas evidências registradas na auditoria E6.3 (`docs/E6_3_AUDITORIA_ARTIGO.md`).
- Não são inventadas orientações que não estejam fundamentadas na auditoria.

---