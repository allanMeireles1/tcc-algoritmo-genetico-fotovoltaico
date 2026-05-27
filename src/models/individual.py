"""Modelo de indivíduo da população genética."""

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass(slots=True)
class Individual:
    """Representa um indivíduo com cromossomo inteiro."""

    num_panels: int
    fitness: float = 0.0
    id: str = field(default_factory=lambda: str(uuid4())[:8])
