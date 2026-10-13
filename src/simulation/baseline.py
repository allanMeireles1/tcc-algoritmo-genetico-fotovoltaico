"""Método direto de comparação (baseline)."""

import math

from src.core.config import GAConfig
from src.genetic.algorithm import max_panels_by_roof
from src.genetic.fitness import calc_energy_kwh_month, evaluate_fitness


def direct_sizing_panels(problem: dict) -> int:
    """Calcula painéis por consumo e limita pela área disponível."""
    energy_per_panel = calc_energy_kwh_month(
        num_panels=1,
        panel_power_wp=float(problem["panel_power_wp"]),
        irradiance_kwh_m2_day=float(problem["irradiance_kwh_m2_day"]),
        system_efficiency=float(problem["system_efficiency"]),
    )
    estimated = math.ceil(float(problem["monthly_consumption_kwh"]) / max(energy_per_panel, 0.001))
    max_by_area = max_panels_by_roof(
        roof_usable_area_m2=float(problem["roof_usable_area_m2"]),
        panel_area_m2=float(problem["panel_area_m2"]),
    )
    return min(estimated, max_by_area)


def evaluate_direct_baseline(problem: dict, config: GAConfig) -> tuple[int, float, float, float]:
    """Avalia baseline: painéis, fitness, energia e custo."""
    panels = direct_sizing_panels(problem)
    fitness, energy, cost = evaluate_fitness(panels, problem, config)
    return panels, fitness, energy, cost
