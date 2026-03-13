"use client";

import { useState, useEffect } from "react";
import { Settings, Save, Shield, Globe, Terminal, User, Loader2 } from "lucide-react";
import { apiRequest } from "@/lib/api";
import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";

export default function SettingsPage() {
    const [config, setConfig] = useState<any>({
        proxy_url: "",
        scrape_interval: 1,
        keywords: "",
        locations: ""
    });
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        const saved = localStorage.getItem("autoapply_config");
        if (saved) setConfig(JSON.parse(saved));
    }, []);

    const handleSave = async () => {
        setSaving(true);
        const toastId = toast.loading("Deploying system updates...");
        try {
            localStorage.setItem("autoapply_config", JSON.stringify(config));
            await new Promise(r => setTimeout(r, 1000));
            toast.success("Settings deployed", { id: toastId });
        } catch (e) {
            toast.error("Deployment failed", { id: toastId });
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="p-8 lg:p-12 max-w-4xl mx-auto space-y-12">
            <header className="space-y-2">
                <Badge variant="ghost" className="px-0">Core System</Badge>
                <h1 className="text-4xl font-bold tracking-tight text-white leading-tight">
                    System Configuration
                </h1>
                <p className="text-white/40 text-lg font-medium leading-relaxed">
                    Fine-tune your autonomous discovery engine and security protocols.
                </p>
            </header>

            <div className="space-y-6">
                {/* Proxy Section */}
                <Card className="space-y-6 border-white/5 bg-white/[0.01]">
                    <div className="flex items-center gap-3">
                        <div className="p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                            <Shield className="w-5 h-5 text-white/60" />
                        </div>
                        <h2 className="text-lg font-bold text-white tracking-tight">Privacy & Guardrails</h2>
                    </div>
                    
                    <div className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-[11px] font-bold uppercase tracking-widest text-white/20">Proxy Endpoint</label>
                            <Input 
                                placeholder="http://user:pass@host:port"
                                className="bg-transparent"
                                value={config.proxy_url}
                                onChange={e => setConfig({...config, proxy_url: e.target.value})}
                            />
                            <p className="text-[10px] text-white/20 uppercase tracking-widest font-bold">Recommended for high-volume scraping resilience.</p>
                        </div>
                    </div>
                </Card>

                {/* Automation Section */}
                <Card className="space-y-6 border-white/5 bg-white/[0.01]">
                    <div className="flex items-center gap-3">
                        <div className="p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                            <Terminal className="w-5 h-5 text-white/60" />
                        </div>
                        <h2 className="text-lg font-bold text-white tracking-tight">Engine Parameters</h2>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="space-y-3">
                            <label className="text-[11px] font-bold uppercase tracking-widest text-white/20">Scrape Frequency</label>
                            <select 
                                className="w-full bg-white/[0.03] border border-white/[0.08] rounded-xl px-4 py-3 text-sm font-medium text-white focus:outline-none appearance-none cursor-pointer"
                                value={config.scrape_interval}
                                onChange={e => setConfig({...config, scrape_interval: Number(e.target.value)})}
                            >
                                <option value={1} className="bg-black">Hourly Sync</option>
                                <option value={6} className="bg-black">Every 6 Hours</option>
                                <option value={24} className="bg-black">Daily Sync</option>
                            </select>
                        </div>
                    </div>
                </Card>

                <div className="flex justify-end pt-4">
                    <Button 
                        variant="primary" 
                        className="rounded-full px-10 py-6 font-bold"
                        onClick={handleSave}
                        disabled={saving}
                    >
                        {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                        {saving ? "Deploying..." : "Apply Changes"}
                    </Button>
                </div>
            </div>
        </div>
    );
}
