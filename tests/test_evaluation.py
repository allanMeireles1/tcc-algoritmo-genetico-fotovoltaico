"""Testes do módulo de avaliação (E5.3.1).

Cobre domínio de N, validação de parâmetros, energia, área, orçamento,
viabilidade, tolerâncias numéricas e comparação lexicográfica.
"""

from __future__ import annotations

import dataclasses
import math
from pathlib import Path
import sys

# Ensure src is on PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from src.simulation.evaluation import (
    EvaluationResult,
    Problem,
    EPS_ENERGY,
    EPS_AREA,
    EPS_BUDGET,
    DEFAULT_DAYS_PER_MONTH,
    evaluate_candidate,
    compare_lexicographic,
    is_feasible,
    build_problem_from_data,
)
from src.storage.loader import load_cities, load_panels, load_irradiance


# -----------------------------------------------------------------------------
# Fixtures e dados de referência
# -----------------------------------------------------------------------------

CITIES = load_cities()
PANELS = load_panels()
IRRADIANCE_JP = load_irradiance()
CITY_DATA_JP = next(c for c in CITIES if c["city"] == "João Pessoa")
PANEL_DATA = PANELS[0]

# Cria Problem padrão para testes
def make_problem(
    consumption: float = 300.0,
    usable_area: float = 80.0,
    budget: float | None = None,
) -> Problem:
    return build_problem_from_data(
        monthly_consumption_kwh=consumption,
        roof_usable_area_m2=usable_area,
        panel_data=PANEL_DATA,
        city_data=CITY_DATA_JP,
        irradiance_data=IRRADIANCE_JP,
        max_budget_brl=budget,
    )


def replace(prob: Problem, **changes) -> Problem:
    """Helper para criar novo Problem com campos alterados (frozen dataclass)."""
    return dataclasses.replace(prob, **changes)


# -----------------------------------------------------------------------------
# 1. Domínio de N
# -----------------------------------------------------------------------------

class TestNDomain:
    """Validação do domínio N ∈ ℤ≥₀."""

    def test_N_zero_accepted(self):
        prob = make_problem()
        result = evaluate_candidate(0, prob)
        assert result.num_panels == 0
        assert result.feasible is False
        assert result.energy_violation == 1.0

    def test_N_positive_accepted(self):
        prob = make_problem()
        result = evaluate_candidate(5, prob)
        assert result.num_panels == 5
        assert isinstance(result.feasible, bool)

    def test_N_negative_rejected(self):
        prob = make_problem()
        with pytest.raises(ValueError, match="N deve ser >="):
            evaluate_candidate(-1, prob)

    def test_N_fractional_rejected(self):
        prob = make_problem()
        with pytest.raises(ValueError, match="inteiro"):
            evaluate_candidate(2.5, prob)

    def test_N_string_rejected(self):
        prob = make_problem()
        with pytest.raises(ValueError, match="inteiro"):
            evaluate_candidate("5", prob)

    def test_N_true_rejected(self):
        prob = make_problem()
        with pytest.raises(ValueError, match="inteiro"):
            evaluate_candidate(True, prob)

    def test_N_false_rejected(self):
        prob = make_problem()
        with pytest.raises(ValueError, match="inteiro"):
            evaluate_candidate(False, prob)


# -----------------------------------------------------------------------------
# 2. Validação de valores numéricos (NaN, Inf)
# -----------------------------------------------------------------------------

class TestNumericValidation:
    """Validação de finitude dos parâmetros."""

    def test_nan_consumption_rejected(self):
        prob = replace(make_problem(), consumption=float("nan"))
        with pytest.raises(ValueError, match="finito"):
            evaluate_candidate(1, prob)

    def test_inf_consumption_rejected(self):
        prob = replace(make_problem(), consumption=float("inf"))
        with pytest.raises(ValueError, match="finito"):
            evaluate_candidate(1, prob)

    def test_neg_inf_consumption_rejected(self):
        prob = replace(make_problem(), consumption=float("-inf"))
        with pytest.raises(ValueError, match="finito"):
            evaluate_candidate(1, prob)

    def test_nan_usable_area_rejected(self):
        prob = replace(make_problem(), usable_area=float("nan"))
        with pytest.raises(ValueError, match="finito"):
            evaluate_candidate(1, prob)

    def test_nan_panel_area_rejected(self):
        prob = replace(make_problem(), panel_area=float("nan"))
        with pytest.raises(ValueError, match="finito"):
            evaluate_candidate(1, prob)

    def test_nan_panel_power_rejected(self):
        prob = replace(make_problem(), panel_power_wp=float("nan"))
        with pytest.raises(ValueError, match="finito"):
            evaluate_candidate(1, prob)

    def test_nan_efficiency_rejected(self):
        prob = replace(make_problem(), efficiency=float("nan"))
        with pytest.raises(ValueError, match="finito"):
            evaluate_candidate(1, prob)

    def test_nan_unit_cost_rejected(self):
        prob = replace(make_problem(), unit_cost=float("nan"))
        with pytest.raises(ValueError, match="finito"):
            evaluate_candidate(1, prob)

    def test_nan_hsp_rejected(self):
        prob = make_problem()
        hsp = dict(prob.hsp)
        hsp[1] = float("nan")
        prob = replace(prob, hsp=hsp)
        with pytest.raises(ValueError, match="finito"):
            evaluate_candidate(1, prob)

    def test_nan_budget_rejected(self):
        prob = replace(make_problem(budget=10000.0), budget=float("nan"))
        with pytest.raises(ValueError, match="finito"):
            evaluate_candidate(1, prob)


# -----------------------------------------------------------------------------
# 3. Validação de intervalos
# -----------------------------------------------------------------------------

class TestRangeValidation:
    """Validação de limites dos parâmetros."""

    def test_zero_consumption_rejected(self):
        prob = replace(make_problem(), consumption=0.0)
        with pytest.raises(ValueError, match="consumption deve ser > 0"):
            evaluate_candidate(1, prob)

    def test_negative_consumption_rejected(self):
        prob = replace(make_problem(), consumption=-1.0)
        with pytest.raises(ValueError, match="consumption deve ser > 0"):
            evaluate_candidate(1, prob)

    def test_zero_usable_area_rejected(self):
        prob = replace(make_problem(), usable_area=0.0)
        with pytest.raises(ValueError, match="usable_area deve ser > 0"):
            evaluate_candidate(1, prob)

    def test_zero_panel_area_rejected(self):
        prob = replace(make_problem(), panel_area=0.0)
        with pytest.raises(ValueError, match="panel_area deve ser > 0"):
            evaluate_candidate(1, prob)

    def test_zero_panel_power_rejected(self):
        prob = replace(make_problem(), panel_power_wp=0.0)
        with pytest.raises(ValueError, match="panel_power_wp deve ser > 0"):
            evaluate_candidate(1, prob)

    def test_zero_efficiency_rejected(self):
        prob = replace(make_problem(), efficiency=0.0)
        with pytest.raises(ValueError, match="efficiency deve estar em"):
            evaluate_candidate(1, prob)

    def test_efficiency_above_one_rejected(self):
        prob = replace(make_problem(), efficiency=1.1)
        with pytest.raises(ValueError, match="efficiency deve estar em"):
            evaluate_candidate(1, prob)

    def test_zero_unit_cost_rejected(self):
        prob = replace(make_problem(), unit_cost=0.0)
        with pytest.raises(ValueError, match="unit_cost deve ser > 0"):
            evaluate_candidate(1, prob)

    def test_zero_hsp_rejected(self):
        prob = make_problem()
        hsp = dict(prob.hsp)
        hsp[1] = 0.0
        prob = replace(prob, hsp=hsp)
        with pytest.raises(ValueError, match=r"HSP\[1\] deve ser > 0"):
            evaluate_candidate(1, prob)

    def test_zero_budget_rejected(self):
        prob = replace(make_problem(budget=0.0), budget=0.0)
        with pytest.raises(ValueError, match="budget.*deve ser > 0"):
            evaluate_candidate(1, prob)


# -----------------------------------------------------------------------------
# 4. Cálculo energético
# -----------------------------------------------------------------------------

class TestEnergyCalculation:
    """Testes de cálculo de energia e viabilidade energética."""

    def test_energy_formula_matches_E52(self):
        prob = make_problem()
        N = 1
        m = 1
        hsp_jan = prob.hsp[1]
        expected = N * (prob.panel_power_wp / 1000.0) * hsp_jan * DEFAULT_DAYS_PER_MONTH * prob.efficiency
        result = evaluate_candidate(N, prob)
        assert math.isclose(result.energy_by_month[1], expected, rel_tol=1e-10)

    def test_monthly_energy_all_months(self):
        prob = make_problem()
        result = evaluate_candidate(1, prob)
        assert len(result.energy_by_month) == 12
        for m in range(1, 13):
            assert m in result.energy_by_month
            assert result.energy_by_month[m] > 0

    def test_energy_sufficient_feasible(self):
        prob = make_problem(consumption=50.0, usable_area=100.0)
        result = evaluate_candidate(1, prob)
        assert result.energy_violation == 0.0

    def test_energy_deficit_violation(self):
        prob = make_problem(consumption=1000.0, usable_area=100.0)
        result = evaluate_candidate(1, prob)
        assert result.energy_violation > 0.0

    def test_month_critical_identified(self):
        prob = make_problem(consumption=300.0, usable_area=100.0)
        result = evaluate_candidate(4, prob)
        energies = list(result.energy_by_month.values())
        min_energy = min(energies)
        assert math.isclose(min_energy, result.energy_by_month[6], rel_tol=1e-10)


# -----------------------------------------------------------------------------
# 5. Tolerância energética
# -----------------------------------------------------------------------------

class TestEnergyTolerance:
    """Testes da tolerância numérica EPS_ENERGY = 1e-9."""

    def test_exactly_at_tolerance_boundary(self):
        prob = make_problem()
        N = 4
        E_jun = N * (prob.panel_power_wp / 1000.0) * prob.hsp[6] * DEFAULT_DAYS_PER_MONTH * prob.efficiency
        prob_boundary = replace(prob, consumption=E_jun + EPS_ENERGY)
        result = evaluate_candidate(N, prob_boundary)
        assert result.energy_violation == 0.0
        assert result.feasible is True

    def test_just_inside_tolerance_viable(self):
        prob = make_problem()
        N = 4
        E_jun = N * (prob.panel_power_wp / 1000.0) * prob.hsp[6] * DEFAULT_DAYS_PER_MONTH * prob.efficiency
        prob_inside = replace(prob, consumption=E_jun + EPS_ENERGY / 2)
        result = evaluate_candidate(N, prob_inside)
        assert result.energy_violation == 0.0
        assert result.feasible is True

    def test_just_outside_tolerance_violation(self):
        prob = make_problem()
        N = 4
        E_jun = N * (prob.panel_power_wp / 1000.0) * prob.hsp[6] * DEFAULT_DAYS_PER_MONTH * prob.efficiency
        prob_outside = replace(prob, consumption=E_jun + 2 * EPS_ENERGY)
        result = evaluate_candidate(N, prob_outside)
        assert result.energy_violation > 0.0
        expected_violation = (prob_outside.consumption - E_jun - EPS_ENERGY) / prob_outside.consumption
        assert math.isclose(result.energy_violation, expected_violation, rel_tol=1e-10)

    def test_violation_discount_tolerance(self):
        prob = make_problem(consumption=300.0)
        result = evaluate_candidate(1, prob)
        E_jun = result.energy_by_month[6]
        expected = max(0.0, prob.consumption - E_jun - EPS_ENERGY) / prob.consumption
        assert math.isclose(result.energy_violation, expected, rel_tol=1e-10)


# -----------------------------------------------------------------------------
# 6. Área
# -----------------------------------------------------------------------------

class TestAreaConstraint:
    """Testes da restrição de área com tolerância."""

    def test_area_sufficient_violation_zero(self):
        prob = make_problem(usable_area=100.0)
        result = evaluate_candidate(10, prob)
        assert result.area_violation == 0.0

    def test_area_insufficient_violation_positive(self):
        prob = make_problem(usable_area=10.0)
        result = evaluate_candidate(10, prob)
        assert result.area_violation > 0.0

    def test_area_exact_boundary_viable(self):
        prob = make_problem()
        N = 10
        exact_area = N * prob.panel_area
        prob_boundary = replace(prob, usable_area=exact_area + EPS_AREA)
        result = evaluate_candidate(N, prob_boundary)
        assert result.area_violation == 0.0

    def test_area_just_inside_tolerance(self):
        prob = make_problem()
        N = 10
        exact_area = N * prob.panel_area
        prob_inside = replace(prob, usable_area=exact_area + EPS_AREA / 2)
        result = evaluate_candidate(N, prob_inside)
        assert result.area_violation == 0.0

    def test_area_just_outside_tolerance(self):
        prob = make_problem()
        N = 10
        exact_area = N * prob.panel_area
        prob_outside = replace(prob, usable_area=exact_area - 2 * EPS_AREA)
        result = evaluate_candidate(N, prob_outside)
        assert result.area_violation > 0.0
        expected = (N * prob.panel_area - prob_outside.usable_area - EPS_AREA) / prob_outside.usable_area
        assert math.isclose(result.area_violation, expected, rel_tol=1e-10)


# -----------------------------------------------------------------------------
# 7. Orçamento
# -----------------------------------------------------------------------------

class TestBudgetConstraint:
    """Testes da restrição orçamentária com tolerância."""

    def test_no_budget_no_violation(self):
        prob = make_problem(budget=None)
        result = evaluate_candidate(100, prob)
        assert result.budget_violation == 0.0

    def test_budget_sufficient(self):
        prob = make_problem(budget=100000.0)
        result = evaluate_candidate(10, prob)
        assert result.budget_violation == 0.0

    def test_budget_insufficient(self):
        prob = make_problem(budget=1000.0)
        result = evaluate_candidate(10, prob)
        assert result.budget_violation > 0.0

    def test_budget_exact_boundary(self):
        prob = make_problem()
        N = 5
        exact_cost = N * prob.unit_cost
        prob_boundary = replace(prob, budget=exact_cost + EPS_BUDGET)
        result = evaluate_candidate(N, prob_boundary)
        assert result.budget_violation == 0.0

    def test_budget_just_outside_tolerance(self):
        prob = make_problem()
        N = 5
        exact_cost = N * prob.unit_cost
        prob_outside = replace(prob, budget=exact_cost - 2 * EPS_BUDGET)
        result = evaluate_candidate(N, prob_outside)
        assert result.budget_violation > 0.0
        expected = (N * prob.unit_cost - prob_outside.budget - EPS_BUDGET) / prob_outside.budget
        assert math.isclose(result.budget_violation, expected, rel_tol=1e-10)


# -----------------------------------------------------------------------------
# 8. Viabilidade combinada
# -----------------------------------------------------------------------------

class TestFeasibility:
    """Testes de viabilidade combinada (todas as restrições)."""

    def test_all_constraints_satisfied_feasible(self):
        prob = make_problem(consumption=50.0, usable_area=100.0, budget=100000.0)
        result = evaluate_candidate(1, prob)
        assert result.feasible is True
        assert result.violation == 0.0

    def test_energy_violation_makes_infeasible(self):
        prob = make_problem(consumption=1000.0, usable_area=100.0)
        result = evaluate_candidate(1, prob)
        assert result.feasible is False
        assert result.energy_violation > 0.0

    def test_area_violation_makes_infeasible(self):
        prob = make_problem(consumption=50.0, usable_area=1.0)
        result = evaluate_candidate(1, prob)
        assert result.feasible is False
        assert result.area_violation > 0.0

    def test_budget_violation_makes_infeasible(self):
        prob = make_problem(consumption=50.0, usable_area=100.0, budget=100.0)
        result = evaluate_candidate(1, prob)
        assert result.feasible is False
        assert result.budget_violation > 0.0

    def test_violation_sum_matches_total(self):
        prob = make_problem(consumption=1000.0, usable_area=1.0, budget=100.0)
        result = evaluate_candidate(1, prob)
        expected_total = result.energy_violation + result.area_violation + result.budget_violation
        assert math.isclose(result.violation, expected_total, rel_tol=1e-10)


# -----------------------------------------------------------------------------
# 9. Comparação lexicográfica
# -----------------------------------------------------------------------------

class TestLexicographicComparison:
    """Testes da compare_lexicographic (Regra Oficial Seção 6.3)."""

    def make_result(self, num_panels: int, feasible: bool, cost: float,
                    violation: float, energy_violation: float) -> EvaluationResult:
        return EvaluationResult(
            num_panels=num_panels,
            feasible=feasible,
            cost=cost,
            violation=violation,
            energy_violation=energy_violation,
            area_violation=0.0,
            budget_violation=0.0,
            energy_by_month={},
            used_area=0.0,
            occupancy=0.0,
        )

    def test_feasible_beats_infeasible(self):
        A = self.make_result(10, True, 10000.0, 0.0, 0.0)
        B = self.make_result(1, False, 100.0, 0.1, 0.1)
        assert compare_lexicographic(A, B) is A
        assert compare_lexicographic(B, A) is A

    def test_lower_cost_beats_higher_cost_when_both_feasible(self):
        A = self.make_result(4, True, 5400.0, 0.0, 0.0)
        B = self.make_result(5, True, 6750.0, 0.0, 0.0)
        assert compare_lexicographic(A, B) is A
        assert compare_lexicographic(B, A) is A

    def test_lower_violation_beats_higher_when_both_infeasible(self):
        A = self.make_result(1, False, 100.0, 0.1, 0.1)
        B = self.make_result(2, False, 200.0, 0.2, 0.2)
        assert compare_lexicographic(A, B) is A
        assert compare_lexicographic(B, A) is A

    def test_lower_energy_violation_tiebreaker(self):
        A = self.make_result(1, False, 100.0, 0.2, 0.1)
        B = self.make_result(2, False, 200.0, 0.2, 0.15)
        assert compare_lexicographic(A, B) is A
        assert compare_lexicographic(B, A) is A

    def test_lower_num_panels_final_tiebreaker(self):
        A = self.make_result(3, False, 300.0, 0.2, 0.1)
        B = self.make_result(5, False, 500.0, 0.2, 0.1)
        assert compare_lexicographic(A, B) is A
        assert compare_lexicographic(B, A) is A

    def test_deterministic_repeated_comparison(self):
        A = self.make_result(3, False, 300.0, 0.2, 0.1)
        B = self.make_result(5, False, 500.0, 0.2, 0.1)
        for _ in range(100):
            assert compare_lexicographic(A, B) is A
            assert compare_lexicographic(B, A) is A

    def test_same_object_returns_itself(self):
        A = self.make_result(1, True, 100.0, 0.0, 0.0)
        assert compare_lexicographic(A, A) is A


# -----------------------------------------------------------------------------
# 10. Consistência is_feasible vs evaluate_candidate
# -----------------------------------------------------------------------------

class TestConsistency:
    """Consistência entre is_feasible (busca exaustiva) e evaluate_candidate."""

    def test_same_feasibility_classification(self):
        prob = make_problem()
        for N in range(0, 35):
            eval_result = evaluate_candidate(N, prob)
            feasible_direct = is_feasible(N, prob)
            assert eval_result.feasible == feasible_direct, \
                f"N={N}: evaluate={eval_result.feasible}, is_feasible={feasible_direct}"

    def test_zero_candidate(self):
        prob = make_problem()
        assert is_feasible(0, prob) is False
        result = evaluate_candidate(0, prob)
        assert result.feasible is False


# -----------------------------------------------------------------------------
# 11. Integração com dados do projeto
# -----------------------------------------------------------------------------

class TestProjectDataIntegration:
    """Testes usando dados reais do projeto (João Pessoa, painel STD-550W)."""

    def test_build_problem_from_data(self):
        prob = build_problem_from_data(
            monthly_consumption_kwh=300.0,
            roof_usable_area_m2=68.0,
            panel_data=PANEL_DATA,
            city_data=CITY_DATA_JP,
            irradiance_data=IRRADIANCE_JP,
            max_budget_brl=None,
        )
        assert prob.consumption == 300.0
        assert prob.usable_area == 68.0
        assert prob.panel_power_wp == 550.0
        assert prob.panel_area == 2.2
        assert prob.efficiency == 0.82
        assert prob.unit_cost == 1350.0
        assert len(prob.hsp) == 12
        assert prob.hsp[1] == 5.7
        assert prob.hsp[6] == 4.9

    def test_evaluate_with_real_data(self):
        prob = build_problem_from_data(
            monthly_consumption_kwh=300.0,
            roof_usable_area_m2=68.0,
            panel_data=PANEL_DATA,
            city_data=CITY_DATA_JP,
            irradiance_data=IRRADIANCE_JP,
        )
        result = evaluate_candidate(4, prob)
        # Mês crítico (junho, HSP=4.9): 4 * 0.55 * 4.9 * 30 * 0.82 = 265.188
        assert math.isclose(result.energy_by_month[6], 265.188, abs_tol=1e-3)
        assert math.isclose(result.cost, 5400.0, abs_tol=1e-6)
        assert result.used_area == 8.8
        assert math.isclose(result.occupancy, 8.8 / 68.0, rel_tol=1e-10)


# -----------------------------------------------------------------------------
# 12. Regressão: compatibilidade com fórmulas antigas
# -----------------------------------------------------------------------------

class TestRegressionCompatibility:
    """Garante que fórmulas energéticas não regrediram (conversão Wp→kWp)."""

    def test_energy_not_scaled_by_1000(self):
        prob = make_problem(consumption=300.0, usable_area=100.0)
        result = evaluate_candidate(1, prob)
        expected_jan = 550.0 / 1000.0 * 5.7 * 30.0 * 0.82
        assert math.isclose(result.energy_by_month[1], expected_jan, rel_tol=1e-10)

    def test_cost_matches_unit_cost(self):
        prob = make_problem()
        result = evaluate_candidate(5, prob)
        assert math.isclose(result.cost, 5 * 1350.0, rel_tol=1e-10)


# -----------------------------------------------------------------------------
# Execução direta
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    pytest.main([__file__, "-v"])