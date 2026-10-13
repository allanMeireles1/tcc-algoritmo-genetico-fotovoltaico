"""Thin service layer that wraps the existing ``src`` package and returns
DTOs defined in ``schemas``.  This keeps the API routes thin and allows
reuse of the same adapters from other contexts (scripts, tests, etc)."""

from __future__ import annotations

from dataclasses import asdict
from typing import List, Optional

from fastapi import HTTPException

from src.core.config import GAConfig
from src.models.roof import RoofInput
from src.models.result import (
    ScenarioRunResult,
    GenerationStats,
    OptimizationOutcome,
    SensitivityPoint,
    TimingPoint,
)
from src.storage.loader import load_cities, load_panels
from src.simulation.runner import run_optimization, build_problem
from src.simulation.baseline import evaluate_direct_baseline
from src.simulation.experiments import (
    run_consumption_sensitivity,
    run_population_timing_experiment,
    run_generations_timing_experiment,
)

from backend.schemas import (
    OptimizeRequest,
    BaselineRequest,
    SensitivityRequest,
    PopulationTimingRequest,
    GenerationsTimingRequest,
    GenerationStatsDTO,
    ScenarioRunResultDTO,
    OptimizationOutcomeDTO,
    FitnessBreakdownDTO,
    SensitivityPointDTO,
    TimingPointDTO,
    BaselineResponse,
)


# ----------------------------------------------------------------- city / panel helpers
_cities: Optional[list] = None
_panels: Optional[list] = None


def _ensure_loaded():
    global _cities, _panels
    if _cities is None:
        _cities = load_cities()
        _panels = load_panels()


def city_lookup(city_name: str) -> dict:
    _ensure_loaded()
    # Normalize: strip trailing " (XX)" suffix added by _list_cities()
    # so both "João Pessoa" and "João Pessoa (PB)" are accepted.
    normalized = city_name.split(" (")[0] if " (" in city_name else city_name
    for c in _cities:
        if c["city"] == normalized:
            return c
    raise HTTPException(status_code=404, detail=f"Cidade '{city_name}' não encontrada")


def panel_default() -> dict:
    _ensure_loaded()
    if not _panels:
        raise HTTPException(status_code=500, detail="Nenhum painel configurado")
    return _panels[0]


def _list_cities() -> List[str]:
    _ensure_loaded()
    return [f"{c['city']} ({c.get('state', '')})".strip() for c in _cities]


def _list_panels() -> List[dict]:
    _ensure_loaded()
    return list(_panels)


# ------------------------------------------------------------------ optimize
def optimize_adapter(req: OptimizeRequest) -> OptimizationOutcomeDTO:
    city_data = city_lookup(req.roof.city)
    panel_data = panel_default()
    ga_cfg: GAConfig = req.config.to_ga_config()
    outcome: OptimizationOutcome = run_optimization(
        roof=req.roof.to_roof_input(),
        city_data=city_data,
        panel_data=panel_data,
        config=ga_cfg,
        runs=req.runs,
    )
    # Map dataclass -> DTO
    return _outcome_to_dto(outcome)


def _outcome_to_dto(m: OptimizationOutcome) -> OptimizationOutcomeDTO:
    # NB: src dataclasses use slots=True, so __dict__ is unavailable -> asdict().
    return OptimizationOutcomeDTO(
        result=ScenarioRunResultDTO.model_validate(asdict(m.result)),
        history=[GenerationStatsDTO.model_validate(asdict(h)) for h in m.history],
        summary=m.summary,
        final_population=[asdict(ind) for ind in m.final_population],
        fitness_breakdown=(
            FitnessBreakdownDTO.model_validate(asdict(m.fitness_breakdown))
            if m.fitness_breakdown
            else None
        ),
    )


# ------------------------------------------------------------------ baseline
def baseline_adapter(req: BaselineRequest) -> BaselineResponse:
    city_data = city_lookup(req.roof.city)
    panel_data = panel_default()
    problem = build_problem(req.roof.to_roof_input(), city_data, panel_data)
    panels, fitness, energy, cost = evaluate_direct_baseline(problem, GAConfig())
    return {"panels": panels, "fitness": fitness, "energy_kwh_month": energy, "cost_brl": cost}


# ------------------------------------------------------------------ sensitivity
def sensitivity_adapter(req: SensitivityRequest) -> List[SensitivityPointDTO]:
    city_data = city_lookup(req.roof.city)
    panel_data = panel_default()
    points = run_consumption_sensitivity(
        roof=req.roof.to_roof_input(),
        city_data=city_data,
        panel_data=panel_data,
        config=req.config.to_ga_config(),
        consumption_levels=req.consumption_levels,
    )
    return [SensitivityPointDTO.model_validate(asdict(p)) for p in points]


# ------------------------------------------------------------------ population timing
def pop_timing_adapter(req: PopulationTimingRequest) -> List[TimingPointDTO]:
    city_data = city_lookup(req.roof.city)
    panel_data = panel_default()
    points = run_population_timing_experiment(
        roof=req.roof.to_roof_input(),
        city_data=city_data,
        panel_data=panel_data,
        base_config=req.config.to_ga_config(),
        population_sizes=req.population_sizes,
    )
    return [TimingPointDTO.model_validate(asdict(p)) for p in points]


# ------------------------------------------------------------------ generations timing
def gen_timing_adapter(req: GenerationsTimingRequest) -> List[TimingPointDTO]:
    city_data = city_lookup(req.roof.city)
    panel_data = panel_default()
    points = run_generations_timing_experiment(
        roof=req.roof.to_roof_input(),
        city_data=city_data,
        panel_data=panel_data,
        base_config=req.config.to_ga_config(),
        generation_counts=req.generation_counts,
    )
    return [TimingPointDTO.model_validate(asdict(p)) for p in points]
