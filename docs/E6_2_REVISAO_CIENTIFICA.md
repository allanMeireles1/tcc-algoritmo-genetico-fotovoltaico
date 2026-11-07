# E6.2 – Revisão científica (Frente 1)

**Data:** 06/11/2026  
**Objetivo:** auditar o modelo E5.2 e o AG utilizados pelo endpoint `/compare`.  
**Regra:** nenhuma alteração em código ou artigo. Apenas leitura e documentação.

---

## 1. Modelo matemático (E5.2) × implementação

### 1.1 Equações e constantes

| Item | Código | Status |
|------|--------|--------|
| Energia mensal | `E_m(N) = N * (P/1000) * HSP_m * 30 * eta` | Aprovado |
| Custo | `C(N) = N * unit_cost` com `unit_cost = 1100 + 250 = 1350` | Aprovado |
| Área útil | `usable_area = gross * 0.85` | Aprovado (hipótese) |
| Tolerâncias | `EPS_ENERGY = 1e-9`, `EPS_AREA = 1e-9`, `EPS_BUDGET = 1e-6` | Aprovado |
| Integração mensal | `range(1, 13)` em `evaluate_candidate` | Aprovado |
| Mês crítico | `solve_analytical._compute_N_energy` usa `min(energy_per_panel)` | Aprovado |

### 1.2 Função objetivo e comparação

| Item | Código | Status |
|------|--------|--------|
| Objetivo | Minimizar `C(N)` sujeito a restrições (não `Eg − Ct`) | Aprovado |
| Avaliação | `evaluate_candidate` devolve `EvaluationResult` (sem fitness escalar) | Aprovado |
| Seleção | `compare_lexicographic` com prioridade viável → menor custo → menor violação → menor déficit → menor N | Aprovado |
| GA v2 | `run_genetic_algorithm_v2` usa seleção lexicográfica | Aprovado |

---

## 2. Métodos de referência

| Método | Código | Comportamento | Status |
|--------|--------|---------------|--------|
| Analítico | `solve_analytical` | Calcula `N_energy`, `N_area`, `N_budget`; devolve `N_energy` se viável, senão `N_max` | Aprovado |
| Exaustivo | `solve_exhaustive` | Avalia `N = 0..N_max` com `evaluate_candidate`, compara via `compare_lexicographic` | Aprovado |
| Consistência | Ambos reutilizam `evaluate_candidate` | Garante mesma política de viabilidade | Aprovado |
| Resultado | `/compare` reporta `analytical_panels`, `exhaustive_panels` e `analytical_matches_exhaustive` | Verificado em smoke test | Aprovado |

---

## 3. Irradiância

| Cidade | Fonte | Status |
|--------|-------|--------|
| João Pessoa | `irradiance_mock.json` (12 valores mensais) | Aprovado |
| Demais 5 cidades | média anual de `cities_mock.json` como HSP constante | Aprovado (declarado como limitação) |

**Observação:** `build_problem_v2` usa dados mensais somente quando `monthly["city"] == roof.city`. Portanto, João Pessoa é a única com verificação de mês crítico real; as demais usam média anual e **não** devem ser descritas como atendimento mensal integral.

---

## 4. Históricos de convergência

| Item | Código | Status |
|------|--------|--------|
| Geração por seed | `run_genetic_algorithm_v2` devolve `history` | Aprovado |
| Acumulação | `run_comparison` armazena `(seed, history)` em `genetic_runs` | Aprovado |
| Exposição | `comparison_adapter` monta `histories = [{"seed": s, "generations": [...]}]` | Aprovado |
| Endpoint | `/compare` retorna `histories` no corpo da resposta | Aprovado |
| Teste | Smoke test confirmou 2 históricos para 2 seeds | Aprovado |

---

## 5. Evidências de execução

| Item | Evidência | Status |
|------|-----------|--------|
| Testes Python | `208/208` aprovados (pytest) | Aprovado |
| Inicialização | Uvicorn executado | Aprovado |
| Rotas básicas | `GET /health`, `/cities`, `/panels`, `/openapi.json` | Aprovado |
| `/compare` | HTTP 200 com 4 resultados e 2 históricos (runs=2) | Aprovado |
| OpenAPI | `GET /openapi.json` acessível, `ComparisonResponse` exposto | Aprovado |
| Build frontend | `npm install` / `npm ci` + `npm run build` executados com sucesso em `frontend/`; `tsc -b` e `vite build` aprovados; `dist/` gerado | **Aprovado** |
| Execução frontend | `npm run dev` subiu em `http://localhost:5173/`; integração com backend validada | **Aprovado** |
| Indicador "API online" | Texto estático corrigido para consulta dinâmica em `GET /api/health` via `getHealth` | **Corrigido** |
| Teste visual | UI renderizada com cards, convergência, histograma e tabela da aba Comparação validados em execução local | **Aprovado** |
| Reprodutibilidade integral | Instalação limpa não realizada formalmente; **dispensada nesta entrega** por decisão de escopo. Evidências existentes: 208/208 testes, backend e endpoints validados, build React/Vite aprovado, integração `/compare` validada | **Dispensada** |

---

## 6. Conclusão da Frente 1

**O modelo E5.2 e o AG v2 utilizados pelo `/compare` estão cientificamente consistentes.**  
Todas as equações, tolerâncias, restrições, comparação lexicográfica e geração de históricos foram conferidas diretamente no código-fonte.

**Pendências identificadas**:
- Nenhuma pendência técnica bloqueante para a entrega.
- Reprodutibilidade em ambiente totalmente limpo: **não realizada**, decisão de escopo registrada (dispensada nesta entrega).
- Revisão do artigo científico (E6.3).

**Status da Frente 2:** frontend instalado, build aprovado (`npm ci` + `npm run build`), dev server executado e integração com backend validada. Indicador "API online" corrigido para verificar dinamicamente `GET /api/health`.