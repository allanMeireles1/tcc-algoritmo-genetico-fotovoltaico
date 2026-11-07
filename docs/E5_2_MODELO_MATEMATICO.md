# E5.2 — Modelo Matemático Formal do Problema de Dimensionamento Fotovoltaico

**Data:** 03/11/2026  
**Projeto:** TCC — Aplicação de Algoritmos Genéticos no Dimensionamento de Sistemas Fotovoltaicos Residenciais na Região do Nordeste Brasileiro  
**Etapa:** Especificação do modelo matemático (pós-auditoria E5.1)  
**Status:** Documento de especificação — **nenhuma implementação autorizada**

---

## 1. Classificação das Informações

Este documento utiliza três categorias explícitas para cada parâmetro ou escolha:

| Categoria | Significado |
|-----------|-------------|
| ✅ **Confirmado pela auditoria** | Valor ou comportamento identificado diretamente no código-fonte ou nos arquivos de dados do projeto atual. |
| 🟡 **Hipótese adotada para a formulação** | Escolha provisória necessária para formalizar o modelo matemático. Não é fato confirmado; precisa de validação posterior. |
| ⏳ **Pendente de validação** | Informação que precisa ser conferida nos arquivos, aprovada pelo orientador, ou obtida de fonte externa. |

> **Regra:** Nenhuma hipótese será apresentada como fato confirmado. Onde houver incerteza, ela será declarada explicitamente.

---

## 2. Definição do Problema

### 2.1 Enunciado

> **Determinar a quantidade de módulos fotovoltaicos que minimiza o custo estimado do sistema, sujeita ao atendimento integral do consumo mensal da residência em todos os meses do ano, ao limite de área útil do telhado e, quando informado, ao orçamento máximo.**

### 2.2 Variável de Decisão

$$N \in \mathbb{Z}_{\ge 0}$$

Quantidade de módulos fotovoltaicos. $N = 0$ é classificado como **inviável** para qualquer consumo mensal positivo.

### 2.3 Entradas do Problema

| Símbolo | Descrição | Unidade | Origem |
|---------|-----------|---------|--------|
| $E_{\text{consumo}}$ | Consumo mensal da residência | kWh/mês | Entrada do usuário |
| $A_{\text{útil}}$ | Área útil disponível no telhado | m² | Derivada de largura × comprimento × fator |
| $A_{\text{módulo}}$ | Área ocupada por cada módulo | m² | Dados do painel |
| $P_{\text{módulo}}$ | Potência nominal de cada módulo | Wp | Dados do painel |
| $HSP_m$ | Horas de sol pico no mês $m$ | h/dia (≡ kWh/m²/dia) | Dados de irradiância |
| $\eta$ | Fator global de desempenho | adimensional | Dados do painel |
| $C_{\text{unit}}$ | Custo unitário por módulo (módulo + instalação/módulo) | R$ | Dados do painel |
| $B_{\max}$ | Orçamento máximo informado (opcional) | R$ | Entrada do usuário |

---

## 3. Modelo Matemático Proposto

### 3.1 Função Objetivo

$$\boxed{\min_{N} \; C(N)}$$

#### 3.1.1 Versão Inicial (sem custo fixo)

$$C(N) = N \cdot C_{\text{unit}}$$

#### 3.1.2 Versão Estendida (com custo fixo — não usada na primeira versão)

$$C(N) = C_{\text{fixo}} + N \cdot C_{\text{unit}}$$

> 🟡 **Hipótese adotada:** A primeira versão do modelo utiliza **apenas custo variável linear** ($C(N) = N \cdot C_{\text{unit}}$). Custos fixos (inversor, estrutura base, projeto, licenças) não são modelados por falta de dados. Esta limitação deve ser declarada no TCC.

### 3.2 Modelo de Geração Energética Mensal

Para cada mês $m \in \{1,\dots,12\}$:

$$E_m(N) = N \cdot \frac{P_{\text{módulo}}}{1000} \cdot HSP_m \cdot D \cdot \eta$$

| Símbolo | Significado | Unidade |
|---------|-------------|---------|
| $E_m(N)$ | Energia estimada no mês $m$ | kWh/mês |
| $P_{\text{módulo}}$ | Potência nominal do módulo | Wp |
| $HSP_m$ | Horas de sol pico no mês $m$ | h/dia (≡ kWh/m²/dia) |
| $D$ | Dias considerados no mês | dias |
| $\eta$ | Fator global de desempenho | adimensional |

> ✅ **Confirmado pela auditoria:** A fórmula acima é **dimensionalmente coerente** (kW × h/dia × dia = kWh). A fórmula anterior no código utilizava `panel_power_wp` (em Wp) diretamente como se fosse kWp, sem a divisão por 1000, resultando em superestimação numérica da geração (fator 1000). A nova fórmula aplica a conversão Wp → kWp corretamente. A área do módulo não entra na fórmula quando se utiliza a potência elétrica nominal do módulo (kWp), que já representa a saída elétrica do painel sob condições padrão.

> 🟡 **Hipótese adotada:** $D = 30$ dias para todos os meses (hipótese simplificadora uniforme).

> ⏳ **Pendente de validação:** 
> - Confirmar que `panel_power_wp = 550` no JSON representa **Wp** (não kWp).
> - Confirmar que `irradiance_kwh_m2_day` e `HSP_m` representam **horas de sol pico** (h/dia ≡ kWh/m²/dia).
> - Confirmar que `system_efficiency = 0.82` representa **fator global de desempenho** (perdas de inversor, temperatura, cabeamento, sujeira, mismatch) e não duplica perdas já embutidas no HSP.

### 3.3 Restrições

#### 3.3.1 Restrição Energética — Obrigatória (Mês Crítico)

$$\boxed{E_m(N) \ge E_{\text{consumo}} \quad \forall m \in \{1,\dots,12\}}$$

Equivalentemente:

$$N \ge \max_{m} \left\lceil \frac{E_{\text{consumo}}}{\frac{P_{\text{módulo}}}{1000} \cdot HSP_m \cdot D \cdot \eta} \right\rceil$$

> 🟡 **Decisão adotada:** **Mês crítico** (pior caso mensal) para garantir atendimento integral em todos os meses. A média anual **não** é usada como critério de viabilidade.

> ⏳ **Limitação dos dados:** O arquivo `irradiance_mock.json` contém dados mensais **apenas para João Pessoa**. As outras 5 cidades em `cities_mock.json` têm apenas média anual. Para cidades sem dados mensais, a restrição energética **não pode ser verificada mês a mês** com os dados atuais. Esta limitação deve ser declarada explicitamente no TCC.

> 🟡 **Decisão de escopo adotada:** **Experimentos principais (atendimento integral mensal): apenas João Pessoa**, utilizando os 12 valores mensais de `irradiance_mock.json`. **Experimentos complementares:** as outras 5 cidades podem ser apresentadas usando a média anual de `cities_mock.json` como HSP constante, mas **sem afirmar atendimento integral em todos os meses** — rotuladas como "estimativa baseada em mês médio". Isso preserva o escopo regional do trabalho sem atribuir aos dados uma precisão que eles não possuem.

#### 3.3.2 Restrição Física (Área) — Obrigatória

$$\boxed{N \cdot A_{\text{módulo}} \le A_{\text{útil}}}$$

$$N_{\max} = \left\lfloor \frac{A_{\text{útil}}}{A_{\text{módulo}}} \right\rfloor$$

> ✅ **Confirmado pela auditoria:** O código atual calcula `max_panels_by_roof` exatamente como $\lfloor A_{\text{útil}} / A_{\text{módulo}} \rfloor$ com `DEFAULT_ROOF_USABLE_FACTOR = 0.85`.

> 🟡 **Hipótese adotada:** Fator de aproveitamento $f = 0.85$ aplicado sobre área bruta ($A_{\text{útil}} = A_{\text{bruta}} \times 0.85$). **Hipótese simplificadora** — não substitui projeto de layout, não considera orientação, inclinação, obstáculos, espaçamentos entre fileiras ou sombreamento.

#### 3.3.3 Restrição de Orçamento — Opcional

$$\boxed{C(N) \le B_{\max} \quad \text{se } B_{\max} \text{ for informado}}$$

> 🟡 **Hipótese adotada:** Orçamento é restrição **dura** quando informado. Se não informado, não se aplica.

#### 3.3.4 Restrição de Integralidade

$$\boxed{N \in \mathbb{Z}_{\ge 0}}$$

$N = 0$ → inviável para $E_{\text{consumo}} > 0$.

---

### 3.4 Formulação Consolidada

$$\begin{aligned}
\min_{N} \quad & C(N) = N \cdot C_{\text{unit}} \\
\text{s.t.} \quad & N \cdot \frac{P_{\text{módulo}}}{1000} \cdot HSP_m \cdot D \cdot \eta \ge E_{\text{consumo}} - \varepsilon_E \quad \forall m \in \{1,\dots,12\} \\
& N \cdot A_{\text{módulo}} \le A_{\text{útil}} + \varepsilon_A \\
& N \cdot C_{\text{unit}} \le B_{\max} + \varepsilon_B \quad \text{(se } B_{\max} \text{ informado)} \\
& N \in \mathbb{Z}_{\ge 0}
\end{aligned}$$

> 🟡 **Hipótese adotada:** As tolerâncias numéricas $\varepsilon_E = 10^{-9}$ kWh, $\varepsilon_A = 10^{-9}$ m², $\varepsilon_B = 10^{-6}$ R$ são definidas na Seção 6.2.2 e aplicadas consistentemente em todos os métodos (analítica, exaustiva, AG).

---

## 4. Solução Analítica (Referência Prática)

Dada a linearidade do modelo, a solução ótima pode ser obtida diretamente. **A solução analítica incorpora as mesmas tolerâncias numéricas** da avaliação computacional (Seção 6.2.2), garantindo consistência entre os três métodos.

### 4.1 Quantidade Mínima por Energia (Mês Crítico, com Tolerância)

$$N_{\text{energia}} = \max_{m} \left\lceil \frac{E_{\text{consumo}} - \varepsilon_E}{\frac{P_{\text{módulo}}}{1000} \cdot HSP_m \cdot D \cdot \eta} \right\rceil$$

Onde $\varepsilon_E = 10^{-9}$ kWh. Se o numerador se tornar $\le 0$ (consumo muito pequeno), define-se $N_{\text{energia}} = 1$ (pelo menos um módulo para consumo positivo).

### 4.2 Limite por Área (com Tolerância)

$$N_{\text{área}} = \left\lfloor \frac{A_{\text{útil}} + \varepsilon_A}{A_{\text{módulo}}} \right\rfloor$$

Onde $\varepsilon_A = 10^{-9}$ m².

### 4.3 Limite por Orçamento (se aplicável, com Tolerância)

$$N_{\text{orçamento}} = \left\lfloor \frac{B_{\max} + \varepsilon_B}{C_{\text{unit}}} \right\rfloor \quad \text{(apenas se } B_{\max} \text{ for informado)}$$

Onde $\varepsilon_B = 10^{-6}$ R$.

### 4.4 Limite Combinado e Viabilidade

$$N_{\text{limite}} = \min\left(N_{\text{área}},\; N_{\text{orçamento}}\right) \quad \text{(se } B_{\max} \text{ informado; caso contrário, } N_{\text{limite}} = N_{\text{área}}\text{)}$$

A solução é **viável** se e somente se:

$$N_{\text{energia}} \le N_{\text{limite}}$$

Nesse caso, a solução ótima (menor custo) é:

$$N^* = N_{\text{energia}}$$

Pois o custo $C(N) = N \cdot C_{\text{unit}}$ é estritamente crescente em $N$, e $N_{\text{energia}}$ é o menor $N$ que atende à restrição energética dentro da tolerância.

Se $N_{\text{energia}} > N_{\text{limite}}$ → **problema inviável**. Reportar qual restrição falhou:
- $N_{\text{energia}} > N_{\text{área}}$ → "Área insuficiente"
- $N_{\text{energia}} > N_{\text{orçamento}}$ → "Orçamento insuficiente"

> 🟡 **Hipótese adotada:** O consumo é obrigatoriamente positivo ($E_{\text{consumo}} > 0$) e todos os parâmetros energéticos são válidos ($P_{\text{módulo}}, HSP_m, D, \eta > 0$). A busca exaustiva, a solução analítica e a avaliação do AG **devem retornar exatamente a mesma quantidade $N^*$ e o mesmo custo** quando existir solução viável, pois todos compartilham a mesma definição de viabilidade com tolerâncias.

---

## 5. Busca Exaustiva (Referência de Ótimo no Modelo)

### 5.1 Algoritmo

```
exhaustive_search(problem):
    N_max = floor(problem.usable_area / problem.panel_area)
    best = None
    for N in 0 .. N_max:
        if is_feasible(N, problem):
            cost = N * problem.unit_cost
            if best is None or cost < best.cost:
                best = {N: N, cost: cost, feasible: True}
    if best is None:
        return {feasible: False, reason: "nenhum N viável encontrado"}
    return best
```

### 5.2 Verificação de Viabilidade (com Tolerância)

```
is_feasible(N, problem):
    if N == 0 and problem.consumption > 0: return False
    for m in 1..12:
        E = N * (problem.panel_power_wp / 1000) * problem.HSP[m] * 30 * problem.efficiency
        if E < problem.consumption - EPS_ENERGY: return False
    if N * problem.panel_area > problem.usable_area + EPS_AREA: return False
    if problem.budget is not None and N * problem.unit_cost > problem.budget + EPS_BUDGET: return False
    return True
```

> 🟡 **Hipótese adotada:** A busca exaustiva utiliza **exatamente a mesma política de viabilidade** da avaliação do AG (Seção 6.2.2), com as mesmas tolerâncias $\varepsilon_E, \varepsilon_A, \varepsilon_B$. Isso garante que `exhaustive_search` e `evaluate_candidate` classifiquem a viabilidade de forma idêntica para as mesmas entradas. A busca exaustiva percorre $N = 0 \dots N_{\max}$ onde $N_{\max} = \lfloor A_{\text{útil}} / A_{\text{módulo}} \rfloor$. Para os parâmetros atuais (área máx. ~70 m², painel 2.2 m² → $N_{\max} \approx 31$), o espaço de busca é trivial (< 100 avaliações). Isso confirma que **a busca exaustiva encontra o ótimo global instantaneamente** neste modelo.

---

## 6. Função de Avaliação do AG (Feasibility-First)

O AG deve priorizar viabilidade sobre custo. Não usar soma ponderada de grandezas incompatíveis.

### 6.1 Visão Geral da Estratégia de Seleção (Introdução Conceitual)

A regra de seleção **oficial e completa** é a **Comparação Lexicográfica** definida na **Seção 6.3**. A descrição abaixo é apenas uma introdução conceitual simplificada; a implementação deve utilizar exclusivamente `compare_lexicographic` da Seção 6.3.

Em alto nível, a prioridade é:

1. **Viável** sempre vence **inviável**.
2. Entre **viáveis**: **menor custo** vence.
3. Entre **inviáveis**: **menor violação total** vence.
4. Desempates: menor déficit energético relativo → menor quantidade de módulos.

> 🟡 **Hipótese adotada:** A regra operacional completa, com todos os desempates e o contrato do objeto `EvaluationResult`, está definida na **Seção 6.3**. A implementação deve utilizar exclusivamente `compare_lexicographic` da Seção 6.3. Esta seção (6.1) é apenas uma introdução conceitual.

$$\text{viol}(N) = \underbrace{\frac{\max\left(0, E_{\text{consumo}} - \min_m E_m(N) - \varepsilon_E\right)}{E_{\text{consumo}}}}_{\text{violação energética relativa}} + \underbrace{\frac{\max\left(0, N \cdot A_{\text{módulo}} - A_{\text{útil}} - \varepsilon_A\right)}{A_{\text{útil}}}}_{\text{violação de área relativa}} + \underbrace{\frac{\max\left(0, N \cdot C_{\text{unit}} - B_{\max} - \varepsilon_B\right)}{B_{\max}}}_{\text{violação orçamentária (se aplicável)}}$$

> 🟡 **Hipótese adotada:** Violações normalizadas relativamente (0 a 1+) para permitir comparação entre restrições de naturezas diferentes. Soma simples assume pesos iguais entre tipos de violação — aceitável para ordenação de inviáveis, não para fitness final. As tolerâncias $\varepsilon_E, \varepsilon_A, \varepsilon_B$ são definidas na Seção 6.2.2.

### 6.2.1 Validação de Entrada (Pré-condições do Modelo)

Para que as fórmulas de violação e a avaliação sejam matematicamente bem-definidas, os seguintes parâmetros devem satisfazer as condições abaixo **antes** de qualquer cálculo:

| Parâmetro | Símbolo | Condição | Justificativa |
|-----------|---------|----------|---------------|
| Consumo mensal | $E_{\text{consumo}}$ | $> 0$ | Denominador na violação energética; problema trivial se 0 |
| Área útil | $A_{\text{útil}}$ | $> 0$ | Denominador na violação de área (normalização); área positiva menor que a do módulo resulta em $N_{\max}=0$, classificado como inviável por restrição física |
| Área do módulo | $A_{\text{módulo}}$ | $> 0$ | Divisão por zero em $N_{\max}$ |
| Potência do módulo | $P_{\text{módulo}}$ | $> 0$ | Divisão por zero em $N_{\text{energia}}$ |
| HSP mensal | $HSP_m$ | $> 0 \quad \forall m$ | Divisão por zero em $N_{\text{energia}}$; geração nula |
| Eficiência | $\eta$ | $0 < \eta \le 1$ | Fator de desempenho físico |
| Custo unitário | $C_{\text{unit}}$ | $> 0$ | Custo nulo ou negativo não faz sentido |
| Orçamento informado | $B_{\max}$ | $> 0$ (se fornecido) | Denominador na violação orçamentária |

> ✅ **Confirmado pela auditoria:** O código atual possui `validate_roof_input` em `src/utils/validators.py` que checa largura, comprimento, consumo e orçamento positivos. As validações de parâmetros do painel e irradiância devem ser adicionadas no ponto de entrada do modelo (`build_problem` ou nova camada de avaliação).

> 🟡 **Hipótese adotada:** A validação falha rápido (exceção) se qualquer pré-condição não for satisfeita. Não há valores default silenciosos para parâmetros inválidos.

### 6.2.2 Tolerância Numérica para Verificação de Viabilidade

Para evitar classificações incorretas por erros de ponto flutuante em situações de fronteira (ex.: geração estimada praticamente igual ao consumo), define-se a seguinte política de tolerância:

| Verificação | Tolerância | Condição de Viabilidade | Fórmula de Violação (para ordenar inviáveis) |
|-------------|------------|------------------------|----------------------------------------------|
| Energia (mês $m$) | $\varepsilon_E = 10^{-9}$ kWh | $E_m(N) \ge E_{\text{consumo}} - \varepsilon_E$ | $V_E = \frac{\max(0, E_{\text{consumo}} - E_m(N) - \varepsilon_E)}{E_{\text{consumo}}}$ |
| Área | $\varepsilon_A = 10^{-9}$ m² | $N \cdot A_{\text{módulo}} \le A_{\text{útil}} + \varepsilon_A$ | $V_A = \frac{\max(0, N \cdot A_{\text{módulo}} - A_{\text{útil}} - \varepsilon_A)}{A_{\text{útil}}}$ |
| Orçamento | $\varepsilon_B = 10^{-6}$ R$ | $N \cdot C_{\text{unit}} \le B_{\max} + \varepsilon_B$ | $V_B = \frac{\max(0, N \cdot C_{\text{unit}} - B_{\max} - \varepsilon_B)}{B_{\max}}$ |

- **Justificativa:** As tolerâncias são ordens de magnitude menores que a precisão física dos dados de entrada (HSP em casas decimais, custo em centavos, área em cm²). Não alteram parâmetros físicos nem hipóteses do modelo.
- **Aplicação consistente:** A mesma tolerância é usada na verificação de viabilidade (`is_feasible`), no cálculo de violações, na busca exaustiva e na solução analítica.
- **Viabilidade numérica:** Um candidato é **viável** se e somente se **todas** as restrições forem satisfeitas dentro de suas respectivas tolerâncias.
- **Violação relativa:** Excessos dentro da tolerância não geram violação positiva (fórmula acima). A violação total é $V = V_E + V_A + V_B$.

> 🟡 **Hipótese adotada:** $\varepsilon_E = 10^{-9}$ kWh, $\varepsilon_A = 10^{-9}$ m², $\varepsilon_B = 10^{-6}$ R$. Valores conservadores, ordens de magnitude abaixo da precisão dos dados de entrada.

### 6.3 Comparação Lexicográfica (Regra Oficial de Seleção)

A abordagem **feasibility-first** é naturalmente expressa como **comparação lexicográfica** entre dois indivíduos. **Não há fallback escalar** — a implementação deve utilizar `compare_lexicographic` diretamente no operador de torneio do AG. Se a arquitetura atual do AG exigir uma função `fitness` escalar, deve-se adaptar o operador de seleção para aceitar um comparador personalizado (`key` ou `cmp`), em vez de introduzir uma aproximação escalar que não garante a preservação da ordem lexicográfica.

#### Regra de Comparação Lexicográfica (Regra Oficial)

Dado dois indivíduos $A$ e $B$ com avaliações completas (incluindo `num_panels`), a regra oficial é:

```
def compare_lexicographic(A: EvaluationResult, B: EvaluationResult) -> EvaluationResult:
    """
    Comparação lexicográfica feasibility-first (Regra Oficial).
    Retorna o indivíduo superior.
    """
    # 1. Viabilidade tem prioridade absoluta
    if A.feasible and not B.feasible:
        return A
    if not A.feasible and B.feasible:
        return B
    
    # 2. Ambos viáveis: menor custo vence
    if A.feasible and B.feasible:
        if A.cost != B.cost:
            return A if A.cost < B.cost else B
    
    # 3. Ambos inviáveis: menor violação total vence
    if A.violation != B.violation:
        return A if A.violation < B.violation else B
    
    # 4. Desempate: menor déficit energético relativo
    if A.energy_violation != B.energy_violation:
        return A if A.energy_violation < B.energy_violation else B
    
    # 5. Desempate final: menor quantidade de módulos (determinístico)
    return A if A.num_panels < B.num_panels else B
```

> 🟡 **Hipótese adotada:** A implementação **deve** usar `compare_lexicographic` diretamente no torneio do AG (sem fitness escalar). Se o operador de seleção atual exigir uma função `fitness` escalar, deve-se adaptar o operador para aceitar um comparador personalizado (ex.: `key=functools.cmp_to_key(compare_lexicographic)` ou sobrescrever `__lt__` em `EvaluationResult`). **Não existe fallback escalar** — nenhuma constante de separação de faixas (`1_000_000`, `1e9`, `LARGE_CONSTANT`), nenhuma função `fitness_from_evaluation`, nenhum `fitness_scalar` em `EvaluationResult`. Qualquer aproximação escalar que não garanta a preservação exata da ordem lexicográfica é proibida.

> ✅ **Confirmado pela auditoria:** A comparação lexicográfica elimina a necessidade de pesos arbitrários entre restrições e garante que **qualquer solução viável é estritamente superior a qualquer inviável**, independentemente da magnitude numérica dos custos ou violações.

---

## 7. Métodos de Referência e Comparação Experimental

### 7.1 Três Métodos a Comparar

| Método | Funcionamento | Papel no TCC |
|--------|---------------|--------------|
| **Solução Analítica** | Calcula $N_{\text{viável}}$ diretamente via fórmulas (Seção 4) | Referência prática — o que um engenheiro faria |
| **Busca Exaustiva** | Avalia todo $N \in [0, N_{\max}]$, seleciona viável de menor custo | Referência de ótimo global no modelo matemático |
| **Algoritmo Genético** | Busca evolutiva com operadores atuais, avaliação feasibility-first | Método investigado — objeto de estudo do TCC |

### 7.2 Condições de Comparação Justa

- **Mesmas entradas:** consumo, área, painel, irradiância, eficiência, custo, orçamento.
- **Mesmo modelo energético:** mês crítico, 30 dias, $\eta$ global.
- **Mesmas restrições:** energia (12 meses), área, orçamento opcional.
- **Múltiplas execuções do AG:** pelo menos 30 runs com seeds diferentes para estatísticas.

### 7.3 Métricas Principais

| Métrica | Definição | Aplicável a |
|---------|-----------|-------------|
| $N_{\text{solução}}$ | Quantidade de módulos | Todos |
| $E_m$ | Geração estimada por mês | Todos |
| $\text{Atendimento}_m(\\%) = \min\left(1,\frac{E_m}{E_{\text{consumo}}}\right)\times100$ | % atendimento por mês | Todos |
| $C(N)$ | Custo estimado | Todos |
| $\text{Ocupação} = N \cdot A_{\text{módulo}} / A_{\text{útil}}$ | Ocupação da área | Todos |
| $\text{Viável?}$ | Sim/Não | Todos |
| $\text{Motivo inviabilidade}$ | Energia/Área/Orçamento | Se inviável |
| $\text{Gap}\% = \frac{C_{\text{AG}} - C_{\text{exaustiva}}}{C_{\text{exaustiva}}} \times 100$ | Diferença de custo vs ótimo | Apenas se ambos viáveis |
| $\text{Taxa viabilidade}_{\text{AG}} = \frac{\text{runs viáveis}}{\text{total runs}}$ | Estabilidade do AG | Apenas AG |
| $C_{\text{média viáveis}}$ | Custo médio entre runs viáveis | Apenas AG |
| $t_{\text{execução}}$ | Tempo de CPU | Todos |

> 🟡 **Hipótese adotada:** `Gap%` só calculado quando **tanto o AG quanto a busca exaustiva encontram solução viável**. Se o AG falha em encontrar viável em alguma run, reporta-se taxa de viabilidade e melhor custo entre as viáveis.

---

## 8. Inventário de Parâmetros (Valores Atuais do Projeto)

| Parâmetro | Valor Atual | Unidade | Arquivo Origem | Categoria |
|-----------|-------------|---------|----------------|-----------|
| `panel_power_wp` | 550.0 | Wp | `panels_mock.json` | ✅ Confirmado |
| `panel_area_m2` | 2.2 | m² | `panels_mock.json` | ✅ Confirmado |
| `panel_cost_brl` | 1100.0 | R$ | `panels_mock.json` | ✅ Confirmado |
| `installation_cost_per_panel_brl` | 250.0 | R$/painel | `panels_mock.json` | ✅ Confirmado |
| `system_efficiency` | 0.82 | — | `panels_mock.json` | ✅ Confirmado (valor) / 🟡 Hipótese (interpretação) |
| `irradiance_kwh_m2_day` (João Pessoa) | 5.4 | kWh/m²/dia | `cities_mock.json` | ✅ Confirmado (média anual) |
| `HSP_m` (João Pessoa) | jan:5.7 ... dez:5.8 | kWh/m²/dia | `irradiance_mock.json` | ✅ Confirmado (apenas JP) / ⏳ Pendente (outras cidades) |
| `DEFAULT_ROOF_USABLE_FACTOR` | 0.85 | — | `constants.py` | ✅ Confirmado (valor) / 🟡 Hipótese (interpretação) |
| `DEFAULT_DAYS_PER_MONTH` | 30 | dias | `constants.py` | ✅ Confirmado (valor) / 🟡 Hipótese (uniforme) |
| `cost_weight_alpha` | 0.08 | — | `config.py` | ✅ Confirmado (fitness antiga) / **não usado no novo modelo** |
| `waste_penalty_weight` | 0.9 | — | `config.py` | ✅ Confirmado (fitness antiga) / **não usado no novo modelo** |
| `deficit_penalty_weight` | 1.5 | — | `config.py` | ✅ Confirmado (fitness antiga) / **não usado no novo modelo** |
| `budget_penalty_weight` | 2.0 | — | `config.py` | ✅ Confirmado (fitness antiga) / **não usado no novo modelo** |

> **Custo unitário consolidado:** $C_{\text{unit}} = 1100 + 250 = 1350$ R$/painel$ (módulo + instalação por painel). Não inclui inversor, estrutura fixa, projeto, licenças, conexão.

---

## 9. Limitações Explícitas do Modelo (para o TCC)

| Limitação | Impacto | Mitigação no TCC |
|-----------|---------|------------------|
| **Dados mensais apenas para João Pessoa** | Restrição de mês crítico não verificável para outras 5 cidades | Declarar explicitamente; usar média anual como proxy para outras cidades, com ressalva |
| **Fator 0.85 de área é genérico** | Não reflete layout real, orientação, espaçamentos | Classificar como "hipótese simplificadora"; não apresentar como regra de instalação |
| **Eficiência 0.82 sem decomposição** | Não se sabe quais perdas estão incluídas | Declarar como "fator global de desempenho assumido"; não afirmar que agrega perdas específicas |
| **Custo não inclui inversor/estrutura fixa** | Subestima custo real do sistema | Denominar "custo de módulos + instalação por módulo"; não chamar de "custo total do sistema" |
| **Irradiação = HSP médio** | Não captura variabilidade diária, sombreamento, envelhecimento | Usar termo "estimativa de geração mensal média"; não "garantia de geração" |
| **Consumo mensal constante** | Não considera sazonalidade de consumo | Declarar hipótese; consumo informado como valor único mensal |
| **Dias por mês = 30** | Pequeno erro sazonal | Hipótese simplificadora uniforme |
| **Problema unidimensional (apenas N)** | Busca exaustiva trivializa a otimização | Reconhecer honestamente; justificar AG como objeto de estudo metodológico |

---

## 10. Questões em Aberto (Precisam de Decisão Antes da Implementação)

| # | Questão | Opções | Recomendação |
|---|---------|--------|--------------|
| Q1 | **Escopo de cidades nos experimentos** | (a) Usar média anual como HSP constante para todos os meses em todas as cidades<br>(b) Restringir experimentos principais a João Pessoa (dados mensais); outras cidades apenas como complemento com média anual | (b) adotada — experimentos principais de atendimento integral mensal apenas em João Pessoa; outras cidades apenas complementares com média anual, rotuladas como estimativa de mês médio |
| Q2 | **Validação da unidade de `irradiance_kwh_m2_day`** | Confirmar que 5.4 = HSP (h/dia ≡ kWh/m²/dia) e não irradiância instantânea (W/m²) | Verificar fonte declarada "Mock inspirado em INPE/SONDA" — SONDA fornece irradiação global horizontal média diária em Wh/m²/dia |
| Q3 | **Interpretação de `system_efficiency = 0.82`** | (a) Fator global (inversor + temperatura + cabeamento + sujeira + mismatch)<br>(b) Apenas eficiência do inversor<br>(c) Valor arbitrário | (a) como hipótese; declarar que não há decomposição documentada |
| Q4 | **Mês crítico vs. média anual na restrição** | Mês crítico (adotado) vs. média anual | Mês crítico mantido; média anual apenas como indicador complementar |

---

## 11. Pseudocódigo Completo da Avaliação (para Implementação)

```python
# Constantes de tolerância numérica (Seção 6.2.2)
EPS_ENERGY = 1e-9    # kWh
EPS_AREA = 1e-9      # m²
EPS_BUDGET = 1e-6    # R$

def _require_finite(name: str, value: float) -> None:
    """Valida que um parâmetro numérico é finito (não NaN, não infinito)."""
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} deve ser um número finito")

def evaluate_candidate(N: int, problem: Problem) -> EvaluationResult:
    """
    Avalia um candidato N segundo o modelo feasibility-first.
    Retorna EvaluationResult com todos os campos necessários para compare_lexicographic.
    NÃO retorna fitness escalar — a comparação é lexicográfica (Seção 6.3).
    """
    import math
    
    # --- Validação de domínio de N (Seção 3.4: N ∈ ℤ≥₀) ---
    # bool é subclasse de int em Python; rejeitar explicitamente
    if isinstance(N, bool) or not isinstance(N, int):
        raise ValueError("N deve ser um número inteiro")
    if N < 0:
        raise ValueError("N deve ser >= 0")
    
    # --- Validação de entrada: finitude (Seção 6.2.1) ---
    _require_finite("consumption", problem.consumption)
    _require_finite("usable_area", problem.usable_area)
    _require_finite("panel_area", problem.panel_area)
    _require_finite("panel_power_wp", problem.panel_power_wp)
    _require_finite("efficiency", problem.efficiency)
    _require_finite("unit_cost", problem.unit_cost)
    for m in range(1, 13):
        _require_finite(f"HSP[{m}]", problem.HSP[m])
    if problem.budget is not None:
        _require_finite("budget", problem.budget)
    
    # --- Validação de entrada: intervalos (Seção 6.2.1) ---
    if problem.consumption <= 0:
        raise ValueError("consumption deve ser > 0")
    if problem.usable_area <= 0:
        raise ValueError("usable_area deve ser > 0")
    if problem.panel_area <= 0:
        raise ValueError("panel_area deve ser > 0")
    if problem.panel_power_wp <= 0:
        raise ValueError("panel_power_wp deve ser > 0")
    if problem.efficiency <= 0 or problem.efficiency > 1:
        raise ValueError("efficiency deve estar em (0, 1]")
    if problem.unit_cost <= 0:
        raise ValueError("unit_cost deve ser > 0")
    for m in range(1, 13):
        if problem.HSP[m] <= 0:
            raise ValueError(f"HSP[{m}] deve ser > 0")
    if problem.budget is not None and problem.budget <= 0:
        raise ValueError("budget, se informado, deve ser > 0")
    
    # --- N = 0 é candidato válido no domínio, mas inviável para consumo > 0 ---
    if N == 0:
        return EvaluationResult(
            num_panels=0,
            feasible=False,
            cost=0.0,
            violation=1.0,
            energy_violation=1.0,
            area_violation=0.0,
            budget_violation=0.0,
            energy_by_month={m: 0.0 for m in range(1, 13)},
            used_area=0.0,
            occupancy=0.0,
            details={"reason": "N=0 não atende consumo > 0"}
        )
    
    # --- Restrição energética: mês crítico (com tolerância) ---
    energy_by_month = {}
    energy_violation = 0.0
    for m in range(1, 13):
        E = N * (problem.panel_power_wp / 1000.0) * problem.HSP[m] * 30.0 * problem.efficiency
        energy_by_month[m] = E
        # Violação desconta a tolerância: max(0, consumo - E - ε_E) / consumo
        deficit = problem.consumption - E - EPS_ENERGY
        if deficit > 0:
            energy_violation = max(energy_violation, deficit / problem.consumption)
    
    # --- Restrição de área (com tolerância) ---
    used_area = N * problem.panel_area
    # Violação desconta a tolerância: max(0, used_area - A_útil - ε_A) / A_útil
    excess_area = used_area - problem.usable_area - EPS_AREA
    area_violation = max(0.0, excess_area) / problem.usable_area if excess_area > 0 else 0.0
    
    # --- Restrição orçamentária (com tolerância) ---
    budget_violation = 0.0
    cost = N * problem.unit_cost
    if problem.budget is not None:
        # Violação desconta a tolerância: max(0, cost - B_max - ε_B) / B_max
        excess_budget = cost - problem.budget - EPS_BUDGET
        budget_violation = max(0.0, excess_budget) / problem.budget if excess_budget > 0 else 0.0
    
    # --- Viabilidade com tolerância numérica ---
    feasible = (energy_violation == 0.0 and area_violation == 0.0 and budget_violation == 0.0)
    total_violation = energy_violation + area_violation + budget_violation
    
    return EvaluationResult(
        num_panels=N,
        feasible=feasible,
        cost=cost,
        violation=total_violation,
        energy_violation=energy_violation,
        area_violation=area_violation,
        budget_violation=budget_violation,
        energy_by_month=energy_by_month,
        used_area=used_area,
        occupancy=used_area / problem.usable_area
    )


def compare_lexicographic(A: EvaluationResult, B: EvaluationResult) -> EvaluationResult:
    """
    Comparação lexicográfica feasibility-first (Regra Oficial, Seção 6.3).
    Retorna o indivíduo superior.
    """
    # 1. Viabilidade tem prioridade absoluta
    if A.feasible and not B.feasible:
        return A
    if not A.feasible and B.feasible:
        return B
    
    # 2. Ambos viáveis: menor custo vence
    if A.feasible and B.feasible:
        if A.cost != B.cost:
            return A if A.cost < B.cost else B
    
    # 3. Ambos inviáveis: menor violação total vence
    if A.violation != B.violation:
        return A if A.violation < B.violation else B
    
    # 4. Desempate: menor déficit energético relativo
    if A.energy_violation != B.energy_violation:
        return A if A.energy_violation < B.energy_violation else B
    
    # 5. Desempate final: menor quantidade de módulos (determinístico)
    return A if A.num_panels < B.num_panels else B
```

---

## 12. Próximos Passos (Após Aprovação deste Documento)

1. **Implementar** `evaluate_candidate` / `is_feasible` / `exhaustive_search` / `analytical_solution` em novo módulo `src/simulation/evaluation.py` (não alterar `fitness.py` antigo).
2. **Criar testes de validação do modelo** (não reprodutibilidade):
   - Coerência dimensional
   - Monotonicidade de energia e custo em $N$
   - Viabilidade respeita todas as restrições
   - Analítica = Exaustiva = Ótimo do modelo
   - AG com feasibility-first encontra ótimo em taxa alta
3. **Atualizar `runner.py`** para usar nova avaliação e rodar os 3 métodos.
4. **Atualizar API/Backend** para expor endpoints de comparação.
5. **Atualizar Frontend** para exibir resultados dos 3 métodos lado a lado.
6. **Documentar resultados experimentais** no TCC II.

---

## 13. Autorização

> **Este documento é uma especificação científica.**  
> **Nenhuma alteração de código foi realizada.**  
> **A implementação só inicia após revisão e aprovação explícita deste documento pelo orientador/autor.**

---

**Fim da Especificação E5.2**  
**Próxima entrega:** Implementação condicionada à aprovação.