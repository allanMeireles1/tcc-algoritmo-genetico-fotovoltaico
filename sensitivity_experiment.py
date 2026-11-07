"""E5.4.4 – Análise de sensibilidade dos hiperparâmetros do AG.

Avalia, em três cenários, o efeito de:
- tamanho da população;
- número de gerações;
- taxa de mutação;
- taxa de crossover;
- número de elitistas.

Cada ponto é comparado ao ótimo da busca exaustiva (mesmo Problem).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.core.config import GAConfig
from src.models.roof import RoofInput
from src.simulation.evaluation import build_problem_from_data
from src.simulation.experiments import (
    run_crossover_rate_sensitivity,
    run_elitism_sensitivity,
    run_generations_sensitivity,
    run_mutation_rate_sensitivity,
    run_population_sensitivity,
)
from src.simulation.solvers import solve_exhaustive
from src.storage.loader import load_cities, load_irradiance, load_panels

CITIES = load_cities()
PANEL = load_panels()[0]
IRRADIANCE = load_irradiance()
CITY_JP = next(c for c in CITIES if c["city"] == "João Pessoa")

BASE = GAConfig(
    population_size=20,
    generations=40,
    crossover_rate=0.8,
    mutation_rate=0.2,
    elitism_count=2,
    random_seed=42,
)

SCENARIOS = [
    ("viavel", 200.0, 8.0, 10.0, None),
    ("limite_area", 300.0, 1.0, 2.0, None),
    ("limite_orcamento", 300.0, 8.0, 10.0, 4000.0),
]

SWEEPS = [
    ("População", run_population_sensitivity, [5, 10, 20, 40, 80]),
    ("Gerações", run_generations_sensitivity, [5, 10, 20, 40, 80]),
    ("Taxa de mutação", run_mutation_rate_sensitivity, [0.0, 0.05, 0.1, 0.2, 0.4, 0.6]),
    ("Taxa de crossover", run_crossover_rate_sensitivity, [0.0, 0.3, 0.5, 0.7, 0.8, 0.9, 1.0]),
    ("Elitismo", run_elitism_sensitivity, [0, 1, 2, 3, 5, 10]),
]

print("=== E5.4.4 – Sensibilidade a hiperparâmetros ===\n")

for name, consumption, width, length, budget in SCENARIOS:
    roof = RoofInput(
        width_m=width,
        length_m=length,
        monthly_consumption_kwh=consumption,
        city="João Pessoa",
        max_budget_brl=budget,
    )
    problem = build_problem_from_data(
        roof.monthly_consumption_kwh,
        roof.usable_area_m2(),
        PANEL,
        CITY_JP,
        irradiance_data=IRRADIANCE,
        max_budget_brl=budget,
    )
    reference = solve_exhaustive(problem).best.num_panels
    print(f"# Cenário: {name} | referência exaustiva = {reference} painéis\n")

    for label, sweep_fn, values in SWEEPS:
        points = sweep_fn(roof, CITY_JP, PANEL, BASE, values)
        print(f"  {label}:")
        for point in points:
            status = "ótimo" if point.best_panels == reference else f"gap={reference - point.best_panels}"
            print(
                f"    {point.parameter_value:>6} -> painéis={point.best_panels:>3} | "
                f"{point.execution_time_s * 1000:7.1f} ms | {status}"
            )
        print()
    print()
