"use client";

import React, { useEffect, useState } from "react";
import { Command } from "cmdk";
import { Search, Briefcase, FileText, Settings, Zap, History } from "lucide-react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";

export function CommandMenu() {
  const [open, setOpen] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
    };

    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, []);

  const runCommand = (command: () => void) => {
    setOpen(false);
    command();
  };

  return (
    <Command.Dialog
      open={open}
      onOpenChange={setOpen}
      label="Global Command Menu"
      className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh] bg-black/80 backdrop-blur-sm transition-all animate-in fade-in"
    >
      <div className="w-full max-w-xl overflow-hidden rounded-2xl border border-white/10 bg-[#0a0a0a] shadow-3xl animate-in zoom-in-95 duration-200">
        <div className="flex items-center border-b border-white/5 px-4">
          <Search className="mr-3 h-4 w-4 text-white/20" />
          <Command.Input
            placeholder="Type a command or search..."
            className="flex h-12 w-full bg-transparent py-3 text-sm text-white outline-none placeholder:text-white/20"
          />
          <kbd className="hidden sm:inline-flex h-5 select-none items-center gap-1 rounded border border-white/10 bg-white/5 px-1.5 font-mono text-[10px] font-medium text-white/40 opacity-100">
            <span className="text-xs">ESC</span>
          </kbd>
        </div>

        <Command.List className="max-h-[300px] overflow-y-auto p-2">
          <Command.Empty className="py-6 text-center text-sm text-white/20">
            No results found.
          </Command.Empty>

          <Command.Group heading="Navigation" className="px-2 py-1.5 text-[11px] font-bold uppercase tracking-widest text-white/20">
            <Command.Item
              onSelect={() => runCommand(() => router.push("/"))}
              className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-white/60 hover:text-white hover:bg-white/5 cursor-pointer transition-colors"
            >
              <Briefcase className="h-4 w-4" />
              Go to Dashboard
            </Command.Item>
            <Command.Item
              onSelect={() => runCommand(() => router.push("/resumes"))}
              className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-white/60 hover:text-white hover:bg-white/5 cursor-pointer transition-colors"
            >
              <FileText className="h-4 w-4" />
              Manage Resumes
            </Command.Item>
            <Command.Item
              onSelect={() => runCommand(() => router.push("/applications"))}
              className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-white/60 hover:text-white hover:bg-white/5 cursor-pointer transition-colors"
            >
              <History className="h-4 w-4" />
              View Applications
            </Command.Item>
            <Command.Item
              onSelect={() => runCommand(() => router.push("/settings"))}
              className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-white/60 hover:text-white hover:bg-white/5 cursor-pointer transition-colors"
            >
              <Settings className="h-4 w-4" />
              System Settings
            </Command.Item>
          </Command.Group>

          <Command.Group heading="Actions" className="px-2 py-1.5 mt-2 text-[11px] font-bold uppercase tracking-widest text-white/20">
            <Command.Item
              onSelect={() => runCommand(() => window.dispatchEvent(new Event('trigger-scrape')))}
              className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-white/60 hover:text-white hover:bg-emerald-500/10 hover:text-emerald-400 cursor-pointer transition-colors"
            >
              <Zap className="h-4 w-4" />
              Sync Market Data
            </Command.Item>
          </Command.Group>
        </Command.List>

        <div className="flex items-center justify-between border-t border-white/5 bg-white/[0.01] px-4 py-3">
          <div className="flex items-center gap-4">
             <div className="flex items-center gap-1.5">
                <kbd className="rounded border border-white/10 bg-white/5 px-1 font-mono text-[10px] text-white/40">↑↓</kbd>
                <span className="text-[10px] text-white/20 uppercase font-bold tracking-widest">Navigate</span>
             </div>
             <div className="flex items-center gap-1.5">
                <kbd className="rounded border border-white/10 bg-white/5 px-1 font-mono text-[10px] text-white/40">ENTER</kbd>
                <span className="text-[10px] text-white/20 uppercase font-bold tracking-widest">Execute</span>
             </div>
          </div>
        </div>
      </div>
    </Command.Dialog>
  );
}
