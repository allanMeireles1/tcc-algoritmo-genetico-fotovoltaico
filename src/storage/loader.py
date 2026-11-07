"""Carregamento de dados mockados."""

import json
from pathlib import Path
from typing import Any

from src.utils.validators import validate_scenario


def load_json(path: str | Path) -> Any:
    """Lê e retorna o conteúdo de um arquivo JSON."""
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def load_scenarios(path: str | Path = "data/scenarios_mock.json") -> list[dict[str, Any]]:
    """Carrega e valida cenários de consumo."""
    scenarios = load_json(path)
    for scenario in scenarios:
        validate_scenario(scenario)
    return scenarios


def load_cities(path: str | Path = "data/cities_mock.json") -> list[dict[str, Any]]:
    """Carrega cidades e irradiância média aproximada."""
    return list(load_json(path))


def load_panels(path: str | Path = "data/panels_mock.json") -> list[dict[str, Any]]:
    """Carrega catálogo mockado de painéis."""
    return list(load_json(path))


def load_irradiance(path: str | Path = "data/irradiance_mock.json") -> dict[str, Any]:
    """Carrega dados de irradiância mensal (apenas João Pessoa no mock)."""
    return load_json(path)
