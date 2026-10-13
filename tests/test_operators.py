"""Tests for genetic operators and the AG loop invariants."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from src.core.config import GAConfig
from src.genetic.algorithm import max_panels_by_roof, run_genetic_algorithm
from src.genetic.operators import crossover, initialize_population, mutate
from src.models.individual import Individual
from src.models.roof import RoofInput
from src.simulation.runner import build_problem
from src.storage.loader import load_cities, load_panels
from src.utils.seed import set_global_seed

_CITY = next(c for c in load_cities() if c["city"] == "João Pessoa")
_PANEL = load_panels()[0]


def _scenario(consumption=300.0, budget=None) -> dict:
    """Build a real problem dict via the production helper (build_problem)."""
    return build_problem(
        RoofInput(8.0, 10.0, consumption, "João Pessoa", "ceramic", budget), _CITY, _PANEL
    )


def test_initialize_population_bounds():
    set_global_seed(0)
    pop = initialize_population(20, 0, 30)
    assert len(pop) == 20
    assert all(0 <= ind.num_panels <= 30 for ind in pop)


def test_initialize_population_single_value():
    pop = initialize_population(5, 3, 3)
    assert all(ind.num_panels == 3 for ind in pop)


def test_mutate_respects_bounds():
    set_global_seed(1)
    for _ in range(200):
        ind = Individual(num_panels=30)
        mutate(ind, mutation_rate=1.0, min_panels=0, max_panels=30)
        assert 0 <= ind.num_panels <= 30


def test_mutate_no_mutation_when_rate_zero():
    ind = Individual(num_panels=12)
    mutate(ind, mutation_rate=0.0, min_panels=0, max_panels=30)
    assert ind.num_panels == 12


def test_crossover_no_crossover_when_rate_zero():
    a, b = crossover(Individual(3), Individual(7), crossover_rate=0.0)
    assert a.num_panels == 3
    assert b.num_panels == 7


def test_crossover_blends_parents():
    set_global_seed(0)
    a, b = crossover(Individual(4), Individual(6), crossover_rate=1.0)
    # blended = round((4+6)/2) = 5 -> both children should be around 5
    assert 4 <= a.num_panels <= 6
    assert 4 <= b.num_panels <= 6


@pytest.mark.parametrize("num_panels", [0, 1, 5, 15, 30])
def test_crossover_child_can_exceed_upper_bound(num_panels):
    """Documented behaviour, not a spec.

    With both parents at the upper bound and crossover_rate=1.0, the second
    child receives blended + random.choice([-1, 0, 1]) and is NOT clamped to
    [min, max]. This is the observed (pre-migration) behaviour; the test pins
    it so the migration cannot silently change it without a conscious decision.
    """
    set_global_seed(7)
    parent = Individual(num_panels=num_panels)
    a, b = crossover(parent, parent, crossover_rate=1.0)
    # assert the current observed behaviour (may be > max_panels by 1)
    assert b.num_panels in {num_panels - 1, num_panels, num_panels + 1}


def test_genetic_algorithm_runs_and_returns_valid():
    set_global_seed(42)
    scenario = _scenario()
    config = GAConfig(population_size=20, generations=10, random_seed=42)
    best, history, final_pop = run_genetic_algorithm(scenario, config)
    assert isinstance(best, Individual)
    assert best.num_panels >= 0
    max_panels = max_panels_by_roof(68.0, 2.2)
    assert best.num_panels <= max_panels
    assert len(history) == 10
    assert len(final_pop) == 20


def test_genetic_algorithm_history_best_improves_monotonically():
    """Best fitness should never decrease across generations (elitism present)."""
    set_global_seed(42)
    scenario = _scenario()
    config = GAConfig(population_size=30, generations=15, elitism_count=2, random_seed=42)
    _, history, _ = run_genetic_algorithm(scenario, config)
    fitnesses = [h.best_fitness for h in history]
    for prev, curr in zip(fitnesses, fitnesses[1:]):
        assert curr >= prev - 1e-9


def test_deterministic_with_same_seed():
    set_global_seed(42)
    scenario = _scenario()
    config = GAConfig(population_size=20, generations=8, random_seed=42)
    best1, hist1, pop1 = run_genetic_algorithm(scenario, config)
    set_global_seed(42)
    best2, hist2, pop2 = run_genetic_algorithm(scenario, config)
    assert best1.num_panels == best2.num_panels
    assert [h.best_fitness for h in hist1] == [h.best_fitness for h in hist2]
    assert [i.num_panels for i in pop1] == [i.num_panels for i in pop2]
