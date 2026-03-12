import { useState } from "react";
import { Calendar, Building2, MapPin, Globe, CheckCircle2, ShieldAlert, Loader2, Zap } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { motion, AnimatePresence } from "framer-motion";
import AutoApplyModal from "./AutoApplyModal";
import { apiRequest } from "@/lib/api";

export interface JobListing {
    id: string;
    title: string;
    company_name: string;
    location: string;
    source_platform: string;
    source_url: string;
    match_score: number;
    visa_info: string;
    h1b_sponsor_tier: string;
    discovered_at: string;
    is_dismissed: boolean;
    status: string;
}

interface JobCardProps {
    job: JobListing;
    onDismiss: (id: string) => void;
}

export default function JobCard({ job, onDismiss }: JobCardProps) {
    const [isTailoring, setIsTailoring] = useState(false);
    const [showApplyModal, setShowApplyModal] = useState(false);

    // Score styling logic
    const getScoreColor = (score: number) => {
        if (score >= 80) return "text-emerald-400 border-emerald-400/30 bg-emerald-400/10";
        if (score >= 60) return "text-amber-400 border-amber-400/30 bg-amber-400/10";
        return "text-red-400 border-red-400/30 bg-red-400/10";
    };

    // Convert date to readable relative format
    const getRelativeTime = (isoString?: string) => {
        if (!isoString) return "Recently";
        try {
            return formatDistanceToNow(new Date(isoString), { addSuffix: true });
        } catch {
            return "Recently";
        }
    };

    const handleTailor = async () => {
        setIsTailoring(true);
        try {
            const data = await apiRequest<any>(`/api/resumes/tailor/${job.id}`, {
                method: "POST"
            });

            if (data.google_doc_url) {
                window.open(data.google_doc_url, "_blank");
            }
        } catch (e) {
            console.error("Error tailoring resume:", e);
            alert("An error occurred while tailoring the resume.");
        } finally {
            setIsTailoring(false);
        }
    };

    return (
        <motion.div 
            layout
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            whileHover={{ y: -4, transition: { duration: 0.2 } }}
            className="glass-effect rounded-2xl p-6 flex flex-col gap-4 group relative overflow-hidden"
        >
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            
            {/* Header: Title, Score, Actions */}
            <div className="flex justify-between items-start relative z-10">
                <div className="flex-1">
                    <a
                        href={job.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xl font-bold text-white group-hover:text-blue-400 transition-colors line-clamp-1 leading-tight"
                        title={job.title}
                    >
                        {job.title}
                    </a>
                    <div className="flex items-center gap-2 text-sm text-gray-400 mt-2">
                        <Building2 className="w-4 h-4 text-blue-500/80" />
                        <span className="font-semibold text-gray-200">{job.company_name}</span>
                    </div>
                </div>

                {/* Match Score Badge */}
                <div className={`flex flex-col items-center justify-center w-14 h-14 rounded-xl border-2 shadow-2xl ${getScoreColor(job.match_score || 0)}`}>
                    <span className="text-xl font-black">{job.match_score || 0}</span>
                    <span className="text-[9px] uppercase font-black tracking-tighter opacity-70">Match</span>
                </div>
            </div>

            {/* Meta details */}
            <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-xs text-gray-400 font-medium relative z-10">
                <div className="flex items-center gap-1.5 bg-white/5 px-2 py-1 rounded-lg">
                    <MapPin className="w-3.5 h-3.5 text-blue-500" />
                    {job.location}
                </div>
                <div className="flex items-center gap-1.5 bg-white/5 px-2 py-1 rounded-lg">
                    <Globe className="w-3.5 h-3.5 text-indigo-500" />
                    <span className="capitalize">{job.source_platform}</span>
                </div>
                <div className="flex items-center gap-1.5 bg-white/5 px-2 py-1 rounded-lg">
                    <Calendar className="w-3.5 h-3.5 text-purple-500" />
                    {getRelativeTime(job.discovered_at)}
                </div>
            </div>

            {/* Tags (Visa info, H1B) */}
            <div className="flex gap-2 mt-auto pt-4 border-t border-white/10 relative z-10">
                {job.visa_info === "cpt_opt_ok" && (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] font-bold uppercase tracking-wider border border-emerald-500/20">
                        <CheckCircle2 className="w-3 h-3" /> CPT/OPT OK
                    </span>
                )}
                {job.visa_info === "no_sponsorship" && (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-full bg-red-500/10 text-red-400 text-[10px] font-bold uppercase tracking-wider border border-red-500/20">
                        <ShieldAlert className="w-3 h-3" /> No Sponsor
                    </span>
                )}
                {job.h1b_sponsor_tier === "tier1" && (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-full bg-blue-500/10 text-blue-400 text-[10px] font-bold uppercase tracking-wider border border-blue-500/20">
                        Tier 1 H1B
                    </span>
                )}
            </div>

            {/* Bottom Actions */}
            <div className="flex gap-3 pt-2 relative z-10">
                <button
                    onClick={handleTailor}
                    disabled={isTailoring}
                    className="flex-1 flex justify-center items-center gap-2 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 disabled:opacity-50 text-white text-sm font-bold py-3 rounded-xl transition-all active:scale-95"
                >
                    {isTailoring && <Loader2 className="w-4 h-4 animate-spin" />}
                    {isTailoring ? "Tailoring..." : "Tailor Resume"}
                </button>
                <button
                    onClick={() => setShowApplyModal(true)}
                    className="flex-1 flex justify-center items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-sm font-bold py-3 rounded-xl transition-all shadow-lg shadow-blue-500/20 active:scale-95 group/btn"
                >
                    <Zap className="w-4 h-4 group-hover/btn:fill-current" />
                    Auto-Apply
                </button>
                <button
                    onClick={() => onDismiss(job.id)}
                    className="px-4 flex items-center justify-center bg-transparent hover:bg-red-500/10 text-gray-400 hover:text-red-400 text-xs font-bold py-3 rounded-xl transition-all border border-transparent hover:border-red-500/20 active:scale-95"
                >
                    Dismiss
                </button>
            </div>

            <AnimatePresence>
                {showApplyModal && (
                    <AutoApplyModal job={job} onClose={() => setShowApplyModal(false)} />
                )}
            </AnimatePresence>

        </motion.div>
    );
}
