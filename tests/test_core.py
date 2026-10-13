"""Test the scientific core – calculations, fitness, and deterministic AG.

All numbers are taken from the reference probe scripts (tests/probe_reference*.py).
Tolerance is set to 1e-6 for deterministic floats where appropriate.
"""

import math
from pathlib import Path
import sys

# Ensure src is on PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from src.core.config import GAConfig
from src.genetic.fitness import (
    calc_energy_kwh_month,
    calc_cost_brl,
    evaluate_fitness,
    evaluate_fitness_breakdown,
)
from src.genetic.algorithm import max_panels_by_roof, run_genetic_algorithm
from src.models.roof import RoofInput
from src.simulation.runner import build_problem, run_optimization
from src.simulation.baseline import evaluate_direct_baseline
from src.storage.loader import load_cities, load_panels, load_scenarios
from src.utils.seed import set_global_seed

# Helper constants – these match the mock data
CITY = "João Pessoa"
PANEL_IDX = 0  # there is only one panel entry in panels_mock.json

# Load shared fixture data once
CITIES = load_cities()
PANELS = load_panels()
SCENARIOS = load_scenarios()
CITY_DATA = next(c for c in CITIES if c["city"] == CITY)
PANEL_DATA = PANELS[PANEL_IDX]

# Reference values (from probe_reference.py) – we keep them as constants for reproducibility
REF_ENERGY_1 = 73.06200000000001
REF_ENERGY_5 = 365.31
REF_COST_5 = 1350.0 + 250.0  # panel_cost + installation per panel (already summed in runner)
REF_BASELINE = (5, -233.469, 365.31, 6750.0)
REF_FITNESS_BREAKDOWN = {
    1: {
        "energy_term": 73.06200000000001,
        "cost_penalty": 108.0,
        "waste_penalty": 0.0,
        "deficit_penalty": 340.407,
        "area_penalty": 0.0,
        "budget_penalty": 0.0,
        "fitness_total": -375.34499999999997,
    },
    3: {
        "energy_term": 219.18600000000004,
        "cost_penalty": 324.0,
        "waste_penalty": 0.0,
        "deficit_penalty": 121.22099999999995,
        "area_penalty": 0.0,
        "budget_penalty": 0.0,
        "fitness_total": -226.0349999999999,
    },
    5: {
        "energy_term": 365.31,
        "cost_penalty": 540.0,
        "waste_penalty": 58.779,
        "deficit_penalty": 0.0,
        "area_penalty": 0.0,
        "budget_penalty": 0.0,
        "fitness_total": -233.469,
    },
    10: {
        "energy_term": 730.62,
        "cost_penalty": 1080.0,
        "waste_penalty": 387.558,
        "deficit_penalty": 0.0,
        "area_penalty": 0.0,
        "budget_penalty": 0.0,
        "fitness_total": -736.938,
    },
}

# Reference for a full optimization run (seed=42, pop=60, gens=120, runs=3)
REF_OPT = {
    "best_num_panels": 4,
    "best_energy_kwh_month": 292.24800000000005,
    "best_cost_brl": 5400.0,
    "best_fitness": -151.37999999999988,
    "occupancy": 0.12941176470588237,
    "deficit": 7.751999999999953,
    "surplus": 0.0,
    "benchmark_panels": 5,
    "benchmark_fitness": -233.469,
    "benchmark_energy": 365.31,
    "benchmark_cost": 6750.0,
    "history_len": 120,
}

TOL = 1e-6

def make_roof(width=8.0, length=10.0, consumption=300.0, budget=None):
    return RoofInput(
        width_m=width,
        length_m=length,
        monthly_consumption_kwh=consumption,
        city=CITY,
        roof_type="ceramic",
        max_budget_brl=budget,
    )

def build_common_problem(roof: RoofInput):
    return build_problem(roof, CITY_DATA, PANEL_DATA)

@pytest.mark.parametrize("num_panels,expected", [(1, REF_ENERGY_1), (5, REF_ENERGY_5)])
def test_energy_calc(num_panels, expected):
    energy = calc_energy_kwh_month(
        num_panels=num_panels,
        panel_power_wp=float(PANEL_DATA["panel_power_wp"]),
        irradiance_kwh_m2_day=float(CITY_DATA["irradiance_kwh_m2_day"]),
        system_efficiency=float(PANEL_DATA["system_efficiency"]),
    )
    assert math.isclose(energy, expected, rel_tol=0, abs_tol=TOL)

def test_cost_calc():
    cost = calc_cost_brl(num_panels=5, panel_cost_brl=REF_COST_5)
    assert math.isclose(cost, REF_COST_5 * 5, rel_tol=0, abs_tol=TOL)

def test_baseline_direct():
    roof = make_roof()
    prob = build_common_problem(roof)
    result = evaluate_direct_baseline(prob, GAConfig())
    assert result[0] == REF_BASELINE[0]
    for actual, expected in zip(result[1:], REF_BASELINE[1:]):
        assert math.isclose(actual, expected, rel_tol=0, abs_tol=TOL)

@pytest.mark.parametrize("num,expected", [(1, REF_FITNESS_BREAKDOWN[1]), (3, REF_FITNESS_BREAKDOWN[3]), (5, REF_FITNESS_BREAKDOWN[5]), (10, REF_FITNESS_BREAKDOWN[10])])
def test_fitness_breakdown(num, expected):
    prob = build_common_problem(make_roof())
    bd = evaluate_fitness_breakdown(num, prob, GAConfig())
    for key, exp_val in expected.items():
        actual = getattr(bd, key)
        assert math.isclose(actual, exp_val, rel_tol=0, abs_tol=TOL), f"{key} mismatch"

def test_fitness_total_matches_breakdown():
    prob = build_common_problem(make_roof())
    total_fitness, _, _ = evaluate_fitness(5, prob, GAConfig())
    bd = evaluate_fitness_breakdown(5, prob, GAConfig())
    assert math.isclose(total_fitness, bd.fitness_total, rel_tol=0, abs_tol=TOL)

def test_max_panels_by_roof():
    assert max_panels_by_roof(68.0, 2.2) == 30
    assert max_panels_by_roof(1.0, 2.2) == 1

def test_deterministic_optimization():
    # Seed 42, config matches the reference script (pop=60, gens=120, runs=3)
    cfg = GAConfig(
        population_size=60,
        generations=120,
        crossover_rate=0.8,
        mutation_rate=0.1,
        elitism_count=2,
        random_seed=42,
    )
    roof = make_roof()
    set_global_seed(42)  # ensure global randomness is aligned
    outcome = run_optimization(roof, CITY_DATA, PANEL_DATA, cfg, runs=3)
    r = outcome.result
    # check a subset of reference values – the rest are deterministic by construction
    assert r.best_num_panels == REF_OPT["best_num_panels"]
    assert math.isclose(r.best_energy_kwh_month, REF_OPT["best_energy_kwh_month"], abs_tol=TOL)
    assert math.isclose(r.best_cost_brl, REF_OPT["best_cost_brl"], abs_tol=TOL)
    assert math.isclose(r.best_fitness, REF_OPT["best_fitness"], abs_tol=TOL)
    assert math.isclose(r.roof_occupancy_ratio, REF_OPT["occupancy"], abs_tol=TOL)
    # check history length matches config.generations (120)
    assert len(outcome.history) == REF_OPT["history_len"]

def test_reproducibility_across_runs():
    cfg = GAConfig(population_size=60, generations=120, random_seed=42)
    roof = make_roof()
    set_global_seed(42)
    first = run_optimization(roof, CITY_DATA, PANEL_DATA, cfg, runs=1).result
    set_global_seed(42)
    second = run_optimization(roof, CITY_DATA, PANEL_DATA, cfg, runs=1).result
    assert first.best_num_panels == second.best_num_panels
    assert math.isclose(first.best_fitness, second.best_fitness, abs_tol=TOL)

def test_scenarios_reference():
    # For each mock scenario we compare the best num panels and fitness against the reference printed in probe_reference2.py
    cfg = GAConfig()  # defaults (pop=50, gens=100)
    for sc in SCENARIOS:
        # Derive length so that gross area matches scenario roof_area_m2 (width fixed at 8.0)
        width = 8.0
        length = float(sc["roof_area_m2"]) / width
        roof = RoofInput(
            width_m=width,
            length_m=length,
            monthly_consumption_kwh=float(sc["monthly_consumption_kwh"]),
            city=sc["city"],
            roof_type="ceramic",
            max_budget_brl=None,
        )
        outcome = run_optimization(roof, CITY_DATA, PANEL_DATA, cfg, runs=1)
        # Expected best panels per scenario – taken from probe_reference2 output
        if sc["scenario_name"] == "low":
            assert outcome.result.best_num_panels == 2
        elif sc["scenario_name"] == "medium":
            assert outcome.result.best_num_panels == 4
        elif sc["scenario_name"] == "high":
            assert outcome.result.best_num_panels == 7
        else:
            pytest.fail(f"Unexpected scenario name {sc['scenario_name']}")
