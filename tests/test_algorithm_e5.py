"""Testes da integração do AG com o modelo E5.3.3.

Cobrem a avaliação de indivíduos via EvaluationResult, o torneio
lexicográfico e a convergência do novo AG contra a busca exaustiva
(referência de ótimo global) em problemas controlados.
"""

from __future__ import annotations

import dataclasses
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from src.core.config import GAConfig
from src.genetic.algorithm import (
    run_genetic_algorithm_v2,
    _lexicographic_key,
)
from src.genetic.selection import tournament_selection_lexicographic
from src.models.individual import Individual
from src.simulation.evaluation import (
    Problem,
    evaluate_candidate,
)
from src.simulation.solvers import solve_exhaustive
from src.storage.loader import load_cities, load_panels, load_irradiance
from src.utils.seed import set_global_seed
from src.simulation.evaluation import build_problem_from_data

CITIES = load_cities()
PANELS = load_panels()
IRRADIANCE_JP = load_irradiance()
CITY_JP = next(c for c in CITIES if c["city"] == "João Pessoa")
PANEL_STD = PANELS[0]


def build_problem(
    consumption: float = 300.0,
    usable_area: float = 80.0,
    budget: float | None = None,
    hsp_override: dict[int, float] | None = None,
) -> Problem:
    if hsp_override is None:
        return build_problem_from_data(
            monthly_consumption_kwh=consumption,
            roof_usable_area_m2=usable_area,
            panel_data=PANEL_STD,
            city_data=CITY_JP,
            irradiance_data=IRRADIANCE_JP,
            max_budget_brl=budget,
        )
    return Problem(
        consumption=consumption,
        usable_area=usable_area,
        panel_area=float(PANEL_STD["panel_area_m2"]),
        panel_power_wp=float(PANEL_STD["panel_power_wp"]),
        hsp=hsp_override,
        efficiency=float(PANEL_STD["system_efficiency"]),
        unit_cost=float(PANEL_STD["panel_cost_brl"]) + float(PANEL_STD["installation_cost_per_panel_brl"]),
        budget=budget,
    )


def run_ag(problem: Problem, seed: int = 42) -> Individual:
    config = GAConfig(
        population_size=20,
        generations=60,
        crossover_rate=0.8,
        mutation_rate=0.2,
        elitism_count=2,
        random_seed=seed,
    )
    set_global_seed(seed)
    best, _, _ = run_genetic_algorithm_v2(problem, config)
    return best


# -----------------------------------------------------------------------------
# 1. Torneio lexicográfico
# -----------------------------------------------------------------------------

class TestTournamentLexicographic:
    def test_picks_feasible_over_infeasible(self):
        prob = build_problem(consumption=100.0, usable_area=20.0)
        # N=1 produces ~66 kWh? For consumption 100, June energy per panel ~66 => infeasible.
        # Use N=2 vs N=3 to get feasible (both feasible?). Let's craft: N=2 has energy 132 >100 -> feasible.
        # N=0 is infeasible. Force population with N=0 and N=2.
        ind_inf = Individual(num_panels=0, evaluation=evaluate_candidate(0, prob))
        ind_ok = Individual(num_panels=2, evaluation=evaluate_candidate(2, prob))
        # Ensure both evaluations exist
        assert ind_ok.evaluation.feasible is True
        assert ind_inf.evaluation.feasible is False
        best = tournament_selection_lexicographic([ind_inf, ind_ok], k=2)
        assert best.num_panels == 2

    def test_picks_lower_cost_among_feasible(self):
        prob = build_problem(consumption=50.0, usable_area=20.0)
        ind1 = Individual(num_panels=1, evaluation=evaluate_candidate(1, prob))
        ind2 = Individual(num_panels=2, evaluation=evaluate_candidate(2, prob))
        assert ind1.evaluation.feasible and ind2.evaluation.feasible
        best = tournament_selection_lexicographic([ind1, ind2], k=2)
        assert best.num_panels == 1

    def test_picks_lower_violation_among_infeasible(self):
        prob = build_problem(consumption=300.0, usable_area=200.0)
        # Both are infeasible due to energy? N=1 gives ~66 <300 infeasible; N=2 ~132 <300 infeasible.
        ind1 = Individual(num_panels=1, evaluation=evaluate_candidate(1, prob))
        ind2 = Individual(num_panels=2, evaluation=evaluate_candidate(2, prob))
        assert not ind1.evaluation.feasible and not ind2.evaluation.feasible
        best = tournament_selection_lexicographic([ind1, ind2], k=2)
        # Lower violation is N=2 (more energy)
        assert best.num_panels == 2

    def test_missing_evaluation_raises(self):
        ind1 = Individual(num_panels=1)
        ind2 = Individual(num_panels=2)
        with pytest.raises(ValueError):
            tournament_selection_lexicographic([ind1, ind2], k=2)


# -----------------------------------------------------------------------------
# 2. Convergência do AG vs busca exaustiva
# -----------------------------------------------------------------------------

class TestAGConvergence:
    def test_simple_viable(self):
        prob = build_problem(consumption=50.0, usable_area=20.0)
        ref = solve_exhaustive(prob)
        best = run_ag(prob, seed=42)
        assert best.num_panels == ref.best.num_panels
        assert best.evaluation.feasible is True

    def test_area_infeasible(self):
        prob = build_problem(consumption=300.0, usable_area=1.0)
        ref = solve_exhaustive(prob)
        best = run_ag(prob, seed=42)
        assert best.num_panels == ref.best.num_panels
        assert best.evaluation.feasible is False

    def test_budget_infeasible(self):
        prob = build_problem(consumption=50.0, usable_area=200.0, budget=1000.0)
        ref = solve_exhaustive(prob)
        best = run_ag(prob, seed=42)
        assert best.num_panels == ref.best.num_panels
        assert best.evaluation.feasible is False

    def test_budget_partial(self):
        prob = build_problem(consumption=300.0, usable_area=200.0, budget=5000.0)
        ref = solve_exhaustive(prob)
        best = run_ag(prob, seed=42)
        assert best.num_panels == ref.best.num_panels

    def test_custom_hsp_profile(self):
        hsp = {m: 5.0 for m in range(1, 13)}
        hsp[4] = 3.0  # critical month
        prob = build_problem(consumption=200.0, usable_area=100.0, hsp_override=hsp)
        ref = solve_exhaustive(prob)
        best = run_ag(prob, seed=42)
        assert best.num_panels == ref.best.num_panels

    def test_ag_never_returns_worse_than_zero(self):
        prob = build_problem(consumption=1000.0, usable_area=1.0)  # N_max = 0
        best = run_ag(prob, seed=42)
        assert best.num_panels == 0
        assert best.evaluation.feasible is False

    def test_deterministic(self):
        prob = build_problem(consumption=50.0, usable_area=20.0)
        best1 = run_ag(prob, seed=42)
        best2 = run_ag(prob, seed=42)
        assert best1.num_panels == best2.num_panels
        assert best1.evaluation.cost == best2.evaluation.cost


# -----------------------------------------------------------------------------
# 3. Verificações auxiliares da ordenação lexicográfica
# -----------------------------------------------------------------------------

class TestLexicographicKey:
    def test_feasible_sorts_before_infeasible(self):
        prob = build_problem(consumption=100.0, usable_area=200.0)
        ind_inf = Individual(num_panels=0, evaluation=evaluate_candidate(0, prob))
        ind_ok = Individual(num_panels=2, evaluation=evaluate_candidate(2, prob))
        assert _lexicographic_key(ind_ok) < _lexicographic_key(ind_inf)

    def test_lower_cost_sorts_first_among_feasible(self):
        prob = build_problem(consumption=50.0, usable_area=200.0)
        ind1 = Individual(num_panels=1, evaluation=evaluate_candidate(1, prob))
        ind2 = Individual(num_panels=2, evaluation=evaluate_candidate(2, prob))
        assert _lexicographic_key(ind1) < _lexicographic_key(ind2)

    def test_lower_violation_sorts_first_among_infeasible(self):
        prob = build_problem(consumption=300.0, usable_area=200.0)
        ind1 = Individual(num_panels=1, evaluation=evaluate_candidate(1, prob))
        ind2 = Individual(num_panels=2, evaluation=evaluate_candidate(2, prob))
        assert _lexicographic_key(ind2) < _lexicographic_key(ind1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])