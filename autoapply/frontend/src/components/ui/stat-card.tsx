import { cn } from "@/lib/utils";
import { Card } from "./card";
import { LucideIcon } from "lucide-react";

export function StatCard({ label, value, icon: Icon, delta }: {
  label: string;
  value: string | number;
  icon: LucideIcon;
  delta?: string;
}) {
  return (
    <Card className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-semibold uppercase tracking-widest text-white/30">{label}</span>
        <Icon className="h-4 w-4 text-white/20" />
      </div>
      <div className="text-3xl font-bold tracking-tight text-white">{value}</div>
      {delta && <div className="text-xs text-white/30">{delta}</div>}
    </Card>
  );
}
