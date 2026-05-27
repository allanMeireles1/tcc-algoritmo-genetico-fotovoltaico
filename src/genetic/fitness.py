"""Funções de avaliação de energia, custo e fitness."""

from src.core.config import GAConfig
from src.core.constants import DEFAULT_DAYS_PER_MONTH


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


def evaluate_fitness(num_panels: int, scenario: dict, config: GAConfig) -> tuple[float, float, float]:
    """Calcula fitness com penalidades de custo, desperdício e déficit."""
    energy = calc_energy_kwh_month(
        num_panels=num_panels,
        panel_power_wp=float(scenario["panel_power_wp"]),
        irradiance_kwh_m2_day=float(scenario["irradiance_kwh_m2_day"]),
        system_efficiency=float(scenario["system_efficiency"]),
    )
    cost = calc_cost_brl(num_panels=num_panels, panel_cost_brl=float(scenario["panel_cost_brl"]))
    demand = float(scenario["monthly_consumption_kwh"])

    waste = max(energy - demand, 0.0)
    deficit = max(demand - energy, 0.0)
    panel_area = float(scenario["panel_area_m2"])
    usable_area = float(scenario["roof_usable_area_m2"])
    used_area = num_panels * panel_area
    area_excess = max(used_area - usable_area, 0.0)

    budget_limit = scenario.get("max_budget_brl")
    over_budget = 0.0
    if budget_limit is not None:
        over_budget = max(cost - float(budget_limit), 0.0)

    fitness = (
        energy
        - (config.cost_weight_alpha * cost)
        - (config.waste_penalty_weight * waste)
        - (config.deficit_penalty_weight * deficit)
        - (config.deficit_penalty_weight * area_excess * 10.0)
        - (config.budget_penalty_weight * over_budget / 100.0)
    )
    return fitness, energy, cost
