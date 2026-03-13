import { cn } from "@/lib/utils";

export function Spinner({ className }: { className?: string }) {
  return (
    <div className={cn(
      "h-4 w-4 rounded-full border-2 border-white/10 border-t-white animate-spin",
      className
    )} />
  );
}
