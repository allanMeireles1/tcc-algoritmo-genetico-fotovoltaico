
import random

from core.config import (
    MIN_PANELS,
    MAX_PANELS,
    MUTATION_RATE
)

def crossover(parent1: int, parent2: int) -> int:
    return (parent1 + parent2) // 2

def mutate(individual: int) -> int:

    if random.random() < MUTATION_RATE:
        individual += random.choice([-1, 1])

    individual = max(MIN_PANELS, individual)
    individual = min(MAX_PANELS, individual)

    return individual
