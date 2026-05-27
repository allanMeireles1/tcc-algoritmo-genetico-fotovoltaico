"""Visualização esquemática simples da ocupação do telhado."""

import math

import matplotlib.pyplot as plt

from src.models.result import ScenarioRunResult


def roof_layout_figure(result: ScenarioRunResult, panel_area_m2: float) -> plt.Figure:
    """Renderiza grade simples representando painéis instalados."""
    total_slots = max(1, int(result.roof_usable_area_m2 // panel_area_m2))
    cols = max(1, int(math.sqrt(total_slots)))
    rows = math.ceil(total_slots / cols)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.set_title("Layout esquemático do telhado")
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_aspect("equal")
    ax.axis("off")

    installed = result.best_num_panels
    idx = 0
    for row in range(rows):
        for col in range(cols):
            color = "#2ca02c" if idx < installed else "#f0f0f0"
            rect = plt.Rectangle((col, rows - row - 1), 1, 1, facecolor=color, edgecolor="black", linewidth=0.5)
            ax.add_patch(rect)
            idx += 1
            if idx >= total_slots:
                break

    return fig
