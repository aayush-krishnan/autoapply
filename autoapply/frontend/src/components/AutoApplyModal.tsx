"use client";

import { useState } from "react";
import * as Dialog from "@radix-ui/react-dialog";
import { Loader2, Zap, FileText, CheckCircle2, AlertCircle, X } from "lucide-react";
import { JobListing } from "./JobCard";
import { apiRequest } from "@/lib/api";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

interface AutoApplyModalProps {
    job: JobListing;
    onClose: () => void;
}

export default function AutoApplyModal({ job, onClose }: AutoApplyModalProps) {
    const [status, setStatus] = useState<"idle" | "applying" | "success" | "error">("idle");
    const [message, setMessage] = useState("");

    const handleConfirm = async () => {
        setStatus("applying");
        setMessage("Initializing automated browser...");
        const toastId = toast.loading(`Applying to ${job.company_name}...`);

        try {
            await apiRequest<any>(`/api/apply/${job.id}`, {
                method: "POST"
            });

            setStatus("success");
            toast.success("Application form filled!", { id: toastId });
            setMessage("Application form filled successfully. Review and submit in the browser.");
        } catch (e: any) {
            setStatus("error");
            const errMsg = e.message || "Automation failed";
            toast.error(errMsg, { id: toastId });
            setMessage(errMsg);
        }
    };

    return (
        <Dialog.Root open onOpenChange={(open) => !open && onClose()}>
            <Dialog.Portal>
                <Dialog.Overlay className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md transition-all animate-in fade-in" />
                <Dialog.Content className="fixed left-[50%] top-[50%] z-50 w-full max-w-lg translate-x-[-50%] translate-y-[-50%] animate-in zoom-in-95 fade-in duration-200">
                    <Card className="p-0 overflow-hidden border-white/10 bg-black shadow-3xl">
                        <div className="p-8 space-y-6">
                            <div className="flex items-center justify-between">
                                <div className="p-3 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
                                    <Zap className="h-5 w-5 text-white" />
                                </div>
                                <Dialog.Close asChild>
                                    <Button variant="ghost" className="h-8 w-8 p-0 border border-white/5 rounded-full">
                                        <X className="h-4 w-4" />
                                    </Button>
                                </Dialog.Close>
                            </div>

                            <div className="space-y-2">
                                <Dialog.Title className="text-2xl font-bold tracking-tight text-white">
                                    Automate Application
                                </Dialog.Title>
                                <Dialog.Description className="text-white/40 text-sm leading-relaxed">
                                    Launching high-velocity application engine for {job.title} at {job.company_name}.
                                </Dialog.Description>
                            </div>

                            <div className="space-y-4">
                                <div className="flex items-start gap-4 p-4 rounded-xl bg-white/[0.02] border border-white/[0.04]">
                                    <FileText className="w-5 h-5 text-white/20 mt-0.5" />
                                    <div className="space-y-1">
                                        <div className="text-sm font-medium text-white">Resume Injection</div>
                                        <p className="text-xs text-white/30 leading-relaxed">
                                            The system will generate a PDF from your tailored Google Doc and inject it into {job.company_name}&apos;s ATS form.
                                        </p>
                                    </div>
                                </div>

                                {status !== "idle" && (
                                    <div className={cn(
                                        "p-4 rounded-xl border flex items-center gap-3 transition-all",
                                        status === "applying" && "bg-white/[0.02] border-white/10",
                                        status === "success" && "bg-emerald-500/5 border-emerald-500/10",
                                        status === "error" && "bg-red-500/5 border-red-500/10"
                                    )}>
                                        {status === "applying" && <Loader2 className="h-4 w-4 animate-spin text-white/40" />}
                                        {status === "success" && <CheckCircle2 className="h-4 w-4 text-emerald-400" />}
                                        {status === "error" && <AlertCircle className="h-4 w-4 text-red-400" />}
                                        <span className={cn(
                                            "text-xs font-medium",
                                            status === "applying" && "text-white/40",
                                            status === "success" && "text-emerald-400",
                                            status === "error" && "text-red-400"
                                        )}>
                                            {message}
                                        </span>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="flex items-center justify-end gap-3 p-6 bg-white/[0.02] border-t border-white/[0.04]">
                            <Dialog.Close asChild>
                                <Button variant="ghost" disabled={status === "applying"}>
                                    {status === "success" ? "Done" : "Cancel"}
                                </Button>
                            </Dialog.Close>
                            {status !== "success" && (
                                <Button 
                                    variant="primary" 
                                    className="rounded-xl px-6"
                                    onClick={handleConfirm}
                                    disabled={status === "applying"}
                                >
                                    {status === "applying" ? "Executing..." : "Start Engine"}
                                </Button>
                            )}
                        </div>
                    </Card>
                </Dialog.Content>
            </Dialog.Portal>
        </Dialog.Root>
    );
}
