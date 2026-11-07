# E5.4.7 — Auditoria Científica: Fórmulas, Unidades e Dados

**Data:** 06/11/2026
**Escopo:** verificar consistência entre o artigo, o modelo E5.2 e a implementação atual.
**Regra:** nenhuma alteração de código ou de modelo foi feita nesta auditoria.

## 1. Fórmulas e unidades

| Item | Implementação | Unidade | Status |
|------|---------------|---------|--------|
| Energia mensal | `E_m = N · (P_wp/1000) · HSP_m · 30 · η` | kWh/mês | ✅ dimensionalmente correta (kW × h/dia × dia) |
| Custo | `C(N) = N · C_unit` com `C_unit = 1100 + 250 = 1350` | R$ | ✅ coerente com o modelo linear adotado |
| Área útil | `A_útil = A_bruta · 0,85` | m² | 🟡 hipótese simplificadora |
| Limite por área | `N_max = floor(A_útil / A_módulo)` | painéis | ✅ coerente |
| Restrição energética | `E_m(N) ≥ consumo − 1e-9` para todo mês | kWh | ✅ mês crítico |
| Restrição de orçamento | `N · C_unit ≤ B_max + 1e-6` | R$ | ✅ quando orçamento informado |
| Dias por mês | fixo em 30 | dias | 🟡 hipótese uniforme |
| Eficiência | 0,82 global | adimensional | 🟡 hipótese; sem decomposição de perdas |

## 2. Dados de irradiância

- Arquivo: `data/irradiance_mock.json`.
- Origem declarada: **“Mock inspirado em médias públicas INPE/SONDA”**.
- Unidade: **kWh/m²/dia** (HSP diário).
- Cobertura: **apenas João Pessoa**; demais cidades usam média anual de `cities_mock.json`.
- Média anual de JP: 5,425 kWh/m²/dia; média usada em `cities_mock.json`: 5,4.

**Classificação:** dados **simulados/mock**, não medições de campo.

**Ação obrigatória no TCC:** substituir “dados reais coletados” por “dados simulados inspirados em médias públicas” e registrar a limitação. Se o orientador exigir dados reais, será necessário substituir o arquivo e revalidar os resultados.

## 3. Hipóteses simplificadoras

| Hipótese | Impacto | Status |
|----------|---------|--------|
| Uma única variável de decisão (`N`) | Busca exaustiva trivial; AG sem vantagem demonstrada | 🟡 declarar no TCC |
| Custo linear sem inversor/estrutura/projeto | Subestima custo real | 🟡 declarar |
| Consumo mensal constante | Ignora sazonalidade residencial | 🟡 declarar |
| HSP médio mensal | Ignora variabilidade diária, sombreamento, envelhecimento | 🟡 declarar |
| Fator de área 0,85 | Não representa layout real | 🟡 declarar |
| η = 0,82 global | Perdas agregadas sem decomposição | 🟡 declarar |

## 4. Testes automatizados x validade científica

- A suíte atual valida **funcionamento e reprodutibilidade** (mesmos resultados para mesmas entradas/seeds).
- Ela **não valida** a aderência dos dados à realidade física nem a superioridade do AG.
- A validação científica depende de: dados reais, hipóteses declaradas, análise estatística e comparação justa.

## 5. Verificação de consistência entre métodos

- Analítico, exaustivo e AG v2 usam o mesmo `Problem` e a mesma função `evaluate_candidate`.
- A solução analítica e a busca exaustiva são as referências determinísticas.
- A E5.4.6 confirmou, com 30 seeds por configuração, que o AG reproduz o ótimo nos três cenários de consumo (baixo/médio/alto).

## 6. Pendências e recomendações

1. Corrigir o texto do artigo para não afirmar “dados reais” sem fonte primária.
2. Declarar explicitamente as hipóteses e limitações acima.
3. Definir com o orientador se o modelo permanece unidimensional ou se será ampliado.
4. Se o modelo mudar, refazer E5.4.6/E5.4.5 com o novo espaço de busca.
5. Manter a distinção: **o AG encontrou o ótimo do modelo** ≠ **o AG é vantajoso para o problema real**.

## 7. Conclusão

- Fórmulas e unidades do modelo E5.2: **consistentes internamente**.
- Dados de irradiância: **mock**, não reais — exigem correção de redação.
- A implementação está apta para a consolidação experimental, desde que as limitações sejam declaradas com honestidade no TCC.
