import { useState } from "react";
import { ChevronDown, Settings2, Sun } from "lucide-react";

// --- types -----------------------------------------------------------------
export interface RoofForm {
  width_m: number;
  length_m: number;
  monthly_consumption_kwh: number;
  roof_type: string;
  max_budget_brl: number | null;
}

export interface GAForm {
  population_size: number;
  generations: number;
  crossover_rate: number;
  mutation_rate: number;
  elitism_count: number;
  random_seed: number;
}

export const roofDefaults: RoofForm = {
  width_m: 8,
  length_m: 10,
  monthly_consumption_kwh: 300,
  roof_type: "ceramic",
  max_budget_brl: null,
};

export const gaDefaults: GAForm = {
  population_size: 60,
  generations: 120,
  crossover_rate: 0.8,
  mutation_rate: 0.1,
  elitism_count: 2,
  random_seed: 42,
};

// --- reusable field wrappers ------------------------------------------------
function NumberField({
  label,
  value,
  onChange,
  min,
  max,
  step = 1,
  unit,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  min?: number;
  max?: number;
  step?: number;
  unit?: string;
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-medium text-ink-600">
        {label}
        {unit && <span className="ml-1 text-ink-400">({unit})</span>}
      </span>
      <input
        type="number"
        value={value}
        min={min}
        max={max}
        step={step}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full rounded-lg border border-ink-200 bg-white px-2.5 py-2 text-sm text-ink-900 shadow-sm transition focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
      />
    </label>
  );
}

function SliderField({
  label,
  value,
  min,
  max,
  step,
  onChange,
  display,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (v: number) => void;
  display: string;
}) {
  return (
    <label className="block">
      <span className="mb-1.5 flex items-center justify-between text-xs font-medium text-ink-600">
        {label}
        <span className="font-mono text-brand-700">{display}</span>
      </span>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-brand-600"
      />
    </label>
  );
}

// --- main component ---------------------------------------------------------
interface Props {
  cities: string[];
  roof: RoofForm;
  onRoofChange: (r: RoofForm) => void;
  ga: GAForm;
  onGaChange: (g: GAForm) => void;
  city: string;
  onCityChange: (c: string) => void;
}

export function DashboardForm({
  cities,
  roof,
  onRoofChange,
  ga,
  onGaChange,
  city,
  onCityChange,
}: Props) {
  const [showGA, setShowGA] = useState(false);

  const setRoofField = <K extends keyof RoofForm>(key: K, value: RoofForm[K]) => {
    onRoofChange({ ...roof, [key]: value });
  };
  const setGAField = <K extends keyof GAForm>(key: K, value: GAForm[K]) => {
    onGaChange({ ...ga, [key]: value });
  };

  return (
    <div className="space-y-4">
      {/* Roof inputs ------------------------------------------------------- */}
      <section className="rounded-2xl border border-ink-200 bg-white p-4 shadow-sm">
        <h2 className="mb-4 flex items-center gap-2 text-sm font-semibold text-ink-900">
          <Sun className="h-4 w-4 text-solar-500" aria-hidden />
          Telhado e consumo
        </h2>

        <div className="space-y-3">
          <NumberField
            label="Largura do telhado"
            unit="m"
            value={roof.width_m}
            min={1}
            step={0.5}
            onChange={(v) => setRoofField("width_m", v)}
          />
          <NumberField
            label="Comprimento do telhado"
            unit="m"
            value={roof.length_m}
            min={1}
            step={0.5}
            onChange={(v) => setRoofField("length_m", v)}
          />
          <NumberField
            label="Consumo mensal"
            unit="kWh"
            value={roof.monthly_consumption_kwh}
            min={50}
            step={10}
            onChange={(v) => setRoofField("monthly_consumption_kwh", v)}
          />

          <label className="block">
            <span className="mb-1 block text-xs font-medium text-ink-600">
              Tipo de telhado
            </span>
            <div className="relative">
              <select
                value={roof.roof_type}
                onChange={(e) => setRoofField("roof_type", e.target.value)}
                className="w-full appearance-none rounded-lg border border-ink-200 bg-white px-2.5 py-2 text-sm text-ink-900 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
              >
                <option value="ceramic">Cerâmico</option>
                <option value="fibrocement">Fibrocimento</option>
                <option value="metallic">Metálico</option>
                <option value="mixed">Misto</option>
              </select>
              <ChevronDown
                className="pointer-events-none absolute right-2.5 top-2.5 h-4 w-4 text-ink-400"
                aria-hidden
              />
            </div>
          </label>

          <label className="block">
            <span className="mb-1 block text-xs font-medium text-ink-600">
              Cidade / região
            </span>
            <div className="relative">
              <select
                value={city}
                onChange={(e) => onCityChange(e.target.value)}
                className="w-full appearance-none rounded-lg border border-ink-200 bg-white px-2.5 py-2 text-sm text-ink-900 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
              >
                {cities.length === 0 && <option value="">Carregando…</option>}
                {cities.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
              <ChevronDown
                className="pointer-events-none absolute right-2.5 top-2.5 h-4 w-4 text-ink-400"
                aria-hidden
              />
            </div>
          </label>

          <div className="flex items-center justify-between rounded-lg bg-ink-50 px-3 py-2">
            <span className="text-xs font-medium text-ink-600">
              Definir orçamento máximo
            </span>
            <input
              type="checkbox"
              checked={roof.max_budget_brl !== null}
              onChange={(e) =>
                setRoofField(
                  "max_budget_brl",
                  e.target.checked ? 40000 : null,
                )
              }
              className="h-4 w-4 rounded border-ink-300 accent-brand-600"
            />
          </div>

          {roof.max_budget_brl !== null && (
            <NumberField
              label="Orçamento máximo"
              unit="R$"
              value={roof.max_budget_brl}
              min={1000}
              step={500}
              onChange={(v) => setRoofField("max_budget_brl", v)}
            />
          )}
        </div>
      </section>

      {/* GA parameters (collapsible) --------------------------------------- */}
      <section className="rounded-2xl border border-ink-200 bg-white shadow-sm">
        <button
          type="button"
          onClick={() => setShowGA((s) => !s)}
          aria-expanded={showGA}
          className="flex w-full items-center justify-between px-4 py-4 text-left"
        >
          <h2 className="flex items-center gap-2 text-sm font-semibold text-ink-900">
            <Settings2 className="h-4 w-4 text-ink-400" aria-hidden />
            Parâmetros do AG
          </h2>
          <ChevronDown
            className={`h-4 w-4 text-ink-400 transition-transform ${showGA ? "rotate-180" : ""}`}
            aria-hidden
          />
        </button>

        {showGA && (
          <div className="space-y-4 border-t border-ink-100 px-4 py-4">
            <SliderField
              label="População"
              value={ga.population_size}
              min={20}
              max={200}
              step={10}
              display={String(ga.population_size)}
              onChange={(v) => setGAField("population_size", v)}
            />
            <SliderField
              label="Gerações"
              value={ga.generations}
              min={20}
              max={300}
              step={10}
              display={String(ga.generations)}
              onChange={(v) => setGAField("generations", v)}
            />
            <SliderField
              label="Crossover"
              value={ga.crossover_rate}
              min={0.1}
              max={1}
              step={0.05}
              display={ga.crossover_rate.toFixed(2)}
              onChange={(v) => setGAField("crossover_rate", v)}
            />
            <SliderField
              label="Mutação"
              value={ga.mutation_rate}
              min={0.01}
              max={0.5}
              step={0.01}
              display={ga.mutation_rate.toFixed(2)}
              onChange={(v) => setGAField("mutation_rate", v)}
            />
            <SliderField
              label="Elitismo"
              value={ga.elitism_count}
              min={1}
              max={10}
              step={1}
              display={String(ga.elitism_count)}
              onChange={(v) => setGAField("elitism_count", v)}
            />
            <NumberField
              label="Seed"
              value={ga.random_seed}
              min={0}
              step={1}
              onChange={(v) => setGAField("random_seed", v)}
            />
          </div>
        )}
      </section>
    </div>
  );
}