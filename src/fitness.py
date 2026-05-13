
def fitness(n_paineis, consumo, irradiacao):
    energia_por_painel = irradiacao * 30
    energia_total = n_paineis * energia_por_painel

    custo_por_painel = 1200
    custo_total = n_paineis * custo_por_painel

    desperdicio = max(0, energia_total - consumo) * 0.5

    score = energia_total - (custo_total / 100) - desperdicio

    return score
