import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity,
  ChevronRight,
  Loader2,
  PlayCircle,
  PanelTop,
  AlertTriangle,
  Info,
} from "lucide-react";

import {
  DashboardForm,
  type RoofForm,
  type GAForm,
  roofDefaults,
  gaDefaults,
} from "./components/DashboardForm";
import { DashboardPage } from "./components/DashboardPage";
import { AnalysisPage } from "./components/AnalysisPage";
import { ExperimentsPage } from "./components/ExperimentsPage";
import { MetricCards } from "./components/MetricCards";
import { RoofSketch } from "./components/RoofSketch";
import { EmptyState } from "./components/EmptyState";
import { SymptomBanner } from "./components/SymptomBanner";

import type {
  OptimizationOutcomeDTO,
  BaselineResponse,
  SensitivityPointDTO,
  TimingPointDTO,
} from "./types/api";
import {
  getCities,
  getPanels,
  optimize,
  baseline,
  sensitivity,
  populationTiming,
  generationsTiming,
} from "./lib/api";

type TabKey = "dashboard" | "analysis" | "experiments";

const TABS: { key: TabKey; label: string }[] = [
  { key: "dashboard", label: "Dashboard principal" },
  { key: "analysis", label: "Análise do AG" },
  { key: "experiments", label: "Experimentos" },
];

export function App() {
  // reference catalogues -------------------------------------------------
  const [cities, setCities] = useState<string[]>([]);
  const [panels, setPanels] = useState<Record<string, unknown>[]>([]);

  useEffect(() => {
    getCities()
      .then(setCities)
      .catch(() => setCities([]));
    getPanels()
      .then(setPanels)
      .catch(() => setPanels([]));
  }, []);

  // inputs ---------------------------------------------------------------
  const [roof, setRoof] = useState<RoofForm>(roofDefaults);
  const [ga, setGa] = useState<GAForm>(gaDefaults);
  const [city, setCity] = useState("");

  useEffect(() => {
    if (cities.length && !city) setCity(cities[0]);
  }, [cities, city]);

  // tab state
  const [activeTab, setActiveTab] = useState<TabKey>("dashboard");

  const panel = panels[0];
  const panelArea =
    typeof panel?.panel_area_m2 === "number" ? panel.panel_area_m2 : 2.2;

  // derived --------------------------------------------------------------
  const summary = useMemo(() => {
    const gross = roof.width_m * roof.length_m;
    const usable = gross * 0.85;
    const maxPanels = Math.floor(usable / panelArea);
    return { gross, usable, maxPanels };
  }, [roof.width_m, roof.length_m, panelArea]);

  // run state ------------------------------------------------------------
  const [busy, setBusy] = useState(false);
  const [outcome, setOutcome] = useState<OptimizationOutcomeDTO | null>(null);
  const [baselineResult, setBaselineResult] = useState<BaselineResponse | null>(
    null,
  );
  const [phase, setPhase] = useState<"idle" | "ok" | "error">("idle");
  const [message, setMessage] = useState<string | null>(null);

  // experiments state ----------------------------------------------------
  const [sensitivityPoints, setSensitivityPoints] = useState<
    SensitivityPointDTO[]
  >([]);
  const [popTiming, setPopTiming] = useState<TimingPointDTO[]>([]);
  const [genTiming, setGenTiming] = useState<TimingPointDTO[]>([]);
  const [experimentsBusy, setExperimentsBusy] = useState(false);

  const payload = useMemo(() => {
    const { width_m, length_m, monthly_consumption_kwh, roof_type } = roof;
    return {
      roof: {
        width_m,
        length_m,
        monthly_consumption_kwh,
        city,
        roof_type,
        max_budget_brl: roof.max_budget_brl
          ? Number(roof.max_budget_brl)
          : null,
      },
      config: ga,
      runs: 1,
    };
  }, [roof, ga, city]);

  const runOptimization = useCallback(async () => {
    setBusy(true);
    setPhase("idle");
    setMessage(null);
    try {
      const [opt, base] = await Promise.all([
        optimize(payload),
        baseline(payload),
      ]);
      setOutcome(opt);
      setBaselineResult(base);
      setPhase("ok");
    } catch (err) {
      setOutcome(null);
      setBaselineResult(null);
      setPhase("error");
      setMessage(err instanceof Error ? err.message : "Falha ao otimizar.");
    } finally {
      setBusy(false);
    }
  }, [payload]);

  const runExperiments = useCallback(async () => {
    setExperimentsBusy(true);
    try {
      const base = roof.monthly_consumption_kwh;
      const levels = [base * 0.5, base, Math.min(base * 1.5, base + 300)].map(
        (v) => Math.round(v * 10) / 10,
      );
      const [sens, pop, gen] = await Promise.all([
        sensitivity({
          roof: payload.roof,
          consumption_levels: levels,
          config: ga,
        }),
        populationTiming({
          roof: payload.roof,
          population_sizes: [20, 40, 60, 80, 100],
          config: ga,
        }),
        generationsTiming({
          roof: payload.roof,
          generation_counts: [30, 60, 90, 120],
          config: ga,
        }),
      ]);
      setSensitivityPoints(sens);
      setPopTiming(pop);
      setGenTiming(gen);
    } catch {
      setSensitivityPoints([]);
      setPopTiming([]);
      setGenTiming([]);
    } finally {
      setExperimentsBusy(false);
    }
  }, [payload, ga, roof.monthly_consumption_kwh]);

  // derived UI helpers ---------------------------------------------------
  const result = outcome?.result;
  const roofLabel = `${(roof.length_m * panelArea).toFixed(1)}m×${roof.width_m.toFixed(1)}m`;
  const areaLabel = `Área útil ~${summary.usable.toFixed(1)}m² (~${summary.maxPanels} painéis)`;

  // UI -------------------------------------------------------------------
  return (
    <div className="min-h-screen bg-ink-50 text-ink-900">
      {/* Header ------------------------------------------------- */}
      <header className="border-b border-ink-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-br from-brand-600 to-brand-400 text-white shadow-sm">
              <PanelTop className="h-5 w-5" strokeWidth={2.4} aria-hidden />
            </div>
            <div>
              <h1 className="text-[15px] font-semibold tracking-tight text-ink-900">
                TCC — AG para Dimensionamento Fotovoltaico
              </h1>
              <p className="text-xs text-ink-500">
                Protótipo acadêmico · otimização do número de painéis para
                residências do Nordeste
              </p>
            </div>
          </div>
          <div className="hidden items-center gap-2 sm:flex">
            <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-1 text-[11px] font-medium text-emerald-700 ring-1 ring-inset ring-emerald-200">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
              API online
            </span>
          </div>
        </div>
      </header>

      {/* Body --------------------------------------------------- */}
      <div className="mx-auto grid max-w-7xl gap-6 px-4 py-6 lg:grid-cols-[360px_1fr] lg:px-6">
        {/* Sidebar ------------------------------------------------ */}
        <aside className="space-y-4">
          <DashboardForm
            cities={cities}
            roof={roof}
            onRoofChange={setRoof}
            ga={ga}
            onGaChange={setGa}
            city={city}
            onCityChange={setCity}
          />

          <button
            type="button"
            onClick={runOptimization}
            disabled={busy}
            className="group inline-flex w-full items-center justify-center gap-2 rounded-xl bg-brand-600 px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {busy ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
                Executando otimização…
              </>
            ) : (
              <>
                <PlayCircle className="h-4 w-4" aria-hidden />
                Executar otimização
              </>
            )}
          </button>

          {phase === "error" && message && (
            <SymptomBanner tone="error" title="Falha na otimização">
              {message}
            </SymptomBanner>
          )}
        </aside>

        {/* Main -------------------------------------------------- */}
        <main className="space-y-6">
          <section
            aria-label="Resumo do problema"
            className="rounded-2xl border border-ink-200 bg-white p-4 shadow-sm"
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-ink-500">
                  Resumo das entradas
                </p>
                <p className="mt-1 text-sm text-ink-700">
                  Área bruta{" "}
                  <span className="font-semibold text-ink-900">
                    {summary.gross.toFixed(1)} m²
                  </span>{" "}
                  · Área útil{" "}
                  <span className="font-semibold text-ink-900">
                    {summary.usable.toFixed(1)} m²
                  </span>{" "}
                  · Consumo{" "}
                  <span className="font-semibold text-ink-900">
                    {roof.monthly_consumption_kwh} kWh/mês
                  </span>{" "}
                  · Cidade{" "}
                  <span className="font-semibold text-ink-900">{city}</span>
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className="rounded-lg bg-brand-50 px-2.5 py-1 text-[11px] font-medium text-brand-700 ring-1 ring-inset ring-brand-100">
                  {roofLabel}
                </span>
                <span className="rounded-lg bg-solar-50 px-2.5 py-1 text-[11px] font-medium text-solar-700 ring-1 ring-inset ring-solar-100">
                  {areaLabel}
                </span>
              </div>
            </div>
          </section>

          {/* Tabs ------------------------------------------------ */}
          <div
            role="tablist"
            aria-label="Seções"
            className="inline-flex rounded-xl bg-ink-100 p-1 text-sm"
          >
            {TABS.map((tab) => {
              const active = tab.key === activeTab;
              return (
                <button
                  key={tab.key}
                  type="button"
                  role="tab"
                  aria-selected={active}
                  onClick={() => setActiveTab(tab.key)}
                  className={`rounded-lg px-4 py-2 text-sm font-medium transition focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 ${
                    active
                      ? "bg-white text-ink-900 shadow-sm"
                      : "text-ink-600 hover:text-ink-900"
                  }`}
                >
                  {tab.label}
                </button>
              );
            })}
          </div>

          <RoofSketch
            width={roof.width_m}
            length={roof.length_m}
            occupancy={result?.roof_occupancy_ratio ?? 0}
            panelArea={panelArea}
            numPanels={result?.best_num_panels ?? 0}
          />

          {phase === "idle" && !outcome && (
            <EmptyState onRun={runOptimization} busy={busy} />
          )}

          {outcome && result && (
            <>
              <MetricCards
                result={result}
                summary={{
                  gross: summary.gross,
                  usable: summary.usable,
                  maxPanels: summary.maxPanels,
                  panelArea,
                }}
              />

              <SymptomBanner
                tone="info"
                title="Interpretação da solução"
                icon={<Info className="h-4 w-4" aria-hidden />}
              >
                <span className="text-ink-600">
                  O AG escolheu{" "}
                  <strong className="font-semibold text-ink-900">
                    {result.best_num_panels} painéis
                  </strong>{" "}
                  equilibrando energia estimada (
                  {result.best_energy_kwh_month.toFixed(1)} kWh/mês), custo (R${" "}
                  {result.best_cost_brl.toLocaleString("pt-BR", {
                    minimumFractionDigits: 2,
                  })}
                  ) e penalidades.
                </span>
              </SymptomBanner>

              {(result.energy_deficit_kwh > 0 ||
                result.energy_surplus_kwh > 0 ||
                result.budget_limit_brl !== null) && (
                <div className="flex flex-wrap gap-2 text-xs">
                  {result.energy_deficit_kwh > 0 && (
                    <SymptomBanner tone="warning">
                      Déficit energético estimado:{" "}
                      {result.energy_deficit_kwh.toFixed(1)} kWh/mês
                    </SymptomBanner>
                  )}
                  {result.energy_surplus_kwh > 0 && (
                    <SymptomBanner tone="success">
                      Excedente energético estimado:{" "}
                      {result.energy_surplus_kwh.toFixed(1)} kWh/mês
                    </SymptomBanner>
                  )}
                  {result.budget_limit_brl !== null && (
                    <SymptomBanner tone={result.under_budget ? "success" : "error"}>
                      {result.under_budget
                        ? `Solução dentro do orçamento de R$ ${result.budget_limit_brl.toLocaleString("pt-BR")}`
                        : `Solução acima do orçamento informado`}
                    </SymptomBanner>
                  )}
                </div>
              )}

              <div className="flex items-center gap-2">
                <ChevronRight
                  className="h-4 w-4 text-ink-400"
                  aria-hidden
                />
                <button
                  type="button"
                  onClick={() => setActiveTab("analysis")}
                  className="inline-flex items-center gap-2 rounded-xl border border-ink-200 bg-white px-3.5 py-2 text-sm font-medium text-ink-700 shadow-sm transition hover:bg-ink-50"
                >
                  <Activity className="h-4 w-4 text-brand-600" aria-hidden />
                  Ver análise comparativa do AG
                </button>
              </div>

              <DashboardPage outcome={outcome} result={result} />

              <AnalysisPage
                outcome={outcome}
                result={result}
                baseline={baselineResult}
              />

              <ExperimentsPage
                busy={experimentsBusy}
                onRun={runExperiments}
                sensitivity={sensitivityPoints}
                popTiming={popTiming}
                genTiming={genTiming}
              />
            </>
          )}

          {phase === "error" && !outcome && (
            <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800">
              <div className="flex items-start gap-2">
                <AlertTriangle
                  className="mt-0.5 h-4 w-4 shrink-0"
                  aria-hidden
                />
                <span>
                  A otimização falhou. Verifique a conexão com a API e os dados
                  informados.
                </span>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
