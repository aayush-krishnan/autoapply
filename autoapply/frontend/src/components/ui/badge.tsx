import { cn } from "@/lib/utils";

type BadgeVariant = "default" | "success" | "warning" | "danger" | "ghost" | "outline";

const variants: Record<BadgeVariant, string> = {
  default:  "bg-white/[0.06] text-white/60 border-white/[0.08]",
  success:  "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  warning:  "bg-amber-500/10 text-amber-400 border-amber-500/20",
  danger:   "bg-red-500/10 text-red-400 border-red-500/20",
  ghost:    "bg-transparent text-white/40 border-transparent",
  outline:  "bg-transparent text-white/60 border-white/10",
};

export function Badge({ variant = "default", className, children }: {
  variant?: BadgeVariant;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <span className={cn(
      "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wider",
      variants[variant], className
    )}>
      {children}
    </span>
  );
}
