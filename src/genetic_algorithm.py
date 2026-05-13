
from fitness import fitness
from utils import gerar_populacao, crossover, mutacao


class GeneticAlgorithm:

    def __init__(
        self,
        consumo,
        irradiacao,
        tamanho_populacao=10,
        geracoes=30
    ):

        self.consumo = consumo
        self.irradiacao = irradiacao
        self.tamanho_populacao = tamanho_populacao
        self.geracoes = geracoes
        self.historico = []

    def selecionar(self, populacao):

        populacao_ordenada = sorted(
            populacao,
            key=lambda x: fitness(
                x,
                self.consumo,
                self.irradiacao
            ),
            reverse=True
        )

        return populacao_ordenada[:2]

    def executar(self):

        populacao = gerar_populacao(
            self.tamanho_populacao
        )

        for _ in range(self.geracoes):

            melhores = self.selecionar(populacao)

            melhor_score = fitness(
                melhores[0],
                self.consumo,
                self.irradiacao
            )

            self.historico.append(melhor_score)

            nova_populacao = melhores.copy()

            while len(nova_populacao) < self.tamanho_populacao:

                filho = crossover(
                    melhores[0],
                    melhores[1]
                )

                filho = mutacao(filho)

                nova_populacao.append(filho)

            populacao = nova_populacao

        melhor = max(
            populacao,
            key=lambda x: fitness(
                x,
                self.consumo,
                self.irradiacao
            )
        )

        return melhor
