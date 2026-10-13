import type { ScenarioRunResultDTO } from "../types/api";
import { brl, fmt } from "../lib/format";

interface Summary {
  gross: number;
  usable: number;
  maxPanels: number;
  panelArea: number;
}

interface Props {
  result: ScenarioRunResultDTO;
  summary: Summary;
}

export function MetricCards({ result, summary }: Props) {
  const cards: { label: string; value: string; hint?: string }[] = [
    {
      label: "Painéis (AG)",
      value: String(result.best_num_panels),
      hint: `máx. pela área: ${summary.maxPanels}`,
    },
    {
      label: "Energia estimada",
      value: `${fmt(result.best_energy_kwh_month)} kWh/mês`,
      hint: `consumo: ${fmt(result.monthly_consumption_kwh)} kWh/mês`,
    },
    {
      label: "Custo estimado",
      value: `R$ ${brl(result.best_cost_brl)}`,
      hint:
        result.budget_limit_brl !== null
          ? `limite: R$ ${brl(result.budget_limit_brl)}`
          : undefined,
    },
    {
      label: "Ocupação útil",
      value: `${(result.roof_occupancy_ratio * 100).toFixed(1)}%`,
      hint: `${result.panel_area_m2.toFixed(1)} m² por painel`,
    },
  ];
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((c) => (
        <article
          key={c.label}
          className="rounded-2xl border border-ink-200 bg-white p-4 shadow-sm"
        >
          <p className="text-xs font-medium uppercase tracking-wide text-ink-500">
            {c.label}
          </p>
          <p className="mt-1 text-xl font-semibold tracking-tight text-ink-900">
            {c.value}
          </p>
          {c.hint && <p className="mt-1 text-xs text-ink-500">{c.hint}</p>}
        </article>
      ))}
    </div>
  );
}
