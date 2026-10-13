import { Loader2, PlayCircle, Sparkles } from "lucide-react";

interface Props {
  onRun: () => void;
  busy: boolean;
}

export function EmptyState({ onRun, busy }: Props) {
  return (
    <section
      aria-label="Nenhum resultado"
      className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-ink-300 bg-white px-6 py-14 text-center"
    >
      <div className="grid h-14 w-14 place-items-center rounded-2xl bg-brand-50 text-brand-600 ring-1 ring-inset ring-brand-100">
        <Sparkles className="h-7 w-7" aria-hidden />
      </div>
      <h2 className="mt-4 text-lg font-semibold text-ink-900">
        Configure o problema e execute a otimização
      </h2>
      <p className="mt-1 max-w-md text-sm text-ink-500">
        Informe as dimensões do telhado, o consumo mensal e os parâmetros do
        algoritmo genético na barra lateral. Ao executar, o sistema retornará o
        número recomendado de painéis, a energia estimada e o custo.
      </p>
      <button
        type="button"
        onClick={onRun}
        disabled={busy}
        className="mt-6 inline-flex items-center gap-2 rounded-xl bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 disabled:opacity-60"
      >
        {busy ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
            Executando…
          </>
        ) : (
          <>
            <PlayCircle className="h-4 w-4" aria-hidden />
            Executar otimização
          </>
        )}
      </button>
    </section>
  );
}
