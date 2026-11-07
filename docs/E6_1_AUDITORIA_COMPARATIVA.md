# E6.1 · Relatório de Auditoria Comparativa — Artigo Original × Implementação Real

**Data:** 06/11/2026  
**Escopo:** alinhar o texto científico do TCC com o que efetivamente foi modelado, implementado e testado.  
**Regra:** **nenhuma alteração foi feita no artigo original, no código-fonte ou no modelo matemático**.  
**Finalidade:** servir como base para a revisão da redação (E6.2/E6.3) e para o colega responsável pelo artigo.

---

## 1. Fontes comparadas

| Fonte | Arquivo / artefato |
|-------|--------------------|
| Artigo original | `docs/Modelo_Artigo_Tcc_Final 2026.md` |
| Modelo matemático | `docs/E5_2_MODELO_MATEMATICO.md` |
| Auditoria científica anterior | `docs/E5_4_7_AUDITORIA_CIENTIFICA.md` |
| Revisão de escopo | `docs/E5_4_8_REVISAO_ESCOPO.md` |
| Resultados experimentais | `results/e5_4_6/summary.json`, `results/e5_4_6/raw.jsonl` |
| Implementação | `src/simulation/evaluation.py`, `src/simulation/runner.py`, `src/simulation/solvers.py`, `src/genetic/*` |
| API / Frontend | `backend/routes.py`, `frontend/src/components/ComparisonPage.tsx` |

---

## 2. Matriz de divergências

| # | Tema | O artigo descreve | A implementação real | Evidência |
|---|------|-------------------|----------------------|-----------|
| 1 | **Função objetivo** | Maximizar `Fitness = Eg − Ct`. | **Minimizar custo** `C(N) = N · C_unit`, sujeito a cobertura energética em todos os 12 meses, área útil e orçamento opcional. | `docs/E5_2_MODELO_MATEMATICO.md`, `src/simulation/evaluation.py` |
| 2 | **Complexidade do problema** | "Otimização combinatória de alta complexidade", "diversas variáveis interdependentes". | **Uma única variável de decisão inteira** (`N`). Parâmetros fixos (painel, η, fator 0,85); consumo constante; custo linear. | `docs/E5_2_MODELO_MATEMATICO.md`, `docs/E5_4_7_AUDITORIA_CIENTIFICA.md` |
| 3 | **Dados de irradiância** | "Coletar e tratar dados **reais** de irradiância de João Pessoa". | Dados **mock** (médias sobres postas; `irradiance_mock.json`); mensal apenas para João Pessoa; demais cidades usam média anual. | `docs/E5_4_7_AUDITORIA_CIENTIFICA.md`, `data/irradiance_mock.json` |
| 4 | **Comparação entre métodos** | Comparar AG com "métodos tradicionais" e **payback**. | Comparação **AG × analítico × exaustivo** sobre o mesmo `Problem`; não há método de instalador/planilha nem análise de payback. | `results/e5_4_6/summary.json`, `docs/E5_2_MODELO_MATEMATICO.md` |
| 5 | **Parâmetros do AG** | pop 100, gens 200, crossover 80%, mutação 5%. | **pop 10/20, gens 20/40, crossover 80%, mutação 20%**, elitismo 2, seeds controladas. Estudos de sensibilidade mostraram que 5% não é o valor usado na consolidação. | `tests/test_genetic.py`, `results/e5_4_6/summary.json` |
| 6 | **Status dos resultados** | Resultados **preliminares** de um protótipo (Tabela 1 única). | **180 execuções consolidadas** (3 cenários × 2 configurações × 30 seeds), todas com `optimal_rate = 1.0` e reprodutíveis. | `results/e5_4_6/summary.json` |
| 7 | **Plataforma / interface** | Protótipo em **Streamlit** (`app.py`). | Hoje o projeto também expõe **API FastAPI** (`backend/`) com **frontend React/Vite** (`frontend/`); o Streamlit continua presente como protótipo original. | `README.md`, `backend/routes.py`, `frontend/src/components/ComparisonPage.tsx` |

---

## 3. Formulação matemática correta (E5.2, resumo)

O modelo efetivamente implementado e testado é:

$$
\min_{N} \; C(N) = N \cdot C_{\text{unit}}
$$

sujeito a:

$$
E_m(N) \ge E_{\text{consumo}}, \quad \forall m \in {1,\dots,12}
$$

$$
N \cdot A_{\text{módulo}} \le A_{\text{útil}},
\qquad C(N) \le B_{\max} \;(\text{se informado}),
\qquad N \in \mathbb{Z}_{\ge 0}
$$

com:

- $E_m(N) = N \cdot (P_{\text{módulo}}/1000)\cdot HSP_m \cdot D \cdot \eta$
- $C_{\text{unit}} = 1100 + 250 = 1350$ R$/painel
- $A_{\text{útil}} = A_{\text{bruta}} \times 0{,}85$
- $D = 30$ dias, $\eta = 0{,}82$ (hipótese global)

**Interação genética:** o AG usa **comparação lexicográfica *feasibility-first***, não uma função fitness escalar. Isto difere do `Fitness = Eg − Ct` descrito no artigo.

---

## 4. Resultados experimentais consolidados (E5.4.6)

- **Cenários:** baixo (150 kWh/mês), médio (300 kWh/mês), alto (500 kWh/mês).
- **Configurações:** `pop10/gens20` e `pop20/gens40`.
- **Seeds:** 30 por configuração.
- **Total:** 180 execuções do AG (3 cenários × 2 configurações × 30 seeds).
- **Taxa de ótimo:** **100%** em todos os grupos (o AG igualou a busca exaustiva em todos os casos).
- **Tempo médio do AG:** ~5–7 ms (`pop10/gens20`) e ~22–24 ms (`pop20/gens40`).
- **Tempo analítico/exaustivo:** ~4–670 µs e ~0,42–2,8 ms, respectivamente.
- **Nº ótimo de painéis:** baixo = 3, médio = 5, alto = 8.

Fonte: `results/e5_4_6/summary.json`.

> **Regra de honestidade:** os experimentos mostram que **o AG reproduz o ótimo do modelo**, **não** que "o AG é superior" ou "o AG é melhor em produção". Para este modelo unidimensional, os métodos determinísticos são de custo computacional menor.

---

## 5. Recomendações de correção (por seção do artigo)

| Seção | O que corrigir |
|-------|----------------|
| **Resumo / Objetivo Geral** | Trocar a justificativa `Eg − Ct` pela **minimização de custo com cobertura energética mensal**, sem afirmar multiobjetivo. |
| **Objetivos específicos** | Ajustar para: (a) modelar minimização de custo com restrições energéticas/físicas; (b) implementar e validar o AG v2; (c) comparar AG × analítico × exaustivo; (d) analisar sensibilidade de hiperparâmetros. |
| **1.1 Contexto e Justificativa** | Qualificar a "alta complexidade combinatória" — o problema implementado é **unidimensional**; manter o texto teórico, mas deixar claro que é simplificação. |
| **2.2 / 2.3** | Declarar dados **mock** como limitação, substituindo a promessa de dados reais. |
| **3.3** | A teoria de AG pode ser mantida; explicitar o uso de **comparação lexicográfica** no modelo final. |
| **4.1** | Adotar formalmente o modelo E5.2 (min-cost com restrições), corrigindo o fitness. |
| **4.4** | Atualizar os parâmetros do AG para os valores **efetivamente testados** (pop 10/20, gens 20/40, mutação 20%, elitismo 2). |
| **5.3 / 5.5** | Substituir tabela única e "resultados preliminares" por um quadro das 180 execuções consolidadas, com taxas de ótimo e tempos. |
| **6. Conclusões** | Registrar que o AG **encontra o ótimo do modelo**, e que a vantagem do AG não é demonstrada neste espaço de busca simplificado. |

---

## 6. Pontos que precisam de alinhamento entre autores

1. **Objetivo geral:** o texto do artigo deve ser reescrito de acordo com a Alternativa A (minimização de custo com cobertura mensal), ou a implementação precisa ser mudada — não há caminho intermediário sem nova decisão.
2. **Dados de irradiância:** ou declarar mock (recomendado), ou migrar para dados reais e revalidar os resultados.
3. **Comparação:** ou manter "métodos computacionais exatos/heurísticos", ou incluir de fato um benchmark de método tradicional/planilha e uma análise de payback.
4. **Parâmetros do AG:** ajustar o texto para os valores consolidados ou apresentar a variação testada na E5.4.4.
5. **Escopo de variáveis:** manter 1 variável de decisão pode reduzir o interesse científico; se ampliar, é preciso refazer os experimentos E5.4.4–E5.4.6.
6. **Papel da interface:** definir se a redação apresentará o protótipo Streamlit, a aplicação FastAPI + React/Vite, ou ambos.

---

## 7. Encaminhamento

- **Enviar este relatório ao colega responsável pelo artigo** antes da revisão completa da redação (E6.2).
- **Não alterar** o modelo, os experimentos ou as APIs até haver decisão explícita sobre os itens acima.
- **Manter** os padrões já registrados:
  - o AG achou o ótimo do modelo (100% de taxa);
  - os dados são mock;
  - o modelo é unidimensional;
  - o objetivo é minimizar custo com restrições — **não** `Eg − Ct`.

Esses pontos garantem que o TCC apresente **exatamente o que foi desenvolvido, testado e demonstrado**.
