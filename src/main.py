
import random

from core.config import RANDOM_SEED
from data.scenarios import SCENARIOS

from simulation.runner import SimulationRunner
from visualization.plotter import plot_convergence
from utils.logger import print_header


def main():

    random.seed(RANDOM_SEED)

    print_header(
        "Sistema de Otimização Fotovoltaica"
    )

    for scenario_name, scenario_data in SCENARIOS.items():

        print_header(
            f"CENÁRIO: {scenario_name.upper()}"
        )

        runner = SimulationRunner(
            scenario_name,
            scenario_data
        )

        ga, result = runner.run()

        print(f"Consumo: {result['consumption']} kWh")
        print(f"Irradiação: {result['irradiation']}")
        print(f"Melhor número de painéis: {result['best_panels']}")
        print(f"Fitness final: {result['fitness']}")

        plot_convergence(
            ga.history,
            f"Convergência - {scenario_name}"
        )


if __name__ == "__main__":
    main()
