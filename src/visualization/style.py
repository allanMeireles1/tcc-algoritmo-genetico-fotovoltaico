"""Estilo visual consistente para gráficos acadêmicos."""

import matplotlib.pyplot as plt

ACADEMIC_STYLE = {
    "figure.facecolor": "white",
    "axes.facecolor": "#fafafa",
    "axes.edgecolor": "#333333",
    "axes.labelcolor": "#222222",
    "axes.titleweight": "bold",
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "grid.alpha": 0.35,
    "grid.linestyle": "--",
}

COLORS = {
    "primary": "#1f4e79",
    "secondary": "#2e86ab",
    "accent": "#f18f01",
    "success": "#2ca02c",
    "warning": "#d62728",
    "neutral": "#7f8c8d",
    "ag": "#1f77b4",
    "baseline": "#ff7f0e",
}


def apply_academic_style() -> None:
    """Aplica rcParams padronizados para apresentação em banca."""
    plt.rcParams.update(ACADEMIC_STYLE)
