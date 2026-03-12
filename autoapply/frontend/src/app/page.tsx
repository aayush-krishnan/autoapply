"use client";

import { useState, useEffect } from "react";
import { Search, MapPin, SlidersHorizontal, RefreshCw, Briefcase } from "lucide-react";
import StatsBar from "@/components/StatsBar";
import JobCard, { JobListing } from "@/components/JobCard";
import { motion } from "framer-motion";

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

      const [jobsRes, statsRes] = await Promise.all([
        fetch(`http://localhost:8000/api/jobs?${params.toString()}`),
        fetch("http://localhost:8000/api/dashboard/summary"),
      ]);

      if (jobsRes.ok) {
        const data = await jobsRes.json();
        setJobs(data.jobs);
      }
      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData);
      }
    } catch (error) {
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
    try {
      const res = await fetch("http://localhost:8000/api/jobs/scrape", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sources: ["indeed", "linkedin", "twitter", "wellfound"] }),
      });
      if (res.ok) {
        await fetchDashboardData();
      }
    } catch (error) {
      console.error("Scrape failed:", error);
    } finally {
      setScraping(false);
    }
  };

  const handleDismiss = async (id: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/jobs/${id}/dismiss`, {
        method: "PUT",
      });
      if (res.ok) {
        setJobs(jobs.filter((j) => j.id !== id));
        fetch("http://localhost:8000/api/dashboard/summary")
          .then(res => res.json())
          .then(data => setStats(data));
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="min-h-screen bg-background selection:bg-blue-500/30">
      <div className="hero-gradient">
        <div className="p-8 max-w-7xl mx-auto">
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-12"
          >
            <div>
              <h1 className="text-4xl font-black text-white tracking-tight flex items-center gap-3">
                <Briefcase className="w-10 h-10 text-blue-500" />
                Job Discovery Engine
              </h1>
              <p className="text-gray-400 text-base mt-2 font-medium max-w-2xl">
                High-volume discovery & auto-apply for PM roles, tailored for <span className="text-white font-bold">MEM Students</span>.
              </p>
            </div>
            <button
              onClick={handleScrape}
              disabled={scraping}
              className="group relative flex items-center gap-2 bg-white text-black hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed px-8 py-4 rounded-2xl font-black transition-all shadow-[0_0_40px_rgba(255,255,255,0.1)]"
            >
              <RefreshCw className={`w-5 h-5 ${scraping ? "animate-spin" : "group-hover:rotate-180 transition-transform duration-500"}`} />
              {scraping ? "Scanning Market..." : "Scrape Latest Jobs"}
            </button>
          </motion.div>

          <StatsBar stats={stats} />

          {/* Filters Bar */}
          <motion.div 
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-effect rounded-3xl p-5 mb-12 flex flex-wrap gap-5 shadow-2xl"
          >
            <div className="flex-1 min-w-[280px] relative group">
              <Search className="w-5 h-5 absolute left-4 top-4 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
              <input
                type="text"
                placeholder="Search role, company, or tech stack..."
                className="w-full bg-white/5 border border-white/5 hover:border-white/10 focus:border-blue-500/50 rounded-2xl pl-12 pr-4 py-4 text-sm font-semibold text-white focus:outline-none transition-all placeholder:text-gray-500 shadow-inner"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>

            <div className="w-56 relative group">
              <MapPin className="w-5 h-5 absolute left-4 top-4 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
              <input
                type="text"
                placeholder="Location..."
                className="w-full bg-white/5 border border-white/5 hover:border-white/10 focus:border-blue-500/50 rounded-2xl pl-12 pr-4 py-4 text-sm font-semibold text-white focus:outline-none transition-all placeholder:text-gray-500 shadow-inner"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
              />
            </div>

            <div className="w-56 relative group">
              <SlidersHorizontal className="w-5 h-5 absolute left-4 top-4 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
              <select
                className="w-full bg-white/5 border border-white/5 hover:border-white/10 focus:border-blue-500/50 rounded-2xl pl-12 pr-4 py-4 text-sm font-semibold text-white focus:outline-none transition-all appearance-none cursor-pointer shadow-inner"
                value={minScore}
                onChange={(e) => setMinScore(e.target.value)}
              >
                <option value="" className="bg-black">Any Match Score</option>
                <option value="80" className="bg-black">High Match (80+)</option>
                <option value="60" className="bg-black">Solid Match (60+)</option>
              </select>
            </div>
          </motion.div>

          {/* Jobs Grid */}
          {loading ? (
            <div className="flex flex-col justify-center items-center h-96 gap-4">
              <div className="w-12 h-12 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin" />
              <p className="text-gray-400 font-bold animate-pulse">Fetching opportunities...</p>
            </div>
          ) : jobs.length > 0 ? (
            <motion.div 
              layout
              className="grid grid-cols-1 lg:grid-cols-2 gap-6"
            >
              {jobs.map((job) => (
                <JobCard key={job.id} job={job} onDismiss={handleDismiss} />
              ))}
            </motion.div>
          ) : (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-32 glass-effect rounded-3xl border-dashed border-2 border-white/5"
            >
              <div className="w-20 h-20 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-6">
                <Briefcase className="w-10 h-10 text-gray-600" />
              </div>
              <h3 className="text-2xl font-black text-white">No matches found</h3>
              <p className="text-gray-500 text-base mt-2 max-w-sm mx-auto">Try expanding your search criteria or trigger a fresh scrape of the job market.</p>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
