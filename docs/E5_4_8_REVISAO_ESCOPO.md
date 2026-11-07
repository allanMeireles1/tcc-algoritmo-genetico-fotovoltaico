# E5.4.8 — Revisão de Escopo: Artigo Original × Modelo E5.2

**Data:** 06/11/2026
**Base:** `docs/Modelo_Artigo_Tcc_Final 2026.md` (artigo ainda não finalizado)
**Objetivo:** verificar se a simplificação adotada na E5.2 preserva os objetivos e hipóteses aprovados no projeto original.

## 1. O que o artigo original promete

| Item | Redação no artigo |
|------|-------------------|
| Objetivo geral | Maximizar a diferença entre energia gerada e custo total; avaliar 3 cenários (baixo, médio, alto consumo) |
| Cromossomo | Número de painéis solares |
| Função de aptidão | Diferença entre energia gerada e custo total do sistema |
| Dados de irradiância | "Coletar e tratar dados **reais** de irradiância de João Pessoa" |
| Comparação | Comparar AG com métodos tradicionais em eficiência energética, custo e tempo de retorno do investimento |
| Problema descrito na introdução | Otimização combinatória de alta complexidade, com variáveis interdependentes (nº painéis, inclinação, orientação, inversor, área, consumo, irradiância) |

## 2. O que a E5.2 formalizou

| Item | Modelo adotado |
|------|----------------|
| Variável de decisão | Único: `N` = quantidade de painéis |
| Objetivo | `min C(N) = N × 1350` |
| Restrição central | Energia ≥ consumo em **todos os 12 meses** (mês crítico), área útil, orçamento opcional |
| Comparação | Analítica × Exaustiva × AG v2 sobre o mesmo `Problem` |
| Irradiância | Dados **mock** (média JP 5,4 kWh/m²/dia; mensal mock apenas para JP) |
| Método comparado | Busca exaustiva e analítica (não "opções tradicionais" de dimensionamento real) |

## 3. Divergências identificadas

### 3.1 Função objetivo
- **Artigo:** maximizar `Eg − Ct` (energia menos custo).
- **E5.2:** minimizar custo sujeito a cobertura total (mês crítico).

As formulações **não são equivalentes**. A E5.2 é conservadora (qualquer déficit mensal é rejeitado); a do artigo não impõe viabilidade energética. O ponto ótimo pode diferir.

**Ação necessária:** o texto do TCC deve declarar a escolha (ou o orientador deve validar a alteração). Não basta chamar as duas de "a mesma função".

### 3.2 Complexidade declarada x real
- O artigo chama o problema de "otimização combinatória de alta complexidade" com "diversas variáveis interdependentes".
- A implementação atual tem **uma única variável inteira** e custo linear → solução determinística trivial.

**Ação necessária:** remover ou qualificar afirmações de alta complexidade no texto, ou ampliar variáveis — a ampliação está suspensa até consulta ao orientador.

### 3.3 Dados de irradiância
- O artigo diz "dados **reais** de João Pessoa".
- O projeto usa **mock** (`irradiance_mock.json`, `cities_mock.json`), com ressalva de média anual; mensal apenas para JP.

**Ação necessária:** trocar "dados reais coletados" por "dados simulados/inspirados em médias públicas, mantidos como limitação declarada". Ou substituir por dados reais (INPE/NASA POWER) — escopo a definir.

### 3.4 Métodos tradicionais comparados
- O artigo promete comparação com "métodos tradicionais de dimensionamento" em eficiência, custo e **tempo de retorno do investimento**.
- A E5.4 compara AG × analítico × exaustivo — não inclui o método de planilha/regra prática do instalador, nem análise de payback.

**Ação necessária:** ou incluir o método tradicional direto como benchmark adicional (baseline já existe na arquitetura), ou reescrever o objetivo para "comparação entre métodos computacionais exatos e heurísticos".

### 3.5 Três cenários (baixo, médio, alto)
- O artigo prevê explicitamente 150 / 300 / 500 kWh/mês.
- A E5.4.6 cobre exatamente esses três cenários. **Alinhado.**

## 4. O que está alinhado

- Cromossomo = nº de painéis: **alinhado**.
- AG implementado manualmente, sem libs evolutivas: **alinhado**.
- João Pessoa como cidade de referência: **alinhado**.
- 3 cenários de consumo: **alinhado** (cobertos na E5.4.6).
- Objetivo de comparar com métodos de dimensionamento simples: parcialmente atendido via baseline/analítico.

## 5. Decisão oficial (Alternativa A)

A decisão adotada é **preservar o modelo E5.2** (minimização de custo sujeita a cobertura energética mensal, área útil e orçamento). Consequências obrigatórias para a redação:

1. **Objetivo geral** deve ser reescrito para refletir o modelo implementado: *minimizar o custo total do sistema fotovoltaico garantindo o atendimento do consumo em todos os meses*.
2. **Objetivos específicos** devem ser ajustados:
   - modelar o problema como minimização de custo com restrições energéticas e físicas;
   - implementar e validar o AG v2 nesse modelo;
   - comparar AG × analítico × exaustivo;
   - analisar sensibilidade dos hiperparâmetros do AG.
3. **Corrigir afirmações infladas** no artigo: "alta complexidade", "dados reais coletados", "otimização multiobjetivo".
4. **Registrar limitações**: dados mock, custo linear, uma variável de decisão, mês completo sem sazonalidade de consumo.
5. **NÃO** alterar o modelo para `Eg − λ·Ct` nem ampliar variáveis sem nova decisão explícita do orientador.

> **Nota de correção:** a frase anterior de que "não foi necessária mudança no objetivo geral do artigo" está **incorreta** e foi substituída por esta decisão. O objetivo original (maximizar `Eg − Ct`) diverge do modelo implementado (minimizar custo com cobertura mensal). O relatório será entregue ao colega responsável pela redação para que ele atualize o manuscrito — sem reescrita silenciosa do conteúdo original.

## 6. Próximos passos

- E5.4.6: consolidação experimental (30 seeds, IC 95%) — concluída.
- E5.4.7: auditoria científica — concluída.
- E5.4.8: este documento — decisão oficial registrada (Alternativa A).
- **Entrega:** repassar este relatório ao colega de redação, destacando as seções 3.1, 3.2, 3.3 e 5.

