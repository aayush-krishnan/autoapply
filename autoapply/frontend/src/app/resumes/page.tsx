"use client";

import { useState, useEffect } from "react";
import { User, BookOpen, Briefcase, Wrench, Save, Plus, Trash2 } from "lucide-react";
import { apiRequest } from "@/lib/api";

export default function ResumesPage() {
    const [activeTab, setActiveTab] = useState("personal");
    const [profile, setProfile] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const data = await apiRequest<any>("/api/resumes/master");
                setProfile(data);
            } catch (e) {
                console.error("Failed to fetch master profile:", e);
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, []);

    const handleSave = async () => {
        setSaving(true);
        try {
            await apiRequest("/api/resumes/master", {
                method: "POST",
                body: JSON.stringify(profile),
            });
            alert("Profile saved successfully!");
        } catch (e) {
            console.error(e);
            alert("Failed to save profile.");
        } finally {
            setSaving(false);
        }
    };

    if (loading || !profile) {
        return (
            <div className="p-8 max-w-5xl mx-auto flex justify-center items-center h-full">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    const tabs = [
        { id: "personal", label: "Personal Details", icon: User },
        { id: "education", label: "Education", icon: BookOpen },
        { id: "experience", label: "Experience", icon: Briefcase },
        { id: "skills", label: "Skills", icon: Wrench },
    ];

    return (
        <div className="p-8 max-w-5xl mx-auto h-full flex flex-col">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-white">Master Profile</h1>
                    <p className="text-gray-400 text-sm mt-1">This data powers your auto-generated tailored resumes.</p>
                </div>
                <button
                    onClick={handleSave}
                    disabled={saving}
                    className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-5 py-2.5 rounded-lg font-medium transition-colors shadow-lg shadow-blue-500/20"
                >
                    <Save className="w-4 h-4" />
                    {saving ? "Saving..." : "Save Profile"}
                </button>
            </div>

            <div className="flex gap-8 flex-1 min-h-0">
                {/* Left Sidebar Navigation */}
                <div className="w-64 space-y-2">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${activeTab === tab.id
                                    ? "bg-[#1f1f1f] text-white border border-[#333]"
                                    : "text-gray-400 hover:bg-[#111] hover:text-gray-200 border border-transparent"
                                }`}
                        >
                            <tab.icon className="w-4 h-4" />
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* Right Content Area */}
                <div className="flex-1 bg-[#111111] border border-[#222] rounded-xl p-6 overflow-y-auto">
                    {/* PERSONAL TAB */}
                    {activeTab === "personal" && (
                        <div className="space-y-6">
                            <h2 className="text-lg font-semibold text-white mb-4">Personal Details</h2>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-xs text-gray-400 mb-1">Full Name</label>
                                    <input
                                        type="text"
                                        className="w-full bg-[#1a1a1a] border border-[#333] rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                                        value={profile.personal?.name || ""}
                                        onChange={(e) => setProfile({ ...profile, personal: { ...profile.personal, name: e.target.value } })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs text-gray-400 mb-1">Email</label>
                                    <input
                                        type="email"
                                        className="w-full bg-[#1a1a1a] border border-[#333] rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                                        value={profile.personal?.email || ""}
                                        onChange={(e) => setProfile({ ...profile, personal: { ...profile.personal, email: e.target.value } })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs text-gray-400 mb-1">LinkedIn URL</label>
                                    <input
                                        type="text"
                                        className="w-full bg-[#1a1a1a] border border-[#333] rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                                        value={profile.personal?.linkedin || ""}
                                        onChange={(e) => setProfile({ ...profile, personal: { ...profile.personal, linkedin: e.target.value } })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs text-gray-400 mb-1">Location</label>
                                    <input
                                        type="text"
                                        className="w-full bg-[#1a1a1a] border border-[#333] rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                                        value={profile.personal?.location || ""}
                                        onChange={(e) => setProfile({ ...profile, personal: { ...profile.personal, location: e.target.value } })}
                                    />
                                </div>
                            </div>
                        </div>
                    )}

                    {/* EXPERIENCE TAB */}
                    {activeTab === "experience" && (
                        <div className="space-y-6">
                            <div className="flex justify-between items-center mb-4">
                                <h2 className="text-lg font-semibold text-white">Work Experience</h2>
                                <button
                                    onClick={() => {
                                        const newExp = { company: "", title: "", dates: "", bullets: [""] };
                                        setProfile({ ...profile, experience: [...(profile.experience || []), newExp] });
                                    }}
                                    className="flex items-center gap-1 text-xs text-blue-400 font-medium hover:text-blue-300"
                                >
                                    <Plus className="w-3 h-3" /> Add Role
                                </button>
                            </div>

                            {(profile.experience || []).map((exp: any, idx: number) => (
                                <div key={idx} className="bg-[#1a1a1a] border border-[#333] rounded-lg p-5 relative mb-4">
                                    <button
                                        className="absolute top-4 right-4 text-gray-500 hover:text-red-400"
                                        onClick={() => {
                                            const newExpList = [...profile.experience];
                                            newExpList.splice(idx, 1);
                                            setProfile({ ...profile, experience: newExpList });
                                        }}
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                    <div className="grid grid-cols-2 gap-4 mb-4 pr-8">
                                        <div>
                                            <label className="block text-xs text-gray-400 mb-1">Company</label>
                                            <input
                                                type="text"
                                                className="w-full bg-[#222] border border-[#444] rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-500"
                                                value={exp.company}
                                                onChange={(e) => {
                                                    const newExpList = [...profile.experience];
                                                    newExpList[idx].company = e.target.value;
                                                    setProfile({ ...profile, experience: newExpList });
                                                }}
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-xs text-gray-400 mb-1">Title</label>
                                            <input
                                                type="text"
                                                className="w-full bg-[#222] border border-[#444] rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-500"
                                                value={exp.title}
                                                onChange={(e) => {
                                                    const newExpList = [...profile.experience];
                                                    newExpList[idx].title = e.target.value;
                                                    setProfile({ ...profile, experience: newExpList });
                                                }}
                                            />
                                        </div>
                                        <div className="col-span-2">
                                            <label className="block text-xs text-gray-400 mb-1">Dates (e.g., Jun 2021 - Present)</label>
                                            <input
                                                type="text"
                                                className="w-full bg-[#222] border border-[#444] rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-500"
                                                value={exp.dates}
                                                onChange={(e) => {
                                                    const newExpList = [...profile.experience];
                                                    newExpList[idx].dates = e.target.value;
                                                    setProfile({ ...profile, experience: newExpList });
                                                }}
                                            />
                                        </div>
                                    </div>

                                    {/* Bullets */}
                                    <div>
                                        <label className="block text-xs text-gray-400 mb-2">Master Bullets (Include all details, Gemini will filter these later)</label>
                                        <div className="space-y-2">
                                            {exp.bullets.map((b: string, bIdx: number) => (
                                                <div key={bIdx} className="flex gap-2 mb-2">
                                                    <textarea
                                                        className="w-full bg-[#222] border border-[#444] rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-blue-500 resize-none"
                                                        rows={2}
                                                        value={b}
                                                        onChange={(e) => {
                                                            const newExpList = [...profile.experience];
                                                            newExpList[idx].bullets[bIdx] = e.target.value;
                                                            setProfile({ ...profile, experience: newExpList });
                                                        }}
                                                    />
                                                    <button
                                                        className="p-2 text-gray-500 hover:text-red-400 bg-[#222] border border-[#444] rounded-lg shrink-0 flex items-start"
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
                                                className="text-xs text-blue-400 font-medium hover:text-blue-300 py-1"
                                            >
                                                + Add Bullet
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* EDUCATION TAB */}
                    {activeTab === "education" && (
                        <div className="space-y-6">
                            <div className="flex justify-between items-center mb-4">
                                <h2 className="text-lg font-semibold text-white">Education</h2>
                                <button
                                    onClick={() => {
                                        const newEdu = { institution: "", degree: "", field: "", graduation: "", gpa: "", relevant_courses: [] };
                                        setProfile({ ...profile, education: [...(profile.education || []), newEdu] });
                                    }}
                                    className="flex items-center gap-1 text-xs text-blue-400 font-medium hover:text-blue-300"
                                >
                                    <Plus className="w-3 h-3" /> Add Institution
                                </button>
                            </div>

                            {(profile.education || []).map((edu: any, idx: number) => (
                                <div key={idx} className="bg-[#1a1a1a] border border-[#333] rounded-lg p-5 relative mb-4">
                                    <button
                                        className="absolute top-4 right-4 text-gray-500 hover:text-red-400"
                                        onClick={() => {
                                            const newEduList = [...profile.education];
                                            newEduList.splice(idx, 1);
                                            setProfile({ ...profile, education: newEduList });
                                        }}
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="col-span-2">
                                            <label className="block text-xs text-gray-400 mb-1">Institution</label>
                                            <input
                                                type="text"
                                                className="w-full bg-[#222] border border-[#444] rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-500"
                                                value={edu.institution}
                                                onChange={(e) => {
                                                    const newEduList = [...profile.education];
                                                    newEduList[idx].institution = e.target.value;
                                                    setProfile({ ...profile, education: newEduList });
                                                }}
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-xs text-gray-400 mb-1">Degree</label>
                                            <input
                                                type="text"
                                                className="w-full bg-[#222] border border-[#444] rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-500"
                                                value={edu.degree}
                                                onChange={(e) => {
                                                    const newEduList = [...profile.education];
                                                    newEduList[idx].degree = e.target.value;
                                                    setProfile({ ...profile, education: newEduList });
                                                }}
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-xs text-gray-400 mb-1">Graduation Date</label>
                                            <input
                                                type="text"
                                                className="w-full bg-[#222] border border-[#444] rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-500"
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
                    )}

                    {/* SKILLS TAB */}
                    {activeTab === "skills" && (
                        <div className="space-y-8">
                            <h2 className="text-lg font-semibold text-white mb-4">Skills & Expertise</h2>
                            
                            {['technical', 'domain', 'soft'].map((category) => (
                                <div key={category} className="space-y-3">
                                    <label className="block text-xs uppercase font-black tracking-widest text-gray-500">{category} Skills</label>
                                    <div className="flex flex-wrap gap-2">
                                        {(profile.skills[category] || []).map((skill: string, sIdx: number) => (
                                            <div key={sIdx} className="flex items-center gap-2 bg-[#1a1a1a] border border-[#333] px-3 py-1.5 rounded-lg text-sm group">
                                                <span>{skill}</span>
                                                <button 
                                                    onClick={() => {
                                                        const newSkills = {...profile.skills};
                                                        newSkills[category].splice(sIdx, 1);
                                                        setProfile({...profile, skills: newSkills});
                                                    }}
                                                    className="text-gray-600 hover:text-red-400 transition-colors"
                                                >
                                                    <Trash2 className="w-3.5 h-3.5" />
                                                </button>
                                            </div>
                                        ))}
                                        <button 
                                            onClick={() => {
                                                const skill = prompt(`Add ${category} skill:`);
                                                if (skill) {
                                                    const newSkills = {...profile.skills};
                                                    newSkills[category] = [...(newSkills[category] || []), skill];
                                                    setProfile({...profile, skills: newSkills});
                                                }
                                            }}
                                            className="px-3 py-1.5 rounded-lg border border-dashed border-[#444] text-xs text-blue-400 hover:bg-blue-400/5 transition-colors"
                                        >
                                            + Add
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
