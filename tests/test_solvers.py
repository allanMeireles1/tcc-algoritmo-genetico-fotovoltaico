"""Testes da solução analítica e da busca exaustiva (E5.3.2).

Cobrem viabilidade, restrições, fronteiras de tolerância e consistência entre
os dois métodos. Utiliza o módulo src.simulation.solvers.
"""

from __future__ import annotations

import dataclasses
import math
from pathlib import Path
import sys

# Ensure src is on PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from src.simulation.solvers import (
    AnalyticalSolution,
    ExhaustiveResult,
    solve_analytical,
    solve_exhaustive,
)
from src.simulation.evaluation import (
    Problem,
    EPS_ENERGY,
    EPS_AREA,
    EPS_BUDGET,
    evaluate_candidate,
)
from src.storage.loader import load_cities, load_panels, load_irradiance

# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------

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
    """Convenient builder using the standard panel and city data.

    Allows optional HSP override to test diferentes perfis mensais.
    """
    # Use the official helper from evaluation module
    from src.simulation.evaluation import build_problem_from_data
    if hsp_override is None:
        return build_problem_from_data(
            monthly_consumption_kwh=consumption,
            roof_usable_area_m2=usable_area,
            panel_data=PANEL_STD,
            city_data=CITY_JP,
            irradiance_data=IRRADIANCE_JP,
            max_budget_brl=budget,
        )
    else:
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

def replace(prob: Problem, **changes) -> Problem:
    """Helper to create a new frozen Problem with altered fields."""
    return dataclasses.replace(prob, **changes)

# -----------------------------------------------------------------------------
# Helper to compare two EvaluationResult objects with tolerances
# -----------------------------------------------------------------------------

def assert_evaluation_close(a, b, rel_tol=1e-9, abs_tol=1e-12):
    assert a.num_panels == b.num_panels
    assert a.feasible == b.feasible
    assert math.isclose(a.cost, b.cost, rel_tol=rel_tol, abs_tol=abs_tol)
    assert math.isclose(a.violation, b.violation, rel_tol=rel_tol, abs_tol=abs_tol)
    assert math.isclose(a.energy_violation, b.energy_violation, rel_tol=rel_tol, abs_tol=abs_tol)
    assert math.isclose(a.area_violation, b.area_violation, rel_tol=rel_tol, abs_tol=abs_tol)
    assert math.isclose(a.budget_violation, b.budget_violation, rel_tol=rel_tol, abs_tol=abs_tol)
    for m in range(1, 13):
        assert math.isclose(a.energy_by_month[m], b.energy_by_month[m], rel_tol=rel_tol, abs_tol=abs_tol)
    assert math.isclose(a.used_area, b.used_area, rel_tol=rel_tol, abs_tol=abs_tol)
    assert math.isclose(a.occupancy, b.occupancy, rel_tol=rel_tol, abs_tol=abs_tol)

# -----------------------------------------------------------------------------
# 1. Analytical solution basic scenarios
# -----------------------------------------------------------------------------

class TestAnalyticalBasic:
    """Test analytical solution on simple viable/inviável scenarios."""

    def test_viable_simple(self):
        prob = build_problem(consumption=50.0, usable_area=100.0)
        sol = solve_analytical(prob)
        # Energy constraint should dominate; compute expected N_energy
        energy_per_panel = (
            prob.panel_power_wp / 1000.0 * prob.hsp[6] * 30 * prob.efficiency
        )
        N_expected = math.ceil((prob.consumption - EPS_ENERGY) / energy_per_panel)
        assert sol.num_panels == N_expected
        assert sol.feasible is True
        assert_evaluation_close(sol.evaluation, evaluate_candidate(sol.num_panels, prob))

    def test_infeasible_due_to_area(self):
        # Make area very small so N_area < N_energy
        prob = build_problem(consumption=300.0, usable_area=1.0)
        sol = solve_analytical(prob)
        # N_area should bind
        N_area = int(math.floor((prob.usable_area + EPS_AREA) / prob.panel_area))
        assert sol.N_area == N_area
        assert sol.num_panels == N_area
        assert sol.feasible is False
        assert_evaluation_close(sol.evaluation, evaluate_candidate(sol.num_panels, prob))

    def test_infeasible_due_to_budget(self):
        # Budget too low to afford N_energy
        prob = build_problem(consumption=300.0, usable_area=200.0, budget=1000.0)
        sol = solve_analytical(prob)
        N_budget = int(math.floor((prob.budget + EPS_BUDGET) / prob.unit_cost))
        assert sol.N_budget == N_budget
        assert sol.num_panels == N_budget
        assert sol.feasible is False
        assert_evaluation_close(sol.evaluation, evaluate_candidate(sol.num_panels, prob))

    def test_no_budget(self):
        prob = build_problem(consumption=300.0, usable_area=200.0, budget=None)
        sol = solve_analytical(prob)
        assert sol.N_budget is None
        # Should be feasible because area is enough
        assert sol.feasible is True
        assert_evaluation_close(sol.evaluation, evaluate_candidate(sol.num_panels, prob))

    def test_zero_usable_area_insufficient_for_one_panel(self):
        # Usable area less than panel area, N_area = 0
        prob = build_problem(consumption=10.0, usable_area=0.5)
        sol = solve_analytical(prob)
        assert sol.N_area == 0
        assert sol.num_panels == 0
        assert sol.feasible is False
        assert_evaluation_close(sol.evaluation, evaluate_candidate(0, prob))

    def test_focal_tolerance_boundary_energy(self):
        # Set consumption exactly at energy threshold (critical month)
        prob = build_problem(consumption=300.0, usable_area=200.0)
        # Compute energy per panel for month 6 (critical)
        E_per_panel = (
            prob.panel_power_wp / 1000.0 * prob.hsp[6] * 30 * prob.efficiency
        )
        N_energy = math.ceil((prob.consumption - EPS_ENERGY) / E_per_panel)
        # Adjust consumption to be exactly at threshold for N_energy panels
        adjusted_consumption = N_energy * E_per_panel + EPS_ENERGY
        prob_adj = replace(prob, consumption=adjusted_consumption)
        sol = solve_analytical(prob_adj)
        assert sol.num_panels == N_energy
        assert sol.feasible is True
        assert_evaluation_close(sol.evaluation, evaluate_candidate(N_energy, prob_adj))

# -----------------------------------------------------------------------------
# 2. Exhaustive search basic verification
# -----------------------------------------------------------------------------

class TestExhaustiveBasic:
    def test_exhaustive_returns_best_viable(self):
        prob = build_problem(consumption=50.0, usable_area=100.0)
        result = solve_exhaustive(prob)
        # Since area is generous, optimal N should equal analytical N_energy
        analytic = solve_analytical(prob)
        assert result.best.num_panels == analytic.num_panels
        assert result.best.feasible is True
        assert_evaluation_close(result.best, analytic.evaluation)

    def test_exhaustive_infeasible_due_to_area(self):
        prob = build_problem(consumption=300.0, usable_area=1.0)
        result = solve_exhaustive(prob)
        analytic = solve_analytical(prob)
        assert result.best.num_panels == analytic.num_panels
        assert result.best.feasible is False
        assert_evaluation_close(result.best, analytic.evaluation)
        # Ensure N_max matches area bound
        N_area = int(math.floor((prob.usable_area + EPS_AREA) / prob.panel_area))
        assert result.N_max == N_area

    def test_exhaustive_includes_zero(self):
        prob = build_problem(consumption=1000.0, usable_area=0.5)
        result = solve_exhaustive(prob)
        # N_max will be 0, best must be N=0
        assert result.N_max == 0
        assert result.best.num_panels == 0
        assert result.best.feasible is False
        assert_evaluation_close(result.best, evaluate_candidate(0, prob))

    def test_exhaustive_deterministic(self):
        prob = build_problem(consumption=300.0, usable_area=200.0)
        first = solve_exhaustive(prob)
        second = solve_exhaustive(prob)
        assert first.best.num_panels == second.best.num_panels
        assert_evaluation_close(first.best, second.best)
        assert first.N_max == second.N_max

# -----------------------------------------------------------------------------
# 3. Cross‑validation between analytical and exhaustive
# -----------------------------------------------------------------------------

class TestCrossValidation:
    """Vários cenários para garantir que a solução analítica coincide com a
    busca exaustiva (o padrão de referência)."""

    @pytest.mark.parametrize("consumption, area, budget", [
        (50.0, 200.0, None),               # simple viable
        (300.0, 80.0, None),               # area tight but viable
        (300.0, 80.0, 5000.0),              # budget limits
        (300.0, 20.0, None),               # area makes infeasible
        (500.0, 200.0, 2000.0),             # both area and budget restrictive
    ])
    def test_analytical_equals_exhaustive(self, consumption, area, budget):
        prob = build_problem(consumption=consumption, usable_area=area, budget=budget)
        analytic = solve_analytical(prob)
        exhaustive = solve_exhaustive(prob)
        # Both must pick the same N and evaluation
        assert analytic.num_panels == exhaustive.best.num_panels
        assert analytic.feasible == exhaustive.best.feasible
        assert_evaluation_close(analytic.evaluation, exhaustive.best)

    def test_custom_hsp_profile(self):
        # Define a synthetic HSP profile with a clear month‑critical
        hsp = {m: 5.0 for m in range(1, 13)}
        hsp[4] = 3.0  # April is critical (lowest)
        prob = build_problem(consumption=200.0, usable_area=100.0, hsp_override=hsp)
        analytic = solve_analytical(prob)
        exhaustive = solve_exhaustive(prob)
        assert analytic.num_panels == exhaustive.best.num_panels
        assert analytic.feasible == exhaustive.best.feasible
        assert_evaluation_close(analytic.evaluation, exhaustive.best)

    def test_budget_absent_vs_present(self):
        prob_no_budget = build_problem(consumption=300.0, usable_area=200.0, budget=None)
        prob_with_budget = build_problem(consumption=300.0, usable_area=200.0, budget=10000.0)
        analytic_nb = solve_analytical(prob_no_budget)
        analytic_wb = solve_analytical(prob_with_budget)
        # Budget present but generous should not affect result
        assert analytic_nb.num_panels == analytic_wb.num_panels
        assert analytic_nb.feasible == analytic_wb.feasible
        assert_evaluation_close(analytic_nb.evaluation, analytic_wb.evaluation)

# -----------------------------------------------------------------------------
# 4. Edge cases and tolerance verification
# -----------------------------------------------------------------------------

class TestEdgeCases:
    def test_energy_tolerance_effect(self):
        # Build a problem where area is just enough for N panels (N_max = N)
        prob = build_problem(consumption=300.0, usable_area=11.0)
        # Energy per panel for the critical month (June)
        e_pp = (
            prob.panel_power_wp / 1000.0 * prob.hsp[6] * 30 * prob.efficiency
        )
        # Determine N such that N * e_pp is just enough (within tolerance) for consumption
        N = math.ceil((prob.consumption - EPS_ENERGY) / e_pp)
        # Set consumption to the boundary: N * e_pp + EPS_ENERGY (still feasible)
        consumption_boundary = N * e_pp + EPS_ENERGY
        prob_boundary = replace(prob, consumption=consumption_boundary)
        # Increase consumption just beyond tolerance → should become infeasible
        prob_inf = replace(prob_boundary, consumption=consumption_boundary + EPS_ENERGY)
        analytic = solve_analytical(prob_inf)
        assert analytic.feasible is False
        # Analytical solution should keep the same N (no extra panel added)
        assert analytic.num_panels == N
        # Evaluation must reflect infeasibility and a positive energy violation
        assert analytic.evaluation.feasible is False
        assert analytic.evaluation.energy_violation > 0.0

    def test_area_tolerance_effect(self):
        prob = build_problem(consumption=10.0, usable_area=10.0)
        # Reduce usable area by epsilon → should still allow one panel
        prob_adj = replace(prob, usable_area=prob.usable_area - EPS_AREA / 2)
        analytic = solve_analytical(prob_adj)
        assert analytic.feasible is True
        # Using one panel should fit
        assert analytic.num_panels == 1

    def test_budget_tolerance_effect(self):
        prob = build_problem(consumption=10.0, usable_area=200.0, budget=1350.0)
        # Budget equals cost of one panel; add small epsilon beyond
        prob_adj = replace(prob, budget=prob.budget + EPS_BUDGET / 2)
        analytic = solve_analytical(prob_adj)
        assert analytic.feasible is True
        assert analytic.num_panels == 1

    def test_zero_consumption_not_allowed(self):
        prob = build_problem(consumption=0.0, usable_area=200.0)
        with pytest.raises(ValueError):
            solve_analytical(prob)

    def test_negative_consumption_not_allowed(self):
        prob = build_problem(consumption=-10.0, usable_area=200.0)
        with pytest.raises(ValueError):
            solve_analytical(prob)

# -----------------------------------------------------------------------------
# 5. Ensure solvers do not modify existing API or AG code (no side‑effects)
# -----------------------------------------------------------------------------

class TestNoSideEffects:
    def test_ag_unchanged(self):
        # Import a function from genetic module and ensure it still works
        from src.genetic.algorithm import max_panels_by_roof
        # Expected behaviour unchanged (simple sanity check)
        assert max_panels_by_roof(roof_usable_area_m2=100.0, panel_area_m2=2.2) == max(1, int(100.0 // 2.2))

if __name__ == "__main__":
    pytest.main([__file__, "-v"])