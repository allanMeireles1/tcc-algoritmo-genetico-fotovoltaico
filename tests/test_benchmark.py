"""Tests for benchmark E5.4.5 — tempo e qualidade de execução."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.config import GAConfig
from src.models.roof import RoofInput
from src.simulation.benchmark import run_benchmark
from src.simulation.solvers import solve_exhaustive
from src.simulation.evaluation import build_problem_from_data
from src.storage.loader import load_cities, load_panels, load_irradiance

CITIES = load_cities()
PANELS = load_panels()
CITY_JP = next(c for c in CITIES if c["city"] == "João Pessoa")
PANEL = PANELS[0]
IRRADIANCE = load_irradiance()


def _viavel_roof():
    return RoofInput(8.0, 10.0, 200.0, "João Pessoa", None)


def test_benchmark_returns_all_methods():
    roof = _viavel_roof()
    cfg = GAConfig(population_size=20, generations=40, random_seed=42)
    outcome = run_benchmark(roof, CITY_JP, PANEL, cfg, repetitions=5, warmup=1, irradiance_data=IRRADIANCE)
    methods = {m.method for m in outcome.methods}
    assert methods == {"analytical", "exhaustive", "genetic"}
    for m in outcome.methods:
        assert m.repetitions == 5
        assert m.times_s and len(m.times_s) == 5


def test_benchmark_speedups_positive():
    roof = _viavel_roof()
    cfg = GAConfig(population_size=20, generations=40, random_seed=42)
    outcome = run_benchmark(roof, CITY_JP, PANEL, cfg, repetitions=3, warmup=1, irradiance_data=IRRADIANCE)
    assert outcome.speedups["analytical_over_genetic"] > 0
    assert outcome.speedups["exhaustive_over_genetic"] > 0


def test_benchmark_reference_matches_exhaustive():
    roof = _viavel_roof()
    cfg = GAConfig(population_size=20, generations=40, random_seed=42)
    outcome = run_benchmark(roof, CITY_JP, PANEL, cfg, repetitions=3, warmup=1, irradiance_data=IRRADIANCE)
    # Create same problem and compute exhaustive independently
    problem = build_problem_from_data(
        roof.monthly_consumption_kwh,
        roof.usable_area_m2(),
        PANEL,
        CITY_JP,
        irradiance_data=IRRADIANCE,
        max_budget_brl=roof.max_budget_brl,
    )
    ref = solve_exhaustive(problem).best.num_panels
    assert outcome.reference_panels == ref


def test_benchmark_quality_all_optimal():
    roof = _viavel_roof()
    cfg = GAConfig(population_size=20, generations=40, random_seed=42)
    outcome = run_benchmark(roof, CITY_JP, PANEL, cfg, repetitions=5, warmup=1, irradiance_data=IRRADIANCE)
    for m in outcome.methods:
        assert m.matches_optimum_count == m.repetitions


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))