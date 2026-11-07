# E5.1 — Auditoria Matemática do Modelo de Dimensionamento Fotovoltaico

**Data:** 03/11/2026  
**Projeto:** TCC — Aplicação de Algoritmos Genéticos no Dimensionamento de Sistemas Fotovoltaicos Residenciais na Região do Nordeste Brasileiro  
**Autor da auditoria:** Agente de revisão técnica (não desenvolvedor)  
**Escopo:** Código-fonte em `src/`, dados em `data/`, testes em `tests/`  
**Regra:** Não modificar nada — apenas inspecionar, documentar e diagnosticar.

---

## 1. Resumo Executivo

Esta auditoria examina o modelo matemático atualmente implementado no protótipo do TCC. O sistema combina:

- **Modelo energético simplificado** para estimativa de geração mensal (kWh/mês)
- **Modelo físico de área** para limitar quantidade de painéis pelo telhado
- **Modelo econômico unitário** (custo = painéis × custo por painel)
- **Função fitness** que combina energia (positivo) e penalidades (negativas) em uma única pontuação escalar
- **Algoritmo genético** com cromossomo inteiro (número de painéis) operando sobre esse fitness
- **Baseline (dimensionamento direto)** que calcula painéis pelo consumo e limita pela área

**Principais achados:**

| Item | Status | Gravidade |
|------|--------|-----------|
| Fórmula de energia dimensionalmente inconsistente (ignora `panel_area_m2`) | Confirmado | **Crítico** |
| Fitness soma grandezas incompatíveis (kWh + R$ + m²) sem normalização | Confirmado | **Crítico** |
| Penalidade de área usa peso de déficit (`deficit_penalty_weight`) em vez de peso próprio | Confirmado | **Alto** |
| Crossover pode gerar `child_b = max_panels + 1` (fora dos limites) | Confirmado | **Alto** |
| Dados de irradiância são mockados (média anual única, sem variabilidade mensal real) | Confirmado | **Médio** |
| `system_efficiency` vem do painel, não da cidade/sistema | Confirmado | **Médio** |
| Baseline usa `GAConfig` padrão (pesos de fitness) em vez de configuração própria | Confirmado | **Baixo** |
| Testes verificam reproduzibilidade numérica, não validade física/matemática | Confirmado | **Médio** |

O modelo **não é matematicamente coerente** em sua forma atual. A função fitness mistura unidades distintas (energia, custo, área) com pesos arbitrários, o que torna a otimização dependente de escala e impede interpretação física dos resultados. A fórmula de energia ignora a área do painel, o que é dimensionalmente incorreto. O baseline e o AG compartilham a mesma função fitness, mas o baseline não otimiza — apenas calcula um ponto e o avalia com os mesmos pesos.

---

## 2. Arquitetura Matemática do Modelo Atual

### 2.1 Fluxo de Dados

```
Entrada do usuário (RoofInput)
    │
    ▼
build_problem()  ──► Dicionário `problem` com 13 chaves
    │                         │
    │                         ├── Parâmetros físicos: irradiance, panel_power_wp, panel_area_m2, system_efficiency
    │                         ├── Parâmetros econômicos: panel_cost_brl (+ installation_cost_per_panel_brl)
    │                         └── Restrições: roof_usable_area_m2, max_budget_brl, monthly_consumption_kwh
    │
    ├──► run_genetic_algorithm() ──► Melhor indivíduo (num_panels)
    │                                 │
    │                                 ▼
    │                          evaluate_fitness() ──► fitness_total, energy_kwh, cost_brl
    │
    └──► evaluate_direct_baseline() ──► painéis_diretos, fitness, energia, custo
```

### 2.2 Estrutura do Dicionário `problem` (src/simulation/runner.py:17–32)

| Chave | Origem | Unidade | Descrição |
|-------|--------|---------|-----------|
| `city` | RoofInput | — | Nome da cidade |
| `monthly_consumption_kwh` | RoofInput | kWh/mês | Consumo residencial |
| `roof_area_m2` | RoofInput.gross_area_m2 | m² | Área bruta = largura × comprimento |
| `roof_usable_area_m2` | RoofInput.usable_area_m2() | m² | Área útil = bruta × 0.85 |
| `max_budget_brl` | RoofInput | R$ ou None | Orçamento máximo opcional |
| `roof_type` | RoofInput | — | Tipo de telhado (não usado no cálculo) |
| `irradiance_kwh_m2_day` | cities_mock.json | kWh/m²/dia | Irradiação diária média |
| `panel_power_wp` | panels_mock.json | Wp | Potência de pico do painel |
| `panel_cost_brl` | panels_mock.json | R$ | Custo painel + instalação/painel |
| `panel_area_m2` | panels_mock.json | m² | Área física do painel |
| `system_efficiency` | panels_mock.json | — | Eficiência do sistema (0.82) |

---

## 3. Modelo de Geração Energética

### 3.1 Fórmula Implementada

**Arquivo:** `src/genetic/fitness.py:8–22`

```python
def calc_energy_kwh_month(
    num_panels: int,
    panel_power_wp: float,
    irradiance_kwh_m2_day: float,
    system_efficiency: float,
    days_per_month: int = DEFAULT_DAYS_PER_MONTH,  # = 30
) -> float:
    return (
        num_panels
        * (panel_power_wp / 1000.0)           # Wp → kWp
        * irradiance_kwh_m2_day               # kWh/m²/dia
        * days_per_month                      # dias/mês
        * system_efficiency                   # adimensional
    )
```

**Fórmula matemática:**

$$E_{mensal} = N_{painéis} \times \frac{P_{wp}}{1000} \times H_{sp} \times d_{mês} \times \eta_{sistema}$$

Onde:
- $N_{painéis}$: número inteiro de painéis
- $P_{wp}$: potência de pico do painel [Wp]
- $H_{sp}$: horas de sol pleno (irradiação diária) [kWh/m²/dia]
- $d_{mês}$: dias por mês (fixo = 30)
- $\eta_{sistema}$: eficiência do sistema (adimensional, 0.82)

### 3.2 Análise Dimensional

| Termo | Unidade | Resultado |
|-------|---------|-----------|
| $N_{painéis}$ | — | adimensional |
| $P_{wp}/1000$ | Wp/1000 = kWp | kW |
| $H_{sp}$ | kWh/m²/dia | kWh/m²/dia |
| $d_{mês}$ | dias | dia |
| $\eta_{sistema}$ | — | adimensional |
| **Produto** | kW × kWh/m²/dia × dia | **kWh·kW/m²** ❌ |

**Problema CRÍTICO:** A fórmula resulta em **kWh·kW/m²**, não em kWh. A área do painel ($A_{painel}$ em m²) **não aparece** na fórmula. A irradiação $H_{sp}$ tem unidade kWh/m²/dia (energia por área por tempo). Para obter energia [kWh], precisa-se multiplicar por uma **área** [m²].

**Fórmula dimensionalmente correta seria:**

$$E_{mensal} = N_{painéis} \times A_{painel} \times H_{sp} \times d_{mês} \times \eta_{sistema} \times \frac{P_{wp}}{1000 \times A_{painel} \times 1\text{ kW/m}^2}$$

Ou seja, a potência específica do painel ($P_{wp}/A_{painel}$ em Wp/m²) deve ser usada, ou a área do painel deve entrar explicitamente.

**No código atual:** `panel_area_m2` existe no dicionário `problem` (linha 30 de runner.py) mas **nunca é usado** em `calc_energy_kwh_month`.

### 3.3 Valores de Referência (do painel mock)

| Parâmetro | Valor | Unidade | Fonte |
|-----------|-------|---------|-------|
| `panel_power_wp` | 550.0 | Wp | panels_mock.json |
| `panel_area_m2` | 2.2 | m² | panels_mock.json |
| `system_efficiency` | 0.82 | — | panels_mock.json |
| `irradiance_kwh_m2_day` (João Pessoa) | 5.4 | kWh/m²/dia | cities_mock.json |
| `days_per_month` | 30 | dias | constants.py |

### 3.4 Cálculo com 1 painel (valor de referência dos testes)

$$E = 1 \times \frac{550}{1000} \times 5.4 \times 30 \times 0.82 = 73.062 \text{ kWh/mês}$$

**Teste confirma:** `REF_ENERGY_1 = 73.06200000000001` (tests/test_core.py:42)

### 3.5 Hipóteses e Limitações

1. **Irradiação constante:** Usa média anual única (5.4 kWh/m²/dia), ignora variabilidade mensal (irradiance_mock.json tem dados mensais mas não são usados).
2. **Dias por mês fixo:** 30 dias, ignora meses de 28/29/31 dias.
3. **Eficiência constante:** 0.82 fixa, não varia com temperatura, envelhecimento, sombreamento parcial, orientação/inclinação.
4. **Sem perdas de cabeamento, inversor, mismatch, sujidade** — tudo agregado no 0.82.
5. **Potência nominal (STC):** Assume 550 Wp em condições padrão de teste (1000 W/m², 25°C), não em condições reais de operação (NOCT).
6. **Área do painel ignorada:** Como mostrado, a fórmula é dimensionalmente inconsistente.

---

## 4. Modelo de Dimensionamento Físico

### 4.1 Áreas do Telhado

**Arquivo:** `src/models/roof.py:19–26`

```python
@property
def gross_area_m2(self) -> float:
    return self.width_m * self.length_m

def usable_area_m2(self) -> float:
    return self.gross_area_m2 * DEFAULT_ROOF_USABLE_FACTOR  # 0.85
```

| Conceito | Fórmula | Valor padrão |
|----------|---------|--------------|
| Área bruta | $A_{bruta} = L \times C$ | — |
| Fator de aproveitamento | $f_{aproveitamento} = 0.85$ | constants.py |
| Área útil | $A_{útil} = A_{bruta} \times 0.85$ | — |

### 4.2 Quantidade Máxima de Painéis

**Arquivo:** `src/genetic/algorithm.py:11–13`

```python
def max_panels_by_roof(roof_usable_area_m2: float, panel_area_m2: float) -> int:
    return max(1, int(roof_usable_area_m2 // panel_area_m2))
```

$$N_{max} = \max\left(1, \left\lfloor \frac{A_{útil}}{A_{painel}} \right\rfloor\right)$$

**Exemplo (telhado 8×10 m):**
- $A_{bruta} = 80 \text{ m}^2$
- $A_{útil} = 80 \times 0.85 = 68 \text{ m}^2$
- $A_{painel} = 2.2 \text{ m}^2$
- $N_{max} = \lfloor 68 / 2.2 \rfloor = 30$ painéis

**Teste confirma:** `test_max_panels_by_roof` (tests/test_core.py:152–154)

### 4.3 Ocupação do Telhado

**Arquivo:** `src/simulation/runner.py:65, 79`

```python
area_used = best_individual.num_panels * float(problem["panel_area_m2"])
roof_occupancy_ratio = area_used / max(roof.usable_area_m2(), 0.001)
```

$$\text{Ocupação} = \frac{N_{painéis} \times A_{painel}}{A_{útil}}$$

### 4.4 Limitações do Modelo Físico

| Limitação | Status |
|-----------|--------|
| Não considera orientação (azimute) | Não modelado |
| Não considera inclinação do telhado | Não modelado |
| Não verifica disposição geométrica (layout) | Apenas área total |
| Não considera espaçamento entre fileiras | Não modelado |
| Não considera obstáculos (chaminés, claraboias) | Fator 0.85 genérico |
| Não considera sombreamento (árvores, edifícios) | Não modelado |
| Fator 0.85 é fixo e genérico | Não parametrizado por tipo de telhado |

**O modelo assume que qualquer combinação de painéis que caiba na área total é fisicamente instalável.** Isso superestima a capacidade real de instalação.

---

## 5. Modelo Econômico

### 5.1 Fórmula de Custo

**Arquivo:** `src/genetic/fitness.py:25–27`

```python
def calc_cost_brl(num_panels: int, panel_cost_brl: float) -> float:
    return num_panels * panel_cost_brl
```

$$C_{total} = N_{painéis} \times C_{painel}$$

### 5.2 Composição do `panel_cost_brl`

**Arquivo:** `src/simulation/runner.py:28–29`

```python
"panel_cost_brl": float(panel_data["panel_cost_brl"])
+ float(panel_data["installation_cost_per_panel_brl"]),
```

| Componente | Valor (mock) | Unidade |
|------------|--------------|---------|
| `panel_cost_brl` | 1100.0 | R$/painel |
| `installation_cost_per_panel_brl` | 250.0 | R$/painel |
| **Total por painel** | **1350.0** | **R$/painel** |

**Teste confirma:** `REF_COST_5 = 1350.0 + 250.0 = 1600.0` (tests/test_core.py:44) — *correção: o teste soma, mas o código já soma. O valor unitário final é 1350.0.*

### 5.3 Orçamento e Penalidade

**Arquivo:** `src/genetic/fitness.py:56–60`

```python
budget_penalty = 0.0
budget_limit = problem.get("max_budget_brl")
if budget_limit is not None:
    over_budget = max(cost - float(budget_limit), 0.0)
    budget_penalty = config.budget_penalty_weight * over_budget / 100.0
```

$$\text{Penalidade}_{orçamento} = 
\begin{cases}
w_{budget} \times \frac{\max(C_{total} - B_{max}, 0)}{100} & \text{se } B_{max} \text{ definido} \\
0 & \text{caso contrário}
\end{cases}$$

- $w_{budget} = 2.0$ (GAConfig default)
- Divisão por 100: escala arbitrária para aproximar magnitude das outras penalidades

### 5.4 Limitações Econômicas

| Limitação | Detalhe |
|-----------|---------|
| Custo = apenas painéis + instalação/painel | Ignora inversor, estrutura, cabeamento, mão de obra fixa, projetos, licenças, conexão |
| Custo linear em $N_{painéis}$ | Não captura economias de escala |
| `installation_cost_per_panel_brl` é fixo | Não varia com complexidade do telhado |
| Orçamento só penaliza, não restringe busca | AG pode gerar indivíduos acima do orçamento |
| Divisão por 100 na penalidade | Heurística sem justificativa documentada |

---

## 6. Modelo de Déficit e Excesso Energético

### 6.1 Cálculos

**Arquivo:** `src/genetic/fitness.py:45–46`

```python
waste = max(energy - demand, 0.0)      # excesso (sobra)
deficit = max(demand - energy, 0.0)    # déficit (falta)
```

| Conceito | Fórmula | Unidade |
|----------|---------|---------|
| Geração | $E_{mensal}$ | kWh/mês |
| Consumo (demanda) | $D_{mensal}$ | kWh/mês |
| Excesso (waste) | $\max(E - D, 0)$ | kWh/mês |
| Déficit | $\max(D - E, 0)$ | kWh/mês |

### 6.2 Penalidades Associadas

**Arquivo:** `src/genetic/fitness.py:52–53`

```python
waste_penalty = config.waste_penalty_weight * waste
deficit_penalty = config.deficit_penalty_weight * deficit
```

| Penalidade | Peso padrão | Fórmula |
|------------|-------------|---------|
| Excesso (waste) | $w_{waste} = 0.9$ | $0.9 \times (E - D)^+$ |
| Déficit | $w_{deficit} = 1.5$ | $1.5 \times (D - E)^+$ |

**Assimetria:** Déficit é penalizado 1.67× mais que excesso ($1.5 / 0.9$). Isso reflete preferência por atender o consumo.

### 6.3 Limitações

- Unidades: kWh (energia) multiplicado por peso adimensional → resultado em "kWh ponderados", misturado com R$ e m² na fitness.
- Não há normalização pelo consumo (ex.: % de déficit).
- Não considera valor da energia injetada na rede (compensação, crédito).
- Não considera tarifa de energia (R$/kWh) para converter déficit/excesso em valor econômico.

---

## 7. Função Fitness Completa

### 7.1 Código Fonte

**Arquivo:** `src/genetic/fitness.py:30–76`

```python
def evaluate_fitness_breakdown(num_panels: int, problem: dict, config: GAConfig) -> FitnessBreakdown:
    energy = calc_energy_kwh_month(...)
    cost = calc_cost_brl(num_panels=num_panels, panel_cost_brl=float(problem["panel_cost_brl"]))
    demand = float(problem["monthly_consumption_kwh"])

    waste = max(energy - demand, 0.0)
    deficit = max(demand - energy, 0.0)
    used_area = num_panels * float(problem["panel_area_m2"])
    usable_area = float(problem["roof_usable_area_m2"])
    area_excess = max(used_area - usable_area, 0.0)

    cost_penalty = config.cost_weight_alpha * cost
    waste_penalty = config.waste_penalty_weight * waste
    deficit_penalty = config.deficit_penalty_weight * deficit
    area_penalty = config.deficit_penalty_weight * area_excess * 10.0

    budget_penalty = 0.0
    budget_limit = problem.get("max_budget_brl")
    if budget_limit is not None:
        over_budget = max(cost - float(budget_limit), 0.0)
        budget_penalty = config.budget_penalty_weight * over_budget / 100.0

    fitness_total = (
        energy - cost_penalty - waste_penalty - deficit_penalty - area_penalty - budget_penalty
    )
    ...
```

### 7.2 Fórmula Matemática Completa

$$F(N) = E(N) - \alpha C(N) - w_w \cdot W(N) - w_d \cdot D(N) - w_d \cdot 10 \cdot A_{ex}(N) - w_b \cdot \frac{B_{ex}(N)}{100}$$

Onde:

| Símbolo | Definição | Unidade "bruta" |
|---------|-----------|-----------------|
| $E(N)$ | $N \times \frac{P_{wp}}{1000} \times H_{sp} \times 30 \times \eta$ | kWh/mês |
| $C(N)$ | $N \times C_{painel}$ | R$ |
| $W(N)$ | $\max(E(N) - D, 0)$ | kWh/mês |
| $D(N)$ | $\max(D - E(N), 0)$ | kWh/mês |
| $A_{ex}(N)$ | $\max(N \times A_{painel} - A_{útil}, 0)$ | m² |
| $B_{ex}(N)$ | $\max(C(N) - B_{max}, 0)$ | R$ |

| Parâmetro | Valor padrão | Origem |
|-----------|--------------|--------|
| $\alpha$ (cost_weight_alpha) | 0.08 | GAConfig |
| $w_w$ (waste_penalty_weight) | 0.9 | GAConfig |
| $w_d$ (deficit_penalty_weight) | 1.5 | GAConfig |
| $w_b$ (budget_penalty_weight) | 2.0 | GAConfig |
| Fator 10 em área | 10.0 | Hardcoded (linha 54) |
| Divisor 100 em orçamento | 100.0 | Hardcoded (linha 60) |

### 7.3 Análise de Coerência Dimensional

| Termo | Unidade bruta | Peso | Unidade resultante |
|-------|---------------|------|---------------------|
| $E(N)$ | kWh/mês | 1 (implícito) | kWh/mês |
| $\alpha C(N)$ | R$ | 0.08 | R$ |
| $w_w W(N)$ | kWh/mês | 0.9 | kWh/mês |
| $w_d D(N)$ | kWh/mês | 1.5 | kWh/mês |
| $w_d \cdot 10 \cdot A_{ex}(N)$ | m² | 1.5 × 10 = 15 | m² |
| $w_b \cdot B_{ex}(N)/100$ | R$ | 2.0 / 100 = 0.02 | R$ |

**Resultado:** A fitness soma **kWh + R$ + m²** — **grandezas fisicamente incompatíveis**.

### 7.4 Análise de Escala (Exemplo: Telhado 8×10 m, Consumo 300 kWh/mês)

| $N$ | $E$ (kWh) | $C$ (R$) | $W$ | $D$ | $A_{ex}$ (m²) | $B_{ex}$ | Fitness |
|-----|-----------|----------|-----|-----|---------------|----------|---------|
| 1 | 73.06 | 1.350 | 0 | 226.94 | 0 | 0 | **-375.34** |
| 3 | 219.19 | 4.050 | 0 | 80.81 | 0 | 0 | **-226.03** |
| 4 | 292.25 | 5.400 | 0 | 7.75 | 0 | 0 | **-151.38** ← **ótimo AG (ref)** |
| 5 | 365.31 | 6.750 | 65.31 | 0 | 0 | 0 | **-233.47** ← baseline |
| 10 | 730.62 | 13.500 | 430.62 | 0 | 0 | 0 | **-736.94** |

**Observações críticas:**

1. **Fitness é sempre negativo** nos exemplos acima (energia < penalidades).
2. **Ótimo do AG (N=4) tem fitness -151.38**, mas **baseline (N=5) tem fitness -233.47** (pior). O AG "encontrou" solução melhor pela fitness, mas **N=4 gera 292 kWh vs consumo 300 kWh (déficit 7.75 kWh)**, enquanto **N=5 gera 365 kWh (excesso 65 kWh)**.
3. **A fitness não privilegia atender o consumo** — privilegia o equilíbrio arbitrário imposto pelos pesos.
4. **Custo domina:** $\alpha C(5) = 0.08 \times 6750 = 540$, enquanto $E(5) = 365$. O termo de custo sozinho já supera a energia.
5. **Fator 10 em área e /100 em orçamento** são "magia numérica" sem justificativa física.

### 7.5 Problemas de Otimização

| Problema | Evidência |
|----------|-----------|
| Grandezas incompatíveis somadas | kWh + R$ + m² |
| Pesos arbitrários | 0.08, 0.9, 1.5, 2.0, 10, 100 — sem calibração |
| Escala do custo domina | $\alpha C \gg E$ para $N \ge 5$ |
| Fitness negativa | Sentido de maximização confuso |
| Sensibilidade a escala | Mudar unidade de custo (R$ → centavos) quebraria a fitness |
| Penalidade de área usa peso de déficit | Linha 54: `config.deficit_penalty_weight * area_excess * 10.0` — **bug** |
| Crossover pode violar limites | `operators.py:20`: `child_b = blended + random.choice([-1, 0, 1])` pode exceder `max_panels` |

### 7.6 Breakdown de Referência (tests/test_core.py:46–82)

```python
REF_FITNESS_BREAKDOWN = {
    1: {"energy_term": 73.062, "cost_penalty": 108.0, "waste_penalty": 0.0,
        "deficit_penalty": 340.407, "area_penalty": 0.0, "budget_penalty": 0.0,
        "fitness_total": -375.345},
    3: {"energy_term": 219.186, "cost_penalty": 324.0, "waste_penalty": 0.0,
        "deficit_penalty": 121.221, "area_penalty": 0.0, "budget_penalty": 0.0,
        "fitness_total": -226.035},
    5: {"energy_term": 365.31, "cost_penalty": 540.0, "waste_penalty": 58.779,
        "deficit_penalty": 0.0, "area_penalty": 0.0, "budget_penalty": 0.0,
        "fitness_total": -233.469},
    10: {"energy_term": 730.62, "cost_penalty": 1080.0, "waste_penalty": 387.558,
         "deficit_penalty": 0.0, "area_penalty": 0.0, "budget_penalty": 0.0,
         "fitness_total": -736.938},
}
```

---

## 8. Método de Dimensionamento Direto (Baseline)

### 8.1 Código Fonte

**Arquivo:** `src/simulation/baseline.py:10–30`

```python
def direct_sizing_panels(problem: dict) -> int:
    energy_per_panel = calc_energy_kwh_month(
        num_panels=1,
        panel_power_wp=float(problem["panel_power_wp"]),
        irradiance_kwh_m2_day=float(problem["irradiance_kwh_m2_day"]),
        system_efficiency=float(problem["system_efficiency"]),
    )
    estimated = math.ceil(float(problem["monthly_consumption_kwh"]) / max(energy_per_panel, 0.001))
    max_by_area = max_panels_by_roof(
        roof_usable_area_m2=float(problem["roof_usable_area_m2"]),
        panel_area_m2=float(problem["panel_area_m2"]),
    )
    return min(estimated, max_by_area)
```

### 8.2 Lógica Matemática

1. **Calcula energia por painel:** $E_1 = \frac{P_{wp}}{1000} \times H_{sp} \times 30 \times \eta$
2. **Estima painéis necessários:** $N_{est} = \lceil D / E_1 \rceil$ (teto para cobrir consumo)
3. **Limita pela área:** $N_{max} = \lfloor A_{útil} / A_{painel} \rfloor$
4. **Resultado:** $N_{baseline} = \min(N_{est}, N_{max})$

### 8.3 Exemplo (Consumo 300 kWh/mês, Área útil 68 m²)

- $E_1 = 73.062$ kWh/mês
- $N_{est} = \lceil 300 / 73.062 \rceil = \lceil 4.106 \rceil = 5$
- $N_{max} = 30$
- **Baseline = 5 painéis**

### 8.4 Avaliação do Baseline

**Arquivo:** `src/simulation/baseline.py:26–30`

```python
def evaluate_direct_baseline(problem: dict, config: GAConfig) -> tuple[int, float, float, float]:
    panels = direct_sizing_panels(problem)
    fitness, energy, cost = evaluate_fitness(panels, problem, config)
    return panels, fitness, energy, cost
```

**O baseline usa a MESMA função fitness do AG** (com os mesmos pesos de `GAConfig`) para avaliar sua solução única. Isso significa:

- O baseline **não otimiza** — calcula um ponto determinístico e o pontua.
- A comparação "AG vs Baseline" no teste é: "AG encontrou fitness -151.38 (N=4) vs Baseline fitness -233.47 (N=5)".
- **O baseline seria melhor se o objetivo fosse "atender consumo"** (N=5 gera 365 kWh > 300 kWh), mas a fitness penaliza o custo e o excesso mais que o déficit.

### 8.5 Diferenças entre Modelos AG e Baseline

| Aspecto | AG | Baseline |
|---------|-----|----------|
| Busca | Explora espaço [0, N_max] | Calcula ponto único |
| Critério de parada | Gerações fixas | Cálculo direto |
| Fitness | Mesmo `evaluate_fitness` | Mesmo `evaluate_fitness` |
| Pesos | `GAConfig` passado | `GAConfig` passado (default no teste) |
| Restrição de área | Via `max_panels` na inicialização/mutação | Via `min(estimated, max_by_area)` |
| Restrição de orçamento | Só penalidade | Não considerada no dimensionamento |

---

## 9. Inventário de Parâmetros e Dados

### 9.1 Constantes Globais (`src/core/constants.py`)

| Parâmetro | Valor | Unidade | Arquivo | Significado | Origem |
|-----------|-------|---------|---------|-------------|--------|
| `DEFAULT_DAYS_PER_MONTH` | 30 | dias | constants.py | Dias por mês fixo | Convenção |
| `DEFAULT_ROOF_USABLE_FACTOR` | 0.85 | — | constants.py | Fator de área útil | Estimativa genérica |

### 9.2 Parâmetros do AG (`src/core/config.py`)

| Parâmetro | Valor Default | Unidade | Significado | Origem |
|-----------|---------------|---------|-------------|--------|
| `population_size` | 50 | — | Tamanho da população | Heurística |
| `generations` | 100 | — | Número de gerações | Heurística |
| `crossover_rate` | 0.8 | — | Prob. crossover | Heurística |
| `mutation_rate` | 0.1 | — | Prob. mutação | Heurística |
| `elitism_count` | 2 | — | Elitismo | Heurística |
| `random_seed` | 42 | — | Semente reprodutibilidade | Arbitrária |
| `cost_weight_alpha` | 0.08 | — | Peso custo na fitness | **Arbitrário** |
| `waste_penalty_weight` | 0.9 | — | Peso excesso energia | **Arbitrário** |
| `deficit_penalty_weight` | 1.5 | — | Peso déficit energia | **Arbitrário** |
| `budget_penalty_weight` | 2.0 | — | Peso estouro orçamento | **Arbitrário** |

### 9.3 Dados de Cidades (`data/cities_mock.json`)

| Cidade | Estado | `irradiance_kwh_m2_day` | Unidade | Origem declarada |
|--------|--------|-------------------------|---------|------------------|
| João Pessoa | PB | 5.4 | kWh/m²/dia | Mock |
| Recife | PE | 5.2 | kWh/m²/dia | Mock |
| Natal | RN | 5.6 | kWh/m²/dia | Mock |
| Fortaleza | CE | 5.7 | kWh/m²/dia | Mock |
| Maceió | AL | 5.3 | kWh/m²/dia | Mock |
| Salvador | BA | 5.1 | kWh/m²/dia | Mock |

**Classificação:** **Dados simulados (mock)** — "Mock inspirado em médias públicas INPE/SONDA" (irradiance_mock.json). Não há fonte primária citada, nem incerteza, nem variabilidade mensal usada.

### 9.4 Dados de Painéis (`data/panels_mock.json`)

| Parâmetro | Valor | Unidade | Origem |
|-----------|-------|---------|--------|
| `panel_model` | "STD-550W" | — | Mock |
| `panel_power_wp` | 550.0 | Wp | Mock |
| `panel_area_m2` | 2.2 | m² | Mock |
| `panel_cost_brl` | 1100.0 | R$ | Mock |
| `installation_cost_per_panel_brl` | 250.0 | R$ | Mock |
| `system_efficiency` | 0.82 | — | Mock |

**Classificação:** **Dados simulados (mock)** — Painel genérico 550 Wp, valores típicos de mercado brasileiro aproximados, sem fonte específica.

### 9.5 Dados de Irradiância Mensal (`data/irradiance_mock.json`)

| Mês | kWh/m²/dia |
|-----|------------|
| jan | 5.7 |
| fev | 5.8 |
| mar | 5.6 |
| abr | 5.3 |
| mai | 5.1 |
| jun | 4.9 |
| jul | 5.0 |
| ago | 5.2 |
| set | 5.4 |
| out | 5.6 |
| nov | 5.7 |
| dez | 5.8 |
| **Média anual** | **5.425** |

**Nota:** Este arquivo **não é usado** em nenhum cálculo. O código usa apenas a média anual de `cities_mock.json` (5.4 para João Pessoa). A variabilidade mensal existe no JSON mas é ignorada.

### 9.6 Cenários de Teste (`data/scenarios_mock.json`)

| Cenário | Consumo (kWh/mês) | Área telhado (m²) | Painéis esperados (teste) |
|---------|-------------------|-------------------|---------------------------|
| low | 150 | 30 | 2 |
| medium | 300 | 45 | 4 |
| high | 500 | 70 | 7 |

**Classificação:** **Dados simulados para teste** — Valores escolhidos para exercitar diferentes regimes (área limitante, consumo limitante).

---

## 10. Análise de Coerência Dimensional

### 10.1 Resumo das Inconsistências

| Fórmula/Termo | Unidade Esperada | Unidade Real | Status |
|---------------|------------------|--------------|--------|
| `calc_energy_kwh_month` | kWh | kWh·kW/m² | **Incorreta** (falta $A_{painel}$) |
| `cost_penalty = α × C` | kWh (para somar com E) | R$ | **Incompatível** |
| `waste_penalty = w_w × W` | kWh | kWh | OK (mas peso adimensional) |
| `deficit_penalty = w_d × D` | kWh | kWh | OK (mas peso adimensional) |
| `area_penalty = w_d × 10 × A_ex` | kWh | m² | **Incompatível** |
| `budget_penalty = w_b × B_ex / 100` | kWh | R$ | **Incompatível** |
| **Fitness Total** | kWh (ou adimensional) | kWh + R$ + m² | **Inválida** |

### 10.2 Consequências

1. **Resultado depende de unidades arbitrárias:** Se custo for em centavos (×100), `cost_penalty` aumenta 100× e domina completamente.
2. **Não há como interpretar o valor numérico da fitness:** -151.38 não significa "151 kWh de déficit" nem "151 R$ de economia".
3. **Pesos não são comparáveis:** Alterar $\alpha$ de 0.08 para 0.008 tem efeito diferente de alterar $w_d$ de 1.5 para 0.15, porque as escalas base são diferentes.
4. **Otimização é frágil:** Pequenas mudanças nos pesos ou nas magnitudes das entradas mudam qualitativamente o ótimo.

---

## 11. Testes e Verificações Matemáticas

### 11.1 O que os Testes Verificam (tests/test_core.py)

| Teste | Verifica | Tipo |
|-------|----------|------|
| `test_energy_calc` | Valor numérico exato de `calc_energy_kwh_month` | Reprodutibilidade |
| `test_cost_calc` | Valor numérico exato de `calc_cost_brl` | Reprodutibilidade |
| `test_baseline_direct` | Baseline retorna (5, -233.469, 365.31, 6750.0) | Reprodutibilidade |
| `test_fitness_breakdown` | Breakdown exato para N=1,3,5,10 | Reprodutibilidade |
| `test_fitness_total_matches_breakdown` | Consistência interna | Sanidade |
| `test_max_panels_by_roof` | Cálculo de teto da área | Lógica |
| `test_deterministic_optimization` | AG com seed=42 reproduz referência | Reprodutibilidade |
| `test_reproducibility_across_runs` | Mesma seed → mesmo resultado | Reprodutibilidade |
| `test_scenarios_reference` | Cenários low/medium/high → painéis esperados | Reprodutibilidade |

### 11.2 O que NÃO é Verificado

| Propriedade Matemática | Verificada? |
|------------------------|-------------|
| Coerência dimensional das fórmulas | ❌ Não |
| Monotonicidade de energia em N | ❌ Não (implícita mas não testada) |
| Monotonicidade de custo em N | ❌ Não |
| Limite de área respeitado pelo AG | Parcial (via `max_panels` na inicialização) |
| Limite de orçamento respeitado | ❌ Não (só penalidade) |
| Coerência breakdown vs fitness total | ✅ Sim (`test_fitness_total_matches_breakdown`) |
| Coerência AG vs Baseline (mesmo modelo) | ❌ Não (usam mesma fitness, mas baseline não otimiza) |
| Validade física da fórmula de energia | ❌ Não |
| Sensibilidade a pesos da fitness | ❌ Não |
| Comportamento com entradas nulas/inválidas | Parcial (validators.py) |

### 11.3 Distinção Importante

> **Testes de funcionamento do código ≠ Testes de validade do modelo matemático**

Os 47 testes atuais garantem que **o código produz os mesmos números de antes** (reprodutibilidade). **Não garantem** que esses números representem corretamente a física do problema, nem que a fitness seja matematicamente bem-comportada.

---

## 12. Problemas e Inconsistências Encontrados

### 12.1 Classificação por Gravidade

| ID | Problema | Localização | Gravidade | Evidência |
|----|----------|-------------|-----------|-----------|
| P1 | Fórmula de energia ignora `panel_area_m2` → dimensionalmente incorreta | `fitness.py:16–22` | **Crítico** | Análise dimensional (Seção 3.2) |
| P2 | Fitness soma kWh + R$ + m² sem normalização | `fitness.py:62–64` | **Crítico** | Tabela Seção 7.3 |
| P3 | `area_penalty` usa `deficit_penalty_weight` em vez de peso próprio | `fitness.py:54` | **Alto** | Código: `config.deficit_penalty_weight * area_excess * 10.0` |
| P4 | `crossover` pode gerar `child_b = max_panels + 1` (fora limites) | `operators.py:20` | **Alto** | `blended + random.choice([-1, 0, 1])` sem clamp |
| P5 | Fator 10 em área e /100 em orçamento são "magic numbers" | `fitness.py:54, 60` | **Médio** | Hardcoded sem justificativa |
| P6 | `system_efficiency` vem do painel, não do sistema/cidade | `panels_mock.json`, `runner.py:31` | **Médio** | Eficiência de sistema não deveria ser atributo do painel |
| P7 | Irradiância usa média anual única; variabilidade mensal ignorada | `cities_mock.json` vs `irradiance_mock.json` | **Médio** | `irradiance_mock.json` não é lido |
| P8 | Baseline usa `GAConfig` default (pesos de fitness) em vez de config própria | `baseline.py:28` | **Baixo** | `evaluate_direct_baseline(problem, config)` |
| P9 | `roof_type` informado mas nunca usado no cálculo | `RoofInput`, `runner.py:25` | **Baixo** | Campo existe mas não afeta nada |
| P10 | Testes validam reproduzibilidade, não validade física | `tests/test_core.py` | **Médio** | Seção 11.2 |

### 12.2 Detalhamento dos Críticos

#### P1 — Fórmula de Energia Dimensionalmente Incorreta

**Código atual:**
```python
return num_panels * (panel_power_wp / 1000.0) * irradiance_kwh_m2_day * days_per_month * system_efficiency
```

**Unidades:** $N \times \text{kW} \times \text{kWh/m}^2\text{/dia} \times \text{dia} = \text{kWh}\cdot\text{kW/m}^2$

**Correção necessária:** Incluir área do painel ou usar potência específica (Wp/m²).

#### P2 — Fitness com Grandezas Incompatíveis

**Código atual:**
```python
fitness_total = energy - cost_penalty - waste_penalty - deficit_penalty - area_penalty - budget_penalty
```

**Unidades:** kWh - R$ - kWh - kWh - m² - R$ = **sem sentido físico**

**Correção necessária:** Normalizar todos os termos para uma unidade comum (ex.: R$ via tarifa de energia, ou adimensional via normalização por valores de referência).

#### P3 — Penalidade de Área com Peso Errado

**Código atual (linha 54):**
```python
area_penalty = config.deficit_penalty_weight * area_excess * 10.0
```

**Problema:** Usa `deficit_penalty_weight` (1.5) para penalidade de área. Não existe `area_penalty_weight` no `GAConfig`.

#### P4 — Crossover Fora dos Limites

**Código atual (linha 18–20):**
```python
blended = round((parent_a.num_panels + parent_b.num_panels) / 2)
child_a = Individual(num_panels=blended)
child_b = Individual(num_panels=blended + random.choice([-1, 0, 1]))
```

Se `parent_a = parent_b = max_panels`, então `blended = max_panels` e `child_b` pode ser `max_panels + 1`. A mutação tem clamp (linha 28–29), mas o crossover não.

---

## 13. Limitações Científicas do Modelo

| Limitação | Impacto no TCC |
|-----------|----------------|
| **Fórmula de energia fisicamente incorreta** | Invalida qualquer conclusão quantitativa sobre geração |
| **Fitness sem unidade coerente** | Impossível interpretar "melhor" solução; otimização é numérica, não física |
| **Pesos arbitrários não calibrados** | Resultado depende de escolhas não justificadas |
| **Dados de entrada são mockados** | Não representa condições reais do Nordeste brasileiro |
| **Variabilidade climática ignorada** | Modelo determinístico para problema estocástico |
| **Baseline não é otimização alternativa** | Comparação AG vs Baseline não é "AG vs método exato" — é "busca vs ponto único" |
| **Sem análise de sensibilidade dos pesos** | Não se sabe quão robusto é o ótimo encontrado |
| **Sem validação contra dados reais** | Modelo não calibrado nem validado |

---

## 14. Questões que Precisam Ser Decididas Antes da E5.2

| # | Questão | Opções | Recomendação |
|---|---------|--------|--------------|
| Q1 | **Qual o objetivo real da otimização?** | (a) Minimizar custo atendendo consumo<br>(b) Maximizar energia dentro do orçamento<br>(c) Maximizar autossuficiência (minimizar déficit)<br>(d) Função multi-objetivo (Pareto) | Definir **um** objetivo principal claro. A fitness atual mistura tudo sem hierarquia. |
| Q2 | **Como normalizar a fitness?** | (a) Converter tudo para R$ (tarifa energia + custo)<br>(b) Normalizar cada termo por valor de referência<br>(c) Usar função multi-objetivo (NSGA-II)<br>(d) Manter soma ponderada mas com pesos calibrados | (a) ou (b) são mais simples e interpretáveis. (c) exige AG multi-objetivo. |
| Q3 | **Corrigir fórmula de energia?** | (a) Adicionar `panel_area_m2` explicitamente<br>(b) Usar `panel_power_wp / panel_area_m2` (Wp/m²) × irradiância<br>(c) Usar modelo mais completo (temperatura, NOCT, perdas) | (a) ou (b) mínimo para consistência dimensional. |
| Q4 | **Tratar penalidade de área?** | (a) Adicionar `area_penalty_weight` no `GAConfig`<br>(b) Tornar área restrição dura (inviabilizar indivíduo)<br>(c) Remover (já limitada por `max_panels`) | (b) é mais limpo: área já é limite duro na inicialização/mutação. |
| Q5 | **Corrigir crossover?** | (a) Clampar `child_b` em `[min_panels, max_panels]`<br>(b) Usar crossover que preserva limites por construção | (a) correção mínima. |
| Q6 | **Usar dados reais de irradiância?** | (a) Manter mock (TCC I é metodológico)<br>(b) Integrar base INPE/SONDA ou NASA POWER<br>(c) Usar dados mensais do `irradiance_mock.json` | (a) aceitável para TCC I se declarado como limitação. (c) fácil e melhora realismo. |
| Q7 | **Baseline deve usar mesma fitness?** | (a) Sim — compara "mesmo critério"<br>(b) Não — baseline deve otimizar seu próprio objetivo (ex.: min custo s.t. energia ≥ consumo) | (b) faz mais sentido científico: comparar métodos com seus próprios objetivos. |
| Q8 | **Incluir custo de inversor/estrutura fixo?** | (a) Manter linear (apenas painéis)<br>(b) Adicionar custo fixo + variável | (b) mais realista, muda forma da função custo. |

---

## 15. Resumo Final para Apresentação

### O que o sistema realmente calcula hoje

1. **Energia mensal:** Fórmula $E = N \times P_{kWp} \times H_{sp} \times 30 \times \eta$ — **dimensionalmente incorreta** (falta área do painel).
2. **Custo:** Linear $C = N \times (C_{painel} + C_{instalação})$ — apenas painéis, sem custo fixo.
3. **Área:** Limite duro $N_{max} = \lfloor A_{útil} / A_{painel} \rfloor$ com fator 0.85 genérico.
4. **Fitness:** $F = E - \alpha C - w_w W - w_d D - w_d \cdot 10 \cdot A_{ex} - w_b \cdot B_{ex}/100$ — **soma kWh + R$ + m²**.
5. **AG:** Busca em $[0, N_{max}]$ com crossover/mutação inteiros, seleção por torneio, elitismo.
6. **Baseline:** $N = \min(\lceil D/E_1 \rceil, N_{max})$ avaliado pela mesma fitness do AG.

### Objetivo matemático implícito da fitness atual

A fitness **maximiza uma combinação linear arbitrária** onde:
- Energia contribui positivamente (1 × kWh)
- Custo contribui negativamente (0.08 × R$)
- Excesso de energia penalizado (0.9 × kWh)
- Déficit penalizado mais forte (1.5 × kWh)
- Área excedente penalizada com peso de déficit × 10 (15 × m²)
- Orçamento excedente penalizado com peso 2.0 / 100 (0.02 × R$)

**Não há objetivo físico explícito** — é uma função de "pontuação" inventada.

### Grandezas combinadas

| Grandeza | Unidade | Peso efetivo | Sinal |
|----------|---------|--------------|-------|
| Energia gerada | kWh/mês | 1.0 | + |
| Custo total | R$ | 0.08 | – |
| Excesso energia | kWh/mês | 0.9 | – |
| Déficit energia | kWh/mês | 1.5 | – |
| Área excedente | m² | 15.0 | – |
| Orçamento excedente | R$ | 0.02 | – |

### Problemas matemáticos identificados

1. **CRÍTICO:** Energia dimensionalmente errada (ignora área do painel).
2. **CRÍTICO:** Fitness soma grandezas incompatíveis (kWh + R$ + m²).
3. **ALTO:** Penalidade de área usa peso errado (`deficit_penalty_weight`).
4. **ALTO:** Crossover pode violar limite superior de painéis.
5. **MÉDIO:** Pesos arbitrários, fatores mágicos (10, 100) sem justificativa.
6. **MÉDIO:** Dados mockados, irradiância média anual apenas, eficiência no painel.
7. **BAIXO:** `roof_type` não usado, baseline usa config do AG.

### Hipóteses sem justificativa

- Fator de aproveitamento de telhado = 0.85 (por que não 0.7 ou 0.9?)
- Eficiência de sistema = 0.82 (valor típico, mas sem fonte)
- Pesos da fitness (0.08, 0.9, 1.5, 2.0) — escolhidos como?
- Fator 10 na penalidade de área — por que 10?
- Divisor 100 na penalidade de orçamento — por que 100?
- Irradiação média anual representativa para dimensionamento mensal?

### Decisões necessárias na E5.2

1. **Definir objetivo único de otimização** (custo, energia, autossuficiência, multi-objetivo).
2. **Corrigir fórmula de energia** para consistência dimensional.
3. **Normalizar fitness** (unidade comum ou multi-objetivo).
4. **Calibrar ou justificar pesos** (sensitivity analysis).
5. **Corrigir bugs** (crossover, peso de área).
6. **Decidir papel do baseline** (método exato alternativo vs. heurística de comparação).
7. **Documentar limitações dos dados mock** explicitamente no TCC.

---

## 16. Referências de Código (Para Rastreabilidade)

| Seção | Arquivo | Linhas | Função/Classe |
|-------|---------|--------|---------------|
| Energia | `src/genetic/fitness.py` | 8–22 | `calc_energy_kwh_month` |
| Custo | `src/genetic/fitness.py` | 25–27 | `calc_cost_brl` |
| Fitness breakdown | `src/genetic/fitness.py` | 30–76 | `evaluate_fitness_breakdown` |
| Fitness total | `src/genetic/fitness.py` | 79–82 | `evaluate_fitness` |
| AG principal | `src/genetic/algorithm.py` | 21–66 | `run_genetic_algorithm` |
| Max painéis/área | `src/genetic/algorithm.py` | 11–13 | `max_panels_by_roof` |
| Crossover | `src/genetic/operators.py` | 13–21 | `crossover` |
| Mutação | `src/genetic/operators.py` | 24–29 | `mutate` |
| Seleção | `src/genetic/selection.py` | 8–10 | `tournament_selection` |
| Baseline sizing | `src/simulation/baseline.py` | 10–23 | `direct_sizing_panels` |
| Baseline eval | `src/simulation/baseline.py` | 26–30 | `evaluate_direct_baseline` |
| Build problem | `src/simulation/runner.py` | 17–32 | `build_problem` |
| Run optimization | `src/simulation/runner.py` | 35–118 | `run_optimization` |
| Roof input | `src/models/roof.py` | 8–26 | `RoofInput` |
| Resultados | `src/models/result.py` | 18–69 | `FitnessBreakdown`, `ScenarioRunResult` |
| GA Config | `src/core/config.py` | 6–19 | `GAConfig` |
| Constantes | `src/core/constants.py` | 3–5 | `DEFAULT_*` |
| Dados cidades | `data/cities_mock.json` | 1–8 | — |
| Dados painéis | `data/panels_mock.json` | 1–10 | — |
| Irradiância mensal | `data/irradiance_mock.json` | 1–19 | — (não usado) |
| Cenários | `data/scenarios_mock.json` | 1–32 | — |
| Testes core | `tests/test_core.py` | 1–213 | 47 testes |

---

**Fim do Relatório de Auditoria Matemática (E5.1)**  
**Próxima etapa (E5.2):** Definição formal da função fitness e comparação metodológica — **aguardando autorização**.