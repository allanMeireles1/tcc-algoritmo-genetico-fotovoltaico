import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  BarChart,
  Bar,
  Cell,
} from "recharts";

import { fmt } from "../lib/format"

import type { OptimizationOutcomeDTO } from "../types/api";

interface Props {
  outcome: OptimizationOutcomeDTO;
  result: OptimizationOutcomeDTO["result"];
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

export function DashboardPage({ outcome, result }: Props) {
  const history = outcome.history;

  // Subsample the history so the chart stays readable for long runs.
  const maxPoints = 60;
  const stride = Math.max(1, Math.ceil(history.length / maxPoints));
  const convergence = history
    .filter((_, i) => i % stride === 0 || i === history.length - 1)
    .map((h) => ({
      generation: h.generation,
      melhor: Number(h.best_fitness.toFixed(3)),
      media: Number(h.avg_fitness.toFixed(3)),
    }));

  const energy = [
    {
      nome: "Consumo da residência",
      valor: Number(result.monthly_consumption_kwh.toFixed(1)),
    },
    {
      nome: "Geração estimada (AG)",
      valor: Number(result.best_energy_kwh_month.toFixed(1)),
    },
  ];

  const occupancy = [
    {
      nome: "Área útil",
      ocupada: Number(result.roof_occupancy_ratio.toFixed(4)),
      livre: Number((1 - result.roof_occupancy_ratio).toFixed(4)),
    },
  ];

  const surplusDeficit = [
    {
      nome: "Balanço",
      Déficit: Number(result.energy_deficit_kwh.toFixed(1)),
      Excedente: Number(result.energy_surplus_kwh.toFixed(1)),
    },
  ];

  return (
    <section className="space-y-4">
      <ChartCard
        title="Evolução do fitness (convergência)"
        caption="O algoritmo melhora as soluções ao longo das gerações."
      >
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={convergence} margin={{ top: 4, right: 12, bottom: 4, left: -12 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="generation" tick={AXIS} />
            <YAxis tick={AXIS} />
            <Tooltip
              formatter={(value) => fmt(value, 3)}
              labelFormatter={(label) => `Geração ${label}`}
            />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Line
              type="monotone"
              dataKey="melhor"
              stroke="#2563eb"
              strokeWidth={2}
              dot={false}
              name="Melhor fitness"
            />
            <Line
              type="monotone"
              dataKey="media"
              stroke="#94a3b8"
              strokeWidth={1.5}
              strokeDasharray="4 3"
              dot={false}
              name="Fitness médio"
            />
          </LineChart>
        </ResponsiveContainer>
      </ChartCard>

      <div className="grid gap-4 lg:grid-cols-2">
        <ChartCard
          title="Geração estimada × consumo"
          caption="A solução atende (ou não) o consumo da residência."
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={energy} margin={{ top: 4, right: 12, bottom: 4, left: -8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
              <XAxis dataKey="nome" tick={{ ...AXIS, fontSize: 10 }} interval={0} />
              <YAxis tick={AXIS} unit=" kWh" />
              <Tooltip formatter={(v) => `${fmt(v)} kWh/mês`} />
              <Bar dataKey="valor" radius={[6, 6, 0, 0]}>
                <Cell fill="#f59e0b" />
                <Cell fill="#16a34a" />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="Balanço energético"
          caption="Déficit quando a geração fica abaixo do consumo; excedente quando ultrapassa."
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              layout="vertical"
              data={surplusDeficit}
              margin={{ top: 4, right: 16, bottom: 4, left: 24 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
              <XAxis type="number" tick={AXIS} unit=" kWh" />
              <YAxis type="category" dataKey="nome" tick={AXIS} width={70} />
              <Tooltip formatter={(v) => `${fmt(v)} kWh/mês`} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Bar dataKey="Déficit" stackId="a" fill="#dc2626" radius={[0, 6, 6, 0]} />
              <Bar dataKey="Excedente" stackId="a" fill="#16a34a" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <ChartCard
        title="Ocupação do telhado"
        caption="Restrição física do telhado aplicada ao dimensionamento."
      >
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            layout="vertical"
            data={occupancy}
            margin={{ top: 4, right: 16, bottom: 4, left: 24 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
            <XAxis
              type="number"
              domain={[0, 1]}
              tick={AXIS}
              tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`}
            />
            <YAxis type="category" dataKey="nome" tick={AXIS} width={70} />
            <Tooltip
              formatter={(v) => `${((typeof v === "number" ? v : 0) * 100).toFixed(1)}%`}
            />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Bar dataKey="ocupada" stackId="a" name="Ocupada" fill="#2563eb" radius={[6, 0, 0, 6]} />
            <Bar dataKey="livre" stackId="a" name="Livre" fill="#e2e8f0" radius={[0, 6, 6, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
    </section>
  );
}
