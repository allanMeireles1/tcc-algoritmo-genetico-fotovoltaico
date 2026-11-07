"""Modelos de saída de simulação e execução."""

from dataclasses import dataclass, field

from src.models.individual import Individual
from src.simulation.evaluation import EvaluationResult, Problem


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


@dataclass(slots=True, frozen=True)
class ConvergenceMetrics:
    """Métricas de convergência de uma execução do AG."""

    run_seed: int
    best_panels_trajectory: tuple[int, ...]  # best_panels por geração
    generations: int
    converged: bool
    convergence_generation: int | None  # índice da geração em que estabilizou
    first_optimal_generation: int | None  # primeira geração com o ótimo conhecido
    generations_to_optimum: int | None
    final_best_panels: int
    stability_end_count: int  # quantas gerações finais têm o mesmo valor


@dataclass(slots=True, frozen=True)
class MethodResult:
    """Resultado de um método (analítico, exaustivo ou AG) em uma execução experimental."""

    method: str
    run_index: int
    run_seed: int | None
    execution_time_s: float
    evaluation: EvaluationResult


@dataclass(slots=True)
class ComparisonOutcome:
    """Pacote experimental comparando AG, solução analítica e busca exaustiva no mesmo Problem."""

    execution_label: str
    city: str
    problem: Problem
    results: list[MethodResult]
    config: dict
    analytical_diagnostic: dict
    summary: dict
    convergence: list[ConvergenceMetrics] = field(default_factory=list)
    convergence_summary: dict = field(default_factory=dict)
    genetic_histories: dict[int, list[GenerationStats]] = field(default_factory=dict)


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


@dataclass(slots=True, frozen=True)
class BenchmarkMethodStats:
    """Estatísticas de tempo e qualidade de um método no benchmark (E5.4.5)."""

    method: str
    repetitions: int
    times_s: tuple[float, ...]
    mean_s: float
    median_s: float
    std_s: float
    min_s: float
    max_s: float
    best_panels_values: tuple[int, ...]
    feasible_count: int
    matches_optimum_count: int
    mean_cost_brl: float
    mean_energy_kwh_month: float


@dataclass(slots=True)
class BenchmarkOutcome:
    """Resultado do benchmark comparativo entre os três métodos (E5.4.5)."""

    execution_label: str
    city: str
    repetitions: int
    warmup: int
    config: dict
    reference_panels: int
    methods: list[BenchmarkMethodStats]
    speedups: dict[str, float]
    summary: dict
