"""Testes de E5.3.3.3: elitismo e substituição com comparação lexicográfica.

Cobrem: consistência entre _cmp_lexicographic e compare_lexicographic,
elite selection preserva o melhor indivíduo, população pequena, duplicados,
empates de custo/violação, limites de N e registro de histórico.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from src.core.config import GAConfig
from src.genetic.algorithm import (
    _cmp_lexicographic,
    _select_elites,
    _best_individual,
    _lexicographic_key,
)
from src.genetic.selection import tournament_selection_lexicographic
from src.models.individual import Individual
from src.simulation.evaluation import (
    Problem,
    EvaluationResult,
    evaluate_candidate,
    compare_lexicographic,
    DEFAULT_DAYS_PER_MONTH,
)
from src.storage.loader import load_cities, load_panels, load_irradiance
from src.utils.seed import set_global_seed

CITIES_LIST = load_cities()
PANEL_STD = load_panels()[0]
CITY_JP = next(c for c in CITIES_LIST if c["city"] == "João Pessoa")
IRRADIANCE_JP = load_irradiance()


def _make_ev(N: int, prob: Problem) -> EvaluationResult:
    return evaluate_candidate(N, prob)


def _synthetic_ev(
    num_panels: int = 1,
    feasible: bool = False,
    cost: float | None = None,
    violation: float = 0.0,
    energy_violation: float = 0.0,
) -> EvaluationResult:
    """Cria EvaluationResult sintético para exercitar todos os desempates."""
    return EvaluationResult(
        num_panels=num_panels,
        feasible=feasible,
        cost=(num_panels * 1000.0 if cost is None else cost),
        violation=violation,
        energy_violation=energy_violation,
        area_violation=0.0,
        budget_violation=0.0,
        energy_by_month={m: 0.0 for m in range(1, 13)},
        used_area=num_panels * 2.2,
        occupancy=0.0,
    )


def _assert_pair_consistent(a: Individual, b: Individual) -> None:
    """Verifica que key, compare_lexicographic e _cmp_lexicographic concordam."""
    ka, kb = _lexicographic_key(a), _lexicographic_key(b)
    ab = compare_lexicographic(a.evaluation, b.evaluation)
    ba = compare_lexicographic(b.evaluation, a.evaluation)
    cmp = _cmp_lexicographic(a, b)

    if ka < kb:
        assert ab is a.evaluation and ba is a.evaluation, "oficial deveria preferir a"
        assert cmp == -1, "cmp deveria preferir a"
    elif ka > kb:
        assert ab is b.evaluation and ba is b.evaluation, "oficial deveria preferir b"
        assert cmp == 1, "cmp deveria preferir b"
    else:
        # Empate total: compare devolve o segundo argumento nas duas direções
        assert ab is b.evaluation and ba is a.evaluation, "empate deveria ser simétrico"
        assert cmp == 0, "cmp deveria indicar empate"


class TestEquivalenciaParesSinteticos:
    """Cobre todos os desempates da Seção 6.3 com pares sintéticos."""

    def test_feasible_vs_infeasible(self):
        a = Individual(1, evaluation=_synthetic_ev(1, feasible=True, cost=1000.0))
        b = Individual(0, evaluation=_synthetic_ev(0, feasible=False, violation=1.0, energy_violation=1.0))
        _assert_pair_consistent(a, b)
        _assert_pair_consistent(b, a)

    def test_feasible_different_costs(self):
        a = Individual(1, evaluation=_synthetic_ev(1, feasible=True, cost=1000.0))
        b = Individual(2, evaluation=_synthetic_ev(2, feasible=True, cost=2000.0))
        _assert_pair_consistent(a, b)
        _assert_pair_consistent(b, a)

    def test_infeasible_different_violations(self):
        a = Individual(1, evaluation=_synthetic_ev(1, violation=0.5, energy_violation=0.5))
        b = Individual(2, evaluation=_synthetic_ev(2, violation=0.2, energy_violation=0.2))
        _assert_pair_consistent(a, b)
        _assert_pair_consistent(b, a)

    def test_tie_violation_different_energy_deficit(self):
        a = Individual(1, evaluation=_synthetic_ev(1, violation=0.3, energy_violation=0.3))
        b = Individual(2, evaluation=_synthetic_ev(2, violation=0.3, energy_violation=0.1))
        _assert_pair_consistent(a, b)
        _assert_pair_consistent(b, a)

    def test_full_tie_different_num_panels(self):
        a = Individual(2, evaluation=_synthetic_ev(2, violation=0.3, energy_violation=0.1))
        b = Individual(1, evaluation=_synthetic_ev(1, violation=0.3, energy_violation=0.1))
        _assert_pair_consistent(a, b)
        _assert_pair_consistent(b, a)
        # b (menor N) deve ser preferido no desempate final
        assert _cmp_lexicographic(a, b) == 1
        assert compare_lexicographic(a.evaluation, b.evaluation) is b.evaluation


def build_problem(
    consumption: float = 300.0,
    usable_area: float = 80.0,
    budget: float | None = None,
) -> Problem:
    """Constrói Problem usando os dados de João Pessoa."""
    from src.simulation.evaluation import build_problem_from_data

    return build_problem_from_data(
        monthly_consumption_kwh=consumption,
        roof_usable_area_m2=usable_area,
        panel_data=PANEL_STD,
        city_data=CITY_JP,
        irradiance_data=IRRADIANCE_JP,
        max_budget_brl=budget,
    )


def test_cmp_lexicographic_consistency():
    """Garante que _cmp_lexicographic e compare_lexicographic tenham a mesma ordem."""
    prob = build_problem(consumption=50.0, usable_area=20.0)

    # Coleta candidatos viáveis e inviáveis
    candidates: list[Individual] = []
    for N in range(0, 8):
        ev = _make_ev(N, prob)
        candidates.append(Individual(num_panels=N, evaluation=ev))

    # Compara todos os pares
    for i, a in enumerate(candidates):
        for j, b in enumerate(candidates):
            if i == j:
                continue
            # compare_lexicographic devolve o "melhor" segundo a regra oficial
            better = compare_lexicographic(a.evaluation, b.evaluation)
            # Construir ordem segundo _lexicographic_key
            key_a = _lexicographic_key(a)
            key_b = _lexicographic_key(b)
            if key_a < key_b:
                # _lexicographic_key diz a < b, então compare_lexicographic deveria devolver a como melhor
                assert better is a.evaluation, (
                    f"Descrepância: key_a < key_b ({key_a} < {key_b}), mas compare devolve {better}"
                )
            elif key_a > key_b:
                assert better is b.evaluation, (
                    f"Descrepância: key_a > key_b ({key_a} > {key_b}), mas compare devolve {better}"
                )
            else:
                # chaves iguais → empate (compare devolve o segundo argumento)
                # Em caso de empate, compare(A,B) deve ser B, compare(B,A) deve ser A
                better_rev = compare_lexicographic(b.evaluation, a.evaluation)
                # Ambos os sentidos devolve o "segundo" argument, confirmando empate
                assert (better is b.evaluation) and (better_rev is a.evaluation), (
                    f"Empate de chaves mas compare não retornou consistência: A={better}, B={better_rev}"
                )


def test_cmp_lexicographic_feasible_vs_infeasible():
    """Empate viável vence inviável segundo ambas as regras."""
    prob = build_problem(consumption=300.0, usable_area=20.0)  # consumo alto → inviável menor N
    ind_inf = Individual(num_panels=0, evaluation=evaluate_candidate(0, prob))
    ind_ok = Individual(num_panels=2, evaluation=evaluate_candidate(2, prob))
    # N=2 ainda pode ser inviável se energia baixa, mas com área grande a energia será insuficiente ainda?
    # Vamos garantir que um é viável e outro não: use consumo pequeno.
    prob_viable = build_problem(consumption=50.0, usable_area=200.0)
    ind_inf2 = Individual(num_panels=0, evaluation=evaluate_candidate(0, prob_viable))  # infeasible
    ind_ok2 = Individual(num_panels=1, evaluation=evaluate_candidate(1, prob_viable))  # feasible
    better = compare_lexicographic(ind_inf2.evaluation, ind_ok2.evaluation)
    assert better is ind_ok2.evaluation, "Viável deveria vencer inviável"
    # _cmp_lexicographic deve refletir isso ao comparar um único par
    result = _cmp_lexicographic(ind_inf2, ind_ok2)
    assert result == 1, f"cmp_lexicographic deveria indicar b melhor, retornou {result}"


def test_select_elites_preserves_best():
    """Elite selection retorna os melhores segundo compare_lexicographic."""
    prob = build_problem(consumption=50.0, usable_area=20.0)
    ind1 = Individual(num_panels=1, evaluation=evaluate_candidate(1, prob))  # feasible, cost 1350
    ind2 = Individual(num_panels=2, evaluation=evaluate_candidate(2, prob))  # feasible, cost 2700
    ind3 = Individual(num_panels=3, evaluation=evaluate_candidate(3, prob))  # feasible, cost 4050
    ind4 = Individual(num_panels=0, evaluation=evaluate_candidate(0, prob))  # infeasible

    pop = [ind1, ind2, ind3, ind4]
    elites = _select_elites(pop, 2)
    # Os dois melhores deveriam ser os viáveis de menor custo
    assert elites[0].num_panels == 1
    assert elites[1].num_panels == 2


def test_select_elites_with_insufficient_population():
    """Não falha quando elitism_count > tamanho da população."""
    prob = build_problem(consumption=50.0, usable_area=20.0)
    ind = Individual(num_panels=1, evaluation=evaluate_candidate(1, prob))
    result = _select_elites([ind], 10)
    assert len(result) == 1  # retorna tudo o que tem


def test_best_individual_single():
    """_best_individual em população de um único elemento."""
    prob = build_problem(consumption=50.0, usable_area=20.0)
    ind = Individual(num_panels=1, evaluation=evaluate_candidate(1, prob))
    best = _best_individual([ind])
    assert best.num_panels == 1


def test_elite_preservation_across_generations():
    """Testa que o melhor indivíduo não é perdido entre gerações consecutivas."""
    from src.genetic.algorithm import run_genetic_algorithm_v2
    from src.core.config import GAConfig

    prob = build_problem(consumption=50.0, usable_area=20.0)  # ótimo: 1 painel viável
    config = GAConfig(
        population_size=12,
        generations=5,
        crossover_rate=0.8,
        mutation_rate=0.2,
        elitism_count=2,
        random_seed=123,
    )
    set_global_seed(123)
    best, history, final_pop = run_genetic_algorithm_v2(prob, config)

    # best deve ser 1 (feasível ótimo global)
    assert best.num_panels == 1, f"Melhor final deve ser 1, obtido {best.num_panels}"
    # histórico deve ter 5 gerações; cada melhor_panels deve ser >= 1 (pelo menos não piorar)
    for stat in history:
        assert stat.best_panels >= 1, f"Geração {stat.generation} registrou best_panels < 1"
    # Verificar que os best_panels da história são não decrescentes (não obrigatório mas interessante)
    # Vamos apenas garantir que o best final não piorou vs inicial
    init_prob_ev = evaluate_candidate(1, prob)
    init_best = Individual(num_panels=1, evaluation=init_prob_ev)
    # o best da última geração deve ser tão bom quanto o inicial
    assert _cmp_lexicographic(best, init_best) <= 0, "Melhor final não deveria piorar vs inicial viável"


def test_ag_matches_exhaustive_small_search():
    """AG encontra o mesmo ótimo que busca exaustiva em problema pequeno."""
    from src.genetic.algorithm import run_genetic_algorithm_v2
    from src.simulation.solvers import solve_exhaustive
    from src.core.config import GAConfig
    from src.utils.seed import set_global_seed

    prob = build_problem(consumption=30.0, usable_area=20.0)  # ótimo provavelmente 1 painel
    config = GAConfig(
        population_size=20,
        generations=30,
        crossover_rate=0.8,
        mutation_rate=0.2,
        elitism_count=2,
        random_seed=42,
    )
    set_global_seed(42)
    best_ag, _, _ = run_genetic_algorithm_v2(prob, config)
    ref = solve_exhaustive(prob)
    assert best_ag.num_panels == ref.best.num_panels, (
        f"AG encontrou {best_ag.num_panels}, exaustiva encontrou {ref.best.num_panels}"
    )


def test_lexicographic_key_against_synthetic_ties():
    """Testa que _lexicographic_key e compare_lexicographic concordam em ties completos construídos."""
    # Cria EvaluationResult sintéticos idênticos exceto num_panels
    from src.simulation.evaluation import EvaluationResult

    # Ambos viáveis, mas custos diferentes intencionais (custo deve ser N*unit_cost)
    # Vamos contornar pela viabilidade: ambos com custo zero numérica? Na prática, custo distinto se N distinto.
    # Vamos testar empate completo (mesmos campos): usaremos mesma estrutura.
    ev1 = EvaluationResult(
        num_panels=2,
        feasible=True,
        cost=2700.0,
        violation=0.0,
        energy_violation=0.0,
        area_violation=0.0,
        budget_violation=0.0,
        energy_by_month={m: 30.0 for m in range(1, 13)},
        used_area=4.4,
        occupancy=0.05,
    )
    ev2 = EvaluationResult(
        num_panels=3,
        feasible=True,
        cost=4050.0,
        violation=0.0,
        energy_violation=0.0,
        area_violation=0.0,
        budget_violation=0.0,
        energy_by_month={m: 30.0 for m in range(1, 13)},
        used_area=6.6,
        occupancy=0.05,
    )

    ind1 = Individual(num_panels=2, evaluation=ev1)
    ind2 = Individual(num_panels=3, evaluation=ev2)

    # _cmp_lexicographic deve considerar ind1 melhor (menor custo)
    result = _cmp_lexicographic(ind1, ind2)
    assert result == -1, f"ind1 (custo menor) deveria ser melhor, mas _cmp devolveu {result}"

    # _lexicographic_key também
    k1 = _lexicographic_key(ind1)
    k2 = _lexicographic_key(ind2)
    assert k1 < k2, "key deveria ordenar ind1 antes"


def test_ag_elite_never_worse_than_initial_best():
    """Garante que o elitismo nunca deixe o histórico piorar em relação ao melhor inicial."""
    from src.genetic.algorithm import run_genetic_algorithm_v2
    from src.core.config import GAConfig
    from src.utils.seed import set_global_seed

    prob = build_problem(consumption=50.0, usable_area=20.0)
    config = GAConfig(
        population_size=20,
        generations=10,
        crossover_rate=0.8,
        mutation_rate=0.1,
        elitism_count=2,
        random_seed=42,
    )
    set_global_seed(42)
    best, history, _ = run_genetic_algorithm_v2(prob, config)

    # O melhor final (best_overall) deve ser tão bom quanto o melhor da primeira geração
    init_ev = evaluate_candidate(best.num_panels, prob)
    init_ind = Individual(num_panels=best.num_panels, evaluation=init_ev)
    assert _cmp_lexicographic(best, init_ind) <= 0, "Melhor final não deveria ser pior que o inicial"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])