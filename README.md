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

```bash
pip install -r requirements.txt
streamlit run app.py
```

## O que a interface permite

- informar dimensões do telhado;
- informar consumo mensal;
- escolher cidade (irradiância mock);
- definir orçamento máximo opcional;
- configurar seed e parâmetros do AG;
- comparar AG com baseline direto;
- visualizar convergência, fitness, custo e ocupação do telhado;
- exportar resultados em JSON/CSV.

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
