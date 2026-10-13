interface Props {
  width: number;
  length: number;
  occupancy: number;
  panelArea: number;
  numPanels: number;
}

export function RoofSketch({ width, length, occupancy, panelArea, numPanels }: Props) {
  const totalArea = width * length;
  const usedArea = numPanels * panelArea;
  const occupancyPercent = occupancy * 100;

  return (
    <section
      aria-label="Layout esquemático do telhado"
      className="rounded-2xl border border-ink-200 bg-white p-4 shadow-sm"
    >
      <h2 className="mb-4 text-sm font-medium uppercase tracking-wide text-ink-500">
        Layout esquemático
      </h2>
      <p className="mb-4 text-sm text-ink-500">
        Área total do telhado: <span className="font-semibold text-ink-900">
          {totalArea.toFixed(1)} m²
        </span> · Área útil ocupada: <span className="font-semibold text-ink-900">
          {usedArea.toFixed(1)} m²
        </span> · Ocupação: <span className="font-semibold text-ink-900">{occupancyPercent.toFixed(1)}%</span>
      </p>

      <div className="relative h-48 w-full rounded-md overflow-hidden bg-gradient-to-br from-solar-50 via-solar-100 to-solar-100">
        {/* Simplified schematic */}
        <div
          className="absolute inset-0 bg-gradient-to-tr from-brand-400 to-brand-600 opacity-15"
        />
        <svg
          className="absolute inset-0 pointer-events-none"
          viewBox="0 0 120 80"
          aria-label="schematic"
        >
          {/* Roof outline */}
          <path
            d="M2 2 L118 2 L118 78 L2 78 Z"
            fill="none"
            stroke="brand-700"
            strokeWidth={1.5}
          />
          {/* Panels grid */}
          <g fill="brand-600" stroke="none">
            {Array.from({ length: Math.ceil(numPanels / 3) }, (_, i) => (
              <rect
                key={i}
                x={10 + (i % 3) * 35}
                y={12 + Math.floor(i / 3) * 24}
                width={30}
                height={18}
              />
            ))}
          </g>
          {/* Label */}
          <text
            x="50%"
            y="50%"
            textAnchor="middle"
            dominantBaseline="middle"
            fill="brand-700"
            fontSize={10}
          >
            {numPanels > 0 ? `${numPanels} painéis` : "—"}
          </text>
        </svg>
      </div>

      <p className="mt-3 text-xs text-ink-500">
        {numPanels > 0 ? "Painéis estimados" : "Nenhum cálculo ainda"}
      </p>
    </section>
  );
}