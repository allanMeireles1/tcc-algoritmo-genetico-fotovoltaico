"""E5.4.5 – Benchmark: tempo de execução e qualidade das soluções.

Executa analítico, busca exaustiva e AG v2 em três cenários, com metodologia
consistente (warmup + repetições, mesma seed por repetição, mesma instância
do problema para todos os métodos).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.core.config import GAConfig
from src.models.roof import RoofInput
from src.simulation.benchmark import run_benchmark
from src.storage.loader import load_cities, load_irradiance, load_panels

CITIES = load_cities()
PANEL = load_panels()[0]
IRRADIANCE = load_irradiance()
CITY_JP = next(c for c in CITIES if c["city"] == "João Pessoa")

CONFIG = GAConfig(
    population_size=20,
    generations=40,
    crossover_rate=0.8,
    mutation_rate=0.2,
    elitism_count=2,
    random_seed=42,
)

SCENARIOS = [
    ("viável", 200.0, 8.0, 10.0, None),
    ("limite_area", 300.0, 1.0, 2.0, None),
    ("limite_orçamento", 300.0, 8.0, 10.0, 4000.0),
]

print("=== E5.4.5 – Benchmark (tempo e qualidade) ===\n")

for name, consumption, width, length, budget in SCENARIOS:
    roof = RoofInput(
        width_m=width,
        length_m=length,
        monthly_consumption_kwh=consumption,
        city="João Pessoa",
        max_budget_brl=budget,
    )
    outcome = run_benchmark(
        roof=roof,
        city_data=CITY_JP,
        panel_data=PANEL,
        config=CONFIG,
        repetitions=5,
        warmup=1,
        irradiance_data=IRRADIANCE,
    )

    print(f"# Cenário: {name} | referência exaustiva = {outcome.reference_panels} painéis")
    print(
        f"{'método':<14} {'rep':>3} {'med(s)':>8} {'std(s)':>8} {'min(s)':>8} {'max(s)':>8} "
        f"{'painéis':>7} {'ótimo(%)':>9} {'custo(R$)':>10}"
    )
    for m in outcome.methods:
        print(
            f"{m.method:<14} {m.repetitions:>3} {m.median_s:8.6f} {m.std_s:8.6f} "
            f"{m.min_s:8.6f} {m.max_s:8.6f} {round(sum(m.best_panels_values)/m.repetitions):>7} "
            f"{100*m.matches_optimum_count/m.repetitions:8.1f}% {m.mean_cost_brl:10.2f}"
        )
    print(
        f"Genético é {outcome.speedups['exhaustive_over_genetic']:.0f}x mais lento que a exaustiva e "
        f"{outcome.speedups['analytical_over_genetic']:.0f}x mais lento que a analítica."
    )
    print()
