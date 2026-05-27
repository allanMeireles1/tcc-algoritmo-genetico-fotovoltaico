"""Interface Streamlit principal com entrada real de telhado."""

from dataclasses import asdict
from io import StringIO

import pandas as pd
import streamlit as st

from src.core.config import GAConfig
from src.core.constants import PROJECT_TITLE
from src.models.roof import RoofInput
from src.simulation.runner import results_to_rows, run_optimization
from src.storage.exporter import create_run_dir, export_csv, export_json
from src.storage.loader import load_cities, load_panels, load_scenarios
from src.utils.logger import setup_logger
from src.utils.validators import validate_roof_input
from src.visualization.charts import (
    ag_vs_baseline_figure,
    best_solution_figure,
    convergence_figure,
    cost_breakdown_figure,
    fitness_by_generation_figure,
    roof_occupancy_figure,
    scenario_comparison_figure,
)
from src.visualization.dashboard import explain_solution
from src.visualization.roof_plot import roof_layout_figure


def _result_download_payload(result_rows: list[dict]) -> tuple[str, str]:
    df = pd.DataFrame(result_rows)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    return df.to_json(orient="records", force_ascii=False, indent=2), csv_buffer.getvalue()


def _city_lookup(cities: list[dict]) -> dict[str, dict]:
    return {f"{city['city']} ({city['state']})": city for city in cities}


def main() -> None:
    """Renderiza dashboard acadêmico e executa simulações."""
    logger = setup_logger()
    cities = load_cities()
    panels = load_panels()
    scenarios = load_scenarios()  # Mantido como presets opcionais.

    st.set_page_config(page_title="TCC AG Fotovoltaico", layout="wide")
    st.title(PROJECT_TITLE)
    st.caption(
        "MVP acadêmico para otimização do número de painéis solares com AG manual, "
        "respeitando dimensões de telhado, consumo e restrições de custo."
    )

    st.sidebar.header("Entradas do problema")
    use_preset = st.sidebar.checkbox("Usar cenário exemplo (opcional)", value=False)
    preset_names = {scenario["scenario_name"]: scenario for scenario in scenarios}
    selected_preset = st.sidebar.selectbox("Preset", options=list(preset_names.keys()), disabled=not use_preset)

    preset = preset_names[selected_preset]
    width_default = 8.0 if not use_preset else 6.0 + float(preset["roof_area_m2"]) / 10.0
    length_default = 10.0 if not use_preset else float(preset["roof_area_m2"]) / max(width_default, 0.1)
    consumption_default = 300.0 if not use_preset else float(preset["monthly_consumption_kwh"])

    width_m = st.sidebar.number_input("Largura do telhado (m)", min_value=1.0, value=width_default, step=0.5)
    length_m = st.sidebar.number_input("Comprimento do telhado (m)", min_value=1.0, value=length_default, step=0.5)
    monthly_consumption = st.sidebar.number_input("Consumo mensal (kWh)", min_value=50.0, value=consumption_default, step=10.0)
    roof_type = st.sidebar.selectbox("Tipo de telhado (opcional)", options=["ceramic", "fibrocement", "metallic", "mixed"])

    city_map = _city_lookup(cities)
    city_option = st.sidebar.selectbox("Cidade / região", options=list(city_map.keys()))
    budget_enabled = st.sidebar.checkbox("Definir orçamento máximo")
    max_budget = st.sidebar.number_input("Orçamento máximo (R$)", min_value=1000.0, value=40000.0, step=500.0, disabled=not budget_enabled)

    st.sidebar.header("Parâmetros do AG")
    population_size = st.sidebar.slider("População", 20, 200, 60, 10)
    generations = st.sidebar.slider("Gerações", 20, 300, 120, 10)
    crossover_rate = st.sidebar.slider("Crossover", 0.1, 1.0, 0.8, 0.05)
    mutation_rate = st.sidebar.slider("Mutação", 0.01, 0.5, 0.1, 0.01)
    elitism_count = st.sidebar.slider("Elitismo", 1, 10, 2, 1)
    random_seed = st.sidebar.number_input("Seed", min_value=0, value=42, step=1)
    runs = st.sidebar.slider("Rodadas por execução", 1, 20, 5, 1)

    config = GAConfig(
        population_size=population_size,
        generations=generations,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
        elitism_count=elitism_count,
        random_seed=int(random_seed),
    )

    panel_data = panels[0]
    city_data = city_map[city_option]
    roof = RoofInput(
        width_m=float(width_m),
        length_m=float(length_m),
        monthly_consumption_kwh=float(monthly_consumption),
        city=str(city_data["city"]),
        roof_type=roof_type,
        max_budget_brl=float(max_budget) if budget_enabled else None,
    )

    st.subheader("Resumo das entradas")
    st.write(
        f"Área bruta: **{roof.gross_area_m2:.2f} m²** | "
        f"Área útil estimada: **{roof.usable_area_m2():.2f} m²** | "
        f"Irradiância ({roof.city}): **{city_data['irradiance_kwh_m2_day']:.2f} kWh/m²/dia**"
    )

    if st.button("Executar otimização", type="primary"):
        try:
            validate_roof_input(roof)
        except ValueError as exc:
            st.error(str(exc))
            return

        result, history, summary = run_optimization(roof=roof, city_data=city_data, panel_data=panel_data, config=config, runs=runs)
        run_dir = create_run_dir()

        export_json(run_dir / "result.json", result)
        export_csv(run_dir / "history.csv", [asdict(h) for h in history])
        export_csv(run_dir / "execution_params.csv", [asdict(config)])
        export_json(run_dir / "execution_summary.json", summary)

        result_rows = results_to_rows([result])
        export_csv(run_dir / "summary.csv", result_rows)
        logger.info("Execução concluída. Resultados salvos em: %s", run_dir)

        st.success(f"Execução concluída. Resultados exportados em {run_dir}")
        st.subheader("Melhor solução encontrada")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Painéis (AG)", str(result.best_num_panels))
        col2.metric("Energia estimada", f"{result.best_energy_kwh_month:.1f} kWh/mês")
        col3.metric("Custo estimado", f"R$ {result.best_cost_brl:,.2f}")
        col4.metric("Ocupação útil", f"{result.roof_occupancy_ratio * 100:.1f}%")

        st.info(explain_solution(result))
        if result.energy_deficit_kwh > 0:
            st.warning(f"Déficit energético estimado: {result.energy_deficit_kwh:.2f} kWh/mês")
        if result.energy_surplus_kwh > 0:
            st.info(f"Excesso energético estimado: {result.energy_surplus_kwh:.2f} kWh/mês")
        if result.budget_limit_brl is not None:
            status = "dentro" if result.under_budget else "acima"
            st.write(f"Orçamento: solução está **{status}** do limite informado.")

        result_df = pd.DataFrame(result_rows)
        st.dataframe(result_df, use_container_width=True)
        st.dataframe(pd.DataFrame([summary]), use_container_width=True)

        st.pyplot(convergence_figure(history))
        st.pyplot(fitness_by_generation_figure(history))
        st.pyplot(ag_vs_baseline_figure(result))
        st.pyplot(best_solution_figure(result))
        st.pyplot(roof_occupancy_figure(result))
        st.pyplot(cost_breakdown_figure([result]))
        st.pyplot(roof_layout_figure(result, panel_area_m2=float(panel_data["panel_area_m2"])))
        st.pyplot(scenario_comparison_figure([result]))

        json_payload, csv_payload = _result_download_payload(result_rows)
        st.download_button("Baixar resultado (JSON)", json_payload, file_name="result.json", mime="application/json")
        st.download_button("Baixar resultado (CSV)", csv_payload, file_name="result.csv", mime="text/csv")


if __name__ == "__main__":
    main()
