"use client";

import { useState, useEffect } from "react";
import { apiRequest } from "@/lib/api";
import { JobListing } from "@/components/JobCard";
import { CheckCircle2, Clock, Loader2, BarChart3, ChevronRight } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { motion, AnimatePresence } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";

export default function ApplicationsPage() {
    const [jobs, setJobs] = useState<JobListing[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchApplied = async () => {
            try {
                const data = await apiRequest<any>("/api/jobs?per_page=100");
                const applied = data.jobs.filter((j: JobListing) => j.status === "applied");
                setJobs(applied);
            } catch (e) {
                toast.error("Failed to fetch applications");
            } finally {
                setLoading(false);
            }
        };
        fetchApplied();
    }, []);

    return (
        <div className="p-8 lg:p-12 max-w-5x mx-auto space-y-12">
            <header className="space-y-2">
                <Badge variant="ghost" className="px-0">Pipeline History</Badge>
                <h1 className="text-4xl font-bold tracking-tight text-white leading-tight">
                    Application Tracker
                </h1>
                <p className="text-white/40 text-lg font-medium leading-relaxed max-w-2xl">
                    Every footprint in your journey to the next big role, documented.
                </p>
            </header>

            {loading ? (
                <div className="flex justify-center py-20">
                    <Loader2 className="w-8 h-8 animate-spin text-white/10" />
                </div>
            ) : (
                <div className="space-y-4">
                    <AnimatePresence mode="popLayout">
                        {jobs.length > 0 ? (
                            jobs.map((job, idx) => (
                                <motion.div
                                    key={job.id}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: idx * 0.05 }}
                                >
                                    <Card className="flex flex-col md:flex-row justify-between items-center gap-6 group hover:bg-white/[0.04]">
                                        <div className="flex-1 space-y-1">
                                            <h3 className="text-lg font-bold text-white tracking-tight">{job.title}</h3>
                                            <div className="text-white/40 text-sm font-medium flex items-center gap-2">
                                                <span>{job.company_name}</span>
                                                <span className="text-white/10">•</span>
                                                <span>{job.location}</span>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-8 w-full md:w-auto justify-between md:justify-end">
                                            <div className="flex flex-col items-end gap-1">
                                                <span className="text-[10px] uppercase font-bold text-white/20 tracking-[0.2em]">Outcome</span>
                                                <Badge variant="success" className="bg-emerald-500/5 border-emerald-500/10 text-emerald-400">
                                                    Submitted
                                                </Badge>
                                            </div>
                                            <div className="flex flex-col items-end gap-1">
                                                <span className="text-[10px] uppercase font-bold text-white/20 tracking-[0.2em]">Timestamp</span>
                                                <span className="text-white/60 font-medium text-sm">
                                                    {job.discovered_at ? formatDistanceToNow(new Date(job.discovered_at), { addSuffix: true }) : "Recent"}
                                                </span>
                                            </div>
                                            <ChevronRight className="w-4 h-4 text-white/10 group-hover:text-white/30 transition-colors hidden md:block" />
                                        </div>
                                    </Card>
                                </motion.div>
                            ))
                        ) : (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="text-center py-32 bg-white/[0.01] border border-dashed border-white/10 rounded-3xl"
                            >
                                <div className="w-16 h-16 rounded-full bg-white/[0.03] flex items-center justify-center mx-auto mb-6 text-white/20">
                                    <BarChart3 className="w-8 h-8" />
                                </div>
                                <h3 className="text-xl font-bold text-white">No activity yet</h3>
                                <p className="text-white/30 text-sm mt-2 max-w-xs mx-auto">Start the engine to populate your application pipeline.</p>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            )}
        </div>
    );
}
