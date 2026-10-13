import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { BaselineResponse, OptimizationOutcomeDTO } from "../types/api";
import { fmt } from "../lib/format";

interface Props {
  outcome: OptimizationOutcomeDTO;
  result: OptimizationOutcomeDTO["result"];
  baseline: BaselineResponse | null;
}

const AXIS = { fontSize: 11, fill: "#64748b" };

function ChartCard({
  title,
  caption,
  children,
}: {
  title: string;
  caption: string;
  children: React.ReactNode;
}) {
  return (
    <figure className="rounded-2xl border border-ink-200 bg-white p-4 shadow-sm">
      <figcaption className="mb-3">
        <p className="text-sm font-semibold text-ink-900">{title}</p>
        <p className="text-xs text-ink-500">{caption}</p>
      </figcaption>
      <div className="h-64 w-full">{children}</div>
    </figure>
  );
}

export function AnalysisPage({ outcome, result, baseline }: Props) {
  // AG × baseline comparison ------------------------------------------------
  const comparison = [
    {
      métrica: "Painéis",
      AG: result.best_num_panels,
      "Método direto": baseline?.panels ?? result.benchmark_panels,
    },
    {
      métrica: "Energia (kWh/mês)",
      AG: Number(result.best_energy_kwh_month.toFixed(1)),
      "Método direto": Number(
        (baseline?.energy_kwh_month ?? result.benchmark_energy_kwh_month).toFixed(1),
      ),
    },
    {
      métrica: "Custo (R$ / 1000)",
      AG: Number((result.best_cost_brl / 1000).toFixed(2)),
      "Método direto": Number(
        ((baseline?.cost_brl ?? result.benchmark_cost_brl) / 1000).toFixed(2),
      ),
    },
  ];

  // Final population histogram ----------------------------------------------
  const bins = new Map<number, number>();
  for (const ind of outcome.final_population) {
    const key = Math.round(ind.num_panels);
    bins.set(key, (bins.get(key) ?? 0) + 1);
  }
  const histogram = [...bins.entries()]
    .sort((a, b) => a[0] - b[0])
    .map(([painéis, contagem]) => ({ painéis, contagem }));

  // Fitness composition ------------------------------------------------------
  const bd = outcome.fitness_breakdown;
  const composition = bd
    ? [
        { name: "Energia (kWh)", value: Number(bd.energy_term.toFixed(2)) },
        { name: "Penalidade de custo", value: Number((-bd.cost_penalty).toFixed(2)) },
        { name: "Penalidade de excesso", value: Number((-bd.waste_penalty).toFixed(2)) },
        { name: "Penalidade de déficit", value: Number((-bd.deficit_penalty).toFixed(2)) },
        { name: "Penalidade de área", value: Number((-bd.area_penalty).toFixed(2)) },
        { name: "Penalidade de orçamento", value: Number((-bd.budget_penalty).toFixed(2)) },
      ]
    : [];

  const COLORS = ["#2563eb", "#ef4444", "#f59e0b", "#8b5cf6", "#0ea5e9", "#64748b"];

  return (
    <section className="space-y-4">
      <ChartCard
        title="AG × método direto"
        caption="Por que usar AG em vez de cálculo direto?"
      >
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={comparison} margin={{ top: 4, right: 16, bottom: 4, left: -8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
            <XAxis dataKey="métrica" tick={{ ...AXIS, fontSize: 10 }} interval={0} />
            <YAxis tick={AXIS} />
            <Tooltip />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Bar dataKey="AG" fill="#2563eb" radius={[6, 6, 0, 0]} />
            <Bar dataKey="Método direto" fill="#f59e0b" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <div className="grid gap-4 lg:grid-cols-2">
        <ChartCard
          title="Histograma da população final"
          caption="Onde a população convergiu na última geração."
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={histogram} margin={{ top: 4, right: 12, bottom: 4, left: -12 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
              <XAxis
                dataKey="painéis"
                tick={AXIS}
                label={{
                  value: "Painéis",
                  position: "insideBottom",
                  offset: -2,
                  fontSize: 11,
                  fill: "#64748b",
                }}
              />
              <YAxis tick={AXIS} allowDecimals={false} />
              <Tooltip formatter={(v) => `${fmt(v, 0)} indivíduos`} />
              <Bar dataKey="contagem" fill="#2563eb" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="Composição da função de fitness"
          caption="Componentes da fitness da melhor solução (energia − penalidades)."
        >
          {bd ? (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={composition}
                  dataKey="value"
                  nameKey="name"
                  innerRadius={50}
                  outerRadius={85}
                  paddingAngle={2}
                  label={(props) => props.value.toFixed(0)}
                >
                  {composition.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v) => fmt(v, 2)} />
                <Legend wrapperStyle={{ fontSize: 10 }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="grid h-full place-items-center text-xs text-ink-400">
              Detalhamento não disponível para esta execução.
            </p>
          )}
        </ChartCard>
      </div>
    </section>
  );
}
