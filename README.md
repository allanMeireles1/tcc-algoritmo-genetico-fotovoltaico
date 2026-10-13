# Aplicação de Algoritmos Genéticos no Dimensionamento Fotovoltaico (MVP TCC)

Protótipo acadêmico em Python/Streamlit para otimizar a quantidade de painéis solares em residências do Nordeste, com entrada realista de telhado e consumo.

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

### Interface Streamlit (protótipo atual)

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
- fitness com penalidades de custo, déficit, excesso e orçamento.

## Limitações e escopo

- não modela baterias, VPL/LCOE ou orientação/inclinação avançada;
- não usa API externa;
- não usa biblioteca pronta de computação evolutiva.

Essas extensões ficam para trabalhos futuros.
