
import random

from genetic.individual import Individual
from genetic.fitness import calculate_fitness
from genetic.operators import crossover, mutate

from core.config import (
    POPULATION_SIZE,
    GENERATIONS,
    MIN_PANELS,
    MAX_PANELS
)


class GeneticAlgorithm:

    def __init__(
        self,
        consumption: float,
        irradiation: float
    ):

        self.consumption = consumption
        self.irradiation = irradiation

        self.history = []
        self.best_individual = None

    def generate_population(self):

        population = []

        for _ in range(POPULATION_SIZE):

            panels = random.randint(
                MIN_PANELS,
                MAX_PANELS
            )

            population.append(
                Individual(panels)
            )

        return population

    def evaluate_population(self, population):

        for individual in population:

            individual.fitness = calculate_fitness(
                individual.number_of_panels,
                self.consumption,
                self.irradiation
            )

    def select_best(self, population):

        population.sort(
            key=lambda x: x.fitness,
            reverse=True
        )

        return population[:2]

    def execute(self):

        population = self.generate_population()

        for generation in range(GENERATIONS):

            self.evaluate_population(population)

            best_two = self.select_best(population)

            best_score = best_two[0].fitness

            self.history.append(best_score)

            new_population = best_two.copy()

            while len(new_population) < POPULATION_SIZE:

                child_panels = crossover(
                    best_two[0].number_of_panels,
                    best_two[1].number_of_panels
                )

                child_panels = mutate(child_panels)

                new_population.append(
                    Individual(child_panels)
                )

            population = new_population

        self.evaluate_population(population)

        self.best_individual = max(
            population,
            key=lambda x: x.fitness
        )

        return self.best_individual
