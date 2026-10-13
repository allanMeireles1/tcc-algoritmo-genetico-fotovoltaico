import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { FlaskConical, Loader2 } from "lucide-react";

import { fmt } from "../lib/format";

import type { SensitivityPointDTO, TimingPointDTO } from "../types/api";

interface Props {
  busy: boolean;
  onRun: () => void;
  sensitivity: SensitivityPointDTO[];
  popTiming: TimingPointDTO[];
  genTiming: TimingPointDTO[];
}

const AXIS = { fontSize: 11, fill: "#64748b" };

export function ExperimentsPage({ busy, onRun, sensitivity, popTiming, genTiming }: Props) {
  const hasData = sensitivity.length > 0 || popTiming.length > 0 || genTiming.length > 0;

  const sensData = sensitivity.map((p) => ({
    consumo: Number(p.consumption_kwh.toFixed(1)),
    painéis: p.best_panels,
    fitness: Number(p.best_fitness.toFixed(2)),
    tempo: Number(p.execution_time_s.toFixed(3)),
  }));

  const timingData = [...popTiming, ...genTiming].map((p) => ({
    tipo: p.label,
    valor: p.parameter_value,
    tempo: Number(p.execution_time_s.toFixed(3)),
    painéis: p.best_panels,
  }));

  return (
    <section className="space-y-4">
      <div className="rounded-2xl border border-ink-200 bg-white p-4 shadow-sm">
        <h2 className="flex items-center gap-2 text-sm font-semibold text-ink-900">
          <FlaskConical className="h-4 w-4 text-brand-600" aria-hidden />
          Experimentos de sensibilidade e desempenho
        </h2>
        <p className="mt-1 text-xs text-ink-500">
          Estes testes reforçam o valor acadêmico: escalabilidade do problema e
          custo computacional do AG.
        </p>
        <button
          type="button"
          onClick={onRun}
          disabled={busy}
          className="mt-3 inline-flex items-center gap-2 rounded-xl border border-ink-200 bg-white px-3.5 py-2 text-sm font-medium text-ink-700 shadow-sm transition hover:bg-ink-50 disabled:opacity-60"
        >
          {busy ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
              Executando experimentos…
            </>
          ) : (
            "Executar experimentos"
          )}
        </button>
      </div>

      {hasData && (
        <>
          <figure className="rounded-2xl border border-ink-200 bg-white p-4 shadow-sm">
            <figcaption className="mb-3">
              <p className="text-sm font-semibold text-ink-900">
                Sensibilidade ao consumo
              </p>
              <p className="text-xs text-ink-500">
                Como o número de painéis responde à variação do consumo mensal.
              </p>
            </figcaption>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={sensData} margin={{ top: 4, right: 16, bottom: 4, left: -12 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis
                    dataKey="consumo"
                    tick={AXIS}
                    label={{ value: "Consumo (kWh/mês)", position: "insideBottom", offset: -2, fontSize: 11, fill: "#64748b" }}
                  />
                  <YAxis tick={AXIS} allowDecimals={false} />
                  <Tooltip formatter={(v, name) => (name === "painéis" ? `${fmt(v, 0)} painéis` : fmt(v, 1))} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Line type="monotone" dataKey="painéis" stroke="#2563eb" strokeWidth={2} dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </figure>

          <figure className="rounded-2xl border border-ink-200 bg-white p-4 shadow-sm">
            <figcaption className="mb-3">
              <p className="text-sm font-semibold text-ink-900">
                Tempo de execução × população / gerações
              </p>
              <p className="text-xs text-ink-500">
                Custo computacional do AG em função dos parâmetros.
              </p>
            </figcaption>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={timingData} margin={{ top: 4, right: 16, bottom: 4, left: -12 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis
                    dataKey="valor"
                    tick={AXIS}
                    label={{ value: "Parâmetro", position: "insideBottom", offset: -2, fontSize: 11, fill: "#64748b" }}
                  />
                  <YAxis tick={AXIS} unit=" s" />
                  <Tooltip formatter={(v) => `${fmt(v, 3)} s`} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Line
                    type="monotone"
                    dataKey="tempo"
                    stroke="#0ea5e9"
                    strokeWidth={2}
                    dot={{ r: 3 }}
                    name="Tempo (s)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </figure>
        </>
      )}

      {!hasData && (
        <div className="rounded-2xl border border-dashed border-ink-300 bg-white px-6 py-8 text-center text-sm text-ink-500">
          Execute a otimização e, em seguida, clique em{" "}
          <span className="font-medium text-ink-700">Executar experimentos</span>{" "}
          para visualizar os gráficos de sensibilidade e desempenho.
        </div>
      )}
    </section>
  );
}