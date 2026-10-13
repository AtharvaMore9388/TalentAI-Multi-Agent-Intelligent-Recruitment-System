"""
TalentAI — Shared Data Models
Pydantic schemas used across agents and API endpoints.
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class Candidate(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    skills: list[str] = Field(default_factory=list)
    experience_years: float = 0.0
    education: str = ""
    summary: str = ""
    raw_resume: str = ""


class JobDescription(BaseModel):
    id: str
    title: str
    company: str
    mandatory_requirements: list[str] = Field(default_factory=list)
    preferred_requirements: list[str] = Field(default_factory=list)
    description: str = ""
    raw_jd: str = ""


class MatchedCandidate(BaseModel):
    candidate: Candidate
    match_score: float
    matched_mandatory: list[str] = Field(default_factory=list)
    matched_preferred: list[str] = Field(default_factory=list)
    missing_mandatory: list[str] = Field(default_factory=list)
    missing_preferred: list[str] = Field(default_factory=list)
    evaluation_notes: str = ""


class AgentMessage(BaseModel):
    """Message exchanged between agents — logged and streamed to frontend."""
    agent: str
    role: str  # "action" | "decision" | "conflict" | "replan" | "result"
    content: str
    timestamp: Optional[str] = None


class RecruitmentState(BaseModel):
    """Shared state object managed by the Orchestrator."""
    job: Optional[JobDescription] = None
    candidates: list[Candidate] = Field(default_factory=list)
    shortlisted: list[MatchedCandidate] = Field(default_factory=list)
    evaluation_passed: bool = False
    replan_count: int = 0
    relaxed_requirements: bool = False
    messages: list[AgentMessage] = Field(default_factory=list)
    final_communications: list[str] = Field(default_factory=list)
    status: str = "pending"  # pending | running | completed | failed


class RecruitmentRequest(BaseModel):
    job_description: str = Field(..., description="Raw job description text")
    resumes: list[str] = Field(..., description="List of raw resume texts")
    top_n: int = Field(default=5, description="Number of top candidates to return")


class RecruitmentResponse(BaseModel):
    state: RecruitmentState
    execution_trace: list[AgentMessage]
