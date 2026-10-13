import type { ReactNode } from "react";
import { AlertTriangle, CheckCircle2, Info, XCircle } from "lucide-react";

type Tone = "info" | "success" | "warning" | "error";

const toneStyles: Record<Tone, { wrap: string; icon: ReactNode }> = {
  info: {
    wrap: "border-brand-200 bg-brand-50 text-brand-900",
    icon: <Info className="h-4 w-4 shrink-0 text-brand-600" aria-hidden />,
  },
  success: {
    wrap: "border-emerald-200 bg-emerald-50 text-emerald-900",
    icon: (
      <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600" aria-hidden />
    ),
  },
  warning: {
    wrap: "border-amber-200 bg-amber-50 text-amber-900",
    icon: (
      <AlertTriangle className="h-4 w-4 shrink-0 text-amber-600" aria-hidden />
    ),
  },
  error: {
    wrap: "border-rose-200 bg-rose-50 text-rose-900",
    icon: <XCircle className="h-4 w-4 shrink-0 text-rose-600" aria-hidden />,
  },
};

interface Props {
  tone?: Tone;
  title?: string;
  icon?: ReactNode;
  children?: ReactNode;
}

export function SymptomBanner({ tone = "info", title, icon, children }: Props) {
  const styles = toneStyles[tone];
  return (
    <div
      role="status"
      className={`flex items-start gap-2.5 rounded-xl border px-3.5 py-2.5 text-sm ${styles.wrap}`}
    >
      {icon ?? styles.icon}
      <div className="min-w-0">
        {title && (
          <p className="font-semibold leading-snug">{title}</p>
        )}
        {children}
      </div>
    </div>
  );
}
