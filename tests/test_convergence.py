"""Testes de convergência E5.4.3.

Cobrem:
- ``compute_convergence_metrics``: cálculo a partir de histórico de gerações;
- ``summarize_convergence``: agregação multi-semente;
- ``run_comparison``: campos ``convergence`` e ``convergence_summary`` preenchidos;
- exportação via ``comparison_to_rows`` e ``convergence_to_rows``.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import dataclasses

import pytest

from src.core.config import GAConfig
from src.models.result import ConvergenceMetrics, GenerationStats
from src.simulation.convergence import (
    compute_convergence_metrics,
    summarize_convergence,
)
from src.simulation.runner import (
    comparison_to_rows,
    convergence_to_rows,
    run_comparison,
)
from src.simulation.solvers import solve_exhaustive
from src.storage.loader import load_cities, load_panels, load_irradiance
from src.models.roof import RoofInput


CITIES = load_cities()
PANEL = load_panels()[0]
IRRADIANCE = load_irradiance()
CITY_JP = next(c for c in CITIES if c["city"] == "João Pessoa")


def make_roof(consumption: float = 300.0, budget: float | None = None) -> RoofInput:
    return RoofInput(
        width_m=8.0,
        length_m=10.0,
        monthly_consumption_kwh=consumption,
        city="João Pessoa",
        max_budget_brl=budget,
    )


def make_config(population_size: int = 20, generations: int = 40, seed: int = 42) -> GAConfig:
    return GAConfig(
        population_size=population_size,
        generations=generations,
        crossover_rate=0.8,
        mutation_rate=0.2,
        elitism_count=2,
        random_seed=seed,
    )


def make_history(best_panels: list[int], seed: int = 0) -> list[GenerationStats]:
    """Constrói histórico sintético com best_panels por geração."""
    return [
        GenerationStats(
            generation=i,
            best_fitness=float(i),
            avg_fitness=float(i),
            best_panels=p,
        )
        for i, p in enumerate(best_panels)
    ]


class TestConvergenceMetrics:
    def test_stabilized_trajectory(self):
        # Melhor sobe 1 → 3 e se mantém em 3; window=5 pega as últimas 5 gerações: 3,3,3,3,3
        hist = make_history([1, 3, 3, 3, 3, 3])
        metrics = compute_convergence_metrics(hist, run_seed=42, optimal_panels=3)
        assert metrics.converged is True
        assert metrics.convergence_generation == 1
        assert metrics.first_optimal_generation == 1
        assert metrics.generations_to_optimum == 2
        assert metrics.final_best_panels == 3
        assert metrics.stability_end_count == 5
        assert metrics.run_seed == 42

    def test_already_optimal_from_first_generation(self):
        hist = make_history([3, 3, 3, 3, 3])
        metrics = compute_convergence_metrics(hist, run_seed=7, optimal_panels=3)
        assert metrics.converged is True
        assert metrics.convergence_generation == 0
        assert metrics.first_optimal_generation == 0
        assert metrics.generations_to_optimum == 1

    def test_infeasible_problem_no_optimal(self):
        hist = make_history([0, 0, 0])
        metrics = compute_convergence_metrics(hist, run_seed=99, optimal_panels=None)
        assert metrics.converged is True
        assert metrics.convergence_generation == 0
        assert metrics.first_optimal_generation is None
        assert metrics.generations_to_optimum is None

    def test_no_stabilization(self):
        # 1,2,0,1,2 — nunca estabiliza nas últimas 5 gerações
        hist = make_history([1, 2, 0, 1, 2])
        metrics = compute_convergence_metrics(hist, run_seed=1, optimal_panels=None)
        assert metrics.converged is False
        assert metrics.convergence_generation is None


class TestSummarizeConvergence:
    def test_empty(self):
        result = summarize_convergence([])
        assert result["runs"] == 0
        assert result["converged_count"] == 0
        assert result["converged_rate"] == 0.0
        assert result["optimal_count"] == 0
        assert result["optimal_rate"] == 0.0
        assert result["final_best_panels_values"] == []
        assert result["all_final_equal"] is False

    def test_partial_convergence(self):
        metrics = [
            ConvergenceMetrics(
                run_seed=42,
                best_panels_trajectory=(1, 2, 3, 3, 3, 3),
                generations=6,
                converged=True,
                convergence_generation=2,
                first_optimal_generation=2,
                generations_to_optimum=3,
                final_best_panels=3,
                stability_end_count=3,
            ),
            ConvergenceMetrics(
                run_seed=123,
                best_panels_trajectory=(2, 4, 5, 5, 5, 5),
                generations=6,
                converged=True,
                convergence_generation=2,
                first_optimal_generation=2,
                generations_to_optimum=3,
                final_best_panels=5,
                stability_end_count=3,
            ),
            ConvergenceMetrics(
                run_seed=777,
                best_panels_trajectory=(1, 3, 3, 3, 3, 3),
                generations=6,
                converged=True,
                convergence_generation=1,
                first_optimal_generation=1,
                generations_to_optimum=2,
                final_best_panels=3,
                stability_end_count=5,
            ),
        ]
        result = summarize_convergence(metrics)
        assert result["runs"] == 3
        assert result["converged_count"] == 3
        assert result["converged_rate"] == 1.0
        assert result["optimal_count"] == 3
        assert result["optimal_rate"] == 1.0
        assert result["final_best_panels_unique"] == [3, 5]
        assert result["all_final_equal"] is False
        assert result["unique_trajectories"] == 3

    def test_all_equal_final_and_trajectories(self):
        metrics = [
            ConvergenceMetrics(
                run_seed=1,
                best_panels_trajectory=(3, 3, 3, 3, 3, 3),
                generations=6,
                converged=True,
                convergence_generation=0,
                first_optimal_generation=0,
                generations_to_optimum=1,
                final_best_panels=3,
                stability_end_count=6,
            ),
            ConvergenceMetrics(
                run_seed=2,
                best_panels_trajectory=(3, 3, 3, 3, 3, 3),
                generations=6,
                converged=True,
                convergence_generation=0,
                first_optimal_generation=0,
                generations_to_optimum=1,
                final_best_panels=3,
                stability_end_count=6,
            ),
        ]
        result = summarize_convergence(metrics)
        assert result["all_final_equal"] is True
        assert result["unique_trajectories"] == 1
        assert result["converged_rate"] == 1.0
        assert result["optimal_rate"] == 1.0
        assert result["final_best_panels_unique"] == [3]


class TestRunComparisonConvergence:
    def test_convergence_fields_present(self):
        roof = make_roof(consumption=50.0, budget=None)
        cfg = make_config(population_size=10, generations=10, seed=42)
        outcome = run_comparison(
            roof=roof,
            city_data=CITY_JP,
            panel_data=PANEL,
            config=cfg,
            runs=1,
            irradiance_data=IRRADIANCE,
        )
        assert hasattr(outcome, "convergence")
        assert hasattr(outcome, "convergence_summary")
        assert isinstance(outcome.convergence, list)
        assert len(outcome.convergence) == 1
        assert isinstance(outcome.convergence_summary, dict)
        assert outcome.convergence_summary["runs"] == 1

    def test_convergence_metrics_structure(self):
        roof = make_roof(consumption=50.0, budget=None)
        cfg = make_config(population_size=10, generations=10, seed=42)
        outcome = run_comparison(
            roof=roof,
            city_data=CITY_JP,
            panel_data=PANEL,
            config=cfg,
            runs=1,
            irradiance_data=IRRADIANCE,
        )
        m = outcome.convergence[0]
        assert m.run_seed == 42
        assert isinstance(m.best_panels_trajectory, tuple)
        assert m.generations > 0
        assert isinstance(m.converged, bool)
        assert m.final_best_panels is not None

    def test_multiple_seeds_stability_summary(self):
        roof = make_roof(consumption=50.0, budget=None)
        cfg = make_config(population_size=15, generations=25, seed=42)
        outcome = run_comparison(
            roof=roof,
            city_data=CITY_JP,
            panel_data=PANEL,
            config=cfg,
            runs=3,
            irradiance_data=IRRADIANCE,
        )
        # O AG pode não convergir para o ótimo em 25 gerações com população pequena;
        # não assertamos optimidade. Verificamos apenas estrutura e consistência.
        assert outcome.convergence_summary["runs"] == 3
        assert 0.0 <= outcome.convergence_summary["converged_rate"] <= 1.0
        assert 0.0 <= outcome.convergence_summary["optimal_rate"] <= 1.0
        assert len(outcome.convergence) == 3
        assert all(m.run_seed in (42, 43, 44) for m in outcome.convergence)


class TestExport:
    def test_convergence_to_rows_structure(self):
        roof = make_roof(consumption=50.0, budget=None)
        cfg = make_config(population_size=10, generations=10, seed=42)
        outcome = run_comparison(
            roof=roof,
            city_data=CITY_JP,
            panel_data=PANEL,
            config=cfg,
            runs=1,
            irradiance_data=IRRADIANCE,
        )
        rows = convergence_to_rows(outcome)
        assert len(rows) == 1
        row = rows[0]
        for field in (
            "run_seed",
            "best_panels_trajectory",
            "generations",
            "converged",
            "convergence_generation",
            "first_optimal_generation",
            "generations_to_optimum",
            "final_best_panels",
            "stability_end_count",
        ):
            assert field in row, f"Campo {field} ausente no dicionário de convergência"


class TestImportAliases:
    def test_imports_work(self):
        from src.simulation.convergence import (
            compute_convergence_metrics as cc,
            summarize_convergence as sc,
        )
        assert cc is compute_convergence_metrics
        assert sc is summarize_convergence


if __name__ == "__main__":
    pytest.main([__file__, "-v"])