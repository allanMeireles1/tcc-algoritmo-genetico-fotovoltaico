const API_BASE = import.meta.env.VITE_API_URL ?? "/api";

function buildUrl(path: string) {
  return `${API_BASE}${path}`;
}

export async function getCities(): Promise<string[]> {
  const res = await fetch(buildUrl("/cities"));
  if (!res.ok) throw new Error(`GET /cities failed: ${res.status}`);
  return res.json();
}

export async function getPanels(): Promise<Record<string, unknown>[]> {
  const res = await fetch(buildUrl("/panels"));
  if (!res.ok) throw new Error(`GET /panels failed: ${res.status}`);
  return res.json();
}

export async function optimize(payload: {
  roof: {
    width_m: number;
    length_m: number;
    monthly_consumption_kwh: number;
    city: string;
    roof_type: string;
    max_budget_brl: number | null;
  };
  config: unknown;
  runs: number;
}) {
  const res = await fetch(buildUrl("/optimize"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(body || `optimize failed: ${res.status}`);
  }
  return res.json();
}

export async function baseline(payload: unknown) {
  const res = await fetch(buildUrl("/baseline"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`baseline failed: ${res.status}`);
  return res.json();
}

export async function sensitivity(payload: unknown) {
  const res = await fetch(buildUrl("/experiments/sensitivity"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`sensitivity failed: ${res.status}`);
  return res.json();
}

export async function populationTiming(payload: unknown) {
  const res = await fetch(buildUrl("/experiments/population-timing"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`population-timing failed: ${res.status}`);
  return res.json();
}

export async function generationsTiming(payload: unknown) {
  const res = await fetch(buildUrl("/experiments/generations-timing"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`generations-timing failed: ${res.status}`);
  return res.json();
}