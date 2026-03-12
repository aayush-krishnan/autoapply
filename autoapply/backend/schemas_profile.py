from pydantic import BaseModel, Field

class PersonalInfo(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    portfolio: str = ""
    location: str = ""


class EducationEntry(BaseModel):
    institution: str = ""
    degree: str = ""
    graduation: str = ""
    gpa: str = ""
    relevant_courses: list[str] = Field(default_factory=list)


class ExperienceEntry(BaseModel):
    company: str = ""
    title: str = ""
    dates: str = ""
    bullets: list[str] = Field(default_factory=list)
    skills_demonstrated: list[str] = Field(default_factory=list)


class Skills(BaseModel):
    technical: list[str] = Field(default_factory=list)
    domain: list[str] = Field(default_factory=list)
    soft: list[str] = Field(default_factory=list)


class MasterProfileSchema(BaseModel):
    personal: PersonalInfo = Field(default_factory=PersonalInfo)
    summary: str = ""
    education: list[EducationEntry] = Field(default_factory=list)
    experience: list[ExperienceEntry] = Field(default_factory=list)
    skills: Skills = Field(default_factory=Skills)
    projects: list[dict] = Field(default_factory=list)
    certifications: list[dict] = Field(default_factory=list)
    publications: list[dict] = Field(default_factory=list)


class TailoredExperienceEntry(ExperienceEntry):
    pass


class TailoredResumeSchema(MasterProfileSchema):
    fidelity_score: int = 100
