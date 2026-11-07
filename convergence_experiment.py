"""E5.4.3 – Análise de Convergência

Para cada cenário e semente, executa ``run_comparison`` (1 run do AG por seed)
e imprime a evolução da geração a geração, além das métricas de convergência e
uma tabela com as execuções e taxas de convergência/ótimo.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.models.roof import RoofInput
from src.core.config import GAConfig
from src.simulation.runner import run_comparison, convergence_to_rows
from src.storage.loader import load_cities, load_panels, load_irradiance

CITIES = load_cities()
PANEL = load_panels()[0]
IRRADIANCE = load_irradiance()
CITY_JP = next(c for c in CITIES if c["city"] == "João Pessoa")


def make_scenario(name: str, consumption: float, area_w: float, area_l: float, budget: float | None):
    return (
        RoofInput(
            width_m=area_w,
            length_m=area_l,
            monthly_consumption_kwh=consumption,
            city="João Pessoa",
            max_budget_brl=budget,
        ),
        name,
    )


SCENARIOS = [
    ("viavel_simples", 200.0, 8.0, 10.0, None),
    ("viavel_alto", 500.0, 8.0, 10.0, None),
    ("limite_area", 300.0, 1.0, 2.0, None),
    ("orcamento_parcial", 300.0, 8.0, 10.0, 4000.0),
    ("orcamento_viavel", 200.0, 8.0, 10.0, 15000.0),
]

SEEDS = [42, 123, 999]
CONFIGS = [
    (20, 40),
    (10, 20),
]

print("=== E5.4.3 – Análise de Convergência ===\n")

for label, cons, w, l, budget in SCENARIOS:
    print(f"# Cenário: {label} (consumo={cons}, área={w}x{l}, budget={budget})")
    roof = make_scenario(label, cons, w, l, budget)[0]
    for pop, gens in CONFIGS:
        summaries = []
        print(f"  Config: pop={pop}, gens={gens}")
        for seed in SEEDS:
            cfg = GAConfig(
                population_size=pop,
                generations=gens,
                crossover_rate=0.8,
                mutation_rate=0.2,
                elitism_count=2,
                random_seed=seed,
            )
            outcome = run_comparison(
                roof=roof,
                city_data=CITY_JP,
                panel_data=PANEL,
                config=cfg,
                runs=1,
                irradiance_data=IRRADIANCE,
            )
            conv = outcome.convergence[0]
            print(f"    seed={seed} | traj={conv.best_panels_trajectory} |", end=" ")
            print(f"converged={conv.converged} | gens_to_opt={conv.generations_to_optimum}")
            summaries.append(outcome.convergence_summary)
        print()

        runs = sum(s["runs"] for s in summaries)
        conv_n = sum(s["converged_count"] for s in summaries)
        opt_n = sum(s["optimal_count"] for s in summaries)
        gens_opt = [g for s in summaries for g in s["generations_to_optimum_values"]]
        mean_to_opt = sum(gens_opt) / len(gens_opt) if gens_opt else None
        print(f"  >> Agregado: convergido={conv_n}/{runs} ({conv_n/runs:.0%}) |", end=" ")
        print(f"ótimo={opt_n}/{runs} ({opt_n/runs:.0%}) |", end=" ")
        print(f"média gerações até ótimo={mean_to_opt:.1f}" if mean_to_opt else "ótimo não atingido")
        print()
