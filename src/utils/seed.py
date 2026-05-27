"""Utilitário de reprodutibilidade."""

import random


def set_global_seed(seed: int) -> None:
    """Configura seed global para o módulo random."""
    random.seed(seed)
