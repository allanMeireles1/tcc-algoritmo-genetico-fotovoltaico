
def calculate_fitness(
    number_of_panels: int,
    consumption: float,
    irradiation: float
) -> float:

    energy_per_panel = irradiation * 35
    generated_energy = number_of_panels * energy_per_panel

    panel_cost = 1200
    total_cost = number_of_panels * panel_cost

    unmet_energy_penalty = max(
        0,
        consumption - generated_energy
    ) * 0.8

    excess_energy_penalty = max(
        0,
        generated_energy - consumption
    ) * 0.3

    score = (
        generated_energy
        - (total_cost / 100)
        - unmet_energy_penalty
        - excess_energy_penalty
    )

    return score
