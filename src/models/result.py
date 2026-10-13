"""Modelos de saída de simulação e execução."""

from dataclasses import dataclass, field

from src.models.individual import Individual


@dataclass(slots=True)
class GenerationStats:
    """Resumo por geração."""

    generation: int
    best_fitness: float
    avg_fitness: float
    best_panels: int


@dataclass(slots=True)
class FitnessBreakdown:
    """Componentes da função de fitness para visualização."""

    energy_term: float
    cost_penalty: float
    waste_penalty: float
    deficit_penalty: float
    area_penalty: float
    budget_penalty: float
    fitness_total: float
    energy_kwh: float
    cost_brl: float


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
    panel_area_m2: float
    energy_surplus_kwh: float
    energy_deficit_kwh: float
    benchmark_panels: int
    benchmark_fitness: float
    benchmark_energy_kwh_month: float
    benchmark_cost_brl: float
    budget_limit_brl: float | None
    under_budget: bool
    execution_time_s: float
    generations: int
    run_seed: int


@dataclass(slots=True)
class OptimizationOutcome:
    """Pacote completo retornado após otimização."""

    result: ScenarioRunResult
    history: list[GenerationStats]
    summary: dict
    final_population: list[Individual] = field(default_factory=list)
    fitness_breakdown: FitnessBreakdown | None = None


@dataclass(slots=True)
class SensitivityPoint:
    """Ponto de experimento de sensibilidade ao consumo."""

    consumption_kwh: float
    best_panels: int
    best_fitness: float
    execution_time_s: float


@dataclass(slots=True)
class TimingPoint:
    """Ponto de experimento de tempo de execução."""

    label: str
    parameter_value: int
    execution_time_s: float
    best_panels: int
