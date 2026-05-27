"""Métodos de seleção para algoritmo genético."""

import random

from src.models.individual import Individual


def tournament_selection(population: list[Individual], k: int = 3) -> Individual:
    """Retorna o melhor indivíduo entre k competidores aleatórios."""
    competitors = random.sample(population, k=min(k, len(population)))
    return max(competitors, key=lambda ind: ind.fitness)
