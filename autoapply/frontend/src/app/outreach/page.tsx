"use client";

import { Send, Clock, Sparkles } from "lucide-react";

export default function OutreachPage() {
    return (
        <div className="p-8 max-w-7xl mx-auto min-h-screen bg-background text-white">
            <header className="mb-12">
                <h1 className="text-4xl font-black flex items-center gap-3">
                    <Send className="w-10 h-10 text-indigo-500" />
                    Network Outreach
                </h1>
                <p className="text-gray-400 mt-2 font-medium">Coming soon: Automated LinkedIn follow-ups and warm intros.</p>
            </header>

            <div className="text-center py-40 glass-effect rounded-[40px] border border-white/5 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 to-transparent opacity-50" />
                <div className="relative z-10">
                    <div className="w-24 h-24 bg-indigo-500/10 rounded-full flex items-center justify-center mx-auto mb-8 animate-pulse">
                        <Sparkles className="w-12 h-12 text-indigo-400" />
                    </div>
                    <h2 className="text-3xl font-black mb-4">Phase 9 Construction</h2>
                    <p className="text-gray-500 max-w-md mx-auto text-lg">
                        We are building the Gemini-powered outreach engine to automate your networking strategy. Stay tuned!
                    </p>
                </div>
            </div>
        </div>
    );
}
