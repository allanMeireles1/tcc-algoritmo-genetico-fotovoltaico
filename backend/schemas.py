"""Pydantic v2 models — request/response contracts for the API.

Mirrors ``src.core.config.GAConfig`` and ``src.models.roof.RoofInput`` on the
input side, and the ``src.models.result`` dataclasses on the output side.
No business logic here, only shape + validation.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from src.core.config import GAConfig
from src.models.roof import RoofInput


# ------------------------------------------------------------------ inputs
class GAConfigDTO(BaseModel):
    population_size: int = Field(default=50, ge=1, le=500)
    generations: int = Field(default=100, ge=1, le=1000)
    crossover_rate: float = Field(default=0.8, ge=0, le=1)
    mutation_rate: float = Field(default=0.1, ge=0, le=1)
    elitism_count: int = Field(default=2, ge=0, le=50)
    random_seed: int = Field(default=42, ge=0)
    cost_weight_alpha: float = Field(default=0.08, ge=0)
    waste_penalty_weight: float = Field(default=0.9, ge=0)
    deficit_penalty_weight: float = Field(default=1.5, ge=0)
    budget_penalty_weight: float = Field(default=2.0, ge=0)

    def to_ga_config(self) -> GAConfig:
        return GAConfig(**self.model_dump())


class RoofDTO(BaseModel):
    width_m: float = Field(..., gt=0)
    length_m: float = Field(..., gt=0)
    monthly_consumption_kwh: float = Field(..., gt=0)
    city: str = Field(..., min_length=1)
    roof_type: str = Field(default="ceramic")
    max_budget_brl: Optional[float] = Field(default=None, gt=0)

    def to_roof_input(self) -> RoofInput:
        return RoofInput(
            width_m=self.width_m,
            length_m=self.length_m,
            monthly_consumption_kwh=self.monthly_consumption_kwh,
            city=self.city,
            roof_type=self.roof_type,
            max_budget_brl=self.max_budget_brl,
        )


# composite request bodies (so GA config is not a query-param)
class OptimizeRequest(BaseModel):
    roof: RoofDTO
    config: GAConfigDTO = Field(default_factory=GAConfigDTO)
    runs: int = Field(default=1, ge=1, le=20)


class BaselineRequest(BaseModel):
    roof: RoofDTO


class ComparisonRequest(BaseModel):
    roof: RoofDTO
    config: GAConfigDTO = Field(default_factory=GAConfigDTO)
    runs: int = Field(default=1, ge=1, le=100)


class SensitivityRequest(BaseModel):
    roof: RoofDTO
    consumption_levels: List[float] = Field(..., min_length=1)
    config: GAConfigDTO = Field(default_factory=GAConfigDTO)


class PopulationTimingRequest(BaseModel):
    roof: RoofDTO
    population_sizes: List[int] = Field(..., min_length=1)
    config: GAConfigDTO = Field(default_factory=GAConfigDTO)


class GenerationsTimingRequest(BaseModel):
    roof: RoofDTO
    generation_counts: List[int] = Field(..., min_length=1)
    config: GAConfigDTO = Field(default_factory=GAConfigDTO)


# ----------------------------------------------------------------- outputs
class GenerationStatsDTO(BaseModel):
    generation: int
    best_fitness: float
    avg_fitness: float
    best_panels: int


class ScenarioRunResultDTO(BaseModel):
    execution_label: str
    city: str
    best_num_panels: int
    best_fitness: float
    best_energy_kwh_month: float
    best_cost_brl: float
    monthly_consumption_kwh: float
    roof_area_m2: float
    roof_usable_area_m2: float
    roof_occupancy_ratio: float
    panel_area_m2: float
    energy_surplus_kwh: float
    energy_deficit_kwh: float
    benchmark_panels: int
    benchmark_fitness: float
    benchmark_energy_kwh_month: float
    benchmark_cost_brl: float
    budget_limit_brl: Optional[float]
    under_budget: bool
    execution_time_s: float
    generations: int
    run_seed: int


class FitnessBreakdownDTO(BaseModel):
    energy_term: float
    cost_penalty: float
    waste_penalty: float
    deficit_penalty: float
    area_penalty: float
    budget_penalty: float
    fitness_total: float
    energy_kwh: float
    cost_brl: float


class OptimizationOutcomeDTO(BaseModel):
    result: ScenarioRunResultDTO
    history: List[GenerationStatsDTO]
    summary: dict
    final_population: List[dict]
    fitness_breakdown: Optional[FitnessBreakdownDTO]


class SensitivityPointDTO(BaseModel):
    consumption_kwh: float
    best_panels: int
    best_fitness: float
    execution_time_s: float


class TimingPointDTO(BaseModel):
    label: str
    parameter_value: int
    execution_time_s: float
    best_panels: int


class BaselineResponse(BaseModel):
    panels: int
    fitness: float
    energy_kwh_month: float
    cost_brl: float


class ComparisonResponse(BaseModel):
    summary: dict
    results: list[dict]
    histories: list[dict] = []


# Alias for readability in routes
OptimizeResponse = OptimizationOutcomeDTO
