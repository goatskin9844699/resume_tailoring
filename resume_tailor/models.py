"""Data models for resume-tailor."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class Experience(BaseModel):
    """Work experience information."""
    company: str
    title: str
    startdate: str
    enddate: str
    highlights: List[str]
    location: str = ""


class Education(BaseModel):
    """Education information."""
    name: str
    school: str
    startdate: str
    enddate: str
    highlights: List[str] = []


class Publication(BaseModel):
    """Publication information."""
    authors: str
    title: str
    location: str
    date: str


class SkillCategory(BaseModel):
    """Skill category information."""
    category: str
    skills: List[str]


class Resume(BaseModel):
    """Resume data model."""
    basic: Dict[str, Any]
    education: List[Education]
    experiences: List[Experience]
    objective: str = ""
    projects: List[Any] = []
    publications: List[Publication] = []
    skills: List[SkillCategory] = [] 