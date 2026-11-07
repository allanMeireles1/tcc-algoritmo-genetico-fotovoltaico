# E6.3 — Auditoria do Artigo Científico (bloco inicial)

**Data:** 07/11/2026  
**Pacote de referência:** `tcc_final_product.zip` — SHA‑256 `F00E5DB7F445F276574CBB0185BC87BCE2D347DB078B5F74091C9060F8BE6378` (315 entradas)  
**Artigo auditado:** `docs/Modelo_Artigo_Tcc_Final 2026.md`  
**Regra:** o artigo original **não foi alterado**. Este documento é um roteiro de edição para o colega responsável.

---

## 0. Errata de metadados (registro)

O arquivo `docs/E6_2_ENCERRAMENTO_TECNICO.md` **dentro do ZIP autenticado** ainda registra:

- SHA‑256 antigo: `1AA97C086412F0AFAE3352AD7C2EA738CA16EDC61E80F866E4550691C26BEE77`
- Quantidade antiga: ~308 arquivos

O pacote efetivamente entregue e autenticado possui:

- SHA‑256: `F00E5DB7F445F276574CBB0185BC87BCE2D347DB078B5F74091C9060F8BE6378`
- Entradas: 315

**Providência:** a versão local do documento de encerramento já foi corrigida para os valores atuais. O ZIP autenticado permanece intacto como referência histórica; a correção entra em eventual republicação.

---

## 1. Como usar este documento

Cada bloco abaixo segue a estrutura:

| Campo | Conteúdo |
|---|---|
| **Localização** | Seção e linhas do artigo |
| **Situação atual** | O que o texto apresenta hoje |
| **Divergência** | Por que não corresponde ao produto |
| **Alteração necessária** | O que o colega deve fazer |
| **Evidência** | Arquivo e localização no projeto |
| **Material visual** | Figura/tabela recomendada |
| **Prioridade** | Obrigatória ou recomendada |

Também há indicação explícita do que **pode ser preservado**, para evitar retrabalho.

---

## 2. Resumo

**Localização:** linhas 9–13.

### Situação atual

O Resumo apresenta o contexto da geração distribuída, a justificativa do dimensionamento e a proposta de usar AG. Porém:

- afirma que o sistema “busca encontrar a configuração mais eficiente”, sem explicitar o objetivo de **minimização de custo**;
- trata dimensões do telhado, consumo, irradiância e custo como “variáveis principais”, sem distinguir **variável de decisão** de **parâmetros/restrições**;
- não menciona que o modelo implementado é **unidimensional**;
- não informa que a irradiância é **simulada (mock)**;
- não apresenta os **resultados obtidos**; usa “Espera-se que os resultados demonstrem...”;
- não menciona as **180 execuções**, a comparação com analítico/exaustivo, nem a arquitetura FastAPI + React/Vite.

### Divergência

O Resumo ainda descreve a proposta antiga (`Eg − Ct`) e um resultado futuro, enquanto o produto tem objetivo, método, dados e resultados consolidados distintos.

### Alteração necessária

Substituir o parágrafo do Resumo por uma versão que contenha, em ordem:

1. contexto e problema;
2. objetivo de **minimizar o custo estimado de aquisição e instalação dos módulos**, sujeito à cobertura energética mensal, à área útil e ao orçamento opcional;
3. **uma única variável de decisão inteira: N**;
4. declaração de **dados simulados** (série mensal para João Pessoa; médias anuais para as demais cidades);
5. comparação **AG × analítico × exaustivo**;
6. **180 execuções** (3 cenários × 2 configurações × 30 seeds) e taxa de ótimo de **100%**;
7. ressalva de que **não há demonstração de superioridade** do AG;
8. arquitetura **FastAPI + React/Vite**, com Streamlit como protótipo legado.

### Sugestão de redação

> O crescimento da geração distribuída de energia solar no Brasil, especialmente no Nordeste, torna o dimensionamento de sistemas fotovoltaicos residenciais um problema relevante. A definição manual da quantidade de painéis pode resultar em sistemas subdimensionados, superdimensionados ou economicamente inviáveis. Este trabalho desenvolve uma aplicação computacional baseada em Algoritmos Genéticos (AG) para determinar a quantidade de módulos fotovoltaicos que minimiza o custo estimado de aquisição e instalação dos módulos, sujeita ao atendimento do consumo mensal em todos os meses, à área útil do telhado e, quando informado, ao orçamento máximo. O modelo adota uma única variável de decisão inteira — a quantidade de módulos (N) — e utiliza dados simulados de irradiância: série mensal para João Pessoa e médias anuais para as demais cidades, o que limita a generalização dos resultados. O AG utiliza comparação lexicográfica *feasibility-first* e é comparado com solução analítica e busca exaustiva. Foram realizadas 180 execuções (três cenários de consumo × duas configurações × 30 seeds). O AG atingiu o ótimo do modelo em 100% das execuções; os métodos determinísticos apresentaram tempos de execução menores. A aplicação é implementada em Python, com backend FastAPI e frontend React/Vite; o protótipo original em Streamlit é mantido como legado. Os resultados indicam que o AG é viável para o problema simplificado, sem demonstrar superioridade sobre os métodos exatos.

### Evidência

- `docs/E5_2_MODELO_MATEMATICO.md`, seções 2.1, 3.1, 3.4, 6.3, 8 e 9.
- `docs/E6_1_AUDITORIA_COMPARATIVA.md`, seção 4.
- `docs/E6_2_REVISAO_CIENTIFICA.md`, seções 5 e 6.
- `results/e5_4_6/summary.json`.
- `README.md` (arquitetura FastAPI + React/Vite; Streamlit legado).

### Material visual

Nenhum. O Resumo deve permanecer em texto corrido.

### Prioridade

**Obrigatória.**

### O que preservar

- A abertura sobre o crescimento da geração distribuída e a relevância do dimensionamento.
- A menção aos riscos de subdimensionamento e superdimensionamento.
- A indicação de que o trabalho usa AG implementado manualmente em Python.

---

## 3. Abstract

**Localização:** linhas 15–19.

### Situação atual

O Abstract repete a estrutura do Resumo, incluindo:

- “The results are expected to demonstrate...”, ou seja, resultados futuros;
- ausência do objetivo de minimização de custo;
- ausência da variável única `N`;
- ausência da declaração de dados simulados;
- ausência das 180 execuções e da comparação com métodos exatos;
- ausência da arquitetura FastAPI + React/Vite.

### Divergência

A versão em inglês precisa espelhar exatamente a versão corrigida do Resumo. Hoje ela está desatualizada em objetivo, escopo e resultados.

### Alteração necessária

Traduzir a versão corrigida do Resumo, mantendo os mesmos fatos e a mesma ressalva sobre ausência de superioridade do AG.

### Sugestão de redação

> The growth of distributed solar generation in Brazil, especially in the Northeast, makes the sizing of residential photovoltaic systems a relevant problem. Manually defining the number of panels can lead to undersized, oversized, or economically unviable systems. This work develops a computational application based on Genetic Algorithms (GA) to determine the number of photovoltaic modules that minimizes the estimated acquisition and installation cost, subject to meeting monthly consumption in all months, the usable roof area, and, when provided, the maximum budget. The model adopts a single integer decision variable — the number of modules (N) — and uses simulated irradiance data: a monthly series for João Pessoa and annual averages for the other cities, which limits generalization. The GA uses lexicographic feasibility-first comparison and is compared with an analytical solution and exhaustive search. A total of 180 runs were performed (three consumption scenarios × two configurations × 30 seeds). The GA reached the model optimum in 100% of the runs; deterministic methods had lower execution times. The application is implemented in Python, with a FastAPI backend and a React/Vite frontend; the original Streamlit prototype is kept as legacy. The results indicate that the GA is viable for the simplified problem, without demonstrating superiority over exact methods.

### Evidência

A mesma do Resumo, com tradução fiel.

### Material visual

Nenhum.

### Prioridade

**Obrigatória.**

### O que preservar

- A estrutura formal de abstract.
- O vocabulário técnico já adequado (distributed generation, sizing, photovoltaic systems).
- A menção ao Nordeste e à relevância regional.

---

## 4. Seção 1.1 — Contexto e Justificativa

**Localização:** linhas 23–30.

### Situação atual

O texto apresenta corretamente o contexto regulatório e o potencial solar do Nordeste. Porém, ao descrever o problema, afirma:

- que o dimensionamento é uma “otimização combinatória de alta complexidade”;
- que existem “diversas variáveis interdependentes, como o número de painéis, a inclinação e orientação dos módulos, a capacidade do inversor...”;
- que “a combinação de todas essas variáveis gera um espaço de possibilidades vasto e não-linear”;
- que os AG “superam limitações dos métodos tradicionais”.

### Divergência

O produto implementado adota uma **simplificação unidimensional**: a única variável de decisão é `N`. Inclinação, orientação, inversor e sombreamento **não são otimizados**. Além disso:

- o espaço de busca é discreto e pequeno (`N` varia de 0 a `N_max`, tipicamente menos de 100 valores);
- a busca exaustiva encontra o ótimo global;
- os experimentos **não demonstram superioridade** do AG sobre métodos exatos.

### Alteração necessária

1. **Preservar** os dois primeiros parágrafos (contexto e justificativa).
2. **Qualificar** a descrição da complexidade: o problema geral pode envolver muitas variáveis, mas o recorte implementado é unidimensional.
3. **Substituir** a afirmação de superioridade por uma descrição de comparação: o AG é o método investigado, comparado com solução analítica e busca exaustiva.
4. **Declarar** que a irradiância é simulada e que apenas João Pessoa possui série mensal.
5. **Manter** a frase final sobre João Pessoa como cidade de referência, acrescentando a ressalva de que a extensão às demais cidades usa média anual.

### Sugestão de parágrafo substituto (para os parágrafos 3–5)

> Embora o problema geral de dimensionamento possa envolver diversas variáveis — como inclinação, orientação, capacidade do inversor, sombreamento e área útil —, este trabalho adota uma simplificação unidimensional: a variável de decisão é a quantidade de módulos fotovoltaicos (N). As demais grandezas são tratadas como entradas ou restrições. Nesse recorte, o espaço de busca é discreto e suficientemente pequeno para que a busca exaustiva seja utilizada como referência de ótimo. O AG é o método investigado e é comparado com a solução analítica e a busca exaustiva; não se assume, a priori, superioridade do AG. Os dados de irradiância são simulados (mock): João Pessoa possui série mensal; as demais cidades usam média anual, o que limita a generalização. A cidade de João Pessoa foi adotada como referência por reunir características representativas da região, e o modelo pode ser estendido a outras cidades desde que dados mensais estejam disponíveis.

### Evidência

- `docs/E5_2_MODELO_MATEMATICO.md`, seções 2.2, 3.3 e 9.
- `docs/E6_1_AUDITORIA_COMPARATIVA.md`, linhas 29–30 e 82.
- `docs/E5_4_8_REVISAO_ESCOPO.md` (escopo e limitações).
- `data/irradiance_mock.json` e `data/cities_mock.json`.

### Material visual

Nenhum. A figura de fluxograma pertence à Seção 4.5 e será tratada no bloco correspondente.

### Prioridade

**Obrigatória.**

### O que preservar

- Parágrafos sobre crescimento do mercado solar, Lei nº 14.300/2022 e potencial do Nordeste.
- A justificativa sobre riscos de dimensionamento manual.
- A referência a João Pessoa como cidade de referência.

---

## 5. Seção 1.2 — Objetivo Geral

**Localização:** linhas 32–34.

### Situação atual

> “Desenvolver uma aplicação utilizando algoritmos genéticos implementados manualmente em Python para a otimização do dimensionamento de sistemas fotovoltaicos residenciais na região Nordeste do Brasil, buscando maximizar a diferença entre a energia gerada e o custo total do sistema, avaliando três cenários de consumo residencial distintos: baixo, médio e alto consumo.”

### Divergência

O objetivo do produto é **minimizar o custo** sujeito à cobertura energética mensal, área e orçamento opcional. Não há maximização de `Eg − Ct`. Também falta mencionar a comparação com métodos de referência.

### Alteração necessária

Substituir o objetivo geral por:

> Desenvolver uma aplicação utilizando algoritmos genéticos implementados manualmente em Python para determinar a quantidade de módulos fotovoltaicos que minimiza o custo estimado de aquisição e instalação dos módulos, sujeita ao atendimento do consumo mensal da residência em todos os meses, à área útil do telhado e, quando informado, ao orçamento máximo, avaliando três cenários de consumo residencial (baixo, médio e alto) e comparando o AG com solução analítica e busca exaustiva.

### Evidência

- `docs/E5_2_MODELO_MATEMATICO.md`, seção 2.1.
- `docs/E6_1_AUDITORIA_COMPARATIVA.md`, seção 3.
- `results/e5_4_6/summary.json` (cenários 150, 300 e 500 kWh/mês).

### Material visual

Nenhum.

### Prioridade

**Obrigatória.**

### O que preservar

- A menção ao AG implementado manualmente em Python.
- A avaliação de três cenários de consumo.
- O escopo regional Nordeste/João Pessoa.

---

## 6. Seção 1.3 — Objetivos Específicos

**Localização:** linhas 36–42.

### Situação atual

Os objetivos específicos incluem:

- modelar a função de aptidão como “diferença entre energia gerada e custo total”;
- “coletar e tratar dados reais de irradiância”;
- comparar com “métodos tradicionais” e avaliar “tempo de retorno do investimento”.

### Divergência

- A função de aptidão foi substituída por **comparação lexicográfica feasibility-first**.
- Os dados de irradiância são **simulados (mock)**.
- A comparação real é **AG × analítico × exaustivo**.
- **Payback não foi calculado** no produto.

### Alteração necessária

Substituir os cinco objetivos específicos por:

1. **Modelar** o problema como minimização do custo estimado de aquisição e instalação dos módulos, sujeito à cobertura do consumo mensal em todos os meses, à área útil do telhado e, quando informado, ao orçamento máximo, tendo `N` como variável inteira.
2. **Implementar manualmente** o AG em Python, com comparação lexicográfica *feasibility-first*, sem bibliotecas especializadas de computação evolutiva.
3. **Organizar e documentar** os dados simulados de irradiância: série mensal para João Pessoa e médias anuais para as demais cidades, declarando a limitação de generalização.
4. **Simular** três cenários de consumo (150, 300 e 500 kWh/mês) e duas configurações de AG (`pop10/gens20` e `pop20/gens40`), com 30 seeds por configuração.
5. **Comparar** o AG com a solução analítica e a busca exaustiva, avaliando quantidade de módulos, custo, cobertura energética e tempo de execução; **não há análise de payback**.

### Evidência

- `docs/E5_2_MODELO_MATEMATICO.md`, seções 6.3, 7 e 8.
- `docs/E6_1_AUDITORIA_COMPARATIVA.md`, seção 4.
- `results/e5_4_6/summary.json`.

### Material visual

Nenhum.

### Prioridade

**Obrigatória.**

### O que preservar

- A ideia de implementar o AG manualmente.
- A avaliação de três cenários.
- A comparação com métodos de referência (com a correção de quais métodos são).

---

## 7. Seção 1.4 — Estrutura do artigo

**Localização:** linhas 44–46.

### Situação atual

O texto afirma:

> “O artigo está dividido em seis seções... Por fim, Seção 6 expõe as considerações finais...”

### Divergência

O arquivo termina na **Seção 5.5** e segue diretamente para as referências. **Não existe Seção 6 — Conclusões.** A estrutura declarada não corresponde ao documento.

### Alteração necessária

Duas opções:

1. **Recomendada:** criar a Seção 6 — Considerações Finais, com síntese dos resultados, limitações e trabalhos futuros, e manter a afirmação de seis seções.
2. **Alternativa:** se a Seção 6 não for criada, alterar o texto para “cinco seções” e remover a menção à Seção 6.

Como o TCC precisa de encerramento científico, a opção 1 é a mais adequada.

Também revisar a descrição da Seção 5: ela deve mencionar os resultados consolidados (180 execuções) e não apenas “resultados obtidos”.

### Evidência

- `docs/Modelo_Artigo_Tcc_Final 2026.md`: cabeçalhos confirmam seções 1–5 e referências, sem Seção 6.
- `docs/E6_2_ENCERRAMENTO_TECNICO.md` (checklist e limitações).
- `docs/E6_1_AUDITORIA_COMPARATIVA.md`, seção 5 (recomendação de conclusão).

### Material visual

Nenhum para a Seção 1.4. A futura Seção 6 pode reaproveitar tabelas de resultados já previstas para a Seção 5.

### Prioridade

**Obrigatória.**

### O que preservar

- A descrição geral das seções 1–5.
- A indicação de que a Seção 4 trata do desenvolvimento computacional.
- A indicação de que a Seção 5 apresenta resultados e discussões.

---

## 8. O que já está correto e deve ser preservado

| Item | Motivo |
|---|---|
| Contexto sobre crescimento da energia solar no Brasil e no Nordeste | Sustentado pela literatura e coerente com o trabalho. |
| Justificativa sobre riscos de sub/superdimensionamento | Coerente com o problema e com a motivação do modelo. |
| Referência à Lei nº 14.300/2022 e a dados do INPE/ABSOLAR | Base bibliográfica adequada; não depende do código. |
| Escolha de João Pessoa como cidade de referência | Coerente com a série mensal disponível em `irradiance_mock.json`. |
| Uso de AG implementado manualmente em Python | Confirmado no código (`src/genetic/*`). |
| Estrutura geral em seções (introdução, metodologia, fundamentação, desenvolvimento, resultados) | Adequada; requer apenas ajustes pontuais e inclusão da Seção 6. |

---

## 9. Próximos blocos da auditoria

**Status atual:** todas as etapas abaixo foram executadas, revisadas e concluídas durante a E6.3; a lista é mantida como registro histórico da ordem prevista para o roteiro de edição.

Ordem sugerida, seguindo o artigo:

1. **Seção 2 — Metodologia** (2.1–2.3): dados mock, ausência de payback, procedimentos realmente executados.
2. **Seção 3 — Fundamentação Teórica** (3.1–3.4): qualificar afirmações de superioridade do AG; manter a teoria clássica.
3. **Seção 4 — Desenvolvimento Computacional** (4.1–4.5): substituir a modelagem antiga pelo E5.2; atualizar parâmetros do AG; revisar fluxograma.
4. **Seção 5 — Resultados e Discussões** (5.1–5.5): substituir simulação preliminar pelos 180 experimentos; atualizar interface e considerações parciais.
5. **Seção 6 — Conclusões** (a criar): sintetizar resultados, limitações e trabalhos futuros.
6. **Referências:** conferir se as citações preservadas continuam pertinentes após a revisão.

---

## 10. Mapa de evidências para o colega

| Afirmação | Evidência principal |
|---|---|
| Objetivo é minimizar custo com restrições | `docs/E5_2_MODELO_MATEMATICO.md`, seções 2.1 e 3.4 |
| Variável de decisão única `N` | `docs/E5_2_MODELO_MATEMATICO.md`, seção 2.2 |
| Energia mensal `E_m(N)` | `docs/E5_2_MODELO_MATEMATICO.md`, seção 3.2 |
| Custo `C(N) = N × 1350` | `docs/E5_2_MODELO_MATEMATICO.md`, seção 8 |
| Comparação lexicográfica | `docs/E5_2_MODELO_MATEMATICO.md`, seção 6.3 |
| Dados mock e limitações | `docs/E5_2_MODELO_MATEMATICO.md`, seções 9 e 10 |
| 180 execuções e 100% de ótimo | `results/e5_4_6/summary.json`; `docs/E6_1_AUDITORIA_COMPARATIVA.md`, seção 4 |
| Parâmetros do AG | `docs/E6_1_AUDITORIA_COMPARATIVA.md`, linha 32 |
| Arquitetura FastAPI + React/Vite | `README.md`; `backend/`; `frontend/` |
| Ausência de payback | `docs/E6_1_AUDITORIA_COMPARATIVA.md`, linha 31 |

---

## 11. Checklist rápido para o colega

- [ ] Reescrever o Resumo com objetivo, variável `N`, dados mock e resultados de 180 execuções.
- [ ] Reescrever o Abstract em espelho ao Resumo.
- [ ] Qualificar a “alta complexidade” na Seção 1.1 e explicar a simplificação unidimensional.
- [ ] Substituir o objetivo geral da Seção 1.2.
- [ ] Atualizar os cinco objetivos específicos da Seção 1.3.
- [ ] Criar a Seção 6 ou corrigir a estrutura declarada na Seção 1.4.
- [ ] Remover qualquer afirmação de superioridade do AG não sustentada pelos experimentos.
- [ ] Declarar explicitamente que a irradiância é simulada.

**Fim do bloco inicial da auditoria E6.3.**

## 16. Seção 3 — Fundamentação Teórica

### 16.1 3.1 — Energia solar fotovoltaica

- **Localização:** linhas 86‑94 do artigo original.
- **Afirmação atual:** descreve o efeito fotovoltaico, os componentes (módulos, inversor, estruturas, medidores), a relação entre desempenho e fatores (irradiação, orientação, inclinação, temperatura, sombreamento) e o destaque ao Nordeste do Brasil (5,0‑6,5 kWh m⁻² dia⁻¹).
- **Divergência/conceito:**  
  *Terminologia*: o artigo usa “irradiância” para expressar kWh m⁻² dia⁻¹; tecnicamente “irradiação solar” ou “horas de sol pico (HSP)” é o termo adequado, pois irradiância mede potência (W m⁻²).  
  *Objetivo*: o texto afirma “visando maximizar a geração energética”, enquanto o modelo adotado **minimiza o custo de aquisição e instalação dos módulos fotovoltaicos**, sujeito ao atendimento da demanda energética e às restrições de área disponível e, quando aplicável, de orçamento. Não se trata de equilíbrio multiobjetivo entre geração e custo.  
  *Escopo simplificado*: o artigo menciona fatores como inclinação, orientação, inversor e sombreamento como variáveis a serem otimizadas; o modelo implementado considera apenas **N** (número de módulos) como variável de decisão e trata esses fatores como entradas fixas. Recomenda‑se acrescentar um parágrafo explicando que a Seção 3 trata da fundamentação geral, mas o escopo experimental do TCC limita‑se a N.
- **O que o colega deve alterar:**  
  * Corrigir “irradiância … kWh m⁻² dia⁻¹” para “irradiação solar média diária (kWh m⁻² dia⁻¹)” ou “horas de sol pico (HSP)”.  
  * Reescrever a frase final para: “O modelo adotado busca minimizar o custo de aquisição e instalação dos módulos fotovoltaicos, sujeito às restrições de atendimento da demanda energética e às limitações de área disponível e, quando aplicável, de orçamento.”  
  * Inserir um parágrafo explicativo: “O modelo computacional adotado neste trabalho simplifica o dimensionamento ao utilizar apenas a variável inteira N (quantidade de módulos); parâmetros como orientação, inclinação, sombreamento e escolha do inversor são considerados como entradas fixas e não como variáveis de otimização.”
- **Informações e resultados a incluir:** nenhuma evidência nova; apenas correções terminológicas e de escopo.
- **Figuras ou tabelas:** Nenhum.
- **Prioridade:** **Obrigatória** (para evitar equívocos de unidade e de objetivo).
- **O que preservar:** a descrição conceitual do efeito fotovoltaico, a lista de componentes do sistema e a menção ao potencial solar do Nordeste.

---

### 16.2 3.2 — Dimensionamento de sistemas fotovoltaicos

- **Localização:** linhas 96‑106.
- **Afirmação atual:** define dimensionamento como cálculo da capacidade ideal, apresenta a equação tradicional \(\text{Potência do Sistema}=\frac{\text{Consumo Mensal}}{\text{Irradiância}\times\text{Rendimento}}\), descreve a escolha do número de módulos, inversor, e critica métodos simples por não considerar restrições físicas e econômicas.
- **Divergência/conceito:**  
  *Fórmula*: a fórmula tradicional está correta conceitualmente, mas combina unidades incompatíveis se o consumo for mensal (kWh) e a irradiância diária (kWh m⁻² dia⁻¹). O modelo simplificado efetivamente implementado utiliza a equação \(E_m(N)=N\cdot(P_{\text{módulo}}/1000)\cdot HSP_m\cdot30\cdot\eta\) (E5.2, seção 3.2), em que \(P_{\text{módulo}}/1000\) converte a potência nominal em kW, \(HSP_m\) representa as horas de sol pleno por dia, \(30\) é a aproximação dos dias do mês e \(\eta\) é a eficiência global; o resultado é a energia mensal estimada em kWh. Essa equação representa o modelo simplificado adotado, e não uma fórmula universal de dimensionamento fotovoltaico.  
  *Inversor e layout*: o artigo menciona a escolha do inversor e a análise detalhada da área do telhado; o modelo real **não** inclui a seleção do inversor nem o layout detalhado – esses aspectos são fora‑de‑escopo.
  *Payback/ROI*: o texto cita “menor tempo de retorno financeiro”; os experimentos consolidados **não calculam** payback ou ROI.
- **O que o colega deve alterar:**  
  * Reescrever a fórmula, adicionando nota de consistência de unidades e indicando a equação usada no modelo.  
  * Inserir parágrafo: “A seleção do inversor e o detalhamento do layout físico do telhado não foram modelados neste trabalho; tais aspectos seriam considerados em futuras extensões.”  
  * Substituir a referência a “menor tempo de retorno” por “o estudo não avalia payback/ROI”.
- **Informações e resultados a incluir:**  
  * Tabela resumindo os parâmetros de entrada (potência do módulo 550 Wp, área do módulo 2,2 m², eficiência 0,82, custo unitário R$ 1.100 + R$ 250).  
  * Equação do modelo mensal \(E_m(N)\) (conforme E5.2).  
  * Fonte: `docs/E5_2_MODELO_MATEMATICO.md`, seções 3.2 e 8.
- **Figuras ou tabelas:** tabela de parâmetros de entrada (recomendada).
- **Prioridade:** **Obrigatória**.
- **O que preservar:** a explicação geral de como o dimensionamento tradicional converte consumo e irradiância em número de módulos, e a crítica ao método simplificado.

---

### 16.3 3.3 — Algoritmos Genéticos aplicados à otimização

- **Localização:** linhas 108‑118.
- **Afirmação atual:** descreve AG (população, cromossomo, genes, fitness, seleção, cruzamento, mutação, elitismo) e afirma que os AG “realizam buscas simultâneas em diferentes regiões do espaço de soluções”, tornando‑os “altamente eficientes para o dimensionamento fotovoltaico residencial”.
- **Divergência/conceito:**  
  *Fitness escalar vs. comparação lexicográfica*: o artigo fala de “função de aptidão”; o AG implementado **não usa** fitness escalar, mas **comparação lexicográfica *feasibility‑first*** (Seção 6.3 do E5.2).  
  *Variável única*: o texto sugere “multiplas variáveis interdependentes”; o modelo real tem **apenas N** como variável de decisão; os demais parâmetros são fixos.
  *Superioridade*: o estudo demonstra que, nos 180 experimentos realizados (3 cenários × 2 configurações × 30 sementes), o AG encontrou o ótimo determinístico em todas as execuções; porém, os métodos analíticos e exaustivos apresentaram tempos de execução menores.
- **O que o colega deve alterar:**  
  * Substituir “função de aptidão” por “regra de seleção baseada em comparação lexicográfica *feasibility‑first*”.  
  * Acrescentar parágrafo explicando que o modelo simplifica o problema a uma única variável N e que outros fatores são tratados como parâmetros fixos.  
  * Reescrever a frase de eficiência: “Nos 180 experimentos realizados (3 cenários × 2 configurações × 30 sementes), o AG encontrou o ótimo determinístico em todas as execuções; entretanto, os métodos analíticos e exaustivos apresentaram tempos de execução menores.”
- **Informações e resultados a incluir:**  
  * Referência ao `compare_lexicographic` e ao objeto `EvaluationResult` (arquivo `src/simulation/evaluation.py`).  
  * Listar os parâmetros de AG efetivamente testados (população 10/20, gerações 20/40, elitismo 2, mutação 20 %, crossover 80 %).  
  * Fonte: `docs/E5_2_MODELO_MATEMATICO.md`, seção 6.3; `docs/E6_1_AUDITORIA_COMPARATIVA.md`, linha 32.
- **Figuras ou tabelas:** fluxograma simplificado do AG (pode ser incluído na Seção 4.5, não obrigatório aqui).
- **Prioridade:** **Obrigatória**.
- **O que preservar:** a explicação conceitual de população, cromossomo, operadores genéticos – esses princípios permanecem válidos.

---

### 16.4 3.4 — Trabalhos relacionados

- **Localização:** linhas 120‑128.
- **Afirmação atual (pontos):**  
  1. PAIXÃO et al., 2025 – AG são “abordagens consolidadas”.  
  2. WAMUSSE 2019 – AG multi‑objetivo reduz área e custo, “altamente eficiente”.  
  3. CAMARILLO‑PEÑARANDA et al., 2015 – GA supera força‑bruta em reconfiguração sob sombreamento parcial.  
  4. RODRIGUES et al., 2024 – fórmulas relacionam consumo e geração.  
  5. Conclusão geral: AG são “superiores aos métodos convencionais”; carência de abordagens heurísticas para dimensionamento residencial unificado.
- **Divergência/conceito (ponto a ponto):**  
  1. PAIXÃO 2025 – a referência está em ResearchGate sem DOI público e precisa ser conferida quanto à existência, autoria, ano e conteúdo efetivamente publicado. Enquanto não confirmada, a afirmação “os AG destacam‑se como uma das abordagens mais consolidadas” não deve ser mantida como fato; recomenda‑se removê‑la ou substituí‑la por “os AG são amplamente citados na literatura de engenharia elétrica”, com a devida verificação da fonte.  
  2. WAMUSSE 2019 – dissertação de mestrado da UFPR; não foi possível obter o texto completo. **Não apresentar como resultado confirmado.** Se o documento original não for conferido, remover a afirmação específica de redução de área/custo ou substituí‑la por uma menção genérica ao estudo, sem atribuir resultados não verificados.  
  3. CAMARILLO‑PEÑARANDA 2015 – o resumo confirma desempenho superior ao método de força‑bruta para reconfiguração sob sombreamento; a afirmação pode ser mantida com a ressalva de escopo (não cobre todos os tipos de dimensionamento).  
  4. RODRIGUES 2024 – alinhado ao tema, mas deve ser mantido somente após confirmar que a publicação realmente sustenta a afirmação associada; caso contrário, ajustar ou remover a citação.  
  5. Afirmação final de superioridade geral: **excessiva**; precisa ser reformulada para “a aplicação de AG tem sido objeto de investigação ativa e apresenta resultados promissores, porém a superioridade não é universal”.  
  6. Base empírica da irradiância: o artigo diz “utilizando como base empírica os índices de irradiância solar característicos da região Nordeste”. Na prática, usa‑se **dados simulados** (série mensal para João Pessoa, médias anuais para outras cidades). **Corrigir** para “utilizando dados simulados de irradiação/HSP inspirados nos índices da região Nordeste”, assegurando que a terminologia corresponda à grandeza efetivamente usada na implementação.  
- **O que o colega deve alterar:**  
  1. PAIXÃO 2025 – conferir existência, autoria, ano e conteúdo; enquanto não confirmada, remover a menção de “abordagens mais consolidadas” ou substituí‑la por formulação genérica devidamente referenciada.  
  2. WAMUSSE 2019 – não apresentar resultados como confirmados; se não houver acesso ao documento original, remover a afirmação específica de redução de área/custo.  
  3. CAMARILLO‑PEÑARANDA 2015 – manter com nota de escopo (“reconfiguração sob sombreamento parcial”).  
  4. RODRIGUES 2024 – confirmar a sustentação da afirmação antes de manter a citação.  
  5. Reescrever a conclusão geral para evitar afirmações absolutas de superioridade.  
  6. Alterar a frase sobre a base de irradiância para refletir o uso de dados simulados, com terminologia coerente (HSP/irradiação).
- **Informações e resultados a incluir:**  
  * Verificar existência, autoria, ano e conteúdo do preprint PAIXÃO 2025; enquanto não confirmado, não usar a citação para sustentar afirmação específica.  
  * Acessar a dissertação WAMUSSE 2019 (repositório UFPR) para confirmar o conteúdo; se não houver acesso, não apresentar os resultados como confirmados.  
  * Manter a referência ao artigo de Camarillo‑Peñaranda (já verificado).  
  * Confirmar a referência RODRIGUES 2024 antes de mantê‑la.  
  * Atualizar a frase sobre a base de irradiância para dados simulados coerentes com a grandeza usada.
- **Figuras ou tabelas:** nenhuma necessária, apenas revisão de citações.
- **Prioridade:** **Obrigatória** (para garantir precisão das referências e evitar afirmações não sustentadas).
- **O que preservar:** a estrutura geral da seção e o reconhecimento de que AG são tema ativo de pesquisa.

---

## 17. Resumo das alterações obrigatórias para a Seção 3

| Subseção | Alteração obrigatória | Evidência |
|---|---|---|
| 3.1 | Corrigir “irradiância … kWh m⁻² dia⁻¹” para “irradiação solar média diária”; reescrever objetivo para a formulação oficial de minimização de custo sujeito às restrições; inserir parágrafo sobre simplificação unidimensional. | `docs/Modelo_Artigo_Tcc_Final 2026.md`, linhas 86‑94 |
| 3.2 | Ajustar fórmula com nota de unidade; acrescentar parágrafo sobre não‑inclusão do inversor/layout; registrar que payback/ROI não foram avaliados. | `docs/Modelo_Artigo_Tcc_Final 2026.md`, linhas 96‑106; `docs/E5_2_MODELO_MATEMATICO.md` |
| 3.3 | Substituir “função de aptidão” por comparação lexicográfica feasibility‑first; esclarecer variável única N; delimitar os 100 % de sucesso aos 180 experimentos realizados. | `docs/E5_2_MODELO_MATEMATICO.md`, seção 6.3; `scripts/e5_4_6_consolidacao.py` |
| 3.4 | • PAIXÃO 2025: conferir existência/autoria/ano e ajustar ou remover afirmação de “abordagens consolidadas”. <br>• WAMUSSE 2019: não apresentar como confirmado sem conferir o documento original. <br>• CAMARILLO‑PEÑARANDA 2015: manter com ressalva de escopo. <br>• RODRIGUES 2024: manter somente após confirmar sustentação. <br>• Reescrever conclusão geral para evitar alegação absoluta de superioridade. <br>• Corrigir frase sobre base de irradiância para “dados simulados”, coerente com a grandeza usada (HSP/irradiação). | Referências listadas na Bibliografia |

---

**Correções registradas na Seção 3 após revisão do orientador (ajustes aprovados):**

- 3.1 – Formulação oficial de minimização substitui a expressão “equilibrar geração e custo”; terminologia irradiância/irradiação/HSP conferida.
- 3.2 – Unidades e delimitação do modelo simplificado explicitadas; exclusões de escopo (payback, inversor, layout) mantidas.
- 3.3 – Resultado de 100% de ótimo delimitado aos 180 experimentos (3 cenários × 2 configurações × 30 sementes); comparação lexicográfica preservada, sem fitness escalar.
- 3.4 – Exigência de conferência individual das referências (PAIXÃO 2025, WAMUSSE 2019, CAMARILLO‑PEÑARANDA 2015, RODRIGUES 2024); base empírica descrita como dados simulados coerentes com a grandeza utilizada (HSP/irradiação).

**Seção 3 encerrada na auditoria E6.3 (aprovada com ajustes aplicados).**

---

# 18. Seção 4 — Desenvolvimento Computacional (auditoria concluída)

Itens a auditar, na ordem consentida:

1. 4.1 — Modelagem Matemática: validar o modelo E5.2.
2. 4.2 — Estrutura do Algoritmo Genético: conferir o funcionamento efetivo do AG.
3. 4.3 — Representação Cromossômica: verificar a representação de N.
4. 4.4 — Parâmetros do Algoritmo: separar configurações experimentais dos valores padrão.
5. 4.5 — Fluxograma do Sistema: alinhar o fluxograma à implementação atual.

(Padrão de registro por item: localização e afirmação atual; divergência/correção conceitual; orientação objetiva; evidências; figuras/tabelas; prioridade; o que preservar.)

### 18.1 4.1 — Modelagem Matemática: validar o modelo E5.2

- **Localização:** linhas 134‑170 do artigo original.
- **Afirmação atual:** propõe “encontrar configuração capaz de **maximizar a geração de energia elétrica** e, ao mesmo tempo, **minimizar o custo total** do sistema fotovoltaico”. Apresenta a Equação 1 Eg = Np × Pp × Is × N, define Ct = Np × Cp e a função fitness *Eg − Ct*; inclui restrições de área, demanda e limites de painéis.
- **Divergência/conceito:**
  1. **Objetivo oficial:** o modelo E5.2 **minimiza o custo de aquisição e instalação dos módulos**, sujeito ao atendimento da demanda energética e às restrições de área e orçamento; a geração não é objetivo, mas restrição de viabilidade.
  2. **Equação correta:** o modelo implementado utiliza a equação mensal
     \[E_m(N)=N\cdot\frac{P_{\text{módulo}}}{1000}\cdot HSP_m\cdot30\cdot\eta\]
     onde \(P_{\text{módulo}}/1000\) converte Wp em kW, \(HSP_m\) são horas de sol pleno por dia, \(30\) dias/mês e \(\eta\) a eficiência global; o resultado está em kWh/mês.
  3. **Variáveis:** a única variável de decisão do algoritmo é a quantidade inteira \(N\) de módulos; parâmetros como irradiação, eficiência e área são entradas fixas.
  4. **Fitness escalar:** a expressão *Eg − Ct* não aparece no código; a avaliação ocorre por **comparação lexicográfica *feasibility‑first*** (funções `evaluate_candidate` e `compare_lexicographic`).
- **Orientação objetiva:**
  1. Reescrever o objetivo para “minimizar o custo de aquisição e instalação dos módulos fotovoltaicos, sujeito ao atendimento da demanda energética e às restrições de área e orçamento”.
  2. Substituir a Equação 1 por \(E_m(N)\) acima, indicando claramente unidades.
  3. Remover a menção à fitness escalar *Eg − Ct* e citar a regra oficial de comparação lexicográfica (`compare_lexicographic`).
  4. Deixar explícito que a única variável de decisão é \(N\).
- **Evidências:** `docs/E5_2_MODELO_MATEMATICO.md` (Seção 3.2); código em `src/simulation/evaluation.py` (funções `evaluate_candidate`, `compare_lexicographic`).
- **Figuras/tabelas:** tabela resumindo parâmetros de entrada (potência do módulo, HSP médio, eficiência, área disponível, orçamento).
- **Prioridade:** **Obrigatória** (corrige objetivo e terminologia fundamentais).
- **Preservar:** a descrição de restrições físicas e econômicas e a motivação de usar um AG para busca.

---

### 18.2 4.2 — Estrutura do Algoritmo Genético: conferir o funcionamento efetivo do AG

- **Localização:** linhas 174‑180 do artigo original.
- **Afirmação atual:** descreve o AG como processo baseado em seleção natural, avaliação por “função fitness”, cruzamento, mutação e parada.
- **Divergência/conceito:**
  1. O repositório contém duas implementações: `run_genetic_algorithm` (v1, fitness escalar) e `run_genetic_algorithm_v2` (v2, comparação lexicográfica). Os experimentos reportados (180 execuções) utilizam **v2** (`scripts/e5_4_6_consolidacao.py`).
  2. Seleção ocorre via `tournament_selection_lexicographic`; elitismo e ordenação utilizam `_select_elites` e `_cmp_lexicographic` (lexicographic). Não há fitness escalar.
  3. Operadores de crossover e mutação são os de `src/genetic/operators.py` (crossover aritmético, mutação por deslocamento).
- **Orientação objetiva:**
  1. Alterar a descrição para mencionar **AG v2**, uso de comparação lexicográfica (`compare_lexicographic`) e ausência de fitness escalar.
  2. Incluir nota de que a versão v1 existe, mas **não** foi usada nos resultados publicados.
  3. Referenciar explicitamente as funções `tournament_selection_lexicographic`, `_select_elites`, `crossover`, `mutate`.
- **Evidências:** `src/genetic/algorithm.py` (funções `run_genetic_algorithm_v2`, `_select_elites`, `_cmp_lexicographic`); `src/genetic/selection.py`; `src/genetic/operators.py`.
- **Figuras/tabelas:** fluxograma simplificado do AG v2 (pode ser extraído de `visualization/charts.py`).
- **Prioridade:** **Obrigatória** (para alinhar a narrativa ao código efetivo).
- **Preservar:** princípios gerais de população, seleção, crossover, mutação e critério de parada.

---

### 18.3 4.3 — Representação Cromossômica: verificar a representação de N

- **Localização:** linhas 184‑190 do artigo original.
- **Afirmação atual:** “O cromossomo foi representado por um valor inteiro correspondente à quantidade de painéis solares instalados no sistema…”.
- **Divergência/conceito:** O código realmente usa **um único gene inteiro N**; todos os demais parâmetros são fixos. Não há múltiplos genes.
- **Orientação objetiva:**
  1. Substituir a frase por “A representação cromossômica adotada neste trabalho utiliza **um único gene inteiro N**, que corresponde à quantidade de módulos fotovoltaicos. Demais parâmetros (irradiação, eficiência, área, orçamento) são parâmetros de entrada e não variáveis de decisão”.
  2. Caso deseje mencionar “variáveis interdependentes”, adicionar explicação de que, no modelo implementado, apenas N varia.
- **Evidências:** `src/models/individual.py` (campo `num_panels`); `src/genetic/operators.initialize_population`.
- **Prioridade:** **Obrigatória** (evita interpretação equivocada de múltiplas variáveis).
- **Preservar:** a ideia de que o cromossomo codifica a quantidade de painéis.

---

### 18.4 4.4 — Parâmetros do algoritmo: separar configurações experimentais dos valores padrão

- **Localização:** linhas 194‑207 do artigo original.
- **Afirmação atual:** lista parâmetros padrão (população = 100, gerações = 200, crossover = 80 %, mutação = 5 %).
- **Divergência/conceito:** Nas execuções consolidadas (`scripts/e5_4_6_consolidacao.py`) foram usados **população = 10 ou 20**, **gerações = 20 ou 40**, **crossover = 80 %**, **mutação = 20 %**, **elitismo = 2**. O `GAConfig` dataclass tem valores padrão diferentes (pop = 50, gens = 100, mutação = 0.1). O artigo não deixa claro qual conjunto foi efetivamente utilizado.
- **Orientação objetiva:**
  1. Atualizar a tabela de parâmetros no artigo para refletir os valores **experimentais** (pop = 10/20, gens = 20/40, crossover = 80 %, mutação = 20 %, elitismo = 2) e mencionar que são os que alimentaram os 180 experimentos.
  2. Incluir nota que os valores padrão do `GAConfig` (pop = 50, gens = 100, mutação = 0.1) **não** foram usados nos resultados publicados.
- **Evidências:** `scripts/e5_4_6_consolidacao.py` (linhas 38‑41, 84‑89); `src/core/config.py` (valores padrão).
- **Figuras/tabelas:** tabela resumindo os parâmetros testados por configuração (pop = 10/20, gens = 20/40, etc.).
- **Prioridade:** **Obrigatória** (para evitar suposições incorretas sobre a configuração do algoritmo).
- **Preservar:** a afirmação de que os parâmetros podem ser ajustados permanece válida, agora com os ajustes explicitados.

---

### 18.5 4.5 — Fluxograma do Sistema: alinhar o fluxograma à implementação atual

- **Localização:** linhas 212‑222 do artigo original (Figura 1 e legenda).
- **Afirmação atual:** descreve fluxo genérico com “função fitness”.
- **Divergência/conceito:**
  1. O código v2 não utiliza fitness escalar; a avaliação ocorre por **comparação lexicográfica feasibility‑first** (`compare_lexicographic`).
  2. O fluxo inclui etapas específicas que não aparecem na descrição: (a) **restrição de área/orçamento** que define `max_panels` (`max_panels_by_roof`, `N_area`, `N_budget`); (b) **elitismo via `_select_elites`**; (c) **reavaliação a cada geração**; (d) **registro de histórico de gerações** (`GenerationStats`).
- **Orientação objetiva:**
  1. Atualizar a legenda da Figura 1 para: “1) Recebe dados de entrada (consumo, irradiação/HSP, características do módulo, orçamento). 2) Constrói o *Problem* com restrição de área e orçamento. 3) Gera população inicial de indivíduos (valor inteiro N). 4) Avalia cada indivíduo via `evaluate_candidate` → `EvaluationResult`. 5) Seleciona elite lexicograficamente (`_select_elites`). 6) Seleção por torneio lexicográfico (`tournament_selection_lexicographic`). 7) Operadores de crossover e mutação. 8) Reavaliação a cada geração. 9) Critério de parada (número de gerações). 10) Resultado final: melhor indivíduo segundo comparação lexicográfica.”
  2. Substituir a referência a “função fitness” por “regra de comparação lexicográfica”.
  3. Incluir no diagrama (se for recriado) ícones para as etapas de **restrição de área/orçamento** e **elitismo**.
- **Evidências:** `src/genetic/algorithm.py` (funções `run_genetic_algorithm_v2`, `_select_elites`, `_cmp_lexicographic`); `src/simulation/runner.py` (construção do `Problem`).
- **Figuras/tabelas:** atualizar a Figura 1 do artigo original; se precisar regenerar o diagrama, utilizar `visualization/charts.py` como referência.
- **Prioridade:** **Obrigatória** (para que o leitor compreenda corretamente o fluxo real do algoritmo).
- **Preservar:** a estrutura geral de “entrada → população → avaliação → seleção → operadores → parada”.

---

## 19. Resumo das alterações obrigatórias para a Seção 4

| Subseção | Alteração obrigatória | Evidência |
|---|---|---|
| 4.1 | Substituir o objetivo duplo (“maximizar geração e minimizar custo”) pela minimização de custo sujeita às restrições; trocar a Equação 1 por \(E_m(N)\); remover a fitness escalar *Eg − Ct*; explicitar \(N\) como única variável de decisão. | `docs/E5_2_MODELO_MATEMATICO.md`, Seção 3.2; `src/simulation/evaluation.py` |
| 4.2 | Descrever o **AG v2** com comparação lexicográfica; citar `tournament_selection_lexicographic`, `_select_elites` e `_cmp_lexicographic`; registrar que a versão v1 (fitness escalar) não foi usada nos resultados. | `src/genetic/algorithm.py`; `src/genetic/selection.py` |
| 4.3 | Explicitar que o cromossomo é **um único gene inteiro N** (quantidade de módulos); demais parâmetros são entradas fixas, não genes. | `src/models/individual.py`; `src/genetic/operators.py` |
| 4.4 | Substituir os parâmetros 100/200/80 %/5 % pelos valores experimentais: população 10/20, gerações 20/40, crossover 80 %, mutação 20 %, elitismo 2; registrar que os defaults do `GAConfig` (50/100/0,1) não foram usados. | `scripts/e5_4_6_consolidacao.py`; `src/core/config.py` |
| 4.5 | Atualizar o fluxograma: remover “função fitness”; incluir avaliação por comparação lexicográfica, restrição de área/orçamento, elitismo e reavaliação a cada geração. | `src/genetic/algorithm.py`; `src/simulation/runner.py` |

---

**Fim da auditoria da Seção 4.**

> **Pendência transversal:** a Seção 5 (Resultados e Discussões) ainda menciona a interface Streamlit e a versão antiga do protótipo; a auditoria da Seção 5 deverá alinhar o texto à stack atual (FastAPI + React/Vite) e ao pacote `tcc_final_product.zip`.

---

# 20. Seção 5 — Resultados e Discussões (auditoria em andamento)

### 20.1 5.1 — Desenvolvimento do Protótipo

- **Localização no artigo:** Seção 5.1, linhas 224‑230 do documento original.
- **Afirmações atuais:**
  1. O protótipo é descrito como desenvolvido em **Python com Streamlit**.
  2. A interface permite informar largura e comprimento do telhado, consumo mensal, cidade e orçamento máximo.
  3. O sistema calcula a área útil e executa o processo de otimização, identificando configuração compatível com as restrições do usuário.
- **Divergências em relação ao produto final:**
  1. **Tecnologia da interface (correção obrigatória):** o artigo descreve Streamlit, mas o produto final utiliza backend **Python com FastAPI** e frontend **React com Vite**, integrados por API. A referência ao Streamlit deve ser removida da descrição do produto final; se mencionado, apenas como histórico documentado.
  2. **Ajuste de escopo:** distinguir *dados de entrada do cenário*, *parâmetros do modelo*, *restrições efetivamente implementadas* e *elementos da interface de configuração/visualização*. Não afirmar que toda entrada é variável de otimização — a única variável de decisão continua sendo \(N\) (quantidade inteira de módulos).
- **Orientação objetiva ao colega:**
  1. Substituir a descrição tecnológica do protótipo por **Python/FastAPI (backend) e React/Vite (frontend)**.
  2. Explicar que a interface envia os parâmetros da simulação ao backend, que executa o modelo e retorna os resultados.
  3. Preservar a descrição da entrada de dados, do cálculo da área útil e da execução da otimização — sempre confirmando no produto cada funcionalidade.
  4. Esclarecer que o dimensionamento utiliza \(N\) como única variável de decisão.
  5. Evitar descrever o produto como sistema comercial completo de dimensionamento fotovoltaico.
- **Informações e evidências a incluir:**
  1. Arquitetura FastAPI + React/Vite.
  2. Separação entre frontend, backend e lógica de otimização.
  3. Integração entre interface e execução da simulação.
  4. Referência ao pacote final `tcc_final_product.zip`.
  5. Evidências já verificadas no produto: `backend/routes.py` (`/health`, `/cities`, `/panels`, `/optimize`, `/baseline`, `/compare`, `/experiments/*`); `frontend/src/components/DashboardForm.tsx` (campos de telhado, consumo, tipo de telhado, cidade, orçamento e parâmetros do AG); `src/models/roof.py` (`gross_area_m2` e `usable_area_m2`, com `DEFAULT_ROOF_USABLE_FACTOR`).
- **Figuras ou tabelas recomendadas:**
  1. Figura recomendada — Interface do produto final: captura real da tela de configuração da simulação, mostrando os parâmetros de entrada.
  2. Figura recomendada — Arquitetura do sistema: diagrama próprio mostrando React/Vite, API FastAPI e módulo de otimização.
  3. As imagens devem ser capturas/diagramas reais do produto, não ilustrativas.
- **Prioridade:**
  1. **Obrigatória:** corrigir Streamlit para FastAPI + React/Vite.
  2. **Obrigatória:** alinhar a descrição das entradas e funcionalidades ao produto final.
  3. **Recomendada:** inserir uma figura real da interface.
  4. **Recomendada:** apresentar um diagrama da arquitetura.
- **O que preservar:**
  1. Motivação de desenvolver uma aplicação para auxiliar no dimensionamento.
  2. Possibilidade de informar características do cenário residencial.
  3. Cálculo da área útil do telhado, quando aplicável.
  4. Execução automatizada do processo de otimização.
  5. Apresentação da solução ao usuário.
- **Ressalva documental:** a auditoria baseia-se no texto original e nas informações consolidadas sobre o produto; a confirmação de cada funcionalidade deve ser feita nas evidências do pacote final — componentes e campos do frontend, endpoints e modelos de entrada do FastAPI, fluxo de execução da simulação e cálculo da área útil com aplicação das restrições. Não orientar o colega a afirmar que uma funcionalidade existe apenas porque aparece no artigo antigo.
- **Parecer da 5.1:** **aprovada conceitualmente, com confirmação técnica das funcionalidades.** A principal divergência está identificada (arquitetura antiga vs. FastAPI + React/Vite); a orientação ao colega está definida; **não é necessário modificar o produto nem recuperar o Streamlit**.

---

### 20.2 5.2 — Implementação do Algoritmo Genético

- **Localização no artigo:** Seção 5.2, linhas 232‑237 do documento original.
- **Afirmações atuais:**
  1. Foram utilizados operadores clássicos de AG: população inicial, seleção por torneio, crossover, mutação e elitismo.
  2. Cada indivíduo representa uma configuração do sistema, codificado pela quantidade de painéis instalados.
  3. A avaliação utiliza uma função de aptidão (fitness) que considera energia gerada, custo, limitações físicas e déficits energéticos.
  4. O algoritmo busca melhorar o equilíbrio entre desempenho energético e viabilidade econômica.
- **Divergências identificadas:**
  1. **Função de aptidão escalar:** o texto indica uso de fitness escalar, porém os experimentos empregam **AG v2** com avaliação por **comparação lexicográfica *feasibility‑first*** (ver `src/simulation/evaluation.py`).
  2. **Critério de seleção:** o artigo menciona “seleção por torneio” sem especificar que a implementação utiliza `tournament_selection_lexicographic` (lexicográfico).
  3. **Representação dos indivíduos:** a descrição não deixa claro que o indivíduo contém **um único gene inteiro \(N\)** – a quantidade de módulos – e que nenhum outro parâmetro é variável.
  4. **Objetivo do algoritmo:** a frase “melhor equilíbrio entre desempenho energético e viabilidade econômica” sugere otimização multi‑objetivo. Na realidade o algoritmo **minimiza o custo** sujeito a restrições de demanda, área e orçamento, usando a regra de comparação lexicográfica para ordenar soluções viáveis e inviáveis.
- **Orientação objetiva ao colega:**
  1. Manter a explicação dos operadores genéticos (população, seleção, crossover, mutação, elitismo).
  2. Identificar explicitamente que a versão utilizada nos experimentos é **AG v2**, conforme `src/genetic/algorithm.py`.
  3. Substituir “função de aptidão (fitness)” por **avaliação baseada em comparação lexicográfica feasibility‑first** (citar `evaluate_candidate` e `compare_lexicographic`).
  4. Especificar que a seleção é feita por **torneio lexicográfico** (`tournament_selection_lexicographic`).
  5. Deixar claro que cada indivíduo possui **um único gene inteiro \(N\)** que representa a quantidade de módulos.
  6. Reformular o objetivo para “encontrar a configuração de menor custo que satisfaça todas as restrições (energia, área, orçamento)”, evitando a impressão de otimização multi‑objetivo.
  7. Mencionar que a versão v1 baseada em fitness escalar **não foi utilizada** nos resultados publicados.
- **Evidências técnicas a incluir:**
  1. `src/genetic/algorithm.py` (implementação do AG v2, `_select_elites`, `_cmp_lexicographic`).
  2. `src/genetic/selection.py` (`tournament_selection_lexicographic`).
  3. `src/simulation/evaluation.py` (avaliação lexicográfica, `EvaluationResult`, `compare_lexicographic`).
  4. `src/genetic/operators.py` (crossover e mutação).
  5. `src/models/individual.py` (campo `num_panels`).
  6. `scripts/e5_4_6_consolidacao.py` (configurações experimentais que geram os 180 execuções).
- **Figuras/tabelas recomendadas:**
  - Tabela resumida dos componentes efetivos do AG v2 (indivíduo = \(N\), avaliação lexicográfica, seleção por torneio, elitismo = 2, crossover = 80 %, mutação = 20 %).
- **Prioridade:**
  1. **Obrigatória:** remover a referência a fitness escalar e inserir avaliação lexicográfica.
  2. **Obrigatória:** indicar que a implementação utilizada é AG v2.
  3. **Obrigatória:** esclarecer a representação de \(N\) como único gene.
  4. **Obrigatória:** reformular o objetivo para minimização de custo com restrições.
  5. **Recomendada:** incluir a tabela resumida dos componentes.
- **O que preservar:**
  1. Descrição geral de operadores genéticos.
  2. Explicação de que o algoritmo evolui soluções ao longo das gerações.
  3. Manter a motivação de usar AG para buscar soluções de dimensionamento.
- **Ressalva documental:** a auditoria parte do texto original e das evidências consolidadas no repositório. A validação final de cada ponto deve ser feita nas evidências do pacote `tcc_final_product.zip` (código, rotas, componentes UI). Não se deve afirmar que uma funcionalidade existe apenas porque aparece no artigo antigo.
- **Parecer da 5.2:** **Aguardando aprovação.** A orientação está alinhada às decisões científicas e à implementação experimental consolidada. A confirmação definitiva das referências de código depende da conferência do pacote final, mas as divergências conceituais do texto original estão identificadas.

---

**Status da auditoria da Seção 5:** 5.1 aprovada; 5.2 aprovada; 5.3 aprovada; 5.4 aprovada; 5.5 aprovada. Auditoria da Seção 5 encerrada.

---

**Status da auditoria da Seção 6:** registrada como subseção 20.6; pendência transferida ao roteiro de edição (a seção não existe no artigo original).Auditoria das referências: **aprovada (20.7)**.

---

### 20.3 5.3 — Simulações Iniciais

- **Localização no artigo:** Seção 5.3 (linhas 240‑250 do documento original).
- **Afirmações atuais:**
  1. Simulações realizadas em cenários residenciais de João Pessoa (81 m² bruto, 68,85 m² útil, consumo ≈ 550 kWh/mês).
  2. Resultado apresentado na Tabela 1: 7 módulos, energia estimada 511,4 kWh/mês (85,2 % do consumo), custo R$ 9.450,00, ocupação da área útil 22,4 %.
- **Divergências identificadas:**
  1. O consumo citado no texto (≈ 550 kWh) não corresponde ao percentual exibido (85,2 % → consumo ≈ 600 kWh).
  2. O exemplo (7 módulos) não faz parte dos três cenários oficiais (150, 300, 500 kWh) cujas soluções ótimas são 3, 5 e 8 módulos, conforme `results/e5_4_6/summary.json`.
  3. Portanto, a Tabela 1 representa uma simulação preliminar e não pode ser tratada como parte dos 180 experimentos oficialmente consolidados.
- **Orientação ao colega:**
  1. Indicar que a Tabela 1 refere‑se a uma simulação inicial/preliminar, distinta dos experimentos E5.4.
  2. Não misturar este exemplo com os resultados oficiais; apresentar os três cenários oficiais e suas quantidades ótimas (3, 5, 8 módulos).
  3. Mencionar que foram realizadas 180 execuções (2 configurações × 3 cenários × 30 sementes), obtendo taxa de ótimo 180/180 (100 %).
  4. Incluir tabela resumida dos três cenários (consumo, módulos, custo estimado) e gráficos comparativos de tempo (AG, análise, exaustiva) conforme `summary.json`.
- **Evidências técnicas a incluir:**
  1. `results/e5_4_6/summary.json` (painéis ótimos, tempos médios).
  2. `results/e5_4_6/raw.jsonl` (dados individuais).
  3. `scripts/e5_4_6_consolidacao.py` (configurações).
  4. Captura da Tabela 1 (imagem `image2` do artigo original; transcrição registrada na auditoria).
- **Figuras/tabelas recomendadas:**
  1. Tabela comparativa dos três cenários oficiais (consumo, módulos, custo).
  2. Gráfico de tempos médios (AG pop10/gen20, AG pop20/gen40, análise, exaustiva).
  3. Manter a captura da Tabela 1 como exemplo de simulação preliminar, com nota explicativa.
- **Prioridade:**
  1. **Obrigatória:** esclarecer que a Tabela 1 não faz parte dos 180 experimentos; apresentar os cenários oficiais.
  2. **Obrigatória:** incluir a taxa de obtenção do ótimo (180/180) e os tempos médios.
  3. **Recomendada:** inserir a captura da Tabela 1 como ilustração de simulação inicial.
- **O que preservar:**
  1. Motivação de validar o algoritmo com simulações residenciais.
  2. Demonstração de cálculo de área útil e geração estimada.
  3. Uso de painel de 550 W, área 2,2 m², custo unitário R$ 1.100 + R$ 250.
- **Ressalva documental:** a auditoria baseia‑se nas evidências acima; a confirmação de que a Tabela 1 corresponde a um cenário preliminar deve ser feita ao comparar o consumo implícito (≈ 600 kWh) com o valor textual (≈ 550 kWh) e com os resultados oficiais dos 180 experimentos. Não afirmar que o exemplo faz parte dos resultados experimentais consolidados.
- **Parecer da 5.3:** **Aguardando aprovação** – a auditoria está completa, faltando apenas sua validação para prosseguir.

---

### 20.4 5.4 — Interface Desenvolvida

- **Localização no artigo:** Seção 5.4 (linhas 254‑259 do documento original).

- **Divergência arquitetural:** o artigo descreve a interface como construída em **Python com Streamlit**. O produto final utiliza:
  1. **Backend:** Python + FastAPI.
  2. **Frontend:** React + Vite.
  3. **Comunicação:** API HTTP (JSON) entre frontend e backend.
  4. **Otimização:** executada no backend, com resultados retornados ao frontend.

- **Correções obrigatórias:**
  1. Substituir “Streamlit” por “React + Vite” e mencionar FastAPI no backend.
  2. Explicar que a interface envia os parâmetros da simulação ao backend via API e recebe a solução.
  3. Evitar atribuir à interface cálculos ou lógica de otimização – isso ocorre no backend.
  4. Manter referência histórica a Streamlit apenas como protótipo anterior, se necessário.

- **Funcionalidades e evidências técnicas a incluir:**
  1. `backend/routes.py` – endpoints `/health`, `/cities`, `/panels`, `/optimize`, `/baseline`, `/compare`, `/experiments/*`.
  2. `frontend/src/components/DashboardForm.tsx` – campos de entrada (largura, comprimento, consumo, cidade, orçamento, parâmetros do AG).
  3. `frontend/src/components/DashboardPage.tsx` – visualização de resultados (evolução do fitness, geração × consumo, balanço energético, ocupação do telhado).
  4. `src/models/roof.py` – cálculo de área bruta e útil.
  5. `src/genetic/algorithm.py` – chamada ao otimizador a partir da rota `/optimize`.
  6. `frontend/src/components/MetricCards.tsx` – cartões de métricas resumidas (painéis recomendados, energia estimada, custo, ocupação).

- **Figuras recomendadas:**
  1. **Figura 1 – Interface principal:** captura real da tela de configuração (DashboardForm) mostrando campos de entrada.
  2. **Figura 2 – Arquitetura da aplicação:** diagrama próprio representando React/Vite ↔ FastAPI ↔ camada de otimização.
  3. **Figura 3 – Visualização dos resultados:** captura das abas de resultados (gráficos de convergência, geração × consumo, balança energética, ocupação).

- **Prioridade:**
  1. **Obrigatória:** atualizar a descrição tecnológica (FastAPI + React/Vite).
  2. **Obrigatória:** esclarecer comunicação frontend‑backend.
  3. **Obrigatória:** descrever as funcionalidades efetivamente disponíveis.
  4. **Recomendada:** inserir as capturas das telas (Figura 1 e 3) e o diagrama de arquitetura (Figura 2).

- **O que preservar:** a motivação da interface, a possibilidade de inserir parâmetros, a execução da otimização, a apresentação das métricas e da solução ao usuário – desde que condizentes com a implementação real.

- **Ressalva documental:** a auditoria baseia‑se nas evidências acima; a confirmação de que cada componente citado (formulário, visualizações, endpoints) está presente no pacote final (`tcc_final_product.zip`) deve ser feita antes de afirmar sua existência no artigo.

- **Parecer preliminar da 5.4:** **Aguardando aprovação** – a orientação está completa, faltando apenas sua validação para registrar como aprovada.

---

### 20.5 5.5 — Considerações Parciais

- **Objetivo da análise:** verificar se as considerações parciais do artigo representam corretamente o estado final do produto, os resultados experimentais e as limitações científicas.

- **Afirmações atuais (linhas 260‑266 do documento original):**
  1. Potencial de utilização do AG no dimensionamento fotovoltaico.
  2. Utilização de dados simulados.
  3. Modelo ainda em desenvolvimento.
  4. Consideração de restrições físicas e orçamentárias.
  5. Estimativa de geração energética.
  6. Trabalhos futuros envolvendo dados reais de irradiância, aperfeiçoamento da função fitness e comparação com métodos tradicionais.

- **Divergências identificadas:**
  1. **Estado de desenvolvimento:** o artigo descreve um modelo ainda em desenvolvimento, mas o produto foi encerrado tecnicamente na E6.2. A redação deve distinguir encerramento do desenvolvimento do software de conclusão científica do trabalho.
  2. **Função fitness:** a menção ao aperfeiçoamento da função fitness precisa ser revista — os experimentos usam AG v2 com comparação lexicográfica feasibility‑first, não fitness escalar.
  3. **Dados simulados:** a utilização de dados simulados deve permanecer explícita; não se pode sugerir validação com dados reais de instalações.
  4. **Comparação com métodos tradicionais:** a comparação com método analítico e busca exaustiva **já foi realizada experimentalmente**; não deve aparecer como algo inteiramente futuro. Pode‑se mencionar ampliação para outros métodos e cenários.

- **Conteúdo que deve ser incorporado:**
  1. Conclusão técnica do protótipo computacional.
  2. Modelo E5.2 de minimização de custo sujeito às restrições.
  3. Três cenários de consumo (150, 300, 500 kWh/mês).
  4. 180 execuções experimentais (2 configurações × 3 cenários × 30 sementes).
  5. Obtenção do ótimo determinístico em 180/180 execuções.
  6. Comparação de desempenho temporal, sem alegar superioridade do AG.
  7. Limitações da modelagem e dos dados.

- **Limitações que precisam aparecer:**
  1. Irradiância simulada/mock, sem medições reais.
  2. Série mensal disponível para João Pessoa; demais localidades utilizam médias anuais.
  3. Modelo com **uma única variável de decisão inteira** (quantidade de módulos `N`).
  4. Custo simplificado de R$ 1.350,00 por módulo.
  5. Eficiência global de 0,82.
  6. Fator de aproveitamento da área de 0,85.
  7. Resultados restritos aos cenários e parâmetros testados.
  8. Ausência de validação em instalações reais.

- **Trabalhos futuros recomendados:**
  1. Incorporar séries históricas reais de irradiação solar.
  2. Ampliar a quantidade de localidades e cenários.
  3. Incluir modelos de custos mais completos (outros componentes do sistema).
  4. Investigar variáveis adicionais de dimensionamento.
  5. Avaliar outras configurações e estratégias de otimização.
  6. Realizar validação com instalações fotovoltaicas reais.

- **Prioridade das alterações:**
  1. **Obrigatória:** atualizar o estado de desenvolvimento (produto encerrado na E6.2).
  2. **Obrigatória:** corrigir a descrição da função de avaliação (lexicográfica, não fitness escalar).
  3. **Obrigatória:** incorporar os resultados oficiais (cenários, 180 execuções, 180/180).
  4. **Obrigatória:** registrar as limitações científicas listadas.
  5. **Obrigatória:** atualizar trabalhos futuros.
  6. **Obrigatória:** evitar afirmações de superioridade geral do AG.

- **Evidências técnicas:**
  1. `docs/E6_2_ENCERRAMENTO_TECNICO.md` (checklist definitivo, limitações, trabalhos futuros).
  2. `results/e5_4_6/summary.json` (resultados oficiais).
  3. `docs/E5_2_MODELO_MATEMATICO.md` (modelo oficial).
  4. Distinção transversal: 180 experimentos são resultados científicos; 208/208 testes aprovados são evidência de validação de software.

- **Parecer da 5.5:** **Aprovada** — a seção foi reformulada para refletir o estado encerrado do produto, os resultados oficiais (cenários, 180 execuções, taxa 180/180), a comparação de tempos e as limitações científicas. Não há alegação de validação em instalações reais, apenas a descrição do protótipo técnico concluído.

- **Ressalva documental:** a auditoria baseia‑se nas evidências acima; a confirmação de cada limitação e número (eficiência 0,82, fator 0,85, custo R$ 1.350) deve ser conferida nas constantes do produto (`src/core/constants.py`, `src/models/`).

---

### 20.6 6 — Conclusões

- **Localização no artigo:** o documento original não contém uma Seção 6 com conteúdo. O sumário na linha 46 anuncia “Seção 6 expõe as considerações finais”, mas o texto encerra na Seção 5.5 e segue diretamente para as REFERÊNCIAS.

- **Divergência identificada:** ausência de seção de conclusão final (Seção 6) no corpo do artigo.

- **Orientação ao colega:**
  1. Incluir uma Seção 6 — Conclusões (ou Considerações Finais) no roteiro de edição.
  2. Resumir: produto tecnicamente encerrado, modelo E5.2 (minimização de custo sujeita a restrições), 180 execuções, taxa 180/180, três cenários oficiais (150/300/500 kWh), AG v2 com comparação lexicográfica feasibility‑first, comparação de tempos com métodos determinísticos sem alegar superioridade geral do AG.
  3. Listar limitações científicas (irradiância simulada, única variável \(N\), custo simplificado, sem validação real).
  4. Apresentar contribuições do trabalho e trabalhos futuros.
  5. Manter distinção entre conclusões do produto técnico e conclusões científicas.

- **Figuras recomendadas:** nenhuma obrigatória; pode reutilizar o diagrama de arquitetura da 5.4 como referência final.

- **Prioridade:** Obrigatória — incluir a Seção 6 conforme prometido na introdução do artigo.

- **Evidências técnicas:**
  1. `docs/E6_2_ENCERRAMENTO_TECNICO.md` (encerramento técnico, limitações, trabalhos futuros).
  2. `results/e5_4_6/summary.json` (resultados oficiais).
  3. `docs/E5_2_MODELO_MATEMATICO.md` (modelo oficial).

- **Parecer da Seção 6:** Pendente — aguardando inclusão da seção no roteiro de edição pelo colega.

---

### 20.7 — Auditoria das Referências Bibliográficas

**Status:** auditoria aprovada e consolidada.  
**Escopo:** verificar a correspondência entre citações no corpo do artigo e referências bibliográficas, a identificação correta de autoria e publicação, a consistência dos dados editoriais, a adequação das fontes ao conteúdo em que são utilizadas e a rastreabilidade dos documentos citados.

A auditoria foi realizada sobre a versão original do artigo, sem alteração de seu conteúdo. As recomendações abaixo deverão ser encaminhadas ao responsável pela redação da versão final.

#### 20.7.1 — Diagnóstico geral

Foram identificadas **19 entradas bibliográficas**. Na conferência do corpo do artigo, 18 referências apresentam correspondência com citações identificáveis, enquanto uma entrada não foi localizada nas citações do texto.

A auditoria identificou problemas de natureza distinta:

- divergência entre a autoria apresentada na citação e a autoria efetiva da publicação;
- ordem incorreta dos autores;
- títulos incompletos ou transcritos incorretamente;
- referências institucionais genéricas, sem identificação precisa do documento;
- links que direcionam para páginas genéricas ou mecanismos de busca, em vez da fonte original;
- referências com dados editoriais insuficientes para localização e verificação;
- utilização de trabalhos cujo escopo não corresponde diretamente ao problema de dimensionamento residencial tratado no TCC.

A existência de uma referência bibliográfica não significa, por si só, que ela sustente todas as afirmações associadas a ela. O texto deve respeitar o objeto, o método e os limites de cada publicação.

#### 20.7.2 — Correções obrigatórias de autoria e identificação

**1. SILVA et al. (2023)**

A publicação identificada possui autoria individual: Brenda Andreza Oliveira da Silva. Portanto, a citação no corpo do artigo deve ser corrigida de `SILVA et al. (2023)` para `SILVA (2023)`.

A referência deve apresentar o título correto, os dados do periódico, volume, número, páginas e DOI:

- Autora: Brenda Andreza Oliveira da Silva.
- Título: *Aproveitamento e potencial da energia solar fotovoltaica no nordeste do Brasil*.
- Periódico: *Meio Ambiente (Brasil)*.
- Volume 5, número 1, páginas 55–66, 2023.
- DOI: `10.66205/mabra.v5i1.295`.

**Orientação:** corrigir a autoria na citação e na bibliografia. Utilizar o trabalho para contextualizar o potencial solar do Nordeste, sem tratá-lo como comprovação de que o modelo desenvolvido neste TCC é escalável para todas as cidades ou de que João Pessoa representa toda a região.

**2. ETENE/BNB (2023)**

A entrada está atribuída genericamente à instituição, mas o documento identificado possui autoria individual de Francisco Diniz Bezerra.

A citação recomendada no corpo do texto é `BEZERRA (2023)`. A referência deve identificar o documento *Infraestrutura: Energia Solar*, publicado no *Caderno Setorial ETENE*, ano 8, número 295, julho de 2023, pelo Banco do Nordeste.

**Orientação:** substituir a atribuição genérica pela autoria identificada e utilizar o endereço do registro ou do documento original no repositório do Banco do Nordeste, não apenas a página inicial da instituição.

A informação de que o Nordeste concentra 61,9% dos projetos fotovoltaicos centralizados e 18,9% da geração distribuída exige atenção ao denominador utilizado. O texto deve verificar a tabela e a unidade de medida correspondentes antes de apresentar esses percentuais como participação em número de projetos ou em potência instalada.

**3. CAMARILLO-PEÑARANDA et al. (2015)**

A ordem dos autores está incorreta. O primeiro autor identificado na publicação é Fabio Andrés Ramírez-Quiroz.

A citação no corpo do artigo deve ser alterada para `RAMÍREZ-QUIROZ et al. (2015)`, e a bibliografia deve respeitar a ordem original dos autores.

DOI identificado: `10.17533/udea.redin.n75a10`.

**Orientação:** corrigir a autoria e manter a publicação apenas como referência relacionada à aplicação de algoritmos genéticos em sistemas fotovoltaicos. Seu objeto é a reconfiguração de arranjos fotovoltaicos sob sombreamento parcial, não o dimensionamento residencial por quantidade de módulos. Não utilizar seus resultados como comparação direta de desempenho entre AG e busca exaustiva no problema deste TCC.

**4. WAMUSSE (2019)**

A autoria da citação está adequada, mas o título da referência bibliográfica precisa ser corrigido.

O trabalho identificado é a dissertação *Otimização de sistemas isolados para eletrificação rural considerando a probabilidade de perda de carga*, de Verónica Wamusse, defendida em 2019 no Programa de Pós-Graduação em Engenharia Elétrica da Universidade Federal do Paraná.

Identificador: `https://hdl.handle.net/1884/66850`.

**Orientação:** corrigir título e dados acadêmicos. Na discussão, explicitar que o trabalho trata de sistemas isolados para eletrificação rural, com abordagem distinta do sistema residencial conectado à rede estudado neste TCC.

**5. PAIXÃO et al. (2025)**

A referência apresenta inconsistências na identificação dos autores e utiliza o ResearchGate como se fosse a fonte editorial da publicação.

A publicação identificada é o capítulo *Algoritmos Genéticos na Engenharia Elétrica*, de Joelson Lopes da Paixão e Alzenira da Rosa Abaide, publicado pela Aurum Editora no livro *Caminhos da Pesquisa Multidisciplinar*, páginas 16–24, em 2025.

DOI: `10.63330/aurumpub.019-002`.

**Orientação:** corrigir a citação para `PAIXÃO e ABAIDE (2025)` e utilizar os dados da editora e o DOI como referência de acesso. O capítulo pode fundamentar conceitos gerais de algoritmos genéticos, mas não deve ser apresentado como validação experimental específica de dimensionamento fotovoltaico residencial.

**6. RODRIGUES et al. (2024)**

Foi identificado erro de transcrição no título, que apresenta a expressão “Matemática Applied”.

O título correto é *Matemática Aplicada no Dimensionamento de um Sistema Fotovoltaico Conectado à Rede Elétrica: Alternativa Renovável de Geração de Energia*.

**Orientação:** corrigir o título, preservando os seis autores identificados na publicação, e completar os dados editoriais: *Revista FT*, volume 28, número 130, janeiro de 2024.

DOI: `10.5281/zenodo.10607610`.

O trabalho deve ser utilizado como referência contextual ou educacional, sem atribuir a ele validação técnica do algoritmo genético implementado neste TCC.

**7. INPE (2017)**

A referência ao Atlas Brasileiro de Energia Solar deve apresentar os autores identificados na publicação, em vez de atribuir a autoria exclusivamente à instituição.

A citação recomendada é `PEREIRA et al. (2017)`.

A referência deve identificar a segunda edição do *Atlas brasileiro de energia solar*, publicado pelo INPE em São José dos Campos, em 2017, com 80 páginas.

DOI: `10.34024/978851700089`.

**Orientação:** ajustar a autoria na citação e na bibliografia, mantendo o INPE como instituição editora.

#### 20.7.3 — Correções de links e identificação de documentos normativos

**8. BRASIL (2022) — Lei nº 14.300/2022**

O link atualmente apresentado utiliza um endereço de pesquisa do Google que contém o endereço oficial da legislação.

**Orientação:** substituir o link indireto pelo endereço oficial do Planalto:

`https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2022/lei/l14300.htm`

Manter a identificação da legislação como `BRASIL (2022)`.

**9. ANEEL (2023)**

A referência atual reúne instrumentos normativos distintos: a Resolução Normativa ANEEL nº 1.000/2021 e a Lei nº 14.300/2022.

**Orientação:** separar as referências. A Resolução Normativa nº 1.000 deve ser identificada como ato da ANEEL, de 7 de dezembro de 2021, com citação correspondente ao ano do ato original (`ANEEL, 2021`). A Lei nº 14.300 deve permanecer identificada separadamente como legislação federal (`BRASIL, 2022`).

Caso o artigo utilize uma versão consolidada ou alterada da resolução, deverá indicar precisamente a versão consultada e as alterações consideradas. Não atribuir à ANEEL a autoria da lei federal.

**10. ABSOLAR (2024)**

O endereço apresentado direciona para a página geral da associação, sem identificar o documento específico que sustenta os dados utilizados no artigo.

**Orientação:** identificar a edição, o mês e o número do levantamento ou infográfico utilizado, incluindo o endereço direto do documento. Como os dados da associação são atualizados periodicamente, a referência deve permitir identificar qual versão foi efetivamente consultada.

#### 20.7.4 — Referências que exigem comprovação documental adicional

**11. SORKNÆS (2018)**

A entrada apresenta apenas o nome do autor, o título *Optimization of energy systems using genetic algorithms* e o ano de 2018. Não foi possível confirmar com segurança a publicação exata correspondente a essa descrição.

**Orientação:** solicitar ao responsável pelo artigo a fonte original utilizada. A referência deverá conter dados suficientes para verificação, como periódico ou instituição, título completo, volume, páginas e DOI ou endereço eletrônico. Não completar os dados por suposição. Se a publicação não puder ser localizada e comprovada, remover a referência e reavaliar a afirmação que ela sustentava.

**12. GORE (2014)**

A referência está associada a uma citação direta com indicação da página 32. Entretanto, os dados disponíveis não permitem confirmar com segurança a edição exata utilizada.

**Orientação:** conferir a obra física ou uma versão digital correspondente à edição indicada, verificando título, editora, ano, tradução e página da citação. Se a edição ou a passagem não puder ser comprovada, retirar a citação direta ou substituí-la por uma fonte verificável. Não trocar automaticamente por outra edição sem conferir o conteúdo e a paginação.

**13. OLIVEIRA; LANA (2023)**

A entrada *Energia solar fotovoltaica: expansão e perspectivas no Brasil* não foi localizada entre as citações do corpo do artigo e apresenta dados bibliográficos incompletos.

**Orientação:** verificar se o material foi efetivamente utilizado na fundamentação. Se tiver sido utilizado, completar os dados da publicação e inserir a citação no trecho correspondente. Se não tiver sido utilizado, remover a entrada da bibliografia.

#### 20.7.5 — Referências que podem ser preservadas, com padronização

As seguintes referências podem ser mantidas, desde que a versão final padronize sua apresentação bibliográfica:

- **PINHO e GALDINO:** preservar o Manual de Engenharia para Sistemas Fotovoltaicos, identificando Pinho e Galdino como organizadores, conforme os dados editoriais da edição utilizada.
- **VILLALVA:** preservar a obra, completando o título, a edição e os dados editoriais. A edição identificada é a segunda, de 2015, publicada pela Érica.
- **GIL (2010):** preservar, padronizando a referência conforme a edição efetivamente consultada.
- **GOLDBERG (1989):** preservar, padronizando os dados bibliográficos.
- **HOLLAND (1975):** preservar, padronizando os dados bibliográficos.
- **MITCHELL (1998):** preservar, padronizando os dados bibliográficos.

A padronização deve seguir uma única norma bibliográfica ao longo de todo o artigo, respeitando a natureza de cada fonte — livro, capítulo, artigo, dissertação, legislação ou documento institucional.

#### 20.7.6 — Adequação das fontes às afirmações do artigo

Além da correção formal das referências, o responsável pela redação deve revisar se cada fonte sustenta efetivamente a afirmação associada a ela.

Foram identificados os seguintes cuidados de interpretação:

1. O trabalho de Ramírez-Quiroz et al. trata de reconfiguração de arranjos fotovoltaicos sob sombreamento parcial. Não equivale ao problema de dimensionamento residencial por quantidade de módulos.
2. A dissertação de Wamusse trata de sistemas isolados para eletrificação rural. Não representa o mesmo modelo de sistema conectado à rede utilizado no TCC.
3. O capítulo de Paixão e Abaide apresenta conteúdo geral sobre algoritmos genéticos. Não constitui evidência experimental direta para o desempenho do algoritmo desenvolvido neste projeto.
4. O trabalho de Rodrigues et al. tem caráter contextual e educacional. Não deve ser utilizado como comprovação de desempenho do AG.
5. O trabalho de Silva apresenta uma análise do potencial solar no Nordeste. Não comprova, por si só, a generalização dos resultados experimentais do TCC para todas as localidades da região.
6. Os documentos da ANEEL, da legislação federal, do INPE, da ABSOLAR e do Banco do Nordeste devem ser associados às afirmações específicas que efetivamente documentam, respeitando o período e o escopo dos dados.

A revisão deve evitar que referências de contextualização sejam apresentadas como validação do modelo matemático ou dos resultados experimentais do projeto.

#### 20.7.7 — Ajuste terminológico relacionado à fundamentação

Foi identificada a utilização do termo **irradiância** em associação à unidade `kWh/m²/dia`, em trechos como os indicados na auditoria teórica.

A unidade representa energia solar acumulada por área ao longo de um período, e não irradiância instantânea. Portanto, o texto deverá utilizar a expressão **irradiação solar diária** ou, quando apropriado ao contexto do cálculo, **horas de sol pleno (HSP)**.

**Orientação:** revisar as ocorrências no corpo do artigo, nas tabelas, nas legendas e nas descrições das variáveis, mantendo a terminologia coerente com o modelo efetivamente utilizado.

#### 20.7.8 — Encaminhamento ao responsável pela redação

A versão final do artigo deverá contemplar as seguintes providências:

1. Corrigir as citações de Silva, Bezerra, Ramírez-Quiroz, Paixão e Abaide e Pereira, conforme as autorias identificadas.
2. Corrigir os títulos e os dados editoriais das referências de Wamusse e Rodrigues et al.
3. Separar a referência à Resolução Normativa ANEEL nº 1.000/2021 da referência à Lei nº 14.300/2022.
4. Substituir links genéricos ou indiretos por endereços oficiais ou identificadores permanentes das fontes.
5. Identificar a edição específica do material da ABSOLAR utilizado.
6. Comprovar documentalmente as referências de Sorknæs e Gore antes de mantê-las.
7. Decidir sobre a permanência da referência de Oliveira e Lana, conforme seu uso efetivo no texto.
8. Padronizar as referências de Pinho e Galdino, Villalva, Gil, Goldberg, Holland e Mitchell.
9. Conferir a correspondência entre todas as citações do corpo do artigo e a lista final de referências.
10. Revisar as afirmações sustentadas por trabalhos de escopo diferente, evitando atribuir a essas fontes conclusões que elas não demonstram.
11. Corrigir o uso de “irradiância” quando associado à unidade de energia por área por dia.

#### 20.7.9 — Resultado da auditoria bibliográfica

A auditoria bibliográfica foi concluída e aprovada como orientação editorial para a revisão final do artigo.

As referências não devem ser substituídas indiscriminadamente. O objetivo é preservar as fontes pertinentes, corrigir as identificações incorretas, completar os dados insuficientes e retirar apenas as entradas que não possam ser comprovadas ou que não tenham sido efetivamente utilizadas.

**Responsabilidade pela implementação:** o responsável pela redação do artigo deverá executar as correções, atualizar as citações no texto, revisar a lista bibliográfica e conferir os links e documentos originais.

**Limite desta etapa:** esta auditoria não altera o artigo original nem modifica o produto computacional. Ela registra as divergências e fornece as instruções necessárias para a elaboração da versão final do artigo.

---

## 21. Revisão transversal e status consolidado da E6.3

**Data da consolidação:** 07/11/2026.

| Etapa | Situação |
|---|---|
| Auditoria das Seções 1 a 4 | Concluída |
| Auditoria das Seções 5.1 a 5.5 | Aprovada |
| Auditoria da Seção 5 | Encerrada |
| Seção 6 — Conclusões | Registrada (20.6), pendente de incorporação ao roteiro de edição |
| Auditoria das Referências Bibliográficas | Aprovada (20.7) |
| Revisão transversal | Concluída nesta seção 21 |
| Guia editorial consolidado | Pendente |

### 21.1 — Ajustes de coerência aplicados

1. A seção “Próximos blocos da auditoria” (item 9) deve ser lida como histórica: as etapas nela listadas já foram executadas e aprovadas.
2. A sequência das subseções da Seção 20 está correta: 20.1 a 20.5 (Seção 5), 20.6 (Seção 6) e 20.7 (Referências).
3. A Seção 6 permanece registrada como pendência de redação, não de auditoria: a auditoria apenas constata que a seção não existe no artigo original.
4. A auditoria bibliográfica não altera o artigo original nem o produto; é orientação para a versão final.
5. A distinção 180 experimentos × 208 testes permanece explícita nos blocos 5.3, 5.5 e 6.

### 21.2 — Encaminhamento final

O material está pronto para ser convertido em **guia editorial consolidado** para o colega, reunindo:

- correções obrigatórias por seção;
- sugestões de redação;
- figuras e tabelas recomendadas;
- evidências técnicas e bibliográficas;
- ordem de execução das correções;
- limites de interpretação e ressalvas.

A redação do artigo permanece sob responsabilidade do colega; esta auditoria não substitui o texto original nem decide contenido além das evidências registradas.

