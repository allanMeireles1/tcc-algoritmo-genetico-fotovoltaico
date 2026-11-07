"""Orquestração de execução por entrada real do usuário."""

from dataclasses import asdict
from statistics import mean
from time import perf_counter

from src.core.config import GAConfig
from src.genetic.algorithm import run_genetic_algorithm, run_genetic_algorithm_v2
from src.genetic.fitness import evaluate_fitness, evaluate_fitness_breakdown
from src.models.roof import RoofInput
from src.models.result import (
    ComparisonOutcome,
    GenerationStats,
    MethodResult,
    OptimizationOutcome,
    ScenarioRunResult,
)
from src.simulation.baseline import evaluate_direct_baseline
from src.simulation.convergence import compute_convergence_metrics, summarize_convergence
from src.simulation.evaluation import Problem, build_problem_from_data
from src.simulation.solvers import solve_analytical, solve_exhaustive
from src.storage.loader import load_irradiance
from src.utils.seed import set_global_seed
from src.utils.validators import validate_roof_input


def build_problem(roof: RoofInput, city_data: dict, panel_data: dict) -> dict:
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
        "panel_cost_brl": float(panel_data["panel_cost_brl"])
        + float(panel_data["installation_cost_per_panel_brl"]),
        "panel_area_m2": float(panel_data["panel_area_m2"]),
        "system_efficiency": float(panel_data["system_efficiency"]),
    }


def run_optimization(
    roof: RoofInput,
    city_data: dict,
    panel_data: dict,
    config: GAConfig,
    runs: int = 1,
) -> OptimizationOutcome:
    """Executa AG múltiplas vezes e retorna pacote completo para visualização."""
    validate_roof_input(roof)
    problem = build_problem(roof, city_data, panel_data)

    best_result: ScenarioRunResult | None = None
    best_history: list[GenerationStats] = []
    best_population: list = []
    best_breakdown = None
    run_fitness_values: list[float] = []
    run_times: list[float] = []

    for run_index in range(runs):
        current_seed = config.random_seed + run_index
        set_global_seed(current_seed)
        start = perf_counter()
        best_individual, history, final_population = run_genetic_algorithm(problem, config)
        execution_time = perf_counter() - start

        best_fitness, energy, cost = evaluate_fitness(best_individual.num_panels, problem, config)
        benchmark_panels, benchmark_fitness, benchmark_energy, benchmark_cost = evaluate_direct_baseline(
            problem, config
        )
        breakdown = evaluate_fitness_breakdown(best_individual.num_panels, problem, config)
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
            panel_area_m2=float(problem["panel_area_m2"]),
            energy_surplus_kwh=energy_surplus,
            energy_deficit_kwh=energy_deficit,
            benchmark_panels=benchmark_panels,
            benchmark_fitness=benchmark_fitness,
            benchmark_energy_kwh_month=benchmark_energy,
            benchmark_cost_brl=benchmark_cost,
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
            best_population = final_population
            best_breakdown = breakdown

    if best_result is None:
        raise RuntimeError("Nenhuma execução foi realizada.")

    summary = {
        "runs": runs,
        "fitness_mean": mean(run_fitness_values),
        "fitness_best": max(run_fitness_values),
        "fitness_worst": min(run_fitness_values),
        "execution_time_mean_s": mean(run_times),
    }
    return OptimizationOutcome(
        result=best_result,
        history=best_history,
        summary=summary,
        final_population=best_population,
        fitness_breakdown=best_breakdown,
    )


def results_to_rows(results: list[ScenarioRunResult]) -> list[dict]:
    """Converte resultados para linhas tabulares."""
    return [asdict(result) for result in results]


# =============================================================================
# E5.3.4 — Fluxo experimental: AG v2, solução analítica e busca exaustiva
# =============================================================================

def build_problem_v2(
    roof: RoofInput,
    city_data: dict,
    panel_data: dict,
    irradiance_data: dict | None = None,
) -> Problem:
    """Constrói o Problem oficial (E5.2) a partir da entrada do usuário.

    Usa HSP mensal quando os dados de irradiância correspondem à cidade
    (ex.: João Pessoa); caso contrário, usa a média anual de ``city_data``.
    """
    monthly = irradiance_data
    if monthly is None:
        try:
            monthly = load_irradiance()
        except FileNotFoundError:
            monthly = None
    if monthly is not None and monthly.get("city") != roof.city:
        monthly = None

    return build_problem_from_data(
        monthly_consumption_kwh=roof.monthly_consumption_kwh,
        roof_usable_area_m2=roof.usable_area_m2(),
        panel_data=panel_data,
        city_data=city_data,
        irradiance_data=monthly,
        max_budget_brl=roof.max_budget_brl,
    )


def run_comparison(
    roof: RoofInput,
    city_data: dict,
    panel_data: dict,
    config: GAConfig,
    runs: int = 1,
    irradiance_data: dict | None = None,
) -> ComparisonOutcome:
    """Executa analítico, exaustivo e AG v2 sobre exatamente o mesmo Problem.

    Registra seed, configuração, resultado completo da avaliação e tempo de
    execução de cada método. Não altera o fluxo antigo (``run_optimization``).
    """
    validate_roof_input(roof)
    problem = build_problem_v2(roof, city_data, panel_data, irradiance_data)
    results: list[MethodResult] = []

    start = perf_counter()
    analytical = solve_analytical(problem)
    analytical_time = perf_counter() - start
    results.append(
        MethodResult(
            method="analytical",
            run_index=0,
            run_seed=None,
            execution_time_s=analytical_time,
            evaluation=analytical.evaluation,
        )
    )

    start = perf_counter()
    exhaustive = solve_exhaustive(problem)
    exhaustive_time = perf_counter() - start
    results.append(
        MethodResult(
            method="exhaustive",
            run_index=0,
            run_seed=None,
            execution_time_s=exhaustive_time,
            evaluation=exhaustive.best,
        )
    )

    genetic_times: list[float] = []
    genetic_runs: list[tuple[int, list[GenerationStats]]] = []
    for run_index in range(runs):
        current_seed = config.random_seed + run_index
        set_global_seed(current_seed)
        start = perf_counter()
        best_individual, history, _population = run_genetic_algorithm_v2(problem, config)
        execution_time = perf_counter() - start
        genetic_times.append(execution_time)
        genetic_runs.append((current_seed, history))
        results.append(
            MethodResult(
                method="genetic",
                run_index=run_index,
                run_seed=current_seed,
                execution_time_s=execution_time,
                evaluation=best_individual.evaluation,
            )
        )

    convergence = [
        compute_convergence_metrics(
            history,
            run_seed=seed,
            optimal_panels=exhaustive.best.num_panels,
        )
        for seed, history in genetic_runs
    ]
    convergence_summary = summarize_convergence(convergence)

    genetic_results = [r for r in results if r.method == "genetic"]
    summary = {
        "analytical_panels": analytical.evaluation.num_panels,
        "analytical_feasible": analytical.feasible,
        "exhaustive_panels": exhaustive.best.num_panels,
        "exhaustive_feasible": exhaustive.best.feasible,
        "analytical_matches_exhaustive": (
            analytical.evaluation.num_panels == exhaustive.best.num_panels
        ),
        "genetic_panels_by_seed": {
            str(r.run_seed): r.evaluation.num_panels for r in genetic_results
        },
        "genetic_feasible_by_seed": {
            str(r.run_seed): r.evaluation.feasible for r in genetic_results
        },
        "genetic_execution_time_mean_s": mean(genetic_times) if genetic_times else None,
        "runs": runs,
        "convergence": convergence_summary,
    }

    return ComparisonOutcome(
        execution_label=f"{roof.city}_{roof.width_m:.1f}x{roof.length_m:.1f}",
        city=roof.city,
        problem=problem,
        results=results,
        config=asdict(config),
        analytical_diagnostic={
            "N_energy": analytical.N_energy,
            "N_area": analytical.N_area,
            "N_budget": analytical.N_budget,
            "N_max": analytical.N_max,
            "candidate": analytical.num_panels,
        },
        summary=summary,
        convergence=convergence,
        convergence_summary=convergence_summary,
        genetic_histories=dict(genetic_runs),
    )


def comparison_to_rows(outcome: ComparisonOutcome) -> list[dict]:
    """Exporta resultados da comparação preservando todos os campos da avaliação."""
    return [asdict(result) for result in outcome.results]


def convergence_to_rows(outcome: ComparisonOutcome) -> list[dict]:
    """Exporta as métricas de convergência por execução (um dicionário por seed)."""
    return [asdict(metric) for metric in outcome.convergence]
