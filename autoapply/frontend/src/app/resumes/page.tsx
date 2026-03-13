"use client";

import { useState, useEffect } from "react";
import { User, BookOpen, Briefcase, Wrench, Save, Plus, Trash2, Loader2, ChevronRight } from "lucide-react";
import { apiRequest } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

export default function ResumesPage() {
    const [activeTab, setActiveTab] = useState("personal");
    const [profile, setProfile] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [newSkill, setNewSkill] = useState("");

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const data = await apiRequest<any>("/api/resumes/master");
                setProfile(data);
            } catch (e) {
                toast.error("Failed to fetch master profile");
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, []);

    const handleSave = async () => {
        setSaving(true);
        const toastId = toast.loading("Saving profile changes...");
        try {
            await apiRequest("/api/resumes/master", {
                method: "POST",
                body: JSON.stringify(profile),
            });
            toast.success("Master profile updated", { id: toastId });
        } catch (e) {
            toast.error("Save failed", { id: toastId });
        } finally {
            setSaving(false);
        }
    };

    if (loading || !profile) {
        return (
            <div className="p-12 flex justify-center items-center h-screen">
                <Loader2 className="h-8 w-8 animate-spin text-white/20" />
            </div>
        );
    }

    const tabs = [
        { id: "personal", label: "Personal Info", icon: User },
        { id: "education", label: "Education", icon: BookOpen },
        { id: "experience", label: "Work History", icon: Briefcase },
        { id: "skills", label: "Core Skills", icon: Wrench },
    ];

    return (
        <div className="p-8 lg:p-12 max-w-6xl mx-auto space-y-12">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
                <div className="space-y-2">
                    <Badge variant="ghost" className="px-0">Master Identity</Badge>
                    <h1 className="text-4xl font-bold tracking-tight text-white leading-tight">
                        Career Profile
                    </h1>
                    <p className="text-white/40 text-lg font-medium leading-relaxed">
                        The foundation of your AI-driven resume tailoring.
                    </p>
                </div>
                <Button 
                    variant="primary" 
                    className="rounded-full px-8 py-6 shadow-2xl shadow-white/5"
                    onClick={handleSave}
                    disabled={saving}
                >
                    {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                    {saving ? "Syncing..." : "Push Changes"}
                </Button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-12 items-start">
                {/* Navigation Sidebar */}
                <div className="space-y-2">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={cn(
                                "w-full flex items-center justify-between px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 group",
                                activeTab === tab.id
                                    ? "bg-white/[0.06] text-white"
                                    : "text-white/30 hover:text-white/60 hover:bg-white/[0.02]"
                            )}
                        >
                            <div className="flex items-center gap-3">
                                <tab.icon className={cn("w-4 h-4", activeTab === tab.id ? "text-white" : "text-white/20")} />
                                {tab.label}
                            </div>
                            {activeTab === tab.id && <ChevronRight className="w-3 h-3 text-white/40" />}
                        </button>
                    ))}
                </div>

                {/* Content Area */}
                <Card className="lg:col-span-3 min-h-[600px] border-white/5 bg-white/[0.01]">
                    {/* PERSONAL TAB */}
                    {activeTab === "personal" && (
                        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-300">
                            <div className="space-y-1">
                                <h2 className="text-xl font-bold text-white tracking-tight">Personal Details</h2>
                                <p className="text-sm text-white/30">Your essential contact information.</p>
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
                                <div className="space-y-3">
                                    <label className="text-[11px] font-bold uppercase tracking-widest text-white/20">Full Name</label>
                                    <Input
                                        value={profile.personal?.name || ""}
                                        onChange={(e) => setProfile({ ...profile, personal: { ...profile.personal, name: e.target.value } })}
                                    />
                                </div>
                                <div className="space-y-3">
                                    <label className="text-[11px] font-bold uppercase tracking-widest text-white/20">Email Address</label>
                                    <Input
                                        value={profile.personal?.email || ""}
                                        onChange={(e) => setProfile({ ...profile, personal: { ...profile.personal, email: e.target.value } })}
                                    />
                                </div>
                                <div className="space-y-3">
                                    <label className="text-[11px] font-bold uppercase tracking-widest text-white/20">LinkedIn Profile</label>
                                    <Input
                                        value={profile.personal?.linkedin || ""}
                                        onChange={(e) => setProfile({ ...profile, personal: { ...profile.personal, linkedin: e.target.value } })}
                                    />
                                </div>
                                <div className="space-y-3">
                                    <label className="text-[11px] font-bold uppercase tracking-widest text-white/20">Current Location</label>
                                    <Input
                                        value={profile.personal?.location || ""}
                                        onChange={(e) => setProfile({ ...profile, personal: { ...profile.personal, location: e.target.value } })}
                                    />
                                </div>
                            </div>
                        </div>
                    )}

                    {/* EXPERIENCE TAB */}
                    {activeTab === "experience" && (
                        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-300">
                            <div className="flex justify-between items-end">
                                <div className="space-y-1">
                                    <h2 className="text-xl font-bold text-white tracking-tight">Work History</h2>
                                    <p className="text-sm text-white/30">Gemini will filter these based on job specs.</p>
                                </div>
                                <Button 
                                    variant="outline" 
                                    className="rounded-full h-9 px-4 text-xs"
                                    onClick={() => {
                                        const newExp = { company: "", title: "", dates: "", bullets: [""] };
                                        setProfile({ ...profile, experience: [newExp, ...(profile.experience || [])] });
                                    }}
                                >
                                    <Plus className="w-3.5 h-3.5" /> Append Role
                                </Button>
                            </div>

                            <div className="space-y-6">
                                {(profile.experience || []).map((exp: any, idx: number) => (
                                    <div key={idx} className="group relative bg-white/[0.02] border border-white/[0.04] p-6 rounded-2xl hover:bg-white/[0.03] transition-colors">
                                        <button
                                            className="absolute top-6 right-6 text-white/10 hover:text-red-400 transition-colors"
                                            onClick={() => {
                                                const newExpList = [...profile.experience];
                                                newExpList.splice(idx, 1);
                                                setProfile({ ...profile, experience: newExpList });
                                            }}
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                        
                                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-8">
                                            <div className="space-y-3">
                                                <label className="text-[11px] font-bold uppercase tracking-widest text-white/20">Company</label>
                                                <Input
                                                    className="bg-transparent"
                                                    value={exp.company}
                                                    onChange={(e) => {
                                                        const newExpList = [...profile.experience];
                                                        newExpList[idx].company = e.target.value;
                                                        setProfile({ ...profile, experience: newExpList });
                                                    }}
                                                />
                                            </div>
                                            <div className="space-y-3">
                                                <label className="text-[11px] font-bold uppercase tracking-widest text-white/20">Role Title</label>
                                                <Input
                                                    className="bg-transparent"
                                                    value={exp.title}
                                                    onChange={(e) => {
                                                        const newExpList = [...profile.experience];
                                                        newExpList[idx].title = e.target.value;
                                                        setProfile({ ...profile, experience: newExpList });
                                                    }}
                                                />
                                            </div>
                                        </div>

                                        <div className="space-y-4">
                                            <label className="text-[11px] font-bold uppercase tracking-widest text-white/20">Key Achievements</label>
                                            <div className="space-y-3">
                                                {exp.bullets.map((b: string, bIdx: number) => (
                                                    <div key={bIdx} className="flex gap-3 group/bullet">
                                                        <textarea
                                                            className="flex-1 bg-white/[0.02] border border-white/[0.04] rounded-xl px-4 py-3 text-sm text-white/80 focus:outline-none focus:border-white/20 focus:bg-white/[0.04] transition-all resize-none"
                                                            rows={2}
                                                            value={b}
                                                            onChange={(e) => {
                                                                const newExpList = [...profile.experience];
                                                                newExpList[idx].bullets[bIdx] = e.target.value;
                                                                setProfile({ ...profile, experience: newExpList });
                                                            }}
                                                        />
                                                        <button
                                                            className="opacity-0 group-hover/bullet:opacity-100 p-3 h-fit text-white/10 hover:text-red-400 transition-all bg-white/[0.02] border border-white/[0.04] rounded-xl"
                                                            onClick={() => {
                                                                const newExpList = [...profile.experience];
                                                                newExpList[idx].bullets.splice(bIdx, 1);
                                                                setProfile({ ...profile, experience: newExpList });
                                                            }}
                                                        >
                                                            <Trash2 className="w-4 h-4" />
                                                        </button>
                                                    </div>
                                                ))}
                                                <button
                                                    onClick={() => {
                                                        const newExpList = [...profile.experience];
                                                        newExpList[idx].bullets.push("");
                                                        setProfile({ ...profile, experience: newExpList });
                                                    }}
                                                    className="text-xs text-white/40 font-bold hover:text-white transition-colors py-2 px-1"
                                                >
                                                    + Push Achievement
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* EDUCATION TAB */}
                    {activeTab === "education" && (
                        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-300">
                             <div className="flex justify-between items-end">
                                <div className="space-y-1">
                                    <h2 className="text-xl font-bold text-white tracking-tight">Academic History</h2>
                                    <p className="text-sm text-white/30">Verified credentials.</p>
                                </div>
                                <Button 
                                    variant="outline" 
                                    className="rounded-full h-9 px-4 text-xs"
                                    onClick={() => {
                                        const newEdu = { institution: "", degree: "", field: "", graduation: "", gpa: "", relevant_courses: [] };
                                        setProfile({ ...profile, education: [newEdu, ...(profile.education || [])] });
                                    }}
                                >
                                    <Plus className="w-3.5 h-3.5" /> Append Degree
                                </Button>
                            </div>

                            <div className="space-y-6">
                                {(profile.education || []).map((edu: any, idx: number) => (
                                    <div key={idx} className="relative bg-white/[0.02] border border-white/[0.04] p-6 rounded-2xl">
                                        <button
                                            className="absolute top-6 right-6 text-white/10 hover:text-red-400 transition-colors"
                                            onClick={() => {
                                                const newEduList = [...profile.education];
                                                newEduList.splice(idx, 1);
                                                setProfile({ ...profile, education: newEduList });
                                            }}
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                                            <div className="col-span-1 sm:col-span-2 space-y-3">
                                                <label className="text-[11px] font-bold uppercase tracking-widest text-white/20">Institution</label>
                                                <Input
                                                    className="bg-transparent"
                                                    value={edu.institution}
                                                    onChange={(e) => {
                                                        const newEduList = [...profile.education];
                                                        newEduList[idx].institution = e.target.value;
                                                        setProfile({ ...profile, education: newEduList });
                                                    }}
                                                />
                                            </div>
                                            <div className="space-y-3">
                                                <label className="text-[11px] font-bold uppercase tracking-widest text-white/20">Degree</label>
                                                <Input
                                                    className="bg-transparent"
                                                    value={edu.degree}
                                                    onChange={(e) => {
                                                        const newEduList = [...profile.education];
                                                        newEduList[idx].degree = e.target.value;
                                                        setProfile({ ...profile, education: newEduList });
                                                    }}
                                                />
                                            </div>
                                            <div className="space-y-3">
                                                <label className="text-[11px] font-bold uppercase tracking-widest text-white/20">Graduation Month/Year</label>
                                                <Input
                                                    className="bg-transparent"
                                                    value={edu.graduation}
                                                    onChange={(e) => {
                                                        const newEduList = [...profile.education];
                                                        newEduList[idx].graduation = e.target.value;
                                                        setProfile({ ...profile, education: newEduList });
                                                    }}
                                                />
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* SKILLS TAB */}
                    {activeTab === "skills" && (
                        <div className="space-y-12 animate-in fade-in slide-in-from-bottom-2 duration-300">
                             <div className="space-y-1">
                                <h2 className="text-xl font-bold text-white tracking-tight">Competency Matrix</h2>
                                <p className="text-sm text-white/30">Multi-layered skill categorization.</p>
                            </div>
                            
                            {['technical', 'domain', 'soft'].map((category) => (
                                <div key={category} className="space-y-6">
                                    <label className="block text-[11px] font-bold uppercase tracking-[0.2em] text-white/20">{category} Focus</label>
                                    <div className="flex flex-wrap gap-2.5">
                                        {(profile.skills[category] || []).map((skill: string, sIdx: number) => (
                                            <Badge key={sIdx} variant="outline" className="h-9 px-4 rounded-full bg-white/[0.02] border-white/5 hover:bg-white/[0.04] transition-colors gap-2 group/skill">
                                                {skill}
                                                <button 
                                                    onClick={() => {
                                                        const newSkills = {...profile.skills};
                                                        newSkills[category].splice(sIdx, 1);
                                                        setProfile({...profile, skills: newSkills});
                                                    }}
                                                    className="opacity-0 group-hover/skill:opacity-100 text-white/20 hover:text-red-400 transition-all -mr-1"
                                                >
                                                    <X className="w-3.5 h-3.5" />
                                                </button>
                                            </Badge>
                                        ))}
                                    </div>
                                    <div className="flex gap-2 max-w-sm">
                                        <Input 
                                            placeholder={`Push new ${category} skill...`}
                                            className="h-10 text-xs bg-transparent"
                                            value={category === 'technical' ? newSkill : ""}
                                            onChange={(e) => category === 'technical' && setNewSkill(e.target.value)}
                                            onKeyDown={(e) => {
                                                if (e.key === 'Enter' && e.currentTarget.value) {
                                                    const val = e.currentTarget.value;
                                                    const newSkills = {...profile.skills};
                                                    newSkills[category] = [...(newSkills[category] || []), val];
                                                    setProfile({...profile, skills: newSkills});
                                                    if (category === 'technical') setNewSkill("");
                                                }
                                            }}
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </Card>
            </div>
        </div>
    );
}

function X({ className }: { className?: string }) {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
            <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
        </svg>
    )
}
