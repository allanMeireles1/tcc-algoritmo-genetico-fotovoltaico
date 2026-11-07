"""Benchmark comparativo entre analítico, exaustivo e AG v2 (E5.4.5).

Metodologia consistente de medição:
- todos os métodos operam sobre o mesmo ``Problem``;
- um warmup não medido por método homogeneiza caches de CPU/dis;
- ``R`` repetições medidas com ``time.perf_counter``;
- para o AG, cada repetição usa semente ``random_seed + rep`` (reprodutível);
- mediana é a estatística principal de tempo; média, desvio, mínimo e máximo
  são reportados como dispersão;
- qualidade mensurada por: nº de painéis, viabilidade, custo médio, energia
  média e quantidade de repetições que reproduzem a solução ótima da busca
  exaustiva (referência).
"""

from dataclasses import asdict
from statistics import median, stdev
from time import perf_counter

from src.core.config import GAConfig
from src.genetic.algorithm import run_genetic_algorithm_v2
from src.models.result import BenchmarkMethodStats, BenchmarkOutcome
from src.models.roof import RoofInput
from src.simulation.evaluation import EvaluationResult
from src.simulation.solvers import solve_analytical, solve_exhaustive
from src.simulation.runner import build_problem_v2
from src.utils.seed import set_global_seed

_COST_TOL = 1e-6


def _quality(ev: EvaluationResult) -> tuple[int, bool, float, float]:
    """Extrai (painéis, viável, custo, energia) do resultado de avaliação."""
    energy_total = sum(float(v) for v in ev.energy_by_month.values())
    return (ev.num_panels, ev.feasible, float(ev.cost), float(energy_total))


def _method_stats(
    method: str,
    times_s: list[float],
    qualities: list[tuple[int, bool, float, float]],
    reference: EvaluationResult,
) -> BenchmarkMethodStats:
    return BenchmarkMethodStats(
        method=method,
        repetitions=len(times_s),
        times_s=tuple(times_s),
        mean_s=sum(times_s) / len(times_s),
        median_s=median(times_s),
        std_s=stdev(times_s) if len(times_s) > 1 else 0.0,
        min_s=min(times_s),
        max_s=max(times_s),
        best_panels_values=tuple(q[0] for q in qualities),
        feasible_count=sum(1 for q in qualities if q[1]),
        matches_optimum_count=sum(
            1
            for q in qualities
            if q[0] == reference.num_panels
            and q[1] == reference.feasible
            and abs(q[2] - float(reference.cost)) < _COST_TOL
        ),
        mean_cost_brl=sum(q[2] for q in qualities) / len(qualities),
        mean_energy_kwh_month=sum(q[3] for q in qualities) / len(qualities),
    )


def run_benchmark(
    roof: RoofInput,
    city_data: dict,
    panel_data: dict,
    config: GAConfig,
    repetitions: int = 5,
    warmup: int = 1,
    irradiance_data: dict | None = None,
) -> BenchmarkOutcome:
    """Executa benchmark temporal + de qualidade entre os três métodos.

    Args:
        roof: entrada do telhado.
        city_data: dados da cidade (cities_mock.json).
        panel_data: dados do painel (panels_mock.json).
        config: parâmetros do AG.
        repetitions: número de execuções medidas por método.
        warmup: número de execuções não medidas antes das medições.
        irradiance_data: dados de irradiância (irradiance_mock.json), opcional.
    """
    if repetitions < 1 or warmup < 0:
        raise ValueError("repetitions deve ser >= 1 e warmup >= 0")

    problem = build_problem_v2(roof, city_data, panel_data, irradiance_data)
    reference = solve_exhaustive(problem).best

    runners = {
        "analytical": lambda: solve_analytical(problem).evaluation,
        "exhaustive": lambda: solve_exhaustive(problem).best,
        "genetic": None,  # definido abaixo por repetição (seed progressiva)
    }

    # Warmup (não medido)
    for _ in range(warmup):
        runners["analytical"]()
        runners["exhaustive"]()
        set_global_seed(config.random_seed)
        run_genetic_algorithm_v2(problem, config)

    stats_map: dict[str, BenchmarkMethodStats] = {}

    # Determinísticos: analítico e exaustivo
    for method, runner in (
        ("analytical", runners["analytical"]),
        ("exhaustive", runners["exhaustive"]),
    ):
        times_s: list[float] = []
        qualities: list[tuple[int, bool, float, float]] = []
        for _ in range(repetitions):
            start = perf_counter()
            ev = runner()
            times_s.append(perf_counter() - start)
            qualities.append(_quality(ev))
        stats_map[method] = _method_stats(method, times_s, qualities, reference)

    # Genético: semente progressiva por repetição
    times_s, qualities = [], []
    for rep in range(repetitions):
        seed = config.random_seed + rep
        set_global_seed(seed)
        start = perf_counter()
        best_ind, _, _ = run_genetic_algorithm_v2(problem, config)
        times_s.append(perf_counter() - start)
        qualities.append(_quality(best_ind.evaluation))
    stats_map["genetic"] = _method_stats("genetic", times_s, qualities, reference)

    genetic_med = stats_map["genetic"].median_s
    speedups = {
        "analytical_over_genetic": genetic_med / stats_map["analytical"].median_s,
        "exhaustive_over_genetic": genetic_med / stats_map["exhaustive"].median_s,
    }

    summary = {
        "methods": {m: s.matches_optimum_count / s.repetitions for m, s in stats_map.items()},
        "radios": speedups,
    }

    return BenchmarkOutcome(
        execution_label=f"{roof.city}_{roof.width_m:.1f}x{roof.length_m:.1f}",
        city=roof.city,
        repetitions=repetitions,
        warmup=warmup,
        config=asdict(config),
        reference_panels=reference.num_panels,
        methods=list(stats_map.values()),
        speedups=speedups,
        summary=summary,
    )
