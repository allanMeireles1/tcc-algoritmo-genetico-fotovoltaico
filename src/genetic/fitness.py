"""Funções de avaliação de energia, custo e fitness."""

from src.core.config import GAConfig
from src.core.constants import DEFAULT_DAYS_PER_MONTH
from src.models.result import FitnessBreakdown


def calc_energy_kwh_month(
    num_panels: int,
    panel_power_wp: float,
    irradiance_kwh_m2_day: float,
    system_efficiency: float,
    days_per_month: int = DEFAULT_DAYS_PER_MONTH,
) -> float:
    """Calcula energia mensal aproximada de geração fotovoltaica."""
    return (
        num_panels
        * (panel_power_wp / 1000.0)
        * irradiance_kwh_m2_day
        * days_per_month
        * system_efficiency
    )


def calc_cost_brl(num_panels: int, panel_cost_brl: float) -> float:
    """Calcula custo total simplificado do sistema."""
    return num_panels * panel_cost_brl


def evaluate_fitness_breakdown(
    num_panels: int,
    problem: dict,
    config: GAConfig,
) -> FitnessBreakdown:
    """Decompõe fitness em termos interpretáveis para gráficos."""
    energy = calc_energy_kwh_month(
        num_panels=num_panels,
        panel_power_wp=float(problem["panel_power_wp"]),
        irradiance_kwh_m2_day=float(problem["irradiance_kwh_m2_day"]),
        system_efficiency=float(problem["system_efficiency"]),
    )
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

    return FitnessBreakdown(
        energy_term=energy,
        cost_penalty=cost_penalty,
        waste_penalty=waste_penalty,
        deficit_penalty=deficit_penalty,
        area_penalty=area_penalty,
        budget_penalty=budget_penalty,
        fitness_total=fitness_total,
        energy_kwh=energy,
        cost_brl=cost,
    )


def evaluate_fitness(num_panels: int, problem: dict, config: GAConfig) -> tuple[float, float, float]:
    """Calcula fitness com penalidades de custo, desperdício e déficit."""
    breakdown = evaluate_fitness_breakdown(num_panels, problem, config)
    return breakdown.fitness_total, breakdown.energy_kwh, breakdown.cost_brl
