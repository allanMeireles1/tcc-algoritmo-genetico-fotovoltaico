"""Métodos de seleção para algoritmo genético."""

import random

from src.models.individual import Individual
from src.simulation.evaluation import compare_lexicographic


def tournament_selection(population: list[Individual], k: int = 3) -> Individual:
    """Retorna o melhor indivíduo entre k competidores aleatórios."""
    competitors = random.sample(population, k=min(k, len(population)))
    return max(competitors, key=lambda ind: ind.fitness)


def tournament_selection_lexicographic(population: list[Individual], k: int = 3) -> Individual:
    """Seleção por torneio que usa a comparação lexicográfica oficial (E5.2)."""
    competitors = random.sample(population, k=min(k, len(population)))
    if len(competitors) == 0:
        raise ValueError("População vazia para seleção")
    best = competitors[0]
    if best.evaluation is None:
        raise ValueError("Indivíduo deve possuir evaluation preenchida")
    for competitor in competitors[1:]:
        if competitor.evaluation is None:
            raise ValueError("Indivíduo deve possuir evaluation preenchida")
        if compare_lexicographic(competitor.evaluation, best.evaluation) is competitor.evaluation:
            best = competitor
    return best
