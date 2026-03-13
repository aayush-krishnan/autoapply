import { Briefcase, Building, Target, TrendingUp } from "lucide-react";
import { StatCard } from "./ui/stat-card";

interface StatsProps {
    stats: {
        total_jobs: number;
        jobs_today: number;
        avg_score: number;
        top_companies?: any[];
    };
}

export default function StatsBar({ stats }: StatsProps) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            <StatCard 
                label="Discovered Today" 
                value={stats.jobs_today || 0} 
                icon={Target} 
            />
            <StatCard 
                label="Total Pipeline" 
                value={stats.total_jobs || 0} 
                icon={Briefcase} 
            />
            <StatCard 
                label="Avg Match Score" 
                value={`${stats.avg_score || 0}%`} 
                icon={TrendingUp} 
            />
            <StatCard 
                label="Target Companies" 
                value={stats.top_companies?.length || 0} 
                icon={Building} 
            />
        </div>
    );
}
