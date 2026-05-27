"""Validações básicas dos dados de entrada."""

from typing import Any

from src.models.roof import RoofInput


REQUIRED_SCENARIO_FIELDS = {
    "scenario_name",
    "city",
    "monthly_consumption_kwh",
    "irradiance_kwh_m2_day",
    "panel_power_wp",
    "panel_cost_brl",
    "roof_area_m2",
    "system_efficiency",
}


def validate_scenario(scenario: dict[str, Any]) -> None:
    """Valida presença de campos obrigatórios e valores mínimos."""
    missing = REQUIRED_SCENARIO_FIELDS.difference(scenario.keys())
    if missing:
        raise ValueError(f"Cenário inválido. Campos ausentes: {sorted(missing)}")

    if scenario["monthly_consumption_kwh"] <= 0:
        raise ValueError("monthly_consumption_kwh deve ser maior que zero.")
    if scenario["panel_power_wp"] <= 0:
        raise ValueError("panel_power_wp deve ser maior que zero.")
    if scenario["panel_cost_brl"] <= 0:
        raise ValueError("panel_cost_brl deve ser maior que zero.")
    if not (0 < scenario["system_efficiency"] <= 1):
        raise ValueError("system_efficiency deve estar no intervalo (0, 1].")


def validate_roof_input(roof: RoofInput) -> None:
    """Valida valores informados pelo usuário na interface."""
    if roof.width_m <= 0 or roof.length_m <= 0:
        raise ValueError("Largura e comprimento do telhado devem ser maiores que zero.")
    if roof.monthly_consumption_kwh <= 0:
        raise ValueError("Consumo mensal deve ser maior que zero.")
    if roof.max_budget_brl is not None and roof.max_budget_brl <= 0:
        raise ValueError("Orçamento máximo deve ser maior que zero quando informado.")
