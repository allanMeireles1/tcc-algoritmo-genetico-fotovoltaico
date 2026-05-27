"""Geração de gráficos matplotlib para a interface."""

from dataclasses import asdict
from typing import Sequence

import matplotlib.pyplot as plt
import pandas as pd

from src.models.result import GenerationStats, ScenarioRunResult


def convergence_figure(history: Sequence[GenerationStats]) -> plt.Figure:
    """Figura de convergência: melhor e média por geração."""
    df = pd.DataFrame([asdict(h) for h in history])
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df["generation"], df["best_fitness"], label="Melhor fitness", linewidth=2)
    ax.plot(df["generation"], df["avg_fitness"], label="Fitness médio", linestyle="--")
    ax.set_title("Convergência do algoritmo genético")
    ax.set_xlabel("Geração")
    ax.set_ylabel("Fitness")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    return fig


def fitness_by_generation_figure(history: Sequence[GenerationStats]) -> plt.Figure:
    """Figura de barras de fitness melhor por geração."""
    df = pd.DataFrame([asdict(h) for h in history])
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(df["generation"], df["best_fitness"], color="#1f77b4", alpha=0.75)
    ax.set_title("Fitness por geração (melhor indivíduo)")
    ax.set_xlabel("Geração")
    ax.set_ylabel("Fitness")
    fig.tight_layout()
    return fig


def scenario_comparison_figure(results: Sequence[ScenarioRunResult]) -> plt.Figure:
    """Figura comparando fitness final entre execuções."""
    df = pd.DataFrame([asdict(r) for r in results])
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(df["execution_label"], df["best_fitness"], color="#2ca02c")
    ax.set_title("Comparação de fitness entre execuções")
    ax.set_xlabel("Execução")
    ax.set_ylabel("Melhor fitness")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    return fig


def best_solution_figure(result: ScenarioRunResult) -> plt.Figure:
    """Figura da melhor solução com energia e consumo estimado."""
    fig, ax = plt.subplots(figsize=(6, 4))
    labels = ["Demanda", "Energia gerada"]
    values = [result.monthly_consumption_kwh, result.best_energy_kwh_month]
    ax.bar(labels, values, color=["#9467bd", "#17becf"])
    ax.set_title(f"Melhor solução — {result.execution_label}")
    ax.set_ylabel("kWh/mês")
    fig.tight_layout()
    return fig


def ag_vs_baseline_figure(result: ScenarioRunResult) -> plt.Figure:
    """Compara fitness do AG com o baseline direto."""
    fig, ax = plt.subplots(figsize=(6, 4))
    labels = ["AG", "Baseline"]
    values = [result.best_fitness, result.benchmark_fitness]
    ax.bar(labels, values, color=["#1f77b4", "#ff7f0e"])
    ax.set_title("AG vs baseline (fitness)")
    ax.set_ylabel("Fitness")
    fig.tight_layout()
    return fig


def roof_occupancy_figure(result: ScenarioRunResult) -> plt.Figure:
    """Mostra área útil usada e livre do telhado."""
    used = result.roof_usable_area_m2 * result.roof_occupancy_ratio
    free = max(result.roof_usable_area_m2 - used, 0.0)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie([used, free], labels=["Área ocupada", "Área livre"], autopct="%1.1f%%", colors=["#17becf", "#dddddd"])
    ax.set_title("Ocupação do telhado")
    fig.tight_layout()
    return fig


def cost_breakdown_figure(results: Sequence[ScenarioRunResult]) -> plt.Figure:
    """Compara custo estimado por execução."""
    df = pd.DataFrame([asdict(r) for r in results])
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(df["execution_label"], df["best_cost_brl"], color="#9467bd")
    ax.set_title("Custo estimado por execução")
    ax.set_ylabel("R$")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    return fig
