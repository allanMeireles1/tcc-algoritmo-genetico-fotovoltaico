"""Operadores genéticos: inicialização, crossover e mutação."""

import random

from src.models.individual import Individual


def initialize_population(pop_size: int, min_panels: int, max_panels: int) -> list[Individual]:
    """Cria população inicial com cromossomos inteiros aleatórios."""
    return [Individual(num_panels=random.randint(min_panels, max_panels)) for _ in range(pop_size)]


def crossover(parent_a: Individual, parent_b: Individual, crossover_rate: float) -> tuple[Individual, Individual]:
    """Realiza crossover aritmético simples para cromossomo inteiro."""
    if random.random() > crossover_rate:
        return Individual(parent_a.num_panels), Individual(parent_b.num_panels)

    blended = round((parent_a.num_panels + parent_b.num_panels) / 2)
    child_a = Individual(num_panels=blended)
    child_b = Individual(num_panels=blended + random.choice([-1, 0, 1]))
    return child_a, child_b


def mutate(individual: Individual, mutation_rate: float, min_panels: int, max_panels: int) -> None:
    """Aplica mutação inteira por deslocamento local."""
    if random.random() > mutation_rate:
        return
    delta = random.choice([-2, -1, 1, 2])
    individual.num_panels = max(min_panels, min(max_panels, individual.num_panels + delta))
