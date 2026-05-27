"""Modelos de entrada e restrição física do telhado."""

from dataclasses import dataclass

from src.core.constants import DEFAULT_ROOF_USABLE_FACTOR


@dataclass(slots=True)
class RoofInput:
    """Dados principais informados pelo usuário."""

    width_m: float
    length_m: float
    monthly_consumption_kwh: float
    city: str
    roof_type: str = "ceramic"
    max_budget_brl: float | None = None

    @property
    def gross_area_m2(self) -> float:
        """Área bruta do telhado."""
        return self.width_m * self.length_m

    def usable_area_m2(self) -> float:
        """Área útil aproximada considerando perdas de instalação."""
        return self.gross_area_m2 * DEFAULT_ROOF_USABLE_FACTOR
