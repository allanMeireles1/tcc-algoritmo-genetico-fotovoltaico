"""Experimentos acadêmicos: sensibilidade e tempo de execução."""

from time import perf_counter

from src.core.config import GAConfig
from src.genetic.algorithm import run_genetic_algorithm
from src.models.roof import RoofInput
from src.models.result import SensitivityPoint, TimingPoint
from src.simulation.runner import build_problem
from src.utils.seed import set_global_seed


def run_consumption_sensitivity(
    roof: RoofInput,
    city_data: dict,
    panel_data: dict,
    config: GAConfig,
    consumption_levels: list[float],
) -> list[SensitivityPoint]:
    """Executa AG para diferentes níveis de consumo mensal."""
    points: list[SensitivityPoint] = []
    for index, consumption in enumerate(consumption_levels):
        test_roof = RoofInput(
            width_m=roof.width_m,
            length_m=roof.length_m,
            monthly_consumption_kwh=consumption,
            city=roof.city,
            roof_type=roof.roof_type,
            max_budget_brl=roof.max_budget_brl,
        )
        problem = build_problem(test_roof, city_data, panel_data)
        set_global_seed(config.random_seed + index)
        start = perf_counter()
        best, _, _ = run_genetic_algorithm(problem, config)
        elapsed = perf_counter() - start
        points.append(
            SensitivityPoint(
                consumption_kwh=consumption,
                best_panels=best.num_panels,
                best_fitness=best.fitness,
                execution_time_s=elapsed,
            )
        )
    return points


def run_population_timing_experiment(
    roof: RoofInput,
    city_data: dict,
    panel_data: dict,
    base_config: GAConfig,
    population_sizes: list[int],
) -> list[TimingPoint]:
    """Mede tempo de execução variando tamanho da população."""
    problem = build_problem(roof, city_data, panel_data)
    points: list[TimingPoint] = []

    for index, pop_size in enumerate(population_sizes):
        config = GAConfig(
            population_size=pop_size,
            generations=base_config.generations,
            crossover_rate=base_config.crossover_rate,
            mutation_rate=base_config.mutation_rate,
            elitism_count=base_config.elitism_count,
            random_seed=base_config.random_seed,
            cost_weight_alpha=base_config.cost_weight_alpha,
            waste_penalty_weight=base_config.waste_penalty_weight,
            deficit_penalty_weight=base_config.deficit_penalty_weight,
            budget_penalty_weight=base_config.budget_penalty_weight,
        )
        set_global_seed(config.random_seed + index)
        start = perf_counter()
        best, _, _ = run_genetic_algorithm(problem, config)
        elapsed = perf_counter() - start
        points.append(
            TimingPoint(
                label="População",
                parameter_value=pop_size,
                execution_time_s=elapsed,
                best_panels=best.num_panels,
            )
        )
    return points


def run_generations_timing_experiment(
    roof: RoofInput,
    city_data: dict,
    panel_data: dict,
    base_config: GAConfig,
    generation_counts: list[int],
) -> list[TimingPoint]:
    """Mede tempo de execução variando número de gerações."""
    problem = build_problem(roof, city_data, panel_data)
    points: list[TimingPoint] = []

    for index, generations in enumerate(generation_counts):
        config = GAConfig(
            population_size=base_config.population_size,
            generations=generations,
            crossover_rate=base_config.crossover_rate,
            mutation_rate=base_config.mutation_rate,
            elitism_count=base_config.elitism_count,
            random_seed=base_config.random_seed,
            cost_weight_alpha=base_config.cost_weight_alpha,
            waste_penalty_weight=base_config.waste_penalty_weight,
            deficit_penalty_weight=base_config.deficit_penalty_weight,
            budget_penalty_weight=base_config.budget_penalty_weight,
        )
        set_global_seed(config.random_seed + 100 + index)
        start = perf_counter()
        best, _, _ = run_genetic_algorithm(problem, config)
        elapsed = perf_counter() - start
        points.append(
            TimingPoint(
                label="Gerações",
                parameter_value=generations,
                execution_time_s=elapsed,
                best_panels=best.num_panels,
            )
        )
    return points
