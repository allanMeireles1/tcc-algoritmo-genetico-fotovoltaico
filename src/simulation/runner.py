"""Orquestração de execução por entrada real do usuário."""

from dataclasses import asdict
from statistics import mean
from time import perf_counter

from src.core.config import GAConfig
from src.genetic.algorithm import run_genetic_algorithm
from src.genetic.fitness import evaluate_fitness
from src.models.roof import RoofInput
from src.models.result import GenerationStats, ScenarioRunResult
from src.simulation.baseline import evaluate_direct_baseline
from src.utils.seed import set_global_seed
from src.utils.validators import validate_roof_input


def _build_problem(roof: RoofInput, city_data: dict, panel_data: dict) -> dict:
    """Monta dicionário de problema para AG e baseline."""
    return {
        "city": roof.city,
        "monthly_consumption_kwh": roof.monthly_consumption_kwh,
        "roof_area_m2": roof.gross_area_m2,
        "roof_usable_area_m2": roof.usable_area_m2(),
        "max_budget_brl": roof.max_budget_brl,
        "roof_type": roof.roof_type,
        "irradiance_kwh_m2_day": float(city_data["irradiance_kwh_m2_day"]),
        "panel_power_wp": float(panel_data["panel_power_wp"]),
        "panel_cost_brl": float(panel_data["panel_cost_brl"]) + float(panel_data["installation_cost_per_panel_brl"]),
        "panel_area_m2": float(panel_data["panel_area_m2"]),
        "system_efficiency": float(panel_data["system_efficiency"]),
    }


def run_optimization(
    roof: RoofInput,
    city_data: dict,
    panel_data: dict,
    config: GAConfig,
    runs: int = 1,
) -> tuple[ScenarioRunResult, list[GenerationStats], dict]:
    """Executa AG múltiplas vezes e retorna melhor execução e estatísticas."""
    validate_roof_input(roof)
    problem = _build_problem(roof, city_data, panel_data)

    best_result: ScenarioRunResult | None = None
    best_history: list[GenerationStats] = []
    run_fitness_values: list[float] = []
    run_times: list[float] = []

    for run_index in range(runs):
        current_seed = config.random_seed + run_index
        set_global_seed(current_seed)
        start = perf_counter()
        best_individual, history = run_genetic_algorithm(problem, config)
        execution_time = perf_counter() - start

        best_fitness, energy, cost = evaluate_fitness(best_individual.num_panels, problem, config)
        benchmark_panels, benchmark_fitness = evaluate_direct_baseline(problem, config)
        area_used = best_individual.num_panels * float(problem["panel_area_m2"])
        energy_deficit = max(roof.monthly_consumption_kwh - energy, 0.0)
        energy_surplus = max(energy - roof.monthly_consumption_kwh, 0.0)

        run_result = ScenarioRunResult(
            execution_label=f"{roof.city}_{roof.width_m:.1f}x{roof.length_m:.1f}",
            city=roof.city,
            best_num_panels=best_individual.num_panels,
            best_fitness=best_fitness,
            best_energy_kwh_month=energy,
            best_cost_brl=cost,
            monthly_consumption_kwh=roof.monthly_consumption_kwh,
            roof_area_m2=roof.gross_area_m2,
            roof_usable_area_m2=roof.usable_area_m2(),
            roof_occupancy_ratio=area_used / max(roof.usable_area_m2(), 0.001),
            energy_surplus_kwh=energy_surplus,
            energy_deficit_kwh=energy_deficit,
            benchmark_panels=benchmark_panels,
            benchmark_fitness=benchmark_fitness,
            budget_limit_brl=roof.max_budget_brl,
            under_budget=roof.max_budget_brl is None or cost <= roof.max_budget_brl,
            execution_time_s=execution_time,
            generations=config.generations,
            run_seed=current_seed,
        )
        run_fitness_values.append(best_fitness)
        run_times.append(execution_time)

        if best_result is None or run_result.best_fitness > best_result.best_fitness:
            best_result = run_result
            best_history = history

    if best_result is None:
        raise RuntimeError("Nenhuma execução foi realizada.")

    summary = {
        "runs": runs,
        "fitness_mean": mean(run_fitness_values),
        "fitness_best": max(run_fitness_values),
        "fitness_worst": min(run_fitness_values),
        "execution_time_mean_s": mean(run_times),
    }
    return best_result, best_history, summary


def results_to_rows(results: list[ScenarioRunResult]) -> list[dict]:
    """Converte resultados para linhas tabulares."""
    return [asdict(result) for result in results]
