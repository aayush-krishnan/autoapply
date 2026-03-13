"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Briefcase, FileText, Send, Settings, LineChart, ChevronRight } from "lucide-react";
import { apiRequest } from "@/lib/api";
import { cn } from "@/lib/utils";

export default function Sidebar() {
    const pathname = usePathname();
    const [userName, setUserName] = useState("User");

    useEffect(() => {
        apiRequest<any>("/api/resumes/master")
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
        <div className="w-64 bg-black flex flex-col pt-8 h-full">
            <div className="px-8 mb-10">
                <h1 className="text-lg font-bold tracking-tight text-white">
                    AutoApply
                </h1>
                <div className="h-[1px] w-8 bg-white/20 mt-3" />
            </div>

            <nav className="flex-1 px-4 space-y-1">
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "flex items-center justify-between px-4 py-2.5 rounded-xl text-sm transition-all duration-200 group",
                                isActive
                                    ? "bg-white/[0.06] text-white font-medium"
                                    : "text-white/40 hover:text-white hover:bg-white/[0.03]"
                            )}
                        >
                            <div className="flex items-center gap-3">
                                <item.icon className={cn("w-4 h-4 transition-colors", isActive ? "text-white" : "text-white/20 group-hover:text-white/40")} />
                                {item.name}
                            </div>
                            {isActive && <div className="w-1 h-1 rounded-full bg-white" />}
                        </Link>
                    );
                })}
            </nav>

            <div className="p-6 border-t border-white/[0.06] bg-white/[0.01]">
                <div className="flex items-center gap-3 px-2">
                    <div className="w-8 h-8 rounded-full bg-white text-black flex items-center justify-center font-bold text-xs ring-4 ring-white/5">
                        {userName.charAt(0).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-white truncate">{userName}</div>
                        <div className="text-[10px] text-white/30 uppercase tracking-widest font-bold">Standard</div>
                    </div>
                    <ChevronRight className="w-3 h-3 text-white/10" />
                </div>
            </div>
        </div>
    );
}
