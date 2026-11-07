# Dimensionamento Fotovoltaico Residencial com Algoritmos Genéticos — TCC

Aplicação acadêmica desenvolvida para o TCC de Ciência da Computação. O sistema usa um **Algoritmo Genético (AG)** para determinar a quantidade de módulos fotovoltaicos que **minimiza o custo estimado de aquisição e instalação**, sujeita ao atendimento do consumo mensal da residência, à área útil do telhado e, quando informado, ao orçamento máximo.

> **Importante:** este é um protótipo acadêmico. Os dados de irradiação são **simulados (mock)** e os resultados não substituem um projeto fotovoltaico executado por profissional habilitado.

---

## 1. O que é o projeto

O sistema calcula uma configuração de painéis solares para uma residência a partir de:

- largura e comprimento do telhado;
- consumo mensal de energia (kWh);
- cidade de referência;
- orçamento máximo opcional;
- parâmetros do Algoritmo Genético (população, gerações, crossover, mutação, elitismo e seed).

A saída apresenta:

- quantidade recomendada de painéis;
- energia estimada gerada por mês;
- custo estimado dos módulos;
- ocupação da área útil do telhado;
- déficit ou excedente energético;
- comparação entre AG, solução analítica e busca exaustiva;
- gráficos e tabelas para análise.

### Modelo matemático adotado

A única variável de decisão é **N** (quantidade inteira de módulos). O objetivo é:

> minimizar o custo de aquisição e instalação dos módulos, sujeito à cobertura do consumo mensal em todos os meses, à área útil do telhado e ao orçamento opcional.

A geração mensal estimada é calculada por:

\[
E_m(N)=N\cdot\frac{P_{\text{módulo}}}{1000}\cdot HSP_m\cdot30\cdot\eta
\]

em que `P_módulo` é a potência do módulo (Wp), `HSP_m` são as horas de sol pleno por dia, `30` é a aproximação de dias no mês e `η` é a eficiência global.

A avaliação das soluções usa **comparação lexicográfica feasibility-first** (AG v2), e **não** uma função fitness escalar `Eg − Ct`.

---

## 2. O que já está implementado

- **Backend:** Python + FastAPI, com endpoints para cidades, painéis, otimização, baseline, comparação e experimentos.
- **Frontend:** React + Vite (TypeScript), com dashboard, análise do AG, experimentos e comparação.
- **AG v2:** seleção por torneio lexicográfico, elitismo, crossover e mutação, com avaliação lexicográfica feasibility-first.
- **Modelo E5.2:** minimização de custo com restrições; única variável de decisão `N`.
- **Experimentos oficiais:** 3 cenários de consumo (150, 300 e 500 kWh/mês) × 2 configurações de AG (pop10/gen20 e pop20/gen40) × 30 sementes = **180 execuções**.
- **Resultados:** o AG encontrou o ótimo determinístico em **180/180 execuções**; os métodos analítico e exaustivo foram mais rápidos.
- **Validação de software:** **208/208 testes aprovados**.
- **Documentação:** auditoria do artigo, guia editorial, modelo matemático e encerramento técnico na pasta `docs/`.

> A distinção é importante: **180 experimentos** são resultados científicos; **208 testes** são evidência de validação de software. Os dois números aparecem em contextos diferentes.

---

## 3. Arquitetura

```text
┌─────────────────────────────┐
│  Frontend React + Vite      │
│  http://localhost:5173      │
└──────────────┬──────────────┘
               │ HTTP (JSON)
               │ /api/*
┌──────────────▼──────────────┐
│  Backend FastAPI            │
│  http://localhost:8000      │
└──────────────┬──────────────┘
               │
┌──────────────▼──────────────┐
│  Núcleo científico em Python│
│  src/genetic, src/simulation│
│  src/models, src/core       │
└─────────────────────────────┘
```

O frontend chama `/api/*`; o servidor de desenvolvimento do Vite redireciona essas chamadas para `http://localhost:8000`.

---

## 4. Requisitos para rodar no PC do colega

Instale antes:

| Ferramenta | Versão recomendada | Como verificar |
|---|---|---|
| **Python** | 3.11 ou 3.12 | `python --version` |
| **Node.js** | 20 LTS ou superior | `node --version` |
| **npm** | vem com o Node | `npm --version` |
| **Git** | qualquer versão recente | `git --version` |

No Windows, durante a instalação do Python, marque a opção **“Add python.exe to PATH”**.

---

## 5. Passo a passo para executar (Windows)

### 5.1 Clonar o repositório

Abra o **PowerShell** e execute:

```powershell
git clone https://github.com/allanMeireles1/tcc-algoritmo-genetico-fotovoltaico.git
cd tcc-algoritmo-genetico-fotovoltaico
```

### 5.2 Iniciar o backend (terminal 1)

Ainda na pasta raiz do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn backend.app:app --reload --port 8000
```

Se aparecer erro de política de execução no PowerShell, rode uma vez:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

e ative a venv novamente.

**Teste o backend:** abra no navegador:

```text
http://localhost:8000/docs
```

Se a página do Swagger abrir, o backend está funcionando.

### 5.3 Iniciar o frontend (terminal 2)

Abra **outro terminal PowerShell**, entre na pasta do projeto e execute:

```powershell
cd tcc-algoritmo-genetico-fotovoltaico
cd frontend
npm ci
npm run dev
```

Se `npm ci` falhar, use:

```powershell
npm install
```

**Abra o sistema no navegador:**

```text
http://localhost:5173
```

> Mantenha os **dois terminais abertos** enquanto estiver usando o sistema: um com o backend e outro com o frontend.

---

## 6. Como usar o sistema e tirar prints para o artigo

### 6.1 Primeira simulação (Dashboard principal)

1. Abra `http://localhost:5173`.
2. Confira no topo se o indicador da API está **online**.
3. Preencha os campos, por exemplo:

| Campo | Valor sugerido |
|---|---|
| Largura do telhado | `8` m |
| Comprimento do telhado | `10` m |
| Consumo mensal | `300` kWh |
| Cidade | `João Pessoa` |
| Orçamento máximo | deixar em branco |
| População | `20` |
| Gerações | `40` |
| Crossover | `0,8` |
| Mutação | `0,2` |
| Elitismo | `2` |
| Seed | `42` |

4. Clique em **Executar otimização**.
5. Aguarde os cards e gráficos aparecerem.

**Prints recomendados nesta tela:**
- formulário de entrada preenchido;
- cards com painéis recomendados, energia estimada, custo e ocupação;
- gráfico de evolução das soluções ao longo das gerações;
- gráfico de geração × consumo;
- gráfico de ocupação do telhado.

### 6.2 Aba “Análise do AG”

Clique na aba **Análise do AG**.

**Prints recomendados:**
- comparação AG × método direto;
- histograma da população final;
- composição da avaliação (penalidades e termos).

### 6.3 Aba “Experimentos”

Clique na aba **Experimentos** e execute os experimentos.

**Prints recomendados:**
- sensibilidade ao consumo;
- tempo de execução × população;
- tempo de execução × gerações.

### 6.4 Aba “Comparação”

Clique na aba **Comparação**.

**Prints recomendados:**
- cards com tempos médios e desvio-padrão;
- tabela com execuções analítico, exaustivo e AG;
- gráfico de evolução por seed;
- histograma dos tempos do AG.

### 6.5 Print da API (opcional, mas útil)

Abra:

```text
http://localhost:8000/docs
```

Tire um print da documentação interativa do FastAPI. Isso evidencia o backend e os endpoints.

### 6.6 Dica para capturar a tela no Windows

Use **Win + Shift + S** para recortar a área desejada. O print vai para a área de transferência; cole no Word, PowerPoint ou salve como PNG.

> Para os prints do artigo, use os valores padrão da tela ou os valores sugeridos acima. Os números oficiais dos **180 experimentos** estão em `results/e5_4_6/summary.json` e podem ser citados no texto; não é necessário reproduzir os 180 no navegador.

---

## 7. Rodar os testes (opcional)

Com a venv ativada, na raiz do projeto:

```powershell
pip install pytest pytest-cov
pytest tests/ -v
```

A suíte contém **208 testes**. Para o artigo, o número relevante é **208/208 aprovados**.

---

## 8. Endpoints principais da API

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/health` | Verifica se a API está no ar |
| `GET` | `/cities` | Lista cidades disponíveis |
| `GET` | `/panels` | Lista painéis configurados |
| `POST` | `/optimize` | Executa a otimização com AG |
| `POST` | `/baseline` | Calcula o dimensionamento direto |
| `POST` | `/compare` | Compara AG × analítico × exaustivo |
| `POST` | `/experiments/sensitivity` | Sensibilidade ao consumo |
| `POST` | `/experiments/population-timing` | Tempo × população |
| `POST` | `/experiments/generations-timing` | Tempo × gerações |

Documentação interativa: `http://localhost:8000/docs`.

---

## 9. Estrutura do projeto

```text
tcc-algoritmo-genetico-fotovoltaico/
├── backend/                 # FastAPI (rotas, schemas, serviços)
├── frontend/                # React + Vite + TypeScript
│   └── src/components/      # Dashboard, Análise, Experimentos, Comparação
├── src/
│   ├── core/                # configurações e constantes
│   ├── models/              # telhado, painel, indivíduo, resultado
│   ├── genetic/             # AG v1 e AG v2 (lexicográfico)
│   ├── simulation/          # avaliação, solvers, runner, benchmark
│   ├── visualization/       # gráficos
│   └── storage/             # carga de dados mock
├── data/                    # cidades, painéis e cenários mock
├── results/e5_4_6/          # resultados consolidados dos 180 experimentos
├── tests/                   # suíte de testes (208 testes)
├── docs/                    # auditoria, modelo matemático e guia editorial
├── scripts/                 # consolidação experimental
├── requirements.txt
└── README.md
```

---

## 10. Limitações e escopo

- Irradiação **simulada (mock)**: série mensal para João Pessoa; demais cidades usam média anual.
- Modelo com **uma única variável de decisão inteira**: `N` (quantidade de módulos).
- Custo simplificado de **R$ 1.350,00 por módulo** (R$ 1.100 + R$ 250).
- Eficiência global de **0,82**.
- Fator de aproveitamento da área de **0,85**.
- Não modela baterias, inversor, layout detalhado, payback ou LCOE.
- Resultados restritos aos cenários e parâmetros testados.
- **Sem validação em instalações fotovoltaicas reais.**

Esses pontos devem constar nas limitações do artigo. Não afirmar que o AG é superior aos métodos exatos: nos experimentos, o AG encontrou o ótimo, mas os métodos determinísticos foram mais rápidos.

---

## 11. Documentação de apoio

| Documento | Conteúdo |
|---|---|
| `docs/E5_2_MODELO_MATEMATICO.md` | Modelo matemático oficial (E5.2) |
| `docs/E6_1_AUDITORIA_COMPARATIVA.md` | Matriz de divergências do artigo |
| `docs/E6_2_ENCERRAMENTO_TECNICO.md` | Encerramento técnico, limitações e trabalhos futuros |
| `docs/E6_3_AUDITORIA_ARTIGO.md` | Auditoria completa do artigo (seções 1–6 e referências) |
| `docs/GUIA_EDITORIAL_CONSOLIDADO_ARTIGO.md` | Guia operacional para a redação da versão final |
| `results/e5_4_6/summary.json` | Resultados consolidados dos 180 experimentos |

---

## 12. Solução de problemas

| Problema | Solução |
|---|---|
| `python` não é reconhecido | Reinstale o Python marcando “Add python.exe to PATH” |
| `Activate.ps1 cannot be loaded` | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| `npm` não é reconhecido | Instale o Node.js LTS e reabra o terminal |
| `npm ci` falha | Use `npm install` |
| Página abre, mas a API aparece offline | Verifique se o backend está rodando em `http://localhost:8000` |
| Erro de CORS | Use o frontend em `http://localhost:5173` e o backend em `http://localhost:8000` |
| Porta 8000 ocupada | `uvicorn backend.app:app --reload --port 8001` (e ajuste o proxy, se necessário) |
| Porta 5173 ocupada | O Vite escolhe outra porta; confira a mensagem no terminal |
| `streamlit` não encontrado | O Streamlit é legado; use FastAPI + React/Vite |

---

## 13. Observação sobre o protótipo antigo em Streamlit

O arquivo `app.py` e a dependência `streamlit` são mantidos apenas como **referência histórica**. A versão final do produto usa **FastAPI + React/Vite**. Para o artigo, a descrição correta é a arquitetura atual, não o Streamlit.

---

## 14. Licença e uso

Projeto acadêmico desenvolvido para fins de TCC. Não é um produto comercial de dimensionamento fotovoltaico. Para uso real, consulte um engenheiro ou profissional habilitado.
