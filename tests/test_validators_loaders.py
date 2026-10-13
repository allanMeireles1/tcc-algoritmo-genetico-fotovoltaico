"""Tests for input validation and scenario/panel loaders."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from src.models.roof import RoofInput
from src.storage.loader import load_cities, load_panels, load_scenarios
from src.utils.validators import validate_roof_input, validate_scenario


def test_valid_roof_input():
    roof = RoofInput(8.0, 10.0, 300.0, "João Pessoa", "ceramic", None)
    validate_roof_input(roof)  # must not raise


@pytest.mark.parametrize(
    "width,length,consumption,budget,match",
    [
        (0.0, 10.0, 300.0, None, "zero"),
        (8.0, -1.0, 300.0, None, "zero"),
        (8.0, 10.0, 0.0, None, "Consumo"),
        (8.0, 10.0, 300.0, -100.0, "Orçamento"),
    ],
)
def test_invalid_roof_input(width, length, consumption, budget, match):
    roof = RoofInput(width, length, consumption, "João Pessoa", "ceramic", budget)
    with pytest.raises(ValueError, match=match):
        validate_roof_input(roof)


def test_valid_scenario():
    scenario = {
        "scenario_name": "low",
        "city": "João Pessoa",
        "monthly_consumption_kwh": 150.0,
        "irradiance_kwh_m2_day": 5.4,
        "panel_power_wp": 550.0,
        "panel_cost_brl": 1100.0,
        "roof_area_m2": 30.0,
        "system_efficiency": 0.82,
    }
    validate_scenario(scenario)  # must not raise


def test_scenario_missing_fields():
    with pytest.raises(ValueError, match="Campos ausentes"):
        validate_scenario({"scenario_name": "low"})


def test_scenario_negative_consumption():
    scenario = {
        "scenario_name": "low",
        "city": "João Pessoa",
        "monthly_consumption_kwh": -1.0,
        "irradiance_kwh_m2_day": 5.4,
        "panel_power_wp": 550.0,
        "panel_cost_brl": 1100.0,
        "roof_area_m2": 30.0,
        "system_efficiency": 0.82,
    }
    with pytest.raises(ValueError, match="maior que zero"):
        validate_scenario(scenario)


def test_scenario_efficiency_out_of_range():
    base = {
        "scenario_name": "low",
        "city": "João Pessoa",
        "monthly_consumption_kwh": 150.0,
        "irradiance_kwh_m2_day": 5.4,
        "panel_power_wp": 550.0,
        "panel_cost_brl": 1100.0,
        "roof_area_m2": 30.0,
        "system_efficiency": 0.82,
    }
    bad = dict(base, system_efficiency=1.5)
    with pytest.raises(ValueError, match="system_efficiency"):
        validate_scenario(bad)


def test_loaders_return_expected_keys():
    cities = load_cities()
    assert all("city" in c and "irradiance_kwh_m2_day" in c for c in cities)
    panels = load_panels()
    assert all("panel_power_wp" in p and "panel_cost_brl" in p for p in panels)
    scenarios = load_scenarios()
    assert all("scenario_name" in s for s in scenarios)


def test_roof_usable_area_factor():
    roof = RoofInput(10.0, 10.0, 300.0, "João Pessoa")
    assert roof.gross_area_m2 == 100.0
    assert roof.usable_area_m2() == pytest.approx(85.0)
