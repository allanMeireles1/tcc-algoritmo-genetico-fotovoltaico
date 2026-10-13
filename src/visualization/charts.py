"""Gráficos acadêmicos para demonstração do AG e do problema fotovoltaico."""

from dataclasses import asdict
from typing import Sequence

import matplotlib.pyplot as plt
import pandas as pd

from src.models.individual import Individual
from src.models.result import (
    FitnessBreakdown,
    GenerationStats,
    ScenarioRunResult,
    SensitivityPoint,
    TimingPoint,
)
from src.visualization.style import COLORS, apply_academic_style


def _prepare() -> None:
    apply_academic_style()


def fitness_evolution_figure(history: Sequence[GenerationStats]) -> plt.Figure:
    """Gráfico 1 — Evolução do melhor fitness por geração (convergência)."""
    _prepare()
    df = pd.DataFrame([asdict(h) for h in history])
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(
        df["generation"],
        df["best_fitness"],
        color=COLORS["primary"],
        linewidth=2.2,
        marker="o",
        markersize=3,
        markevery=max(1, len(df) // 15),
        label="Melhor fitness",
    )
    ax.set_title("Evolução do fitness — convergência do algoritmo genético")
    ax.set_xlabel("Geração")
    ax.set_ylabel("Fitness")
    ax.grid(True)
    ax.legend(loc="lower right")
    fig.tight_layout()
    return fig


def best_vs_average_figure(history: Sequence[GenerationStats]) -> plt.Figure:
    """Gráfico 2 — Melhor fitness vs fitness médio da população."""
    _prepare()
    df = pd.DataFrame([asdict(h) for h in history])
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(
        df["generation"],
        df["best_fitness"],
        color=COLORS["ag"],
        linewidth=2,
        label="Melhor fitness",
    )
    ax.plot(
        df["generation"],
        df["avg_fitness"],
        color=COLORS["accent"],
        linewidth=2,
        linestyle="--",
        label="Fitness médio da população",
    )
    ax.set_title("Melhor fitness vs fitness médio — diversidade e estabilidade")
    ax.set_xlabel("Geração")
    ax.set_ylabel("Fitness")
    ax.grid(True)
    ax.legend()
    fig.tight_layout()
    return fig


def energy_vs_consumption_figure(result: ScenarioRunResult) -> plt.Figure:
    """Gráfico 3 — Energia gerada vs consumo mensal."""
    _prepare()
    labels = ["Consumo mensal", "Energia gerada (AG)"]
    values = [result.monthly_consumption_kwh, result.best_energy_kwh_month]
    colors = [COLORS["warning"], COLORS["success"]]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(labels, values, color=colors, width=0.55, edgecolor="#333", linewidth=0.8)
    ax.set_title("Atendimento energético da residência")
    ax.set_ylabel("kWh/mês")
    ax.grid(True, axis="y")

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(values) * 0.02,
            f"{value:.1f}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )
    fig.tight_layout()
    return fig


def roof_area_horizontal_figure(result: ScenarioRunResult) -> plt.Figure:
    """Gráfico 4 — Ocupação do telhado (barras horizontais em m²)."""
    _prepare()
    area_used = result.best_num_panels * result.panel_area_m2
    area_free = max(result.roof_usable_area_m2 - area_used, 0.0)

    fig, ax = plt.subplots(figsize=(8, 3.5))
    categories = ["Área ocupada pelos painéis", "Área útil livre"]
    values = [area_used, area_free]
    colors = [COLORS["secondary"], "#e0e0e0"]

    bars = ax.barh(categories, values, color=colors, edgecolor="#333", linewidth=0.8)
    ax.set_xlabel("Área (m²)")
    ax.set_title(
        f"Ocupação do telhado — {area_used:.1f} m² de {result.roof_usable_area_m2:.1f} m² úteis "
        f"({result.roof_occupancy_ratio * 100:.1f}%)"
    )
    ax.grid(True, axis="x")

    for bar, value in zip(bars, values):
        ax.text(
            value + result.roof_usable_area_m2 * 0.02,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.1f} m²",
            va="center",
            fontsize=9,
        )
    fig.tight_layout()
    return fig


def final_population_histogram(population: Sequence[Individual]) -> plt.Figure:
    """Gráfico 5 — Distribuição de painéis na população final."""
    _prepare()
    panels = [ind.num_panels for ind in population]
    fig, ax = plt.subplots(figsize=(8, 4.5))

    if not panels:
        ax.text(0.5, 0.5, "Sem dados de população", ha="center", va="center")
        return fig

    bins = range(min(panels), max(panels) + 2)
    ax.hist(panels, bins=bins, color=COLORS["primary"], edgecolor="white", alpha=0.85, align="left")
    ax.set_title("Distribuição da população final — quantidade de painéis")
    ax.set_xlabel("Número de painéis")
    ax.set_ylabel("Frequência de indivíduos")
    ax.grid(True, axis="y")
    fig.tight_layout()
    return fig


def ag_vs_baseline_figure(result: ScenarioRunResult) -> plt.Figure:
    """Gráfico 6 — Comparação AG vs método direto (painéis e custo)."""
    _prepare()
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))

    methods = ["Método direto", "Algoritmo genético"]
    panels = [result.benchmark_panels, result.best_num_panels]
    costs = [result.benchmark_cost_brl, result.best_cost_brl]

    axes[0].bar(methods, panels, color=[COLORS["baseline"], COLORS["ag"]], edgecolor="#333")
    axes[0].set_title("Quantidade de painéis")
    axes[0].set_ylabel("Painéis")
    axes[0].grid(True, axis="y")
    for idx, value in enumerate(panels):
        axes[0].text(idx, value + 0.1, str(value), ha="center", fontweight="bold")

    axes[1].bar(methods, costs, color=[COLORS["baseline"], COLORS["ag"]], edgecolor="#333")
    axes[1].set_title("Custo estimado")
    axes[1].set_ylabel("R$")
    axes[1].grid(True, axis="y")
    for idx, value in enumerate(costs):
        axes[1].text(idx, value + max(costs) * 0.02, f"R$ {value:,.0f}", ha="center", fontsize=9)

    fig.suptitle("Por que usar algoritmo genético? — AG vs baseline", fontsize=12, fontweight="bold")
    fig.tight_layout()
    return fig


def fitness_composition_figure(breakdown: FitnessBreakdown) -> plt.Figure:
    """Gráfico 7 — Composição da função de fitness (waterfall simplificado)."""
    _prepare()
    labels = [
        "Energia\n(+) ",
        "Custo\n(-) ",
        "Excesso\n(-) ",
        "Déficit\n(-) ",
        "Área\n(-) ",
        "Orçamento\n(-) ",
        "Fitness\nfinal",
    ]
    values = [
        breakdown.energy_term,
        -breakdown.cost_penalty,
        -breakdown.waste_penalty,
        -breakdown.deficit_penalty,
        -breakdown.area_penalty,
        -breakdown.budget_penalty,
        breakdown.fitness_total,
    ]

    fig, ax = plt.subplots(figsize=(10, 4.5))
    colors = [
        COLORS["success"],
        COLORS["warning"],
        COLORS["accent"],
        COLORS["warning"],
        COLORS["neutral"],
        COLORS["neutral"],
        COLORS["primary"],
    ]
    bars = ax.bar(labels, values, color=colors, edgecolor="#333", linewidth=0.8)
    ax.axhline(0, color="#333", linewidth=0.8)
    ax.set_title("Composição da função de fitness — como a solução foi avaliada")
    ax.set_ylabel("Valor (unidades da função)")
    ax.grid(True, axis="y")

    for bar, value in zip(bars, values):
        offset = abs(value) * 0.05 + 1
        va = "bottom" if value >= 0 else "top"
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + (offset if value >= 0 else -offset),
            f"{value:.1f}",
            ha="center",
            va=va,
            fontsize=8,
        )
    fig.tight_layout()
    return fig


def consumption_sensitivity_figure(points: Sequence[SensitivityPoint]) -> plt.Figure:
    """Gráfico 8 — Sensibilidade: consumo x quantidade de painéis."""
    _prepare()
    df = pd.DataFrame([asdict(p) for p in points])
    fig, ax1 = plt.subplots(figsize=(9, 4.5))

    ax1.plot(
        df["consumption_kwh"],
        df["best_panels"],
        color=COLORS["primary"],
        marker="o",
        linewidth=2,
        label="Painéis (AG)",
    )
    ax1.set_xlabel("Consumo mensal (kWh)")
    ax1.set_ylabel("Quantidade de painéis", color=COLORS["primary"])
    ax1.tick_params(axis="y", labelcolor=COLORS["primary"])
    ax1.grid(True)

    for _, row in df.iterrows():
        ax1.annotate(
            f"{int(row['best_panels'])} painéis",
            (row["consumption_kwh"], row["best_panels"]),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=8,
        )

    ax2 = ax1.twinx()
    ax2.plot(
        df["consumption_kwh"],
        df["best_fitness"],
        color=COLORS["accent"],
        marker="s",
        linestyle="--",
        linewidth=1.5,
        label="Fitness",
    )
    ax2.set_ylabel("Fitness", color=COLORS["accent"])
    ax2.tick_params(axis="y", labelcolor=COLORS["accent"])

    ax1.set_title("Sensibilidade ao consumo — escalabilidade da solução")
    fig.tight_layout()
    return fig


def execution_time_figure(
    pop_points: Sequence[TimingPoint],
    gen_points: Sequence[TimingPoint],
) -> plt.Figure:
    """Gráfico 9 — Tempo de execução vs população e vs gerações."""
    _prepare()
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))

    if pop_points:
        pop_df = pd.DataFrame([asdict(p) for p in pop_points])
        axes[0].plot(
            pop_df["parameter_value"],
            pop_df["execution_time_s"],
            color=COLORS["primary"],
            marker="o",
            linewidth=2,
        )
        axes[0].set_xlabel("Tamanho da população")
        axes[0].set_ylabel("Tempo (s)")
        axes[0].set_title("População × tempo de execução")
        axes[0].grid(True)

    if gen_points:
        gen_df = pd.DataFrame([asdict(p) for p in gen_points])
        axes[1].plot(
            gen_df["parameter_value"],
            gen_df["execution_time_s"],
            color=COLORS["secondary"],
            marker="s",
            linewidth=2,
        )
        axes[1].set_xlabel("Número de gerações")
        axes[1].set_ylabel("Tempo (s)")
        axes[1].set_title("Gerações × tempo de execução")
        axes[1].grid(True)

    fig.suptitle("Desempenho computacional do algoritmo genético", fontsize=12, fontweight="bold")
    fig.tight_layout()
    return fig
