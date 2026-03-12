"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Briefcase, FileText, Send, Settings, LineChart, User } from "lucide-react";

export default function Sidebar() {
    const pathname = usePathname();
    const [userName, setUserName] = useState("User");

    useEffect(() => {
        // Fetch real name from master profile
        fetch("http://localhost:8000/api/resumes/master")
            .then(res => res.json())
            .then(data => {
                if (data?.personal?.name) {
                    setUserName(data.personal.name);
                }
            })
            .catch(e => console.error("Could not fetch user profile", e));
    }, []);

    const navItems = [
        { name: "Dashboard", href: "/", icon: Home },
        { name: "Jobs Feed", href: "/jobs", icon: Briefcase },
        { name: "Resumes", href: "/resumes", icon: FileText },
        { name: "Applications", href: "/applications", icon: LineChart },
        { name: "Outreach", href: "/outreach", icon: Send },
        { name: "Settings", href: "/settings", icon: Settings },
    ];

    return (
        <div className="w-64 bg-[#111111] border-r border-[#222] flex flex-col pt-6 h-full">
            <div className="px-6 mb-8">
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
                    AutoApply
                </h1>
                <p className="text-xs text-gray-400 mt-1">MEM Job Automation</p>
            </div>

            <nav className="flex-1 px-4 space-y-1">
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${isActive
                                ? "bg-blue-500/10 text-blue-400"
                                : "text-gray-400 hover:text-gray-100 hover:bg-[#222]"
                                }`}
                        >
                            <item.icon className="w-4 h-4" />
                            {item.name}
                        </Link>
                    );
                })}
            </nav>

            <div className="p-6 border-t border-[#1a1a1a]">
                <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-full bg-[#111] border border-[#333] flex items-center justify-center font-bold text-sm text-white shadow-inner">
                        {userName.charAt(0).toUpperCase()}
                    </div>
                    <div>
                        <div className="text-sm font-semibold text-white tracking-tight">{userName}</div>
                        <div className="text-[10px] uppercase tracking-widest text-gray-500 font-bold mt-0.5">Free Tier</div>
                    </div>
                </div>
            </div>
        </div>
    );
}
