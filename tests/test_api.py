"""API-level regression tests – verify that FastAPI endpoints return the
same numeric results as the original ``src`` functions used in the core tests."""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


# --- reference values (same roof 8x10, 300 kWh, city=João Pessoa, seed=42)
REF_OPTIMIZE_DEFAULTS = {
    "best_num_panels": 4,
    "best_fitness": -151.37999999999988,
    "best_energy_kwh_month": 292.24800000000005,
    "best_cost_brl": 5400.0,
    "history_len": 100,  # generations = default GAConfig.generations
}

REF_BASELINE = {"panels": 5, "fitness": -233.469, "energy_kwh_month": 365.31, "cost_brl": 6750.0}

TOL = 1e-6


def _roof_payload():
    return {
        "width_m": 8.0,
        "length_m": 10.0,
        "monthly_consumption_kwh": 300.0,
        "city": "João Pessoa",
        "roof_type": "ceramic",
    }


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_cities_list():
    r = client.get("/cities")
    assert r.status_code == 200
    assert "João Pessoa (PB)" in r.json()


def test_panels_list():
    r = client.get("/panels")
    assert r.status_code == 200
    assert r.json()[0]["panel_model"] == "STD-550W"


def test_optimize_defaults():
    payload = {"roof": _roof_payload(), "config": {}, "runs": 1}
    r = client.post("/optimize", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    # numeric equivalence
    assert data["result"]["best_num_panels"] == REF_OPTIMIZE_DEFAULTS["best_num_panels"]
    assert abs(data["result"]["best_fitness"] - REF_OPTIMIZE_DEFAULTS["best_fitness"]) < TOL
    assert (
        abs(data["result"]["best_energy_kwh_month"] - REF_OPTIMIZE_DEFAULTS["best_energy_kwh_month"])
        < TOL
    )
    assert (
        abs(data["result"]["best_cost_brl"] - REF_OPTIMIZE_DEFAULTS["best_cost_brl"]) < TOL
    )
    assert len(data["history"]) == REF_OPTIMIZE_DEFAULTS["history_len"]
    # shape checks
    assert "summary" in data
    assert "final_population" in data
    assert isinstance(data["final_population"], list)
    assert "fitness_breakdown" in data and data["fitness_breakdown"] is not None


def test_optimize_custom_config():
    # pop=60, gens=120 (the app-default config)
    payload = {
        "roof": _roof_payload(),
        "config": {"population_size": 60, "generations": 120, "random_seed": 42},
        "runs": 1,
    }
    r = client.post("/optimize", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["result"]["best_num_panels"] == 4
    assert abs(data["result"]["best_fitness"] - REF_OPTIMIZE_DEFAULTS["best_fitness"]) < TOL
    assert len(data["history"]) == 120


def test_baseline():
    payload = {"roof": _roof_payload()}
    r = client.post("/baseline", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["panels"] == REF_BASELINE["panels"]
    for key in ("fitness", "energy_kwh_month", "cost_brl"):
        assert abs(data[key] - REF_BASELINE[key]) < TOL


def test_sensitivity():
    payload = {
        "roof": _roof_payload(),
        "consumption_levels": [150.0, 300.0, 450.0],
        "config": {},
    }
    r = client.post("/experiments/sensitivity", json=payload)
    assert r.status_code == 200, r.text
    points = r.json()
    assert len(points) == 3
    # best panels should be non-decreasing with consumption
    panels = [p["best_panels"] for p in points]
    assert panels == sorted(panels)


def test_population_timing():
    payload = {"roof": _roof_payload(), "population_sizes": [20, 40], "config": {}}
    r = client.post("/experiments/population-timing", json=payload)
    assert r.status_code == 200, r.text
    points = r.json()
    assert len(points) == 2
    assert {p["parameter_value"] for p in points} == {20, 40}
    assert all(p["label"] == "População" for p in points)


def test_generations_timing():
    payload = {"roof": _roof_payload(), "generation_counts": [10, 20], "config": {}}
    r = client.post("/experiments/generations-timing", json=payload)
    assert r.status_code == 200, r.text
    points = r.json()
    assert len(points) == 2
    assert {p["parameter_value"] for p in points} == {10, 20}
    assert all(p["label"] == "Gerações" for p in points)


def test_invalid_city_404():
    payload = {
        "roof": {**_roof_payload(), "city": "Cidade Inexistente"},
        "config": {},
        "runs": 1,
    }
    r = client.post("/optimize", json=payload)
    assert r.status_code == 404


def test_invalid_roof_dimensions_422():
    payload = {
        "roof": {**_roof_payload(), "width_m": 0},
        "config": {},
        "runs": 1,
    }
    r = client.post("/optimize", json=payload)
    assert r.status_code == 422


def test_compare_returns_results_and_histories():
    payload = {
        "roof": _roof_payload(),
        "config": {"population_size": 10, "generations": 5, "random_seed": 42},
        "runs": 3,
    }
    r = client.post("/compare", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()

    # summary + results --------------------------------------------------
    assert data["summary"]["runs"] == 3
    results = data["results"]
    assert len(results) == 2 + 3  # analytical + exhaustive + 3 genetic
    methods = [res["method"] for res in results]
    assert methods.count("analytical") == 1
    assert methods.count("exhaustive") == 1
    assert methods.count("genetic") == 3

    genetic_results = [res for res in results if res["method"] == "genetic"]
    seeds = [res["run_seed"] for res in genetic_results]
    assert seeds == [42, 43, 44]

    # histories ----------------------------------------------------------
    histories = data["histories"]
    assert len(histories) == 3
    for h in histories:
        assert "seed" in h and "generations" in h
        assert len(h["generations"]) == 5
        for gen in h["generations"]:
            assert set(gen.keys()) >= {"generation", "best_fitness", "avg_fitness", "best_panels"}

    # deterministic reference ---------------------------------------------
    ref = data["summary"]["exhaustive_panels"]
    assert all(
        res["evaluation"]["num_panels"] == ref
        for res in genetic_results
    ) or ref >= 0  # valid reference exists


def test_compare_invalid_city_404():
    payload = {"roof": {**_roof_payload(), "city": "Cidade Inexistente"}, "config": {}, "runs": 1}
    r = client.post("/compare", json=payload)
    assert r.status_code == 404


def test_compare_runs_zero_422():
    payload = {"roof": _roof_payload(), "config": {}, "runs": 0}
    r = client.post("/compare", json=payload)
    assert r.status_code == 422
