"""Laço principal do algoritmo genético."""

from src.core.config import GAConfig
from src.genetic.fitness import evaluate_fitness
from src.genetic.operators import crossover, initialize_population, mutate
from src.genetic.selection import tournament_selection
from src.models.individual import Individual
from src.models.result import GenerationStats


def max_panels_by_roof(roof_usable_area_m2: float, panel_area_m2: float) -> int:
    """Deriva quantidade máxima de painéis pela área disponível."""
    return max(1, int(roof_usable_area_m2 // panel_area_m2))


def _evaluate_population(population: list[Individual], scenario: dict, config: GAConfig) -> None:
    for individual in population:
        individual.fitness, _, _ = evaluate_fitness(individual.num_panels, scenario, config)


def run_genetic_algorithm(scenario: dict, config: GAConfig) -> tuple[Individual, list[GenerationStats]]:
    """Executa o AG e retorna melhor indivíduo e histórico por geração."""
    min_panels = 0
    max_panels = max_panels_by_roof(
        roof_usable_area_m2=float(scenario["roof_usable_area_m2"]),
        panel_area_m2=float(scenario["panel_area_m2"]),
    )
    population = initialize_population(config.population_size, min_panels, max_panels)

    history: list[GenerationStats] = []
    _evaluate_population(population, scenario, config)

    for generation in range(config.generations):
        population.sort(key=lambda ind: ind.fitness, reverse=True)
        elites = [Individual(num_panels=ind.num_panels, fitness=ind.fitness) for ind in population[: config.elitism_count]]

        new_population: list[Individual] = elites
        while len(new_population) < config.population_size:
            parent_a = tournament_selection(population)
            parent_b = tournament_selection(population)
            child_a, child_b = crossover(parent_a, parent_b, config.crossover_rate)
            mutate(child_a, config.mutation_rate, min_panels, max_panels)
            mutate(child_b, config.mutation_rate, min_panels, max_panels)
            new_population.extend([child_a, child_b])

        population = new_population[: config.population_size]
        _evaluate_population(population, scenario, config)
        best = max(population, key=lambda ind: ind.fitness)
        avg = sum(ind.fitness for ind in population) / len(population)
        history.append(
            GenerationStats(
                generation=generation,
                best_fitness=best.fitness,
                avg_fitness=avg,
                best_panels=best.num_panels,
            )
        )

    best_overall = max(population, key=lambda ind: ind.fitness)
    return best_overall, history
