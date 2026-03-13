"use client";

import { useState } from "react";
import { Calendar, Building2, MapPin, Globe, CheckCircle2, ShieldAlert, Loader2, Zap, ExternalLink, X } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { motion, AnimatePresence } from "framer-motion";
import AutoApplyModal from "./AutoApplyModal";
import { apiRequest } from "@/lib/api";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { toast } from "sonner";

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

    const getScoreVariant = (score: number) => {
        if (score >= 80) return "success";
        if (score >= 60) return "warning";
        return "danger";
    };

    const getRelativeTime = (isoString?: string) => {
        if (!isoString) return "Recently";
        try {
            return formatDistanceToNow(new Date(isoString), { addSuffix: true });
        } catch {
            return "Recently";
        }
    };

    const handleTailor = async (e: React.MouseEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsTailoring(true);
        const toastId = toast.loading("Tailoring your resume...");
        try {
            const data = await apiRequest<any>(`/api/resumes/tailor/${job.id}`, {
                method: "POST"
            });

            if (data.google_doc_url && data.google_doc_url !== "#") {
                toast.success("Resume tailored! Opening Google Doc...", { id: toastId });
                window.open(data.google_doc_url, "_blank");
            } else {
                toast.error("Format error in resume response", { id: toastId });
            }
        } catch (e) {
            toast.error("Failed to tailor resume", { id: toastId });
        } finally {
            setIsTailoring(false);
        }
    };

    return (
        <Card className="flex flex-col gap-6 group h-full relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button 
                    variant="ghost" 
                    className="h-8 w-8 p-0 rounded-full hover:bg-red-500/10 hover:text-red-400"
                    onClick={() => onDismiss(job.id)}
                >
                    <X className="w-4 h-4" />
                </Button>
            </div>

            {/* Header */}
            <div className="flex justify-between items-start gap-4">
                <div className="space-y-1.5 flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                        <Badge variant="ghost" className="px-0 lowercase text-white/30">{job.source_platform}</Badge>
                        <span className="text-white/10 text-[10px]">•</span>
                        <span className="text-white/30 text-[10px] uppercase font-bold tracking-widest">{getRelativeTime(job.discovered_at)}</span>
                    </div>
                    <h2 className="text-xl font-bold text-white tracking-tight leading-snug truncate group-hover:text-blue-400 transition-colors">
                        {job.title}
                    </h2>
                    <div className="flex items-center gap-2 text-white/50 text-sm font-medium">
                        <Building2 className="w-3.5 h-3.5" />
                        {job.company_name}
                    </div>
                </div>
                
                <div className="flex flex-col items-center">
                    <div className="text-2xl font-bold tracking-tighter text-white">
                        {job.match_score}
                    </div>
                    <div className="text-[9px] uppercase font-black tracking-widest text-white/20">Match</div>
                </div>
            </div>

            {/* Details & Tags */}
            <div className="space-y-4 flex-1">
                <div className="flex flex-wrap gap-2 text-xs text-white/40">
                    <div className="flex items-center gap-1.5 bg-white/[0.04] px-2.5 py-1 rounded-lg border border-white/[0.04]">
                        <MapPin className="w-3.5 h-3.5" />
                        {job.location}
                    </div>
                    {job.h1b_sponsor_tier === "tier1" && (
                        <Badge variant="success" className="rounded-lg">H1B Tier 1</Badge>
                    )}
                    {job.visa_info === "cpt_opt_ok" && (
                        <Badge variant="default" className="rounded-lg border-emerald-500/20 text-emerald-400 bg-emerald-500/5">CPT/OPT Friendly</Badge>
                    )}
                </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2.5 pt-4">
                <Button 
                    variant="outline" 
                    className="flex-1 rounded-xl h-11"
                    onClick={handleTailor}
                    disabled={isTailoring}
                >
                    {isTailoring ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Loader2 className="w-3.5 h-3.5" />}
                    {isTailoring ? "Tailoring..." : "Tailor"}
                </Button>
                <Button 
                    variant="primary" 
                    className="flex-1 rounded-xl h-11 shadow-lg shadow-white/5 font-bold"
                    onClick={() => setShowApplyModal(true)}
                >
                    <Zap className="w-3.5 h-3.5 fill-black" />
                    Auto-Apply
                </Button>
                <a 
                    href={job.source_url} 
                    target="_blank" 
                    rel="noopener" 
                    className="inline-flex items-center justify-center p-3 rounded-xl bg-white/[0.04] border border-white/[0.06] hover:bg-white/[0.08] transition-colors"
                >
                    <ExternalLink className="w-4 h-4 text-white/40" />
                </a>
            </div>

            <AnimatePresence>
                {showApplyModal && (
                    <AutoApplyModal job={job} onClose={() => setShowApplyModal(false)} />
                )}
            </AnimatePresence>
        </Card>
    );
}
