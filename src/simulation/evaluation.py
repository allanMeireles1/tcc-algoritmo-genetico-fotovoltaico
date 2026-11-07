"""Módulo de avaliação matemática conforme especificação E5.2.

Implementa o contrato de avaliação feasibility-first com comparação lexicográfica,
sem uso de fitness escalar ou constantes artificiais.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


# =============================================================================
# Constantes de tolerância numérica (Seção 6.2.2 da E5.2)
# =============================================================================

EPS_ENERGY = 1e-9    # kWh
EPS_AREA = 1e-9      # m²
EPS_BUDGET = 1e-6    # R$

DEFAULT_DAYS_PER_MONTH = 30


# =============================================================================
# Estruturas de dados do problema e resultado
# =============================================================================

@dataclass(slots=True, frozen=True)
class Problem:
    """Parâmetros do problema de dimensionamento fotovoltaico.

    Corresponde à formulação consolidada da Seção 3.4 da E5.2.
    """
    consumption: float                    # E_consumo (kWh/mês)
    usable_area: float                    # A_útil (m²)
    panel_area: float                     # A_módulo (m²)
    panel_power_wp: float                 # P_módulo (Wp)
    hsp: dict[int, float]                 # HSP_m por mês (1-12), em kWh/m²/dia
    efficiency: float                     # η (adimensional)
    unit_cost: float                      # C_unit (R$/painel)
    budget: float | None = None           # B_max (R$), opcional


@dataclass(slots=True, frozen=True)
class EvaluationResult:
    """Resultado da avaliação de um candidato N.

    Campos necessários para compare_lexicographic (Seção 6.3).
    """
    num_panels: int
    feasible: bool
    cost: float
    violation: float
    energy_violation: float
    area_violation: float
    budget_violation: float
    energy_by_month: dict[int, float]
    used_area: float
    occupancy: float


# =============================================================================
# Validação auxiliar
# =============================================================================

def _require_finite(name: str, value: float) -> None:
    """Valida que um parâmetro numérico é finito (não NaN, não infinito)."""
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} deve ser um número finito")


def _validate_problem(problem: Problem) -> None:
    """Valida as pré-condições do modelo (Seção 6.2.1)."""
    _require_finite("consumption", problem.consumption)
    _require_finite("usable_area", problem.usable_area)
    _require_finite("panel_area", problem.panel_area)
    _require_finite("panel_power_wp", problem.panel_power_wp)
    _require_finite("efficiency", problem.efficiency)
    _require_finite("unit_cost", problem.unit_cost)
    for m in range(1, 13):
        _require_finite(f"HSP[{m}]", problem.hsp[m])
    if problem.budget is not None:
        _require_finite("budget", problem.budget)

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
        if problem.hsp[m] <= 0:
            raise ValueError(f"HSP[{m}] deve ser > 0")
    if problem.budget is not None and problem.budget <= 0:
        raise ValueError("budget, se informado, deve ser > 0")


# =============================================================================
# Avaliação principal
# =============================================================================

def evaluate_candidate(N: int, problem: Problem) -> EvaluationResult:
    """Avalia um candidato N segundo o modelo feasibility-first (Seção 6.2).

    Retorna EvaluationResult com todos os campos necessários para
    compare_lexicographic. NÃO retorna fitness escalar.
    """
    import math

    # --- Validação de domínio de N (Seção 3.4: N ∈ ℤ≥₀) ---
    # bool é subclasse de int em Python; rejeitar explicitamente
    if isinstance(N, bool) or not isinstance(N, int):
        raise ValueError("N deve ser um número inteiro")
    if N < 0:
        raise ValueError("N deve ser >= 0")

    # --- Validação de entrada ---
    _validate_problem(problem)

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
        )

    # --- Restrição energética: mês crítico (com tolerância) ---
    energy_by_month: dict[int, float] = {}
    energy_violation = 0.0
    for m in range(1, 13):
        E = (
            N
            * (problem.panel_power_wp / 1000.0)
            * problem.hsp[m]
            * DEFAULT_DAYS_PER_MONTH
            * problem.efficiency
        )
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
        occupancy=used_area / problem.usable_area,
    )


# =============================================================================
# Comparação lexicográfica (Regra Oficial, Seção 6.3)
# =============================================================================

def compare_lexicographic(A: EvaluationResult, B: EvaluationResult) -> EvaluationResult:
    """Comparação lexicográfica feasibility-first (Regra Oficial, Seção 6.3).

    Retorna o indivíduo superior.

    Ordem de prioridade:
    1. Viável vence inviável.
    2. Entre viáveis, menor custo vence.
    3. Entre inviáveis, menor violação total vence.
    4. Persistindo empate, menor déficit energético vence.
    5. Persistindo empate, menor número de painéis vence (determinístico).
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


# =============================================================================
# Helpers para construção de Problem a partir dos dados existentes
# =============================================================================

_MONTH_ORDER = [
    "jan", "feb", "mar", "apr", "may", "jun",
    "jul", "aug", "sep", "oct", "nov", "dec"
]


def build_problem_from_data(
    monthly_consumption_kwh: float,
    roof_usable_area_m2: float,
    panel_data: dict[str, Any],
    city_data: dict[str, Any],
    irradiance_data: dict[str, Any] | None = None,
    max_budget_brl: float | None = None,
) -> Problem:
    """Constrói Problem a partir dos dicionários de dados do projeto.

    Usa HSP mensal de irradiance_mock.json quando disponível para a cidade;
    caso contrário, usa a média anual de cities_mock.json como HSP constante.
    """
    # Usa irradiance_data passado explicitamente (do irradiance_mock.json)
    if irradiance_data and "monthly_kwh_m2_day" in irradiance_data:
        monthly = irradiance_data["monthly_kwh_m2_day"]
        hsp = {i + 1: float(monthly[_MONTH_ORDER[i]]) for i in range(12)}
    else:
        # Fallback: média anual como HSP constante
        annual_mean = float(city_data.get("irradiance_kwh_m2_day", 5.4))
        hsp = {m: annual_mean for m in range(1, 13)}

    unit_cost = float(panel_data["panel_cost_brl"]) + float(panel_data["installation_cost_per_panel_brl"])

    return Problem(
        consumption=monthly_consumption_kwh,
        usable_area=roof_usable_area_m2,
        panel_area=float(panel_data["panel_area_m2"]),
        panel_power_wp=float(panel_data["panel_power_wp"]),
        hsp=hsp,
        efficiency=float(panel_data["system_efficiency"]),
        unit_cost=unit_cost,
        budget=max_budget_brl,
    )


def is_feasible(N: int, problem: Problem) -> bool:
    """Verificação de viabilidade direta (usada pela busca exaustiva, Seção 5.2).

    Usa exatamente as mesmas tolerâncias de evaluate_candidate.
    """
    if N == 0 and problem.consumption > 0:
        return False
    for m in range(1, 13):
        E = (
            N
            * (problem.panel_power_wp / 1000.0)
            * problem.hsp[m]
            * DEFAULT_DAYS_PER_MONTH
            * problem.efficiency
        )
        if E < problem.consumption - EPS_ENERGY:
            return False
    if N * problem.panel_area > problem.usable_area + EPS_AREA:
        return False
    if problem.budget is not None and N * problem.unit_cost > problem.budget + EPS_BUDGET:
        return False
    return True