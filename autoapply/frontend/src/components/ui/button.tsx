import { cn } from "@/lib/utils";

type ButtonVariant = "primary" | "ghost" | "outline" | "danger";

const variants: Record<ButtonVariant, string> = {
  primary: "bg-white text-black hover:bg-white/90 font-semibold",
  ghost:   "bg-transparent text-white/60 hover:text-white hover:bg-white/[0.06]",
  outline: "border border-white/10 bg-transparent text-white/80 hover:border-white/20 hover:bg-white/[0.04]",
  danger:  "bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20",
};

export function Button({ variant = "ghost", className, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: ButtonVariant }) {
  return (
    <button
      className={cn(
        "inline-flex items-center gap-2 rounded-xl px-4 py-2 text-sm",
        "transition-all duration-150 focus:outline-none focus-visible:ring-2 focus-visible:ring-white/20",
        "disabled:opacity-40 disabled:cursor-not-allowed",
        variants[variant], className
      )}
      {...props}
    />
  );
}
