"""Modelo de indivíduo da população genética."""

from dataclasses import dataclass, field
from uuid import uuid4

from src.simulation.evaluation import EvaluationResult


@dataclass(slots=True)
class Individual:
    """Representa um indivíduo com cromossomo inteiro.

    A partir de E5.3.2, cada indivíduo armazena um ``EvaluationResult``
    que contém todos os atributos relevantes para a comparação lexicográfica.
    O campo ``fitness`` permanece apenas por compatibilidade, mas não é mais
    usado nas seleções.
    """

    num_panels: int
    fitness: float = 0.0  # legado, não utilizado nas novas comparações
    evaluation: EvaluationResult | None = None
    id: str = field(default_factory=lambda: str(uuid4())[:8])
