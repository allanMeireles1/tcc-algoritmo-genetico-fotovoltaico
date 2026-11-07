"""Testes de integração E5.3.4: runner experimental com AG v2, analítico e exaustivo.

Verifica que os três métodos recebem exatamente o mesmo Problem, que seeds,
configurações, tempos e campos completos da avaliação são registrados e que
o fluxo antigo (run_optimization) permanece compatível.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from src.core.config import GAConfig
from src.models.roof import RoofInput
from src.models.result import ComparisonOutcome, MethodResult, OptimizationOutcome
from src.simulation.evaluation import evaluate_candidate
from src.simulation.runner import (
    build_problem,
    build_problem_v2,
    comparison_to_rows,
    run_comparison,
    run_optimization,
)
from src.storage.loader import load_cities, load_irradiance, load_panels

CITY_JP = next(c for c in load_cities() if c["city"] == "João Pessoa")
CITY_REC = next(c for c in load_cities() if c["city"] == "Recife")
PANEL = load_panels()[0]
IRRADIANCE_JP = load_irradiance()

CONFIG = GAConfig(
    population_size=20,
    generations=10,
    crossover_rate=0.8,
    mutation_rate=0.2,
    elitism_count=2,
    random_seed=42,
)


def make_roof(city: str = "João Pessoa", budget: float | None = None) -> RoofInput:
    return RoofInput(
        width_m=4.0,
        length_m=5.0,
        monthly_consumption_kwh=300.0,
        city=city,
        max_budget_brl=budget,
    )


class TestBuildProblemV2:
    def test_joao_pessoa_usa_hsp_mensal(self):
        problem = build_problem_v2(make_roof(), CITY_JP, PANEL, IRRADIANCE_JP)
        monthly = IRRADIANCE_JP["monthly_kwh_m2_day"]
        order = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
        for i, key in enumerate(order):
            assert problem.hsp[i + 1] == monthly[key]
        assert problem.budget is None
        assert problem.consumption == 300.0

    def test_outra_cidade_usa_media_anual(self):
        problem = build_problem_v2(make_roof(city="Recife"), CITY_REC, PANEL, IRRADIANCE_JP)
        # IRRADIANCE_JP é de João Pessoa; deve ser ignorado para Recife
        assert all(abs(problem.hsp[m] - CITY_REC["irradiance_kwh_m2_day"]) < 1e-12 for m in range(1, 13))

    def test_orcamento_propagado(self):
        problem = build_problem_v2(make_roof(budget=5000.0), CITY_JP, PANEL, IRRADIANCE_JP)
        assert problem.budget == 5000.0


class TestRunComparison:
    def test_mesmo_problem_para_todos_os_metodos(self):
        """Todos os resultados são consistentes com evaluate_candidate sobre o mesmo Problem."""
        outcome = run_comparison(make_roof(), CITY_JP, PANEL, CONFIG, runs=2, irradiance_data=IRRADIANCE_JP)
        for method_result in outcome.results:
            recomputed = evaluate_candidate(method_result.evaluation.num_panels, outcome.problem)
            assert recomputed == method_result.evaluation, (
                f"Método {method_result.method} devolveu avaliação inconsistente com o Problem compartilhado"
            )

    def test_tres_metodos_presentes(self):
        outcome = run_comparison(make_roof(), CITY_JP, PANEL, CONFIG, runs=1, irradiance_data=IRRADIANCE_JP)
        methods = [r.method for r in outcome.results]
        assert methods == ["analytical", "exhaustive", "genetic"]

    def test_seeds_registradas(self):
        outcome = run_comparison(make_roof(), CITY_JP, PANEL, CONFIG, runs=3, irradiance_data=IRRADIANCE_JP)
        genetic = [r for r in outcome.results if r.method == "genetic"]
        assert [r.run_seed for r in genetic] == [42, 43, 44]
        assert [r.run_index for r in genetic] == [0, 1, 2]
        assert [r.run_seed for r in outcome.results if r.method != "genetic"] == [None, None]

    def test_tempos_registrados(self):
        outcome = run_comparison(make_roof(), CITY_JP, PANEL, CONFIG, runs=2, irradiance_data=IRRADIANCE_JP)
        assert all(r.execution_time_s > 0.0 for r in outcome.results)
        assert outcome.summary["genetic_execution_time_mean_s"] > 0.0

    def test_config_registrada(self):
        outcome = run_comparison(make_roof(), CITY_JP, PANEL, CONFIG, runs=1, irradiance_data=IRRADIANCE_JP)
        assert outcome.config["population_size"] == CONFIG.population_size
        assert outcome.config["generations"] == CONFIG.generations
        assert outcome.config["random_seed"] == CONFIG.random_seed

    def test_diagnostico_analitico(self):
        outcome = run_comparison(make_roof(), CITY_JP, PANEL, CONFIG, runs=1, irradiance_data=IRRADIANCE_JP)
        diag = outcome.analytical_diagnostic
        assert set(diag) == {"N_energy", "N_area", "N_budget", "N_max", "candidate"}
        assert diag["N_budget"] is None  # sem orçamento
        assert diag["N_max"] == diag["N_area"]

    def test_analitico_coincide_com_exaustiva(self):
        outcome = run_comparison(make_roof(), CITY_JP, PANEL, CONFIG, runs=1, irradiance_data=IRRADIANCE_JP)
        assert outcome.summary["analytical_matches_exhaustive"] is True
        assert outcome.summary["analytical_panels"] == outcome.summary["exhaustive_panels"]

    def test_caso_com_orcamento(self):
        outcome = run_comparison(
            make_roof(budget=5000.0), CITY_JP, PANEL, CONFIG, runs=1, irradiance_data=IRRADIANCE_JP
        )
        assert outcome.problem.budget == 5000.0
        assert outcome.analytical_diagnostic["N_budget"] is not None
        assert outcome.summary["exhaustive_feasible"] == outcome.summary["analytical_feasible"]


class TestExportacao:
    def test_rows_preservam_campos_da_avaliacao(self):
        outcome: ComparisonOutcome = run_comparison(
            make_roof(budget=5000.0), CITY_JP, PANEL, CONFIG, runs=1, irradiance_data=IRRADIANCE_JP
        )
        rows = comparison_to_rows(outcome)
        assert len(rows) == 3
        for row in rows:
            eval_row = row["evaluation"]
            assert set(eval_row) == {
                "num_panels",
                "feasible",
                "cost",
                "violation",
                "energy_violation",
                "area_violation",
                "budget_violation",
                "energy_by_month",
                "used_area",
                "occupancy",
            }
            assert row["method"] in {"analytical", "exhaustive", "genetic"}
            assert row["execution_time_s"] > 0.0

    def test_rows_sinalizam_budget(self):
        outcome = run_comparison(
            make_roof(budget=5000.0), CITY_JP, PANEL, CONFIG, runs=1, irradiance_data=IRRADIANCE_JP
        )
        rows = comparison_to_rows(outcome)
        analytical_row = next(r for r in rows if r["method"] == "analytical")
        assert analytical_row["evaluation"]["budget_violation"] >= 0.0


class TestCompatibilidadeFluxoAntigo:
    def test_run_optimization_antigo_funciona(self):
        outcome = run_optimization(make_roof(), CITY_JP, PANEL, CONFIG, runs=1)
        assert isinstance(outcome, OptimizationOutcome)
        assert outcome.result.best_num_panels >= 0

    def test_build_problem_antigo_inalterado(self):
        scenario = build_problem(make_roof(), CITY_JP, PANEL)
        assert scenario["city"] == "João Pessoa"
        assert scenario["monthly_consumption_kwh"] == 300.0

    def test_sem_orcamento_e_com_orcamento_coexistem(self):
        old_outcome = run_optimization(make_roof(budget=5000.0), CITY_JP, PANEL, CONFIG, runs=1)
        new_outcome = run_comparison(
            make_roof(budget=5000.0), CITY_JP, PANEL, CONFIG, runs=1, irradiance_data=IRRADIANCE_JP
        )
        assert isinstance(old_outcome, OptimizationOutcome)
        assert isinstance(new_outcome, ComparisonOutcome)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
