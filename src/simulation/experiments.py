"""Experimentos acadêmicos: sensibilidade e tempo de execução."""

from dataclasses import replace
from time import perf_counter

from src.core.config import GAConfig
from src.genetic.algorithm import run_genetic_algorithm, run_genetic_algorithm_v2
from src.models.roof import RoofInput
from src.models.result import SensitivityPoint, TimingPoint
from src.simulation.runner import build_problem
from src.simulation.evaluation import build_problem_from_data
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


def _run_hyperparameter_sweep(
    problem,
    base_config: GAConfig,
    label: str,
    parameter: str,
    values: list[float],
) -> list[TimingPoint]:
    """Executa o AG v2 variando um único hiperparâmetro, com a mesma seed."""
    points: list[TimingPoint] = []
    for value in values:
        config = replace(base_config, **{parameter: value})
        set_global_seed(config.random_seed)
        start = perf_counter()
        best, _, _ = run_genetic_algorithm_v2(problem, config)
        elapsed = perf_counter() - start
        points.append(
            TimingPoint(
                label=label,
                parameter_value=value,
                execution_time_s=elapsed,
                best_panels=best.num_panels,
            )
        )
    return points


def _problem_from_roof(roof: RoofInput, city_data: dict, panel_data: dict):
    return build_problem_from_data(
        roof.monthly_consumption_kwh,
        roof.usable_area_m2(),
        panel_data,
        city_data,
        irradiance_data=None,
        max_budget_brl=roof.max_budget_brl,
    )


def run_population_sensitivity(
    roof: RoofInput,
    city_data: dict,
    panel_data: dict,
    base_config: GAConfig,
    population_sizes: list[int],
) -> list[TimingPoint]:
    """Sensibilidade ao tamanho da população (AG v2)."""
    return _run_hyperparameter_sweep(
        _problem_from_roof(roof, city_data, panel_data),
        base_config,
        "População",
        "population_size",
        population_sizes,
    )


def run_generations_sensitivity(
    roof: RoofInput,
    city_data: dict,
    panel_data: dict,
    base_config: GAConfig,
    generation_counts: list[int],
) -> list[TimingPoint]:
    """Sensibilidade ao número de gerações (AG v2)."""
    return _run_hyperparameter_sweep(
        _problem_from_roof(roof, city_data, panel_data),
        base_config,
        "Gerações",
        "generations",
        generation_counts,
    )


def run_mutation_rate_sensitivity(
    roof: RoofInput,
    city_data: dict,
    panel_data: dict,
    base_config: GAConfig,
    mutation_rates: list[float],
) -> list[TimingPoint]:
    """Sensibilidade à taxa de mutação (AG v2)."""
    return _run_hyperparameter_sweep(
        _problem_from_roof(roof, city_data, panel_data),
        base_config,
        "Taxa de mutação",
        "mutation_rate",
        mutation_rates,
    )


def run_crossover_rate_sensitivity(
    roof: RoofInput,
    city_data: dict,
    panel_data: dict,
    base_config: GAConfig,
    crossover_rates: list[float],
) -> list[TimingPoint]:
    """Sensibilidade à taxa de crossover (AG v2)."""
    return _run_hyperparameter_sweep(
        _problem_from_roof(roof, city_data, panel_data),
        base_config,
        "Taxa de crossover",
        "crossover_rate",
        crossover_rates,
    )


def run_elitism_sensitivity(
    roof: RoofInput,
    city_data: dict,
    panel_data: dict,
    base_config: GAConfig,
    elitism_counts: list[int],
) -> list[TimingPoint]:
    """Sensibilidade ao número de elitistas (AG v2)."""
    return _run_hyperparameter_sweep(
        _problem_from_roof(roof, city_data, panel_data),
        base_config,
        "Elitismo",
        "elitism_count",
        elitism_counts,
    )
