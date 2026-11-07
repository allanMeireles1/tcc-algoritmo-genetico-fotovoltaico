"""E5.4.6 — Consolidação experimental com 30 seeds por configuração.

Executa os três cenários de consumo do artigo (baixo=150, médio=300, alto=500),
em duas configurações de AG, com 30 seeds independentes por configuração.

Saídas:
- results/e5_4_6/raw.jsonl   (uma linha por execução do AG e por método determinístico)
- results/e5_4_6/summary.json (estatísticas agregadas + IC 95% normal)
"""

import json
import sys
from pathlib import Path
from statistics import mean, median, stdev

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.core.config import GAConfig
from src.models.roof import RoofInput
from src.simulation.runner import run_comparison
from src.storage.loader import load_cities, load_irradiance, load_panels

CITIES = load_cities()
PANEL = load_panels()[0]
IRRADIANCE = load_irradiance()
CITY_JP = next(c for c in CITIES if c["city"] == "João Pessoa")

OUT = ROOT / "results" / "e5_4_6"
OUT.mkdir(parents=True, exist_ok=True)

SCENARIOS = [
    ("baixo", 150.0, 8.0, 10.0, None),
    ("medio", 300.0, 8.0, 10.0, None),
    ("alto", 500.0, 8.0, 10.0, None),
]

CONFIGS = [
    ("pop10_gen20", 42, 10, 20),
    ("pop20_gen40", 1042, 20, 40),
]

REPETITIONS = 30
Z_95 = 1.96


def ci95(values: list[float]) -> tuple[float, float]:
    """IC 95% por aproximação normal (n=30)."""
    m = mean(values)
    if len(values) < 2:
        return (m, m)
    half = Z_95 * stdev(values) / (len(values) ** 0.5)
    return (m - half, m + half)


def stats(values: list[float]) -> dict:
    lo, hi = ci95(values)
    return {
        "n": len(values),
        "mean": mean(values),
        "median": median(values),
        "std": stdev(values) if len(values) > 1 else 0.0,
        "ci95_low": lo,
        "ci95_high": hi,
        "min": min(values),
        "max": max(values),
    }


raw_records = []
summary = []

for scenario, consumption, width, length, budget in SCENARIOS:
    roof = RoofInput(
        width_m=width,
        length_m=length,
        monthly_consumption_kwh=consumption,
        city="João Pessoa",
        max_budget_brl=budget,
    )

    for config_label, base_seed, pop, gens in CONFIGS:
        cfg = GAConfig(
            population_size=pop,
            generations=gens,
            crossover_rate=0.8,
            mutation_rate=0.2,
            elitism_count=2,
            random_seed=base_seed,
        )
        outcome = run_comparison(
            roof=roof,
            city_data=CITY_JP,
            panel_data=PANEL,
            config=cfg,
            runs=REPETITIONS,
            irradiance_data=IRRADIANCE,
        )

        ref_panels = outcome.summary["exhaustive_panels"]
        ref_feasible = outcome.summary["exhaustive_feasible"]

        for result in outcome.results:
            raw_records.append(
                {
                    "scenario": scenario,
                    "consumption_kwh": consumption,
                    "config": config_label,
                    "method": result.method,
                    "run_index": result.run_index,
                    "run_seed": result.run_seed,
                    "panels": result.evaluation.num_panels,
                    "feasible": result.evaluation.feasible,
                    "cost_brl": result.evaluation.cost,
                    "time_s": result.execution_time_s,
                }
            )

        genetic = [r for r in outcome.results if r.method == "genetic"]
        panels = [r.evaluation.num_panels for r in genetic]
        times = [r.execution_time_s for r in genetic]
        optimal = [
            r for r in genetic
            if r.evaluation.num_panels == ref_panels
            and r.evaluation.feasible == ref_feasible
        ]

        summary.append(
            {
                "scenario": scenario,
                "consumption_kwh": consumption,
                "config": config_label,
                "population_size": pop,
                "generations": gens,
                "seeds": [r.run_seed for r in genetic],
                "reference_panels": ref_panels,
                "reference_feasible": ref_feasible,
                "optimal_count": len(optimal),
                "optimal_rate": len(optimal) / len(genetic),
                "panels_stats": stats([float(p) for p in panels]),
                "time_stats_s": stats(times),
                "analytical_time_s": next(
                    r.execution_time_s for r in outcome.results if r.method == "analytical"
                ),
                "exhaustive_time_s": next(
                    r.execution_time_s for r in outcome.results if r.method == "exhaustive"
                ),
            }
        )

with (OUT / "raw.jsonl").open("w", encoding="utf-8") as fh:
    for record in raw_records:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")

with (OUT / "summary.json").open("w", encoding="utf-8") as fh:
    json.dump(summary, fh, ensure_ascii=False, indent=2)

print("=== E5.4.6 – Consolidação (30 seeds) ===\n")
for row in summary:
    t = row["time_stats_s"]
    print(
        f"{row['scenario']:<6} {row['config']:<12} "
        f"ótimo={row['optimal_count']}/30 ({100*row['optimal_rate']:.0f}%) | "
        f"painéis={row['panels_stats']['mean']:.2f}±{row['panels_stats']['std']:.2f} "
        f"(IC95 {row['panels_stats']['ci95_low']:.2f}–{row['panels_stats']['ci95_high']:.2f}) | "
        f"tempo={1000*t['mean']:.1f} ms IC95 [{1000*t['ci95_low']:.1f}; {1000*t['ci95_high']:.1f}]"
    )

print(f"\nArquivos gerados em {OUT}")
