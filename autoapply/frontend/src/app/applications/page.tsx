"use client";

import { useState, useEffect } from "react";
import { apiRequest } from "@/lib/api";
import { JobListing } from "@/components/JobCard";
import { LineChart, CheckCircle2, Clock, ShieldAlert } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { motion } from "framer-motion";

export default function ApplicationsPage() {
    const [jobs, setJobs] = useState<JobListing[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchApplied = async () => {
            try {
                // Filter for applied jobs (we'll implement this on backend or client side)
                const data = await apiRequest<any>("/api/jobs?per_page=100");
                const applied = data.jobs.filter((j: JobListing) => j.status === "applied");
                setJobs(applied);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        fetchApplied();
    }, []);

    return (
        <div className="p-8 max-w-7xl mx-auto min-h-screen bg-background text-white">
            <header className="mb-12">
                <h1 className="text-4xl font-black flex items-center gap-3">
                    <LineChart className="w-10 h-10 text-emerald-500" />
                    Application Tracker
                </h1>
                <p className="text-gray-400 mt-2 font-medium">Keep track of every submission and stay ahead of the curve.</p>
            </header>

            {loading ? (
                <div className="flex justify-center py-20">
                    <div className="w-10 h-10 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin" />
                </div>
            ) : jobs.length > 0 ? (
                <div className="grid gap-4">
                    {jobs.map((job) => (
                        <motion.div 
                            key={job.id}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="bg-white/5 border border-white/10 rounded-2xl p-6 flex flex-col md:flex-row justify-between items-center gap-6"
                        >
                            <div className="flex-1">
                                <h3 className="text-xl font-bold">{job.title}</h3>
                                <div className="text-gray-400 text-sm font-medium mt-1">{job.company_name} • {job.location}</div>
                            </div>
                            <div className="flex items-center gap-6">
                                <div className="flex flex-col items-end">
                                    <span className="text-[10px] uppercase font-bold text-gray-500 tracking-widest">Status</span>
                                    <span className="flex items-center gap-1.5 text-emerald-400 font-bold text-sm">
                                        <CheckCircle2 className="w-4 h-4" /> Applied
                                    </span>
                                </div>
                                <div className="flex flex-col items-end border-l border-white/10 pl-6">
                                    <span className="text-[10px] uppercase font-bold text-gray-500 tracking-widest">Date</span>
                                    <span className="text-gray-300 font-medium text-sm">
                                        {job.discovered_at ? formatDistanceToNow(new Date(job.discovered_at), { addSuffix: true }) : "Unknown"}
                                    </span>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            ) : (
                <div className="text-center py-32 bg-white/5 rounded-3xl border-dashed border-2 border-white/10">
                    <Clock className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                    <h3 className="text-xl font-bold">No applications yet</h3>
                    <p className="text-gray-500 mt-2">Start using the Auto-Apply engine to see your progress here.</p>
                </div>
            )}
        </div>
    );
}
