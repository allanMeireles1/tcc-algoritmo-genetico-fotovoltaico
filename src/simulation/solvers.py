"""Solução analítica e busca exaustiva para dimensionamento fotovoltaico.

Implementa os métodos de referência da E5.2 (Seções 4 e 5):
- solve_analytical: solução analítica direta
- solve_exhaustive: busca exaustiva no espaço discreto

Ambos utilizam exclusivamente o modelo de avaliação (evaluate_candidate,
compare_lexicographic) sem duplicar fórmulas ou políticas de tolerância.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from src.simulation.evaluation import (
    Problem,
    EvaluationResult,
    EPS_ENERGY,
    EPS_AREA,
    EPS_BUDGET,
    DEFAULT_DAYS_PER_MONTH,
    evaluate_candidate,
    compare_lexicographic,
)


# =============================================================================
# Estruturas de resultado dos solvers
# =============================================================================

@dataclass(slots=True, frozen=True)
class AnalyticalSolution:
    """Resultado da solução analítica.

    Attributes:
        num_panels: Número de painéis recomendado pela fórmula analítica.
        feasible: Se a solução satisfaz todas as restrições.
        N_energy: Mínimo de painéis para atender energia (mês crítico).
        N_area: Máximo de painéis permitido pela área.
        N_budget: Máximo de painéis permitido pelo orçamento (ou None).
        N_max: Limite superior efetivo do espaço de busca.
        evaluation: Avaliação completa do candidato recomendado.
    """
    num_panels: int
    feasible: bool
    N_energy: int
    N_area: int
    N_budget: int | None
    N_max: int
    evaluation: EvaluationResult


@dataclass(slots=True, frozen=True)
class ExhaustiveResult:
    """Resultado da busca exaustiva.

    Attributes:
        best: Melhor candidato encontrado segundo compare_lexicographic.
        evaluated_count: Quantidade de candidatos avaliados (N = 0..N_max).
        N_max: Limite superior do espaço de busca.
    """
    best: EvaluationResult
    evaluated_count: int
    N_max: int


# =============================================================================
# Cálculo dos limites do espaço de busca
# =============================================================================

def _compute_energy_per_panel(problem: Problem) -> dict[int, float]:
    """Calcula energia gerada por painel para cada mês (kWh/mês)."""
    factor = (problem.panel_power_wp / 1000.0) * DEFAULT_DAYS_PER_MONTH * problem.efficiency
    return {m: factor * problem.hsp[m] for m in range(1, 13)}


def _compute_N_energy(problem: Problem) -> int:
    """Mínimo de painéis para atender consumo no mês crítico.

    Fórmula: max(ceil((consumption - EPS_ENERGY) / E_per_panel_m)) para m=1..12
    """
    energy_per_panel = _compute_energy_per_panel(problem)
    # Mês crítico = pior HSP = menor energia por painel
    min_energy_per_panel = min(energy_per_panel.values())
    # Nota: usamos EPS_ENERGY no numerador conforme especificação
    # ceil((consumption - EPS) / E_per_panel)
    N = math.ceil((problem.consumption - EPS_ENERGY) / min_energy_per_panel)
    return max(0, N)


def _compute_N_area(problem: Problem) -> int:
    """Máximo de painéis permitido pela área útil (com tolerância).

    Fórmula: floor((usable_area + EPS_AREA) / panel_area)
    """
    return int(math.floor((problem.usable_area + EPS_AREA) / problem.panel_area))


def _compute_N_budget(problem: Problem) -> int | None:
    """Máximo de painéis permitido pelo orçamento (com tolerância).

    Fórmula: floor((budget + EPS_BUDGET) / unit_cost)
    Retorna None se não houver orçamento.
    """
    if problem.budget is None:
        return None
    return int(math.floor((problem.budget + EPS_BUDGET) / problem.unit_cost))


def _compute_N_max(problem: Problem) -> int:
    """Limite superior do espaço de busca (N = 0, 1, ..., N_max)."""
    N_area = _compute_N_area(problem)
    N_budget = _compute_N_budget(problem)

    if N_budget is None:
        return N_area
    return min(N_area, N_budget)


# =============================================================================
# Solução Analítica (Seção 4 da E5.2)
# =============================================================================

def solve_analytical(problem: Problem) -> AnalyticalSolution:
    """Resolve o problema analiticamente conforme E5.2 Seção 4.

    O modelo minimiza custo = N * unit_cost sujeito a:
    - Energia: E_m(N) >= consumption - EPS_ENERGY para todo m=1..12
    - Área: N * panel_area <= usable_area + EPS_AREA
    - Orçamento (opcional): N * unit_cost <= budget + EPS_BUDGET
    - N ∈ ℤ≥₀

    Passos:
    1. Calcula N_energy = mínimo para atender energia (mês crítico)
    2. Calcula N_area = máximo pela área
    3. Calcula N_budget = máximo pelo orçamento (se houver)
    4. N_max = min(N_area, N_budget) [ou N_area se sem orçamento]
    5. Se N_energy <= N_max: viável, ótimo = N_energy
       Se N_energy > N_max: inviável, melhor permitido = N_max

    A solução é avaliada via evaluate_candidate() para consistência.

    Returns:
        AnalyticalSolution com todos os campos intermediários e avaliação.
    """
    _validate_problem_for_solver(problem)

    N_energy = _compute_N_energy(problem)
    N_area = _compute_N_area(problem)
    N_budget = _compute_N_budget(problem)
    N_max = _compute_N_max(problem)

    # Candidato analítico: N_energy se viável, senão N_max (melhor permitido)
    if N_energy <= N_max:
        candidate_N = N_energy
    else:
        candidate_N = N_max

    evaluation = evaluate_candidate(candidate_N, problem)

    return AnalyticalSolution(
        num_panels=candidate_N,
        feasible=evaluation.feasible,
        N_energy=N_energy,
        N_area=N_area,
        N_budget=N_budget,
        N_max=N_max,
        evaluation=evaluation,
    )


# =============================================================================
# Busca Exaustiva (Seção 5 da E5.2)
# =============================================================================

def solve_exhaustive(problem: Problem) -> ExhaustiveResult:
    """Busca exaustiva no espaço discreto N ∈ {0, 1, ..., N_max}.

    Para cada N:
    1. Avalia via evaluate_candidate(N, problem)
    2. Compara com o melhor atual via compare_lexicographic
    3. Retorna o melhor global

    A busca exaustiva é a referência de ótimo global para o espaço definido.

    Returns:
        ExhaustiveResult com o melhor candidato e metadados.
    """
    _validate_problem_for_solver(problem)

    N_max = _compute_N_max(problem)

    best: EvaluationResult | None = None
    evaluated_count = 0

    for N in range(0, N_max + 1):
        evaluated_count += 1
        candidate = evaluate_candidate(N, problem)
        if best is None:
            best = candidate
        else:
            best = compare_lexicographic(best, candidate)

    assert best is not None, "Espaço de busca não pode ser vazio (N_max >= 0)"

    return ExhaustiveResult(
        best=best,
        evaluated_count=evaluated_count,
        N_max=N_max,
    )


# =============================================================================
# Validação auxiliar
# =============================================================================

def _validate_problem_for_solver(problem: Problem) -> None:
    """Validações básicas para os solvers (reaproveita _validate_problem)."""
    from src.simulation.evaluation import _validate_problem
    _validate_problem(problem)
    # Garante que N_max >= 0
    N_max = _compute_N_max(problem)
    if N_max < 0:
        raise ValueError("Limite superior do espaço de busca é negativo (parâmetros inválidos)")