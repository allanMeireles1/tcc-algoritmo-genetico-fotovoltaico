"""Tests for the academic experiments (sensitivity and timing)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.config import GAConfig
from src.models.result import SensitivityPoint, TimingPoint
from src.models.roof import RoofInput
from src.simulation.experiments import (
    run_consumption_sensitivity,
    run_crossover_rate_sensitivity,
    run_elitism_sensitivity,
    run_generations_sensitivity,
    run_generations_timing_experiment,
    run_mutation_rate_sensitivity,
    run_population_sensitivity,
    run_population_timing_experiment,
)
from src.storage.loader import load_cities, load_panels
from src.utils.seed import set_global_seed

CITIES = load_cities()
PANELS = load_panels()
CITY_DATA = next(c for c in CITIES if c["city"] == "João Pessoa")
PANEL_DATA = PANELS[0]


def _roof(consumption=300.0):
    return RoofInput(8.0, 10.0, consumption, "João Pessoa", "ceramic", None)


def test_sensitivity_returns_points():
    cfg = GAConfig(population_size=20, generations=10, random_seed=42)
    points = run_consumption_sensitivity(
        _roof(), CITY_DATA, PANEL_DATA, cfg, [150.0, 300.0, 450.0]
    )
    assert isinstance(points, list)
    assert len(points) == 3
    assert all(isinstance(p, SensitivityPoint) for p in points)
    assert [p.consumption_kwh for p in points] == [150.0, 300.0, 450.0]
    # best_panels should increase as consumption increases
    assert points[0].best_panels <= points[1].best_panels <= points[2].best_panels


def test_sensitivity_reproducible():
    cfg = GAConfig(population_size=20, generations=10, random_seed=42)
    set_global_seed(42)
    p1 = run_consumption_sensitivity(_roof(), CITY_DATA, PANEL_DATA, cfg, [300.0, 450.0])
    set_global_seed(42)
    p2 = run_consumption_sensitivity(_roof(), CITY_DATA, PANEL_DATA, cfg, [300.0, 450.0])
    assert [x.best_panels for x in p1] == [x.best_panels for x in p2]
    assert [x.best_fitness for x in p1] == [x.best_fitness for x in p2]


def test_population_timing_returns_points():
    base = GAConfig(population_size=20, generations=10, random_seed=42)
    points = run_population_timing_experiment(
        _roof(), CITY_DATA, PANEL_DATA, base, [20, 40]
    )
    assert isinstance(points, list)
    assert len(points) == 2
    assert all(isinstance(p, TimingPoint) for p in points)
    assert {p.parameter_value for p in points} == {20, 40}
    assert all(p.label == "População" for p in points)


def test_generations_timing_returns_points():
    base = GAConfig(population_size=20, generations=10, random_seed=42)
    points = run_generations_timing_experiment(
        _roof(), CITY_DATA, PANEL_DATA, base, [10, 20]
    )
    assert isinstance(points, list)
    assert len(points) == 2
    assert all(isinstance(p, TimingPoint) for p in points)
    assert all(p.label == "Gerações" for p in points)
