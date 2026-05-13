
import json
from pathlib import Path

from genetic.algorithm import GeneticAlgorithm


class SimulationRunner:

    def __init__(self, scenario_name, scenario_data):

        self.scenario_name = scenario_name
        self.scenario_data = scenario_data

    def run(self):

        ga = GeneticAlgorithm(
            consumption=self.scenario_data["consumo"],
            irradiation=self.scenario_data["irradiacao"]
        )

        best = ga.execute()

        result = {
            "scenario": self.scenario_name,
            "consumption": self.scenario_data["consumo"],
            "irradiation": self.scenario_data["irradiacao"],
            "best_panels": best.number_of_panels,
            "fitness": round(best.fitness, 2)
        }

        output_path = Path("results")
        output_path.mkdir(exist_ok=True)

        with open(
            output_path / f"{self.scenario_name}.json",
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(result, file, indent=4)

        return ga, result
