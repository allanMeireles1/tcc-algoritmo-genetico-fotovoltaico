
import random

def gerar_populacao(tamanho, minimo=1, maximo=20):
    return [
        random.randint(minimo, maximo)
        for _ in range(tamanho)
    ]

def crossover(pai1, pai2):
    return (pai1 + pai2) // 2

def mutacao(individuo, taxa=0.3):

    if random.random() < taxa:
        individuo += random.choice([-1, 1])

    individuo = max(1, individuo)
    individuo = min(20, individuo)

    return individuo
