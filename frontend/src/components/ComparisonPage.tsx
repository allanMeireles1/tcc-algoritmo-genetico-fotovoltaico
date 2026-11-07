import { useEffect, useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { FlaskConical, Loader2, Table2 } from "lucide-react";

import { compare } from "../lib/api";
import { fmt, brl } from "../lib/format";

import type { ComparisonResponse, GAConfigDTO, RoofDTO } from "../types/api";

interface Props {
  roof: RoofDTO;
  config: GAConfigDTO;
}

const METHOD_LABEL: Record<string, string> = {
  analytical: "Solução analítica",
  exhaustive: "Busca exaustiva",
  genetic: "Algoritmo Genético",
};

const COLORS = [
  "#2563eb", "#dc2626", "#16a34a", "#d97706", "#7c3aed", "#0891b2",
  "#be185d", "#4d7c0f", "#b45309", "#1d4ed8", "#9d174d", "#047857",
  "#a21caf", "#b91c1c", "#15803d", "#c2410c", "#6d28d9", "#0e7490",
  "#831843", "#3f6212", "#92400e", "#1e40af", "#701a75", "#065f46",
  "#86198f", "#991b1b", "#166534", "#9a3412", "#5b21b6", "#155e75",
];

function mean(values: number[]) {
  return values.reduce((a, b) => a + b, 0) / values.length;
}

function median(values: number[]) {
  const s = [...values].sort((a, b) => a - b);
  const mid = Math.floor(s.length / 2);
  return s.length % 2 ? s[mid] : (s[mid - 1] + s[mid]) / 2;
}

function stdev(values: number[]) {
  const m = mean(values);
  return Math.sqrt(values.reduce((a, b) => a + (b - m) * (b - m), 0) / values.length);
}

function quantile(sorted: number[], q: number) {
  const pos = (sorted.length - 1) * q;
  const base = Math.floor(pos);
  const rest = pos - base;
  if (rest === 0) return sorted[base];
  return sorted[base] + rest * (sorted[base + 1] - sorted[base]);
}

export function ComparisonPage({ roof, config }: Props) {
  const [data, setData] = useState<ComparisonResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hiddenSeeds, setHiddenSeeds] = useState<Set<number>>(new Set());
  const [focusSeed, setFocusSeed] = useState<number | null>(null);

  const runComparison = async () => {
    setBusy(true);
    setError(null);
    setData(null);
    try {
      setData(
        await compare({
          roof,
          config,
          runs: 30,
        }),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao comparar métodos.");
    } finally {
      setBusy(false);
    }
  };

  const geneticResults = useMemo(
    () => (data?.results ?? []).filter((r) => r.method === "genetic"),
    [data],
  );

  const times = geneticResults.map((r) => r.execution_time_s);
  const summary = data?.summary as
    | {
        exhaustive_panels?: number;
        exhaustive_feasible?: boolean;
      }
    | undefined;

  // Limpa os resultados quando o input muda, evitando que o usuário
  // interprete dados de uma configuração anterior como se fossem da atual.
  useEffect(() => {
    setData(null);
    setError(null);
    setHiddenSeeds(new Set());
    setFocusSeed(null);
  }, [roof, config]);

  const optimalCount = geneticResults.filter(
    (r) =>
      r.evaluation.num_panels === summary?.exhaustive_panels &&
      r.evaluation.feasible === summary?.exhaustive_feasible,
  ).length;

  // Convergence data – best panels per generation per seed.
  const convergence = useMemo(() => {
    const histories = data?.histories ?? [];
    const length = Math.max(0, ...histories.map((h) => h.generations.length));
    return Array.from({ length }, (_, i) => {
      const row: Record<string, number | string> = {
        generation: histories[0]?.generations[i]?.generation ?? i + 1,
      };
      for (const h of histories) {
        const g = h.generations[i];
        if (g) row[`seed_${h.seed}`] = g.best_panels;
      }
      return row;
    });
  }, [data]);

  // Histogram of AG execution times (ms).
  const timeHistogram = useMemo(() => {
    if (!times.length) return [];
    const ms = times.map((t) => t * 1000);
    const min = Math.min(...ms);
    const max = Math.max(...ms);
    if (min === max) {
      return [{ label: `${min.toFixed(1)} ms`, count: ms.length }];
    }
    const width = (max - min) / 8;
    const bins = Array.from({ length: 8 }, (_, i) => ({
      label: `${(min + i * width).toFixed(1)}–${(min + (i + 1) * width).toFixed(1)}`,
      count: 0,
    }));
    for (const v of ms) {
      const idx = Math.min(7, Math.floor((v - min) / width));
      bins[idx].count += 1;
    }
    return bins;
  }, [times]);

  const handleLegendClick = (seed: number) => {
    setHiddenSeeds((prev) => {
      const next = new Set(prev);
      if (next.has(seed)) next.delete(seed);
      else next.add(seed);
      return next;
    });
  };

  const seedOptions = (data?.histories ?? []).map((h) => h.seed);

  return (
    <section className="space-y-4" aria-label="Comparação entre métodos" aria-busy={busy}>
      <div className="rounded-2xl border border-ink-200 bg-white p-4 shadow-sm">
        <h2 className="flex items-center gap-2 text-sm font-semibold text-ink-900">
          <FlaskConical className="h-4 w-4 text-brand-600" aria-hidden />
          Comparação entre métodos (AG v2 × analítico × exaustivo)
        </h2>
        <p className="mt-1 text-xs text-ink-500">
          Executa o AG com 30 sementes e compara com a solução determinística no mesmo problema.
          Os históricos de convergência vêm diretamente do backend.
        </p>
        <button
          type="button"
          onClick={runComparison}
          disabled={busy}
          className="mt-3 inline-flex items-center gap-2 rounded-xl bg-brand-600 px-3.5 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {busy ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
              Executando comparação…
            </>
          ) : (
            "Executar comparação (30 seeds)"
          )}
        </button>
        {error && (
          <div className="mt-3 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800" role="alert">
            {error}
          </div>
        )}
      </div>

      {data && (
        <>
          {/* Identificação da configuração executada */}
          <div className="rounded-2xl border border-ink-200 bg-white p-3 shadow-sm">
            <p className="text-xs text-ink-500">
              Configuração usada para esta comparação:
            </p>
            <ul className="list-disc list-inside mt-1 text-sm text-ink-700 space-y-1">
              <li>Cidade: <strong>{roof.city}</strong></li>
              <li>Consumo: <strong>{roof.monthly_consumption_kwh.toFixed(0)} kWh/mês</strong></li>
              <li>
                Telhado: <strong>{roof.width_m} × {roof.length_m} m</strong>{" "}
                {roof.max_budget_brl != null ? `· orçamento R$ {roof.max_budget_brl}` : ""}
              </li>
              <li>
                AG: população <strong>{config.population_size}</strong> · gerações{" "}
                <strong>{config.generations}</strong> · seed <strong>{config.random_seed}</strong>
              </li>
              <li>Execuções: <strong>{typeof data.summary.runs === "number" ? data.summary.runs : 0}</strong> seeds independentes</li>
            </ul>
          </div>

          {/* Resumo cards */}
          <div className="grid gap-4 lg:grid-cols-3">
            {(["analytical", "exhaustive", "genetic"] as const).map((method) => {
              const rows = data.results.filter((r) => r.method === method);
              const ev = rows[0]?.evaluation;
              if (method === "genetic") {
                const ms = times.map((t) => t * 1000);
                const avg = mean(ms);
                const sd = stdev(ms);
                const med = median(ms);
                const sorted = [...ms].sort((a, b) => a - b);
                const q1 = quantile(sorted, 0.25);
                const q3 = quantile(sorted, 0.75);
                return (
                  <div key={method} className="rounded-2xl border border-ink-200 bg-white p-4 shadow-sm">
                    <p className="text-xs font-medium uppercase tracking-wide text-ink-500">
                      Algoritmo Genético ({rows.length} execuções)
                    </p>
                    <p className="mt-2 text-2xl font-semibold text-ink-900">
                      {optimalCount}/{rows.length}
                      <span className="ml-2 text-sm font-medium text-ink-500">atingiram o ótimo</span>
                    </p>
                    <p className="mt-1 text-xs text-ink-500">
                      Tempo médio ± desvio‑padrão: {avg.toFixed(2)} ± {sd.toFixed(2)} ms<br />
                      Mediana (IQR {q1.toFixed(2)}–{q3.toFixed(2)} ms): {med.toFixed(2)} ms
                    </p>
                    {ev && (
                      <p className="mt-1 text-xs text-ink-500">
                        Melhor resultado: {ev.num_panels} módulos · custo {brl(ev.cost)} R$
                      </p>
                    )}
                  </div>
                );
              }
              return (
                <div key={method} className="rounded-2xl border border-ink-200 bg-white p-4 shadow-sm">
                  <p className="text-xs font-medium uppercase tracking-wide text-ink-500">
                    {METHOD_LABEL[method]}
                  </p>
                  {ev ? (
                    <>
                      <p className="mt-2 text-2xl font-semibold text-ink-900">
                        {ev.num_panels} <span className="text-sm font-medium text-ink-500">módulos</span>
                      </p>
                      <p className="mt-1 text-xs text-ink-500">
                        Viável: {ev.feasible ? "sim" : "não"} · Custo: {brl(ev.cost)} R$ · Tempo: {fmt((rows[0]?.execution_time_s ?? 0) * 1000, 2)} ms
                      </p>
                    </>
                  ) : (
                    <p className="mt-2 text-sm text-ink-400">Sem resultados.</p>
                  )}
                </div>
              );
            })}
          </div>

          {/* Convergência */}
          <figure className="rounded-2xl border border-ink-200 bg-white p-4 shadow-sm">
            <figcaption className="mb-3">
              <p className="text-sm font-semibold text-ink-900">Convergência por seed</p>
              <p className="text-xs text-ink-500">
                Número de painéis por geração (não é a fitness; cada linha corresponde a uma seed). Clique na legenda para ocultar/mostrar curvas.
              </p>
              {seedOptions.length > 0 && (
                <div className="mt-2 flex items-center gap-2 text-xs">
                  <label htmlFor="seedFocus" className="text-ink-600">Destacar seed:</label>
                  <select
                    id="seedFocus"
                    className="rounded border border-ink-300 bg-white p-1"
                    value={focusSeed ?? ""}
                    onChange={(e) => setFocusSeed(e.target.value ? Number(e.target.value) : null)}
                  >
                    <option value="">Todas</option>
                    {seedOptions.map((s) => (
                      <option key={s} value={s}>seed {s}</option>
                    ))}
                  </select>
                </div>
              )}
            </figcaption>
            <div className="h-64 w-full" role="img" aria-label="Gráfico de convergência: número de painéis por geração para cada seed">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={convergence} margin={{ top: 4, right: 16, bottom: 4, left: -12 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="generation" tick={{ fontSize: 11, fill: "#64748b" }} label={{ value: "Geração", position: "insideBottom", offset: -2, fontSize: 11, fill: "#64748b" }} />
                  <YAxis tick={{ fontSize: 11, fill: "#64748b" }} allowDecimals={false} label={{ value: "Painéis", angle: -90, position: "insideLeft", offset: 0, fontSize: 11, fill: "#64748b" }} />
                  <Tooltip />
                  <Legend wrapperStyle={{ fontSize: 10 }} onClick={(e: any) => {
                    const key = String(e?.dataKey ?? e?.payload?.dataKey ?? "");
                    const seed = Number(key.replace("seed_", ""));
                    if (Number.isFinite(seed)) handleLegendClick(seed);
                  }} />
                  {data?.histories
                    ?.filter((h) => !hiddenSeeds.has(h.seed))
                    .map((h, i) => {
                      const isFocused = focusSeed !== null && focusSeed !== h.seed;
                      return (
                        <Line
                          key={h.seed}
                          type="stepAfter"
                          dataKey={`seed_${h.seed}`}
                          name={`seed ${h.seed}`}
                          stroke={COLORS[i % COLORS.length]}
                          strokeWidth={isFocused ? 1 : 2}
                          opacity={isFocused ? 0.3 : 1}
                          dot={false}
                        />
                      );
                    })}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </figure>

          {/* Histograma de tempos */}
          <figure className="rounded-2xl border border-ink-200 bg-white p-4 shadow-sm">
            <figcaption className="mb-3">
              <p className="text-sm font-semibold text-ink-900">Distribuição dos tempos do AG</p>
              <p className="text-xs text-ink-500">
                Histograma das 30 execuções genéticas (ms). Os métodos determinísticos não entram nesta distribuição.
              </p>
            </figcaption>
            <div className="h-64 w-full" role="img" aria-label="Histograma de distribuição de tempos de execução do AG (milissegundos), com 30 execuções">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={timeHistogram} margin={{ top: 4, right: 16, bottom: 4, left: -12 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                  <XAxis dataKey="label" tick={{ fontSize: 10, fill: "#64748b" }} />
                  <YAxis tick={{ fontSize: 11, fill: "#64748b" }} allowDecimals={false} />
                  <Tooltip formatter={(v) => `${fmt(v, 0)} execuções`} />
                  <Bar dataKey="count" name="Execuções" fill="#2563eb" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </figure>

          {/* Tabela completa */}
          <div className="rounded-2xl border border-ink-200 bg-white p-4 shadow-sm">
            <h3 className="flex items-center gap-2 text-sm font-semibold text-ink-900">
              <Table2 className="h-4 w-4 text-brand-600" aria-hidden />
              Todas as execuções ({data.results.length})
            </h3>
            <div className="mt-3 max-h-96 overflow-auto" role="region" aria-label="Tabela de resultados">
              <table className="w-full text-left text-sm text-ink-700" aria-describedby="tabela-resultados">
                <thead className="sticky top-0 bg-white text-xs uppercase tracking-wide text-ink-500" id="tabela-resultados">
                  <tr>
                    <th className="py-2 pr-4">Método</th>
                    <th className="py-2 pr-4">Seed</th>
                    <th className="py-2 pr-4">Painéis</th>
                    <th className="py-2 pr-4">Viável</th>
                    <th className="py-2 pr-4">Custo (R$)</th>
                    <th className="py-2 pr-4">Tempo (ms)</th>
                  </tr>
                </thead>
                <tbody className="text-ink-900">
                  {data.results.map((r, i) => (
                    <tr key={`${r.method}-${r.run_index}-${i}`} className="border-t border-ink-100">
                      <td className="py-2 pr-4 font-medium">{METHOD_LABEL[r.method] ?? r.method}</td>
                      <td className="py-2 pr-4">{r.run_seed ?? "—"}</td>
                      <td className="py-2 pr-4">{r.evaluation.num_panels}</td>
                      <td className="py-2 pr-4">{r.evaluation.feasible ? "sim" : "não"}</td>
                      <td className="py-2 pr-4">{brl(r.evaluation.cost)}</td>
                      <td className="py-2 pr-4">{fmt(r.execution_time_s * 1000, 2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </section>
  );
}
