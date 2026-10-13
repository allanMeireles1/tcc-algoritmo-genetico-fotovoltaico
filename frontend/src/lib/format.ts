/**
 * Recharts `Tooltip.formatter` passes `ValueType | undefined`, which is not
 * guaranteed to be a number. This narrows it safely for display purposes.
 */
export function fmt(value: unknown, digits = 1): string {
  if (typeof value === "number") return value.toFixed(digits);
  if (Array.isArray(value)) return value.map((v) => String(v)).join(", ");
  return value == null ? "" : String(value);
}

export function brl(value: number): string {
  return value.toLocaleString("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}