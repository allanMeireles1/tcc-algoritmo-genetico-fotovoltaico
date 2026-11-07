"""Laço principal do algoritmo genético."""

from src.core.config import GAConfig
from src.genetic.fitness import evaluate_fitness
from src.genetic.operators import crossover, initialize_population, mutate
from src.genetic.selection import tournament_selection, tournament_selection_lexicographic
from src.models.individual import Individual
from src.models.result import GenerationStats
from src.simulation.evaluation import Problem, evaluate_candidate, compare_lexicographic
from functools import cmp_to_key


def max_panels_by_roof(roof_usable_area_m2: float, panel_area_m2: float) -> int:
    """Deriva quantidade máxima de painéis pela área disponível."""
    return max(1, int(roof_usable_area_m2 // panel_area_m2))


def _evaluate_population(population: list[Individual], scenario: dict, config: GAConfig) -> None:
    for individual in population:
        individual.fitness, _, _ = evaluate_fitness(individual.num_panels, scenario, config)


def run_genetic_algorithm(
    scenario: dict,
    config: GAConfig,
) -> tuple[Individual, list[GenerationStats], list[Individual]]:
    """Executa o AG e retorna melhor indivíduo, histórico e população final."""
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
    final_population = [
        Individual(num_panels=ind.num_panels, fitness=ind.fitness) for ind in population
    ]
    return best_overall, history, final_population


def _lexicographic_key(ind: Individual) -> tuple:
    """Key de ordenação consistente com compare_lexicographic (E5.2).

    Mantida para o histórico e usos utilitários; as decisões de elitismo e
    melhor indivíduo usam a comparação oficial via _cmp_lexicographic.
    """
    ev = ind.evaluation
    if ev is None:
        raise ValueError("Indivíduo sem evaluation avaliado")
    if ev.feasible:
        return (0, ev.cost, 0.0, 0.0, ev.num_panels)  # viável → menor custo
    else:
        return (1, 0.0, ev.violation, ev.energy_violation, ev.num_panels)  # inviável → menor violação


def _cmp_lexicographic(ind_a: Individual, ind_b: Individual) -> int:
    """Comparador de indivíduos derivado diretamente de compare_lexicographic.

    Retorna -1 se ind_a é melhor, 1 se ind_b é melhor e 0 em empate.
    compare_lexicographic devolve o segundo argumento em empate total:
    chamando nas duas direções distinguimos estrita superioridade de empate.
    """
    if ind_a.evaluation is None or ind_b.evaluation is None:
        raise ValueError("Indivíduo sem evaluation avaliado")
    if ind_a is ind_b or ind_a.evaluation is ind_b.evaluation:
        return 0
    ab = compare_lexicographic(ind_a.evaluation, ind_b.evaluation)
    ba = compare_lexicographic(ind_b.evaluation, ind_a.evaluation)
    if ab is ind_a.evaluation and ba is ind_a.evaluation:
        return -1
    if ab is ind_b.evaluation and ba is ind_b.evaluation:
        return 1
    return 0


def _select_elites(population: list[Individual], elitism_count: int) -> list[Individual]:
    """Seleciona os melhores indivíduos segundo a comparação lexicográfica oficial."""
    if elitism_count <= 0 or not population:
        return []
    count = min(elitism_count, len(population))
    return sorted(population, key=cmp_to_key(_cmp_lexicographic))[:count]


def _best_individual(population: list[Individual]) -> Individual:
    """Retorna o melhor indivíduo segundo a comparação lexicográfica oficial."""
    if not population:
        raise ValueError("População vazia")
    return _select_elites(population, 1)[0]


def run_genetic_algorithm_v2(
    problem: Problem,
    config: GAConfig,
) -> tuple[Individual, list[GenerationStats], list[Individual]]:
    """Versão do AG adaptada ao modelo E5.3.3: usa avaliação e comparação lexicográfica.

    Elitismo e substituição: a nova geração começa com cópias dos melhores
    indivíduos (ordem oficial) e é completada por filhos gerados por torneio
    + crossover + mutação; os filhos substituem integralmente o restante
    (substituição generacional com elitismo), e todos são reavaliados
    antes da próxima geração.
    """
    from src.simulation.evaluation import EPS_AREA, EPS_BUDGET
    from math import floor

    min_panels = 0
    N_area = floor((problem.usable_area + EPS_AREA) / problem.panel_area)
    if problem.budget is not None:
        N_budget = floor((problem.budget + EPS_BUDGET) / problem.unit_cost)
        max_panels = min(N_area, N_budget)
    else:
        max_panels = N_area
    max_panels = max(0, max_panels)
    population = initialize_population(config.population_size, min_panels, max_panels)

    # Avaliação inicial
    for individual in population:
        individual.evaluation = evaluate_candidate(individual.num_panels, problem)

    history: list[GenerationStats] = []
    best_ever = _best_individual(population)

    for generation in range(config.generations):
        # Elitismo: preserva os melhores segundo a regra oficial (E5.3.3.3)
        selected = _select_elites(population, config.elitism_count)
        new_population: list[Individual] = [
            Individual(num_panels=ind.num_panels, evaluation=ind.evaluation) for ind in selected
        ]

        while len(new_population) < config.population_size:
            parent_a = tournament_selection_lexicographic(population)
            parent_b = tournament_selection_lexicographic(population)
            child_a, child_b = crossover(parent_a, parent_b, config.crossover_rate)
            # Clamp para o espaço de busca (o crossover antigo pode sair dos limites)
            child_a.num_panels = max(min_panels, min(max_panels, child_a.num_panels))
            child_b.num_panels = max(min_panels, min(max_panels, child_b.num_panels))
            mutate(child_a, config.mutation_rate, min_panels, max_panels)
            mutate(child_b, config.mutation_rate, min_panels, max_panels)
            new_population.extend([child_a, child_b])

        population = new_population[: config.population_size]
        # Reavaliação antes da próxima geração
        for individual in population:
            individual.evaluation = evaluate_candidate(individual.num_panels, problem)

        # Elitismo nunca perde o melhor já encontrado
        gen_best = _best_individual(population)
        if _cmp_lexicographic(gen_best, best_ever) < 0:
            best_ever = gen_best

        best_fitness = (
            -gen_best.evaluation.cost if gen_best.evaluation.feasible else -gen_best.evaluation.violation
        )
        avg_fitness = sum(
            (-ind.evaluation.cost if ind.evaluation.feasible else -ind.evaluation.violation)
            for ind in population
        ) / len(population)
        history.append(
            GenerationStats(
                generation=generation,
                best_fitness=best_fitness,
                avg_fitness=avg_fitness,
                best_panels=gen_best.num_panels,
            )
        )

    # Melhor indivíduo global segundo a regra oficial
    final_best = _best_individual(population)
    best_overall = final_best if _cmp_lexicographic(final_best, best_ever) <= 0 else best_ever
    final_population = [
        Individual(num_panels=ind.num_panels, evaluation=ind.evaluation) for ind in population
    ]
    return best_overall, history, final_population
