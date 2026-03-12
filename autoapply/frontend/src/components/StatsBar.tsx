import { Briefcase, Building, Target, TrendingUp } from "lucide-react";

interface StatsProps {
    stats: {
        total_jobs: number;
        jobs_today: number;
        avg_score: number;
        top_companies?: any[];
    };
}

export default function StatsBar({ stats }: StatsProps) {
    const statCards = [
        {
            label: "Discovered Today",
            value: stats.jobs_today || 0,
            icon: Target,
            color: "text-blue-400",
            bg: "bg-blue-400/10",
        },
        {
            label: "Total Pipeline",
            value: stats.total_jobs || 0,
            icon: Briefcase,
            color: "text-indigo-400",
            bg: "bg-indigo-400/10",
        },
        {
            label: "Avg Match Score",
            value: stats.avg_score || 0,
            icon: TrendingUp,
            color: "text-emerald-400",
            bg: "bg-emerald-400/10",
        },
        {
            label: "Target Companies",
            value: stats.top_companies?.length || 0,
            icon: Building,
            color: "text-amber-400",
            bg: "bg-amber-400/10",
        },
    ];

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
            {statCards.map((stat) => (
                <div
                    key={stat.label}
                    className="bg-black border border-[#222] shadow-[0_4px_24px_-12px_rgba(0,0,0,0.5)] rounded-2xl p-6 flex items-center gap-5 hover:border-[#444] hover:shadow-[0_4px_30px_-10px_rgba(255,255,255,0.03)] transition-all duration-300 relative overflow-hidden group"
                >
                    {/* Subtle corner glow effect */}
                    <div className={`absolute -right-8 -top-8 w-24 h-24 blur-3xl opacity-20 group-hover:opacity-40 transition-opacity duration-300 ${stat.bg.replace('/10', '')}`} />
                    
                    <div className={`p-3.5 rounded-xl ${stat.bg} ${stat.color} ring-1 ring-inset ring-white/5`}>
                        <stat.icon className="w-6 h-6" />
                    </div>
                    <div>
                        <div className="text-xs uppercase tracking-wider font-semibold text-gray-500 mb-1">{stat.label}</div>
                        <div className="text-3xl font-bold text-white tracking-tight">{stat.value}</div>
                    </div>
                </div>
            ))}
        </div>
    );
}
