"""E5.4.2 – Validação Experimental

Roda um conjunto de cenários controlados (viáveis, limites de área, orçamentos) usando
`run_comparison`. Para cada cenário são testadas diferentes sementes e duas configurações
de população/gerações. O script imprime um resumo que inclui:

- número de painéis obtido por cada método (analítico, exaustivo, AG)
- se o AG foi viável
- se a solução analítica coincide com a exaustiva
- se a avaliação completa de cada método corresponde à recomputação via evaluate_candidate
- se o melhor do AG coincide com o melhor exaustivo (quando possível)
"""

import sys
from pathlib import Path

# garantir import local
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.models.roof import RoofInput
from src.core.config import GAConfig
from src.simulation.runner import run_comparison
from src.storage.loader import load_cities, load_panels, load_irradiance
from src.simulation.evaluation import evaluate_candidate

# Dados de apoio
CITIES = load_cities()
PANEL = load_panels()[0]
IRRADIANCE = load_irradiance()

# Cenários de teste (nome, width, length, consumo, budget)
SCENARIOS = [
    ("viavel_simples", 8.0, 10.0, 200.0, None),          # consumo moderado, sem orçamento
    ("viavel_alto", 8.0, 10.0, 500.0, None),            # consumo alto, ainda viável com área suficiente
    ("limite_area", 1.0, 2.0, 500.0, None),             # área muito pequena → limite de N por área
    ("orcamento_parcial", 8.0, 10.0, 300.0, 4000.0),   # orçamento limita N
    ("orcamento_viavel", 8.0, 10.0, 200.0, 15000.0),   # orçamento suficiente para solução analítica
]

# Sementes a testar
SEEDS = [42, 123, 999]

# Configurações de GA (população, gerações)
CONFIGS = [
    (20, 40),   # maior população, mais gerações
    (10, 20),   # configuração mais leve
]

def main() -> None:
    print("=== E5.4.2 – Validação Experimental ===\n")
    for name, w, l, cons, budget in SCENARIOS:
        city = next(c for c in CITIES if c["city"] == "João Pessoa")
        roof = RoofInput(
            width_m=w,
            length_m=l,
            monthly_consumption_kwh=cons,
            city=city["city"],
            max_budget_brl=budget,
        )
        print(f"# Cenário: {name} (w={w}, l={l}, consumo={cons}, budget={budget})")
        for pop, gens in CONFIGS:
            print(f"  Config GA: pop={pop}, gens={gens}")
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
                    city_data=city,
                    panel_data=PANEL,
                    config=cfg,
                    runs=1,  # única execução do AG por seed
                    irradiance_data=IRRADIANCE,
                )
                # Extrai resultados
                analytical = next(r for r in outcome.results if r.method == "analytical")
                exhaustive = next(r for r in outcome.results if r.method == "exhaustive")
                genetic = next(r for r in outcome.results if r.method == "genetic")
                # Verifica consistência da avaliação (recomputar via evaluate_candidate)
                consistent = all(
                    evaluate_candidate(r.evaluation.num_panels, outcome.problem) == r.evaluation
                    for r in outcome.results
                )
                # Verifica se o melhor AG coincide com o exaustivo (quando exaustivo viável)
                ag_matches_exh = genetic.evaluation.num_panels == exhaustive.evaluation.num_panels
                # Resumo para este seed
                print(
                    f"    seed={seed:3d} | "
                    f"anal={analytical.evaluation.num_panels:2d} "
                    f"exh={exhaustive.evaluation.num_panels:2d} "
                    f"AG={genetic.evaluation.num_panels:2d} "
                    f"AG_feas={genetic.evaluation.feasible} "
                    f"anal_eq_exh={outcome.summary['analytical_matches_exhaustive']} "
                    f"consistent={consistent} "
                    f"AG==exh={ag_matches_exh}"
                )
        print()  # espaçamento entre cenários

if __name__ == "__main__":
    main()
