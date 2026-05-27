"""Modelos de saída de simulação e execução."""

from dataclasses import dataclass


@dataclass(slots=True)
class GenerationStats:
    """Resumo por geração."""

    generation: int
    best_fitness: float
    avg_fitness: float
    best_panels: int


@dataclass(slots=True)
class ScenarioRunResult:
    """Resultado final de uma execução de otimização."""

    execution_label: str
    city: str
    best_num_panels: int
    best_fitness: float
    best_energy_kwh_month: float
    best_cost_brl: float
    monthly_consumption_kwh: float
    roof_area_m2: float
    roof_usable_area_m2: float
    roof_occupancy_ratio: float
    energy_surplus_kwh: float
    energy_deficit_kwh: float
    benchmark_panels: int
    benchmark_fitness: float
    budget_limit_brl: float | None
    under_budget: bool
    execution_time_s: float
    generations: int
    run_seed: int
