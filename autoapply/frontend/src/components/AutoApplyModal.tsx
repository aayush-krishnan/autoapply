import { useState } from "react";
import { Loader2, Zap, FileText, CheckCircle2, AlertCircle } from "lucide-react";
import { JobListing } from "./JobCard";
import { apiRequest } from "@/lib/api";

interface AutoApplyModalProps {
    job: JobListing;
    onClose: () => void;
}

export default function AutoApplyModal({ job, onClose }: AutoApplyModalProps) {
    const [status, setStatus] = useState<"idle" | "applying" | "success" | "error">("idle");
    const [message, setMessage] = useState("");
    const [screenshot, setScreenshot] = useState<string | null>(null);

    const handleConfirm = async () => {
        setStatus("applying");
        setMessage("Exporting tailored resume and launching automated browser...");

        try {
            const data = await apiRequest<any>(`/api/apply/${job.id}`, {
                method: "POST"
            });

            setStatus("success");
            setMessage("Application form filled successfully! Check the browser to review.");
            if (data.screenshot) {
                setScreenshot(data.screenshot); // In a real app we'd serve this from a static route
            }
        } catch (e: any) {
            setStatus("error");
            setMessage(e.message || "An unexpected error occurred.");
            console.error(e);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
            <div className="bg-[#111111] border border-[#333] w-full max-w-lg rounded-2xl p-6 shadow-2xl relative">

                {/* Header */}
                <div className="mb-6">
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                        <Zap className="w-5 h-5 text-blue-500 fill-blue-500/20" />
                        Automate Application
                    </h2>
                    <p className="text-sm text-gray-400 mt-2">
                        You are about to launch the Auto-Apply engine for <span className="text-gray-200 font-medium">{job.company_name}</span>.
                    </p>
                </div>

                {/* Content Box */}
                <div className="bg-[#1a1a1a] rounded-xl p-4 border border-[#222] mb-6">
                    <div className="flex items-start gap-3 mb-4">
                        <FileText className="w-5 h-5 text-gray-400 mt-0.5" />
                        <div>
                            <div className="text-sm text-gray-200 font-medium">Tailored Resume</div>
                            <div className="text-xs text-gray-500 mt-1">We will compile your {job.company_name} specific Google Doc into a PDF and upload it securely.</div>
                        </div>
                    </div>

                    {status === "applying" && (
                        <div className="p-3 bg-blue-900/20 border border-blue-900/40 rounded-lg flex items-center gap-3">
                            <Loader2 className="w-4 h-4 text-blue-400 animate-spin shrink-0" />
                            <span className="text-xs text-blue-300">{message}</span>
                        </div>
                    )}

                    {status === "error" && (
                        <div className="p-3 bg-red-900/20 border border-red-900/40 rounded-lg flex items-start gap-3">
                            <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                            <span className="text-xs text-red-300">{message}</span>
                        </div>
                    )}

                    {status === "success" && (
                        <div className="p-3 bg-emerald-900/20 border border-emerald-900/40 rounded-lg flex items-start gap-3">
                            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                            <span className="text-xs text-emerald-300">{message}</span>
                        </div>
                    )}
                </div>

                {/* Footer Actions */}
                <div className="flex justify-end gap-3 mt-6">
                    <button
                        onClick={onClose}
                        disabled={status === "applying"}
                        className="px-4 py-2 rounded-lg text-sm font-medium text-gray-400 hover:text-white hover:bg-[#222] transition-colors disabled:opacity-50"
                    >
                        {status === "success" ? "Close" : "Cancel"}
                    </button>

                    {status !== "success" && (
                        <button
                            onClick={handleConfirm}
                            disabled={status === "applying"}
                            className="flex items-center gap-2 px-5 py-2 rounded-lg text-sm font-medium bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-lg shadow-blue-500/20 transition-all disabled:opacity-50"
                        >
                            {status === "applying" ? "Applying..." : "Start Engine"}
                        </button>
                    )}
                </div>

            </div>
        </div>
    );
}
