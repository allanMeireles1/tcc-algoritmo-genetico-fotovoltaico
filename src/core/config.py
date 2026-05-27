"""Configurações de execução do algoritmo genético."""

from dataclasses import dataclass


@dataclass(slots=True)
class GAConfig:
    """Parâmetros do algoritmo genético."""

    population_size: int = 50
    generations: int = 100
    crossover_rate: float = 0.8
    mutation_rate: float = 0.1
    elitism_count: int = 2
    random_seed: int = 42
    cost_weight_alpha: float = 0.08
    waste_penalty_weight: float = 0.9
    deficit_penalty_weight: float = 1.5
    budget_penalty_weight: float = 2.0
