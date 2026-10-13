"""Interface Streamlit com dashboard acadêmico em abas."""

from dataclasses import asdict
from io import StringIO

import pandas as pd
import streamlit as st

from src.core.config import GAConfig
from src.core.constants import PROJECT_TITLE
from src.models.roof import RoofInput
from src.simulation.experiments import (
    run_consumption_sensitivity,
    run_generations_timing_experiment,
    run_population_timing_experiment,
)
from src.simulation.runner import results_to_rows, run_optimization
from src.storage.exporter import create_run_dir, export_csv, export_json
from src.storage.loader import load_cities, load_panels, load_scenarios
from src.utils.logger import setup_logger
from src.utils.validators import validate_roof_input
from src.visualization.charts import (
    ag_vs_baseline_figure,
    best_vs_average_figure,
    consumption_sensitivity_figure,
    energy_vs_consumption_figure,
    execution_time_figure,
    final_population_histogram,
    fitness_composition_figure,
    fitness_evolution_figure,
    roof_area_horizontal_figure,
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


def _render_metrics(result) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Painéis (AG)", str(result.best_num_panels))
    col2.metric("Energia estimada", f"{result.best_energy_kwh_month:.1f} kWh/mês")
    col3.metric("Custo estimado", f"R$ {result.best_cost_brl:,.2f}")
    col4.metric("Ocupação útil", f"{result.roof_occupancy_ratio * 100:.1f}%")


def _render_alerts(result) -> None:
    st.info(explain_solution(result))
    if result.energy_deficit_kwh > 0:
        st.warning(f"Déficit energético estimado: {result.energy_deficit_kwh:.2f} kWh/mês")
    if result.energy_surplus_kwh > 0:
        st.success(f"Excesso energético estimado: {result.energy_surplus_kwh:.2f} kWh/mês")
    if result.budget_limit_brl is not None:
        status = "dentro" if result.under_budget else "acima"
        st.write(f"Orçamento: solução está **{status}** do limite informado.")


def main() -> None:
    """Renderiza dashboard acadêmico com abas de análise e experimentos."""
    logger = setup_logger()
    cities = load_cities()
    panels = load_panels()
    scenarios = load_scenarios()

    st.set_page_config(page_title="TCC AG Fotovoltaico", layout="wide")
    st.title(PROJECT_TITLE)
    st.caption(
        "Protótipo acadêmico: otimização do número de painéis com AG manual, "
        "a partir das dimensões do telhado e do consumo da residência."
    )

    st.sidebar.header("Entradas do problema")
    use_preset = st.sidebar.checkbox("Usar preset de exemplo (opcional)", value=False)
    preset_names = {scenario["scenario_name"]: scenario for scenario in scenarios}
    selected_preset = st.sidebar.selectbox("Preset", options=list(preset_names.keys()), disabled=not use_preset)

    preset = preset_names[selected_preset]
    width_default = 8.0 if not use_preset else 6.0 + float(preset["roof_area_m2"]) / 10.0
    length_default = 10.0 if not use_preset else float(preset["roof_area_m2"]) / max(width_default, 0.1)
    consumption_default = 300.0 if not use_preset else float(preset["monthly_consumption_kwh"])

    width_m = st.sidebar.number_input("Largura do telhado (m)", min_value=1.0, value=width_default, step=0.5)
    length_m = st.sidebar.number_input("Comprimento do telhado (m)", min_value=1.0, value=length_default, step=0.5)
    monthly_consumption = st.sidebar.number_input(
        "Consumo mensal (kWh)", min_value=50.0, value=consumption_default, step=10.0
    )
    roof_type = st.sidebar.selectbox(
        "Tipo de telhado (opcional)", options=["ceramic", "fibrocement", "metallic", "mixed"]
    )

    city_map = _city_lookup(cities)
    city_option = st.sidebar.selectbox("Cidade / região", options=list(city_map.keys()))
    budget_enabled = st.sidebar.checkbox("Definir orçamento máximo")
    max_budget = st.sidebar.number_input(
        "Orçamento máximo (R$)", min_value=1000.0, value=40000.0, step=500.0, disabled=not budget_enabled
    )

    st.sidebar.header("Parâmetros do AG")
    population_size = st.sidebar.slider("População", 20, 200, 60, 10)
    generations = st.sidebar.slider("Gerações", 20, 300, 120, 10)
    crossover_rate = st.sidebar.slider("Crossover", 0.1, 1.0, 0.8, 0.05)
    mutation_rate = st.sidebar.slider("Mutação", 0.01, 0.5, 0.1, 0.01)
    elitism_count = st.sidebar.slider("Elitismo", 1, 10, 2, 1)
    random_seed = st.sidebar.number_input("Seed", min_value=0, value=42, step=1)
    runs = st.sidebar.slider("Rodadas por execução", 1, 10, 3, 1)

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
    max_panels_est = int(roof.usable_area_m2() // float(panel_data["panel_area_m2"]))
    st.write(
        f"Área bruta: **{roof.gross_area_m2:.2f} m²** | "
        f"Área útil: **{roof.usable_area_m2():.2f} m²** | "
        f"Máx. painéis (área): **{max_panels_est}** | "
        f"Irradiância ({roof.city}): **{city_data['irradiance_kwh_m2_day']:.2f} kWh/m²/dia**"
    )

    if st.button("Executar otimização", type="primary"):
        try:
            validate_roof_input(roof)
        except ValueError as exc:
            st.error(str(exc))
            return

        with st.spinner("Executando algoritmo genético..."):
            outcome = run_optimization(
                roof=roof,
                city_data=city_data,
                panel_data=panel_data,
                config=config,
                runs=runs,
            )

        st.session_state["outcome"] = outcome
        st.session_state["roof"] = roof
        st.session_state["config"] = config
        st.session_state["panel_data"] = panel_data
        st.session_state["city_data"] = city_data

        run_dir = create_run_dir()
        result = outcome.result
        export_json(run_dir / "result.json", result)
        export_csv(run_dir / "history.csv", [asdict(h) for h in outcome.history])
        export_csv(run_dir / "execution_params.csv", [asdict(config)])
        export_json(run_dir / "execution_summary.json", outcome.summary)
        if outcome.fitness_breakdown:
            export_json(run_dir / "fitness_breakdown.json", outcome.fitness_breakdown)
        export_csv(run_dir / "summary.csv", results_to_rows([result]))
        logger.info("Execução concluída. Resultados em: %s", run_dir)
        st.success(f"Otimização concluída. Arquivos em `{run_dir}`")

    if "outcome" not in st.session_state:
        st.info("Configure as entradas na barra lateral e clique em **Executar otimização**.")
        return

    outcome = st.session_state["outcome"]
    result = outcome.result
    history = outcome.history

    _render_metrics(result)
    _render_alerts(result)

    tab_main, tab_analysis, tab_experiments = st.tabs(
        ["Dashboard principal", "Análise do AG", "Experimentos"]
    )

    with tab_main:
        st.markdown("#### Gráficos essenciais para demonstração do TCC")
        c1, c2 = st.columns(2)
        with c1:
            st.pyplot(fitness_evolution_figure(history))
            st.caption("O algoritmo melhora as soluções ao longo das gerações.")
        with c2:
            st.pyplot(best_vs_average_figure(history))
            st.caption("Convergência com diversidade populacional.")

        c3, c4 = st.columns(2)
        with c3:
            st.pyplot(energy_vs_consumption_figure(result))
            st.caption("A solução atende (ou não) o consumo da residência.")
        with c4:
            st.pyplot(roof_area_horizontal_figure(result))
            st.caption("Restrição física do telhado aplicada ao dimensionamento.")

        st.pyplot(
            roof_layout_figure(result, panel_area_m2=result.panel_area_m2),
        )
        st.caption("Layout esquemático: painéis instalados vs espaço disponível.")

        result_df = pd.DataFrame(results_to_rows([result]))
        st.dataframe(result_df, use_container_width=True)
        json_payload, csv_payload = _result_download_payload(results_to_rows([result]))
        st.download_button("Baixar resultado (JSON)", json_payload, file_name="result.json")
        st.download_button("Baixar resultado (CSV)", csv_payload, file_name="result.csv")

    with tab_analysis:
        st.markdown("#### Análise comparativa e interpretação da fitness")
        c1, c2 = st.columns(2)
        with c1:
            st.pyplot(ag_vs_baseline_figure(result))
            st.caption("Responde: por que usar AG em vez de cálculo direto?")
        with c2:
            st.pyplot(final_population_histogram(outcome.final_population))
            st.caption("Onde a população convergiu na última geração.")

        if outcome.fitness_breakdown:
            st.pyplot(fitness_composition_figure(outcome.fitness_breakdown))
            st.caption("Composição da função de fitness da melhor solução.")

        compare_df = pd.DataFrame(
            [
                {
                    "Método": "Direto",
                    "Painéis": result.benchmark_panels,
                    "Energia (kWh/mês)": result.benchmark_energy_kwh_month,
                    "Custo (R$)": result.benchmark_cost_brl,
                    "Fitness": result.benchmark_fitness,
                },
                {
                    "Método": "AG",
                    "Painéis": result.best_num_panels,
                    "Energia (kWh/mês)": result.best_energy_kwh_month,
                    "Custo (R$)": result.best_cost_brl,
                    "Fitness": result.best_fitness,
                },
            ]
        )
        st.dataframe(compare_df, use_container_width=True)

    with tab_experiments:
        st.markdown("#### Experimentos de sensibilidade e desempenho computacional")
        st.write(
            "Estes testes reforçam o valor acadêmico: escalabilidade do problema "
            "e custo computacional do AG."
        )

        if st.button("Executar experimentos", type="secondary"):
            roof_exp = st.session_state["roof"]
            config_exp = st.session_state["config"]
            panel_exp = st.session_state["panel_data"]
            city_exp = st.session_state["city_data"]

            base = roof_exp.monthly_consumption_kwh
            consumption_levels = [
                max(50.0, base * 0.5),
                base,
                min(base * 1.5, base + 300),
            ]
            consumption_levels = sorted(set(round(v, 1) for v in consumption_levels))

            with st.spinner("Rodando sensibilidade ao consumo..."):
                sensitivity = run_consumption_sensitivity(
                    roof_exp, city_exp, panel_exp, config_exp, consumption_levels
                )

            pop_sizes = [20, 40, 60, 80, 100]
            gen_counts = [30, 60, 90, 120]
            fast_config = GAConfig(
                population_size=config_exp.population_size,
                generations=min(60, config_exp.generations),
                crossover_rate=config_exp.crossover_rate,
                mutation_rate=config_exp.mutation_rate,
                elitism_count=config_exp.elitism_count,
                random_seed=config_exp.random_seed,
            )

            with st.spinner("Medindo tempo vs população e gerações..."):
                pop_timing = run_population_timing_experiment(
                    roof_exp, city_exp, panel_exp, fast_config, pop_sizes
                )
                gen_timing = run_generations_timing_experiment(
                    roof_exp, city_exp, panel_exp, fast_config, gen_counts
                )

            st.session_state["sensitivity"] = sensitivity
            st.session_state["pop_timing"] = pop_timing
            st.session_state["gen_timing"] = gen_timing
            st.success("Experimentos concluídos.")

        if "sensitivity" in st.session_state:
            st.pyplot(consumption_sensitivity_figure(st.session_state["sensitivity"]))
            st.dataframe(
                pd.DataFrame([asdict(p) for p in st.session_state["sensitivity"]]),
                use_container_width=True,
            )

        if "pop_timing" in st.session_state and "gen_timing" in st.session_state:
            st.pyplot(
                execution_time_figure(
                    st.session_state["pop_timing"],
                    st.session_state["gen_timing"],
                )
            )


if __name__ == "__main__":
    main()
