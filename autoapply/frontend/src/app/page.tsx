"use client";

import { useState, useEffect } from "react";
import { Search, MapPin, SlidersHorizontal, RefreshCw, Briefcase, Activity, Target, Zap } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { apiRequest } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { StatCard } from "@/components/ui/stat-card";
import JobCard, { JobListing } from "@/components/JobCard";
import { toast } from "sonner";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";

export default function Dashboard() {
  const [jobs, setJobs] = useState<JobListing[]>([]);
  const [stats, setStats] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);

  // Filters
  const [search, setSearch] = useState("");
  const [location, setLocation] = useState("");
  const [minScore, setMinScore] = useState("");

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.append("keyword", search);
      if (location) params.append("location", location);
      if (minScore) params.append("min_score", minScore);

      const [data, statsData] = await Promise.all([
        apiRequest<any>(`/api/jobs?${params.toString()}`),
        apiRequest<any>("/api/dashboard/summary"),
      ]);

      setJobs(data.jobs);
      setStats(statsData);
    } catch (error) {
      toast.error("Failed to fetch dashboard data");
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [search, location, minScore]);

  const handleScrape = async () => {
    setScraping(true);
    const toastId = toast.loading("Scanning job market...");
    try {
      await apiRequest("/api/jobs/scrape", {
        method: "POST",
        body: JSON.stringify({ sources: ["indeed", "linkedin", "twitter", "wellfound"] }),
      });
      toast.success("Scrape completed successfully", { id: toastId });
      await fetchDashboardData();
    } catch (error) {
      toast.error("Scrape failed", { id: toastId });
      console.error("Scrape failed:", error);
    } finally {
      setScraping(false);
    }
  };

  const handleDismiss = async (id: string) => {
    try {
      await apiRequest(`/api/jobs/${id}/dismiss`, { method: "PUT" });
      setJobs(jobs.filter((j) => j.id !== id));
      toast.success("Job dismissed");
      const statsData = await apiRequest<any>("/api/dashboard/summary");
      setStats(statsData);
    } catch (e) {
      toast.error("Failed to dismiss job");
    }
  };

  // Mock data for charts (would be derived from a real time-series endpoint)
  const chartData = [
    { name: "Mon", count: 12 },
    { name: "Tue", count: 18 },
    { name: "Wed", count: 15 },
    { name: "Thu", count: 25 },
    { name: "Fri", count: 32 },
    { name: "Sat", count: 20 },
    { name: "Sun", count: 28 },
  ];

  const distributionData = [
    { name: "Low", value: stats.score_distribution?.low || 0 },
    { name: "Medium", value: stats.score_distribution?.medium || 0 },
    { name: "High", value: stats.score_distribution?.high || 0 },
  ];

  return (
    <div className="p-8 lg:p-12 max-w-[1600px] mx-auto min-h-screen space-y-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div className="space-y-2">
          <Badge variant="ghost" className="px-0">Platform Overview</Badge>
          <h1 className="text-4xl font-bold tracking-tight text-white leading-tight">
            Intelligence Engine
          </h1>
          <p className="text-white/40 text-lg max-w-xl font-medium leading-relaxed">
            High-fidelity job discovery and automated resonance for MEM students.
          </p>
        </div>
        <div className="flex items-center gap-3">
            <Button 
                variant="outline" 
                className="rounded-full px-6 py-6"
                onClick={() => toast.info("Command Palette (Cmd+K) coming soon")}
            >
                <Search className="w-4 h-4 mr-2" />
                Quick Search
            </Button>
            <Button 
                variant="primary" 
                className="rounded-full px-8 py-6 shadow-2xl shadow-white/5"
                onClick={handleScrape}
                disabled={scraping}
            >
                {scraping ? <RefreshCw className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
                {scraping ? "Scanning..." : "Sync Market Data"}
            </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
            label="Total Discovered" 
            value={stats.total_jobs || 0} 
            icon={Briefcase} 
            delta="+12% from last sync"
        />
        <StatCard 
            label="Daily Velocity" 
            value={stats.jobs_today || 0} 
            icon={Zap} 
            delta="Roles found today"
        />
        <StatCard 
            label="Market Match" 
            value={`${stats.avg_score || 0}%`} 
            icon={Target} 
            delta="Average match quality"
        />
        <StatCard 
            label="System Health" 
            value="Active" 
            icon={Activity} 
            delta="All scrapers online"
        />
      </div>

      {/* Analytics Section */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <Card className="xl:col-span-2 space-y-6">
            <div className="flex items-center justify-between">
                <div className="space-y-1">
                    <h3 className="text-sm font-semibold text-white/80">Discovery Velocity</h3>
                    <p className="text-xs text-white/30 font-medium">Opportunities identified over 7 days</p>
                </div>
                <Badge variant="ghost">Last 7 Days</Badge>
            </div>
            <div className="h-[240px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData}>
                        <defs>
                            <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#ffffff" stopOpacity={0.1}/>
                                <stop offset="95%" stopColor="#ffffff" stopOpacity={0}/>
                            </linearGradient>
                        </defs>
                        <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.05)" />
                        <XAxis 
                            dataKey="name" 
                            axisLine={false} 
                            tickLine={false} 
                            tick={{fill: 'rgba(255,255,255,0.3)', fontSize: 11}} 
                            dy={10}
                        />
                        <YAxis hide />
                        <Tooltip 
                            contentStyle={{background: '#0a0a0a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', fontSize: '12px'}}
                            itemStyle={{color: '#fff'}}
                        />
                        <Area 
                            type="monotone" 
                            dataKey="count" 
                            stroke="#ffffff" 
                            strokeWidth={2}
                            fillOpacity={1} 
                            fill="url(#colorCount)" 
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </Card>
        <Card className="space-y-6">
            <div className="space-y-1">
                <h3 className="text-sm font-semibold text-white/80">Quality Distribution</h3>
                <p className="text-xs text-white/30 font-medium">Match score mapping</p>
            </div>
            <div className="h-[240px] w-full pt-4">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={distributionData} layout="vertical">
                        <XAxis type="number" hide />
                        <YAxis 
                            dataKey="name" 
                            type="category" 
                            axisLine={false} 
                            tickLine={false}
                            tick={{fill: 'rgba(255,255,255,0.4)', fontSize: 12}}
                        />
                        <Tooltip 
                            cursor={{fill: 'rgba(255,255,255,0.02)'}}
                            contentStyle={{background: '#0a0a0a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', fontSize: '12px'}}
                        />
                        <Bar 
                            dataKey="value" 
                            fill="rgba(255,255,255,0.1)" 
                            radius={[0, 4, 4, 0]} 
                            barSize={12}
                        />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </Card>
      </div>

      {/* Main Display: Filters & Jobs */}
      <div className="space-y-8">
        <div className="flex flex-col sm:flex-row items-center gap-4 bg-white/[0.02] border border-white/[0.04] p-2 rounded-2xl">
            <div className="relative flex-1 group w-full">
                <Search className="w-4 h-4 absolute left-4 top-3.5 text-white/20 group-focus-within:text-white transition-colors" />
                <Input 
                    placeholder="Search roles or companies..." 
                    className="pl-12 border-none bg-transparent"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                />
            </div>
            <div className="h-6 w-[1px] bg-white/10 hidden sm:block" />
            <div className="relative w-full sm:w-48 group">
                <MapPin className="w-4 h-4 absolute left-4 top-3.5 text-white/20 group-focus-within:text-white transition-colors" />
                <Input 
                    placeholder="Location" 
                    className="pl-12 border-none bg-transparent"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                />
            </div>
            <div className="h-6 w-[1px] bg-white/10 hidden sm:block" />
            <div className="relative w-full sm:w-48">
                <SlidersHorizontal className="w-4 h-4 absolute left-4 top-3.5 text-white/20" />
                <select
                    className="w-full bg-transparent px-12 py-3 text-sm text-white/40 focus:text-white focus:outline-none appearance-none cursor-pointer"
                    value={minScore}
                    onChange={(e) => setMinScore(e.target.value)}
                >
                    <option value="" className="bg-black">All Scores</option>
                    <option value="80" className="bg-black">High (80+)</option>
                    <option value="60" className="bg-black">Solid (60+)</option>
                </select>
            </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-pulse">
            {[...Array(4)].map((_, i) => (
                <Card key={i} className="h-48 border-dashed" />
            ))}
          </div>
        ) : jobs.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 2xl:grid-cols-3 gap-6">
            <AnimatePresence mode="popLayout">
                {jobs.map((job) => (
                    <motion.div
                        key={job.id}
                        layout
                        initial={{ opacity: 0, scale: 0.98 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.98 }}
                        transition={{ duration: 0.2 }}
                    >
                        <JobCard job={job} onDismiss={handleDismiss} />
                    </motion.div>
                ))}
            </AnimatePresence>
          </div>
        ) : (
          <div className="text-center py-40 bg-white/[0.01] border border-dashed border-white/10 rounded-3xl">
            <h3 className="text-xl font-bold text-white">No opportunities identified</h3>
            <p className="text-white/30 text-sm mt-2">Try adjusting your filters or sync market data.</p>
          </div>
        )}
      </div>
    </div>
  );
}
