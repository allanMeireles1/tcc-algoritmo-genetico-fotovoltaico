"""Helpers de exibição para o dashboard Streamlit."""

from src.models.result import ScenarioRunResult


def explain_solution(result: ScenarioRunResult) -> str:
    """Texto explicativo didático para apresentação em banca."""
    return (
        f"O AG escolheu {result.best_num_panels} painéis para a residência em {result.city} "
        f"porque essa configuração maximizou o fitness final ({result.best_fitness:.2f}), "
        f"equilibrando energia estimada ({result.best_energy_kwh_month:.2f} kWh/mês), "
        f"custo total (R$ {result.best_cost_brl:,.2f}) e penalidades de déficit/sobras. "
        f"Área útil ocupada: {result.roof_occupancy_ratio * 100:.1f}%."
    )
