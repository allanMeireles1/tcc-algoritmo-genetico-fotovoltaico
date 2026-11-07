# Aplicação de Algoritmos Genéticos no Dimensionamento Fotovoltaico (MVP TCC)

Aplicação acadêmica para otimizar a quantidade de painéis solares em residências do Nordeste, com entrada realista de telhado e consumo. O sistema atual combina um back‑end FastAPI com um front‑end React/Vite; o protótipo original em Streamlit (`app.py`) é mantido apenas como referência histórica.

## Objetivo

Resolver, via algoritmo genético manual, o problema:

- entrada: largura e comprimento do telhado, consumo mensal, cidade, orçamento opcional;
- saída: melhor número de painéis, energia estimada, custo, ocupação e déficit/excesso energético.

Foco: otimização heurística e simulação computacional para TCC de Ciência da Computação.

## Estrutura

```text
project/
├── app.py
├── README.md
├── requirements.txt
├── data/
│   ├── cities_mock.json
│   ├── panels_mock.json
│   └── scenarios_mock.json
├── results/
├── assets/
└── src/
    ├── core/
    ├── models/
    ├── genetic/
    ├── simulation/
    ├── visualization/
    ├── storage/
    └── utils/
```

## Como executar

### Fluxo experimental (E5.4)

O fluxo experimental permite comparar **três** abordagens usando o mesmo problema:

- **Solução analítica** – cálculo direto do número ótimo de painéis (E5.3.2).  
- **Busca exaustiva** – avaliação de todos os valores de \(N\) dentro do limite (E5.3.2).  
- **Algoritmo genético v2** – algoritmo evolutivo que utiliza a avaliação e comparação lexicográfica (E5.3.4).

A API Python está disponível em `src/simulation/runner.py`:

```python
from src.core.config import GAConfig
from src.models.roof import RoofInput
from src.simulation.runner import run_comparison

roof = RoofInput(
    width_m=8.0,
    length_m=10.0,
    monthly_consumption_kwh=300.0,
    city="João Pessoa",
    max_budget_brl=None,
)
config = GAConfig(
    population_size=20,
    generations=10,
    crossover_rate=0.8,
    mutation_rate=0.2,
    elitism_count=2,
    random_seed=42,
)

# Executa a comparação (por padrão 1 run do AG)
outcome = run_comparison(
    roof=roof,
    city_data={"city": "João Pessoa", "irradiance_kwh_m2_day": 5.4},
    panel_data={
        "panel_power_wp": 550,
        "panel_cost_brl": 1350,
        "installation_cost_per_panel_brl": 0,
        "panel_area_m2": 2.2,
        "system_efficiency": 0.82,
    },
    config=config,
    runs=3,  # múltiplas sementes para o AG
)
```

`run_comparison` devolve um objeto **`ComparisonOutcome`** contendo:

- `execution_label` e `city`
- o `Problem` usado (garante que os três métodos operarão sobre exatamente os mesmos parâmetros)
- `results`: lista de `MethodResult` (método, seed, tempo, avaliação completa)
- `config` (cópia dos parâmetros do GA)
- `analytical_diagnostic` (valores de N = energia, área, orçamento, etc.)
- `summary` com métricas agregadas (ex.: tempos médios, coincidência de painéis entre analítico e exaustivo, painel por seed).

Para exportar os resultados em forma tabular (CSV/Excel) basta usar:

```python
from src.simulation.runner import comparison_to_rows
rows = comparison_to_rows(outcome)
# rows é uma lista de dicionários – pode ser salva com pandas ou csv
```

O fluxo **legado** (`run_optimization`) permanece inalterado e continua a ser usado pelos serviços da API (`/optimize`). O novo fluxo é independente e pode ser usado para experimentos científicos, estudos de sensibilidade e benchmarking.

#### Convergência (E5.4.3)

`run_comparison` agora preenche `convergence` (métricas por seed) e
`convergence_summary` (agregado) em `ComparisonOutcome`. Para analisar a evolução
geração a geração:

```bash
python convergence_experiment.py
```

Métricas por execução (`ConvergenceMetrics`):

| Campo | Significado |
|---|---|
| `best_panels_trajectory` | melhor número de painéis por geração |
| `converged` | melhor estável nas últimas 5 gerações |
| `convergence_generation` | 1ª geração a partir da qual o melhor não muda |
| `first_optimal_generation` | 1ª geração que atinge o ótimo da busca exaustiva |
| `generations_to_optimum` | gerações até o ótimo (contagem 1‑based) |
| `final_best_panels` | melhor valor final |
| `stability_end_count` | tamanho da cauda estável |

Resultados observados (5 cenários × 3 seeds × 2 configurações = 30 execuções):

- **Taxa de convergência: 100 %** em todas as configurações.
- **Taxa de ótimo: 100 %** — o AG igualou a busca exaustiva em todos os casos.
- `pop=20`/`gens=40`: ótimo já na 1ª geração na maioria dos cenários (média 1,0–1,7 gerações).
- `pop=10`/`gens=20`: ainda 100 % de ótimo; pior caso foi a seed 999 no cenário
  `viavel_simples`, que precisou de 14 gerações (trajetória `14→…→4`).
- Cenários com restrição ativa (`limite_area`, `orcamento_parcial`) convergem
  imediatamente, pois o ótimo é ditado pela restrição.

**Recomendação:** manter os parâmetros atuais. `pop=10`/`gens=20` é suficiente e
mais rápido, mas `pop=20`/`gens=40` oferece margem de segurança sem custo
relevante. Nenhum ajuste de taxa de crossover/mutação mostrou‑se necessário.

### Sensibilidade (E5.4.4)

Novas rotinas em `src/simulation/experiments.py` varrem, via AG v2:

- `run_population_sensitivity`
- `run_generations_sensitivity`
- `run_mutation_rate_sensitivity`
- `run_crossover_rate_sensitivity`
- `run_elitism_sensitivity`

Execução:

```bash
python sensitivity_experiment.py
```

Resultados (3 cenários × 5 varrimentos):

| Parâmetro | Faixa testada | Efeito no ótimo | Efeito no tempo |
|---|---|---|---|
| População | 5–80 | pop=5 fica a 1 gap do ótimo (3 vs 4); pop≥10 é ótimo | ~5→78 ms |
| Gerações | 5–80 | nenhuma variação | ~2→38 ms |
| Mutação | 0.0–0.6 | nenhuma variação | ≈18 ms (constante) |
| Crossover | 0.0–1.0 | nenhuma variação | ~17.6→18.4 ms |
| Elitismo | 0–10 | nenhuma variação | ~17→18 ms |

**Recomendação:** manter `pop≥10`, `gens=20–40`, `mutation=0.2`, `crossover=0.8`, `elitism=2`.
Mesmo `elitism=0` e `mutation=0.0` mantêm o ótimo neste problema (paisagem quase unimodal),
mas a configuração atual oferece margem de segurança a custo negligível (~18 ms).

### Benchmark (E5.4.5)

O benchmark em `src/simulation/benchmark.py` compara **analítico**, **exaustivo**
e **AG v2** com metodologia consistente:

- mesma instância de `Problem` para os três métodos;
- warmup não medido antes das repetições;
- `R` repetições medidas com `time.perf_counter`;
- AG usa sementes `random_seed + rep` (reprodutibilidade);
- estatística principal: mediana; também reporta média, desvio, mínimo e máximo;
- qualidade: painéis, viabilidade, custo médio, energia média e taxa de
  reprodução do ótimo da busca exaustiva.

Execução:

```bash
python benchmark_experiment.py
```

Resultados (3 cenários × 5 repetições, `pop=20`, `gens=40`):

| Método | Tempo mediano | Qualidade |
|---|---|---|
| Analítico | ~0,02–0,03 ms | 100 % do ótimo |
| Exaustivo | ~0,02–0,36 ms | 100 % do ótimo |
| AG v2 | ~14–19 ms | 100 % do ótimo |

O AG foi cerca de **50–800× mais lento** que os métodos determinísticos, mas
entregou a mesma solução ótima em todas as repetições. O custo do AG é
justificado pela flexibilidade da metaheurística; para este espaço de busca
pequeno, analítico/exaustivo são preferíveis em produção.

### Status de implementações (E5.2 – E5.4)

- **E5.2** – Modelo matemático consolidado em `src/simulation/evaluation.py` (`EvaluationResult`, `evaluate_candidate`, `compare_lexicographic`).
- **E5.3.2** – Solução analítica e busca exaustiva em `src/simulation/solvers.py`.
- **E5.3.3.1 / E5.3.3.2 / E5.3.3.3** – Indivíduos, torneio e elitismo com comparador oficial em `src/genetic/*`.
- **E5.3.4** – Fluxo experimental comum em `src/simulation/runner.py` (`run_comparison`).
- **E5.4.1** – Documentação do fluxo experimental adicionada ao `README.md`.
- **E5.4.2** – Validação experimental (todos os cenários confirmam consistência entre métodos e seeds).
- **E5.4.3** – Análise de convergência em `src/simulation/convergence.py` e `tests/test_convergence.py`. Todas as execuções convergiram (100 %); as taxas de ótimo também foram 100 % com as configurações testadas (pop 10‑20, gens 20‑40). Recomenda‑se manter os parâmetros atuais; configurações ainda menores ainda convergem rapidamente.
- **E5.4.4** – Sensibilidade a hiperparâmetros em `src/simulation/experiments.py` e `sensitivity_experiment.py`. População ≥10, gerações ≥5, mutação/crossover/elitismo nas faixas testadas mantêm 100 % de ótimo.
- **E5.4.5** – Benchmark de tempo e qualidade em `src/simulation/benchmark.py` e `benchmark_experiment.py`. Comparação consistente (warmup + repetições) confirma que AG iguala o ótimo, embora seja 50–800× mais lento que analítico/exaustivo.
- **E5.4.6** – Consolidação experimental em `scripts/e5_4_6_consolidacao.py` e `results/e5_4_6/`. 30 seeds por configuração nos cenários baixo/médio/alto; IC 95% e dados brutos registrados.
- **E5.4.7** – Auditoria científica em `docs/E5_4_7_AUDITORIA_CIENTIFICA.md`. Fórmulas/unidades consistentes; irradiância é mock e deve ser declarada como limitação.
- **E5.4.8** – Revisão de escopo em `docs/E5_4_8_REVISAO_ESCOPO.md`. Decisão oficial: **Alternativa A** — preservar o modelo E5.2 (minimizar custo com cobertura energética mensal); o objetivo geral e os objetivos específicos do artigo devem ser reescritos para refletir esse modelo. A divergência entre o objetivo original (`Eg − Ct`) e o modelo implementado está registrada para revisão do texto.
- **E5.5** – Endpoint `/compare` em `backend/routes.py` + `backend/services.py` (`comparison_adapter`), expondo `run_comparison` sem alterar `/optimize` nem `/baseline`.
- **E5.5.1** – Históricos de convergência por seed incluídos na resposta de `/compare` (`histories`, `list[dict]`). A `ComparisonPage` exibe todos os resultados, estatísticas de tempo e gráficos de convergência/histograma com dados reais da API.
- **E5.5.2** – Aprimoramento visual: médias ± desvio‑padrão, mediana + IQR, tratamento de tempos iguais, legenda interativa (ocultar/destacar seeds), rótulos explícitos e acessibilidade nos gráficos.
- **E5.5.3** – Validação de backend concluída: 208 testes aprovados, 6 cidades × 3 consumos, configurações de AG, entradas inválidas e retrocompatibilidade com `/optimize` e `/baseline`. Frontend: `npm ci` + `npm run build` executados com sucesso (`dist/` gerado sem erros TypeScript).
- **E5.5.4** – Documentação final: `CHANGELOG.md` criado, `README.md` atualizado com contrato completo de `/compare`, exemplos JSON e instruções de execução do backend e frontend; OpenAPI/Swagger em `/docs` validado.

### Protótipo original em Streamlit (legado)

Mantido apenas como referência histórica. O sistema em produção usa FastAPI + React/Vite (ver seções abaixo).

```bash
pip install -r requirements.txt
streamlit run app.py
```

### API FastAPI (backend)

```bash
pip install -r requirements.txt
uvicorn backend.app:app --reload --port 8000
```

A documentação interativa (Swagger) fica em `http://localhost:8000/docs`.

### Frontend React/Vite

```bash
cd frontend
npm ci
npm run build   # gera dist/ e faz checagem de tipos (tsc)
npm run dev     # ambiente de desenvolvimento
```

### Testes

```bash
pip install pytest pytest-cov
pytest tests/ -v
```

## Estrutura do backend

```text
backend/
├── __init__.py
├── app.py        # instância FastAPI + CORS
├── routes.py     # endpoints (sem lógica de negócio)
├── services.py   # adaptadores que chamam src/* e retornam DTOs
└── schemas.py    # modelos Pydantic (request/response)
```

## Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET`  | `/health` | Verificação de saúde |
| `GET`  | `/cities` | Lista cidades disponíveis |
| `GET`  | `/panels` | Lista painéis configurados |
| `POST` | `/optimize` | Executa otimização completa (AG) |
| `POST` | `/baseline` | Calcula dimensionamento direto |
| `POST` | `/compare` | AG v2 vs analítico vs exaustivo (mesmo `Problem`, multi-seed) |
| `POST` | `/experiments/sensitivity` | Sensibilidade ao consumo |
| `POST` | `/experiments/population-timing` | Tempo × tamanho da população |
| `POST` | `/experiments/generations-timing` | Tempo × número de gerações |

### Exemplo de requisição `/optimize`

```json
{
  "roof": {
    "width_m": 8.0,
    "length_m": 10.0,
    "monthly_consumption_kwh": 300.0,
    "city": "João Pessoa",
    "roof_type": "ceramic",
    "max_budget_brl": null
  },
  "config": {
    "population_size": 50,
    "generations": 100,
    "crossover_rate": 0.8,
    "mutation_rate": 0.1,
    "elitism_count": 2,
    "random_seed": 42
  },
  "runs": 1
}
```

A resposta espelha a estrutura `OptimizationOutcome` do protótipo original
(`result`, `history`, `summary`, `final_population`, `fitness_breakdown`).

### Exemplo de requisição e resposta `/compare`

`/compare` aceita os mesmos campos de `roof`, `config` e `runs` de `/optimize` (`runs` entre 1 e 100).
Exemplo de requisição (mesma estrutura usada em `/optimize`):

```json
{
  "roof": {
    "width_m": 8.0,
    "length_m": 10.0,
    "monthly_consumption_kwh": 300.0,
    "city": "João Pessoa",
    "roof_type": "ceramic",
    "max_budget_brl": null
  },
  "config": {
    "population_size": 10,
    "generations": 5,
    "crossover_rate": 0.8,
    "mutation_rate": 0.1,
    "elitism_count": 2,
    "random_seed": 42
  },
  "runs": 1
}
```

A resposta usa `summary`, `results` e `histories` exatamente como no `ComparisonResponse`
(`summary: dict`, `results: list[dict]`, `histories: list[dict]`). Trecho real da resposta
acima (valores de tempo variam entre execuções):

```json
{
  "summary": {
    "analytical_panels": 5,
    "analytical_feasible": true,
    "exhaustive_panels": 5,
    "exhaustive_feasible": true,
    "analytical_matches_exhaustive": true,
    "genetic_panels_by_seed": { "42": 5 },
    "genetic_feasible_by_seed": { "42": true },
    "genetic_execution_time_mean_s": 0.001368,
    "runs": 1,
    "convergence": { "runs": 1, "converged_count": 0, "optimal_count": 1, "optimal_rate": 1.0, "generations_to_optimum_values": [3], "final_best_panels_unique": [5] }
  },
  "results": [
    { "method": "analytical", "run_index": 0, "run_seed": null, "execution_time_s": 0.000054, "evaluation": { "num_panels": 5, "feasible": true, "cost": 6750.0 } },
    { "method": "exhaustive",  "run_index": 0, "run_seed": null, "execution_time_s": 0.000368, "evaluation": { "num_panels": 5, "feasible": true, "cost": 6750.0 } },
    { "method": "genetic",     "run_index": 0, "run_seed": 42,   "execution_time_s": 0.001368, "evaluation": { "num_panels": 5, "feasible": true, "cost": 6750.0 } }
  ],
  "histories": [
    { "seed": 42, "generations": [ { "generation": 0, "best_fitness": -9450.0, "avg_fitness": -13770.0, "best_panels": 7 } ] }
  ]
}
```

- `summary`: dicionário com as métricas agregadas (incluindo `convergence`).
- `results`: lista de dicionários — 2 determinísticos (`analytical`, `exhaustive`) + N genéticos (`genetic`, uma linha por seed); cada linha traz `method`, `run_index`, `run_seed`, `execution_time_s` e `evaluation`.
- `histories`: lista de dicionários — uma entrada por seed com `seed` e `generations`; cada geração tem `generation` (começa em **0**), `best_fitness`, `avg_fitness` e `best_panels`.
- A ordem em `results` é sempre: analítico, exaustivo e depois os genéticos na ordem das seeds.

A aba **Comparação** do frontend consome esses três campos e exibe:
- cards com média ± desvio‑padrão e mediana + IQR dos tempos;
- tabela com todas as execuções;
- gráfico de convergência (painéis por geração, linha por seed);
- histograma de distribuição dos tempos do AG.

## O que a interface permite

- informar dimensões do telhado;
- informar consumo mensal;
- escolher cidade (irradiância mock);
- definir orçamento máximo opcional;
- configurar seed e parâmetros do AG;
- comparar AG com baseline direto;
- exportar resultados em JSON/CSV.

## Gráficos acadêmicos (abas)

**Dashboard principal**

1. Evolução do fitness (convergência)
2. Melhor fitness vs fitness médio
3. Energia gerada × consumo
4. Ocupação do telhado (m²) + layout esquemático

**Análise do AG**

5. AG × método direto (painéis e custo)
6. Histograma da população final
7. Composição da função de fitness

**Experimentos**

8. Sensibilidade ao consumo
9. Tempo de execução × população / gerações

**Comparação (E5.5)**

10. Convergência por seed (painéis por geração)
11. Histograma dos tempos do AG (ms)
12. Cards + tabela com as execuções analítico / exaustiva / AG

## Dados mockados

- `data/cities_mock.json`: cidades do Nordeste + irradiância média;
- `data/panels_mock.json`: painel padrão com potência, área, custo e eficiência;
- `data/scenarios_mock.json`: presets opcionais de demonstração.

## Saídas em `results/run_<timestamp>/`

- `result.json` (resumo da melhor solução);
- `history.csv` (histórico por geração);
- `execution_params.csv` (parâmetros do AG);
- `execution_summary.json` (métricas agregadas);
- `summary.csv` (resumo tabular final).

## Conceitos de AG usados

- cromossomo inteiro (`num_panels`);
- seleção por torneio;
- crossover aritmético;
- mutação local;
- elitismo;
- fitness com penalidades de custo, déficit, excesso e orçamento (fluxo legado `/optimize`);
- comparação lexicográfica *feasibility-first* (fluxo experimental `/compare`, E5.5).

## Limitações e escopo

- não modela baterias, VPL/LCOE ou orientação/inclinação avançada;
- não usa API externa;
- não usa biblioteca pronta de computação evolutiva.

Essas extensões ficam para trabalhos futuros.
