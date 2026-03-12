"use client";

import { useState, useEffect } from "react";
import { Settings, Save, Shield, Globe, Terminal, User } from "lucide-react";
import { apiRequest } from "@/lib/api";
import { motion } from "framer-motion";

export default function SettingsPage() {
    const [config, setConfig] = useState<any>({
        proxy_url: "",
        scrape_interval: 1,
        keywords: "",
        locations: ""
    });
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        // In a real app, we'd fetch current settings from the backend
        // For now, we'll initialize with some defaults or local storage
        const saved = localStorage.getItem("autoapply_config");
        if (saved) setConfig(JSON.parse(saved));
    }, []);

    const handleSave = async () => {
        setSaving(true);
        try {
            // Save to local storage for now
            localStorage.setItem("autoapply_config", JSON.stringify(config));
            // In a real app: await apiRequest("/api/config", { method: "POST", body: JSON.stringify(config) });
            await new Promise(r => setTimeout(r, 1000));
            alert("Settings saved successfully!");
        } catch (e) {
            console.error(e);
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="p-8 max-w-4xl mx-auto min-h-screen bg-background text-white">
            <header className="mb-12">
                <h1 className="text-4xl font-black flex items-center gap-3">
                    <Settings className="w-10 h-10 text-blue-500" />
                    System Settings
                </h1>
                <p className="text-gray-400 mt-2 font-medium">Fine-tune your autonomous discovery engine and security.</p>
            </header>

            <div className="space-y-8">
                {/* Proxy Section */}
                <section className="bg-white/5 border border-white/10 rounded-2xl p-6">
                    <div className="flex items-center gap-3 mb-6">
                        <Shield className="w-6 h-6 text-indigo-400" />
                        <h2 className="text-xl font-bold">Anti-Scraping & Privacy</h2>
                    </div>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-xs uppercase font-black tracking-widest text-gray-500 mb-2">Proxy URL</label>
                            <input 
                                type="text"
                                placeholder="http://user:pass@host:port"
                                className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm font-medium focus:border-blue-500 outline-none transition-all"
                                value={config.proxy_url}
                                onChange={e => setConfig({...config, proxy_url: e.target.value})}
                            />
                            <p className="text-[10px] text-gray-500 mt-2 uppercase tracking-tighter font-bold">Recommended for bypassing Indeed/LinkedIn IP blocks.</p>
                        </div>
                    </div>
                </section>

                {/* Automation Section */}
                <section className="bg-white/5 border border-white/10 rounded-2xl p-6">
                    <div className="flex items-center gap-3 mb-6">
                        <Terminal className="w-6 h-6 text-emerald-400" />
                        <h2 className="text-xl font-bold">Engine Configuration</h2>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label className="block text-xs uppercase font-black tracking-widest text-gray-500 mb-2">Scrape Interval (Hours)</label>
                            <select 
                                className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm font-medium outline-none"
                                value={config.scrape_interval}
                                onChange={e => setConfig({...config, scrape_interval: Number(e.target.value)})}
                            >
                                <option value={1}>Every 1 Hour</option>
                                <option value={6}>Every 6 Hours</option>
                                <option value={24}>Every 24 Hours</option>
                            </select>
                        </div>
                    </div>
                </section>

                <div className="flex justify-end pt-4">
                    <button 
                        onClick={handleSave}
                        disabled={saving}
                        className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-bold px-8 py-4 rounded-2xl transition-all active:scale-95 shadow-lg shadow-blue-500/20"
                    >
                        {saving ? <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" /> : <Save className="w-5 h-5" />}
                        {saving ? "Deploying Changes..." : "Save Settings"}
                    </button>
                </div>
            </div>
        </div>
    );
}
