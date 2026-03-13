import { cn } from "@/lib/utils";

export function Input({ className, ...props }: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "w-full rounded-xl border border-white/[0.08] bg-white/[0.04] px-4 py-3",
        "text-sm text-white placeholder:text-white/25",
        "transition-colors focus:border-white/20 focus:outline-none focus:bg-white/[0.06]",
        className
      )}
      {...props}
    />
  );
}
