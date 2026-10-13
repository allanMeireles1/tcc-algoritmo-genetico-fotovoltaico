"""Tests for the storage/export helpers and the results dict shape."""

import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.models.result import OptimizationOutcome, ScenarioRunResult
from src.storage.exporter import create_run_dir, export_csv, export_json
from src.simulation.runner import results_to_rows


def _sample_result() -> ScenarioRunResult:
    return ScenarioRunResult(
        execution_label="x",
        city="João Pessoa",
        best_num_panels=4,
        best_fitness=-151.38,
        best_energy_kwh_month=292.25,
        best_cost_brl=5400.0,
        monthly_consumption_kwh=300.0,
        roof_area_m2=80.0,
        roof_usable_area_m2=68.0,
        roof_occupancy_ratio=0.129,
        panel_area_m2=2.2,
        energy_surplus_kwh=0.0,
        energy_deficit_kwh=7.75,
        benchmark_panels=5,
        benchmark_fitness=-233.47,
        benchmark_energy_kwh_month=365.31,
        benchmark_cost_brl=6750.0,
        budget_limit_brl=None,
        under_budget=True,
        execution_time_s=0.05,
        generations=120,
        run_seed=42,
    )


def test_export_json_roundtrip(tmp_path):
    out = _sample_result()
    path = tmp_path / "result.json"
    export_json(path, out)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["best_num_panels"] == 4
    assert data["city"] == "João Pessoa"


def test_export_csv_writes_file(tmp_path):
    out = _sample_result()
    path = tmp_path / "summary.csv"
    export_csv(path, results_to_rows([out]))
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "best_num_panels" in content


def test_create_run_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run_dir = create_run_dir()
    assert run_dir.exists()
    assert run_dir.name.startswith("run_")


def test_results_to_rows_shape():
    out = _sample_result()
    rows = results_to_rows([out])
    assert isinstance(rows, list)
    assert len(rows) == 1
    assert rows[0]["best_num_panels"] == 4
    assert "execution_label" in rows[0]


def test_optimization_outcome_fields():
    out = _sample_result()
    outcome = OptimizationOutcome(
        result=out,
        history=[],
        summary={"runs": 1},
        final_population=[],
        fitness_breakdown=None,
    )
    assert outcome.result.best_num_panels == 4
    assert outcome.summary == {"runs": 1}
