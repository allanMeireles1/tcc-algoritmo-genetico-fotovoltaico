"""Análise de convergência do AG v2 (E5.4.3).

Funções puras sobre ``GenerationStats``: não executam o algoritmo, apenas
derivam métricas observáveis do histórico de gerações.
"""

from __future__ import annotations

from statistics import mean, median

from src.models.result import ConvergenceMetrics, GenerationStats


def compute_convergence_metrics(
    history: list[GenerationStats],
    run_seed: int,
    optimal_panels: int | None = None,
    stability_window: int = 5,
) -> ConvergenceMetrics:
    """Deriva métricas de convergência de uma execução.

    Args:
        history: histórico por geração retornado por ``run_genetic_algorithm_v2``.
        run_seed: semente usada na execução (registro de reprodutibilidade).
        optimal_panels: referência de ótimo (ex.: melhor da busca exaustiva).
            ``None`` quando não há referência aplicável.
        stability_window: número de gerações finais exigidas para considerar
            que o melhor estabilizou.
    """
    if not history:
        raise ValueError("Histórico vazio não pode ser analisado")

    best_seq = tuple(gen.best_panels for gen in history)
    generations = len(best_seq)
    final_best = best_seq[-1]

    # Estabilidade: o melhor não muda nas últimas `window` gerações
    window = min(stability_window, generations)
    converged = all(best_seq[-(i + 1)] == final_best for i in range(window))

    # Primeira geração a partir da qual o valor não muda mais (somente se convergiu)
    convergence_generation: int | None = None
    if converged:
        for idx in range(generations):
            if all(val == best_seq[idx] for val in best_seq[idx:]):
                convergence_generation = idx
                break

    first_optimal_generation: int | None = None
    generations_to_optimum: int | None = None
    if optimal_panels is not None:
        for idx, val in enumerate(best_seq):
            if val == optimal_panels:
                first_optimal_generation = idx
                generations_to_optimum = idx + 1  # contagem 1-based
                break

    return ConvergenceMetrics(
        run_seed=run_seed,
        best_panels_trajectory=best_seq,
        generations=generations,
        converged=converged,
        convergence_generation=convergence_generation,
        first_optimal_generation=first_optimal_generation,
        generations_to_optimum=generations_to_optimum,
        final_best_panels=final_best,
        stability_end_count=window if converged else 0,
    )


def summarize_convergence(metrics: list[ConvergenceMetrics]) -> dict:
    """Agrega métricas de convergência de várias execuções (seeds)."""
    if not metrics:
        return {
            "runs": 0,
            "converged_count": 0,
            "converged_rate": 0.0,
            "optimal_count": 0,
            "optimal_rate": 0.0,
            "generations_to_optimum_values": [],
            "generations_to_optimum_mean": None,
            "generations_to_optimum_median": None,
            "final_best_panels_values": [],
            "final_best_panels_unique": [],
            "all_final_equal": False,
            "unique_trajectories": 0,
        }

    n = len(metrics)
    converged = [m for m in metrics if m.converged]
    optimal = [m for m in metrics if m.generations_to_optimum is not None]
    gens_opt = [m.generations_to_optimum for m in optimal]
    finals = [m.final_best_panels for m in metrics]
    trajectories = {m.best_panels_trajectory for m in metrics}

    return {
        "runs": n,
        "converged_count": len(converged),
        "converged_rate": len(converged) / n,
        "optimal_count": len(optimal),
        "optimal_rate": len(optimal) / n,
        "generations_to_optimum_values": gens_opt,
        "generations_to_optimum_mean": mean(gens_opt) if gens_opt else None,
        "generations_to_optimum_median": median(gens_opt) if gens_opt else None,
        "final_best_panels_values": finals,
        "final_best_panels_unique": sorted(set(finals)),
        "all_final_equal": len(set(finals)) == 1,
        "unique_trajectories": len(trajectories),
    }
