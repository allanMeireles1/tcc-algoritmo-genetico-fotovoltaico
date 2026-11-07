"""FastAPI router with all endpoints.  No business logic here — delegates to
``backend.services`` adapters and returns DTOs from ``backend.schemas``."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.schemas import (
    OptimizeRequest,
    BaselineRequest,
    ComparisonRequest,
    SensitivityRequest,
    PopulationTimingRequest,
    GenerationsTimingRequest,
    OptimizeResponse,
    BaselineResponse,
    ComparisonResponse,
    SensitivityPointDTO,
    TimingPointDTO,
)
from backend import services

router = APIRouter()


@router.get("/health", response_model=dict)
def health_check():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Cities / Panels helpers (useful for UI dropdowns)
# ---------------------------------------------------------------------------
@router.get("/cities", response_model=list[str])
def list_cities():
    return services._list_cities()


@router.get("/panels", response_model=list[dict])
def list_panels():
    return services._list_panels()


# ---------------------------------------------------------------------------
# 1. Optimisation (full AG run)
# ---------------------------------------------------------------------------
# 6. Comparison (AG + analytical + exhaustive) – new endpoint
# ---------------------------------------------------------------------------
@router.post("/optimize", response_model=OptimizeResponse)
def api_optimize(req: OptimizeRequest):
    try:
        return services.optimize_adapter(req)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# 2. Baseline – direct sizing without GA
# ---------------------------------------------------------------------------
@router.post("/baseline", response_model=BaselineResponse)
def api_baseline(req: BaselineRequest):
    try:
        return services.baseline_adapter(req)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# 2.5 Comparison – AG vs analytical vs exhaustive (new)
# ---------------------------------------------------------------------------
@router.post("/compare", response_model=ComparisonResponse)
def api_compare(req: ComparisonRequest):
    try:
        return services.comparison_adapter(req)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# 3. Sensitivity experiment – vary consumption levels
# ---------------------------------------------------------------------------
@router.post("/experiments/sensitivity", response_model=list[SensitivityPointDTO])
def api_sensitivity(req: SensitivityRequest):
    try:
        return services.sensitivity_adapter(req)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# 4. Timing experiment – population size
# ---------------------------------------------------------------------------
@router.post("/experiments/population-timing", response_model=list[TimingPointDTO])
def api_pop_timing(req: PopulationTimingRequest):
    try:
        return services.pop_timing_adapter(req)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# 5. Timing experiment – generations count
# ---------------------------------------------------------------------------
@router.post("/experiments/generations-timing", response_model=list[TimingPointDTO])
def api_gen_timing(req: GenerationsTimingRequest):
    try:
        return services.gen_timing_adapter(req)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))