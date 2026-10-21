"""
TalentAI — Shared Data Models
Pydantic schemas used across agents, tools, and API endpoints.
Maintains a shared structured profile across ResumeAnalysisAgent, MatchingAgent,
EvaluationAgent, and Orchestrator.
"""
from __future__ import annotations
from typing import Optional, Dict
from pydantic import BaseModel, Field


class Candidate(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    skills: list[str] = Field(default_factory=list)
    confirmed_skills: list[str] = Field(default_factory=list)
    unverified_skills: list[str] = Field(default_factory=list)
    skill_evidence: Dict[str, str] = Field(default_factory=dict)
    experience_years: float = 0.0  # Total relevant experience in years
    professional_experience_years: float = 0.0
    internship_experience_years: float = 0.0
    project_experience_years: float = 0.0
    experience_verified: bool = True
    education: str = ""
    summary: str = ""
    raw_resume: str = ""


class JobDescription(BaseModel):
    id: str
    title: str
    company: str
    mandatory_requirements: list[str] = Field(default_factory=list)
    preferred_requirements: list[str] = Field(default_factory=list)
    min_experience_years: float = 0.0
    max_experience_years: Optional[float] = None  # e.g., 2.0 for 0–2 years
    experience_requirement_text: str = ""
    description: str = ""
    raw_jd: str = ""


class MatchedCandidate(BaseModel):
    candidate: Candidate
    match_score: float
    score_breakdown: Dict[str, float] = Field(default_factory=dict)
    matched_mandatory: list[str] = Field(default_factory=list)
    matched_preferred: list[str] = Field(default_factory=list)
    missing_mandatory: list[str] = Field(default_factory=list)
    missing_preferred: list[str] = Field(default_factory=list)
    eligibility_status: str = "FULLY_ELIGIBLE"  # FULLY_ELIGIBLE | CONDITIONALLY_ELIGIBLE | NON_COMPLIANT
    is_compliant: bool = True
    evaluation_notes: str = ""
    evidence: Dict[str, str] = Field(default_factory=dict)


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
    shortlisted: list[MatchedCandidate] = Field(default_factory=list)  # Authoritative approved shortlist
    conditionally_eligible: list[MatchedCandidate] = Field(default_factory=list)
    rejected: list[MatchedCandidate] = Field(default_factory=list)
    evaluation_passed: bool = False
    replan_count: int = 0
    relaxed_requirements: bool = False
    messages: list[AgentMessage] = Field(default_factory=list)
    final_communications: list[str] = Field(default_factory=list)
    status: str = "pending"  # pending | running | completed | failed
    final_status: str = "pending"  # COMPLETED_SUCCESS | COMPLETED_PARTIAL | COMPLETED_NO_MATCH
    outcome_summary: str = ""


class RecruitmentRequest(BaseModel):
    job_description: str = Field(..., description="Raw job description text")
    resumes: list[str] = Field(..., description="List of raw resume texts")
    top_n: int = Field(default=5, description="Number of top candidates to return")


class RecruitmentResponse(BaseModel):
    state: RecruitmentState
    execution_trace: list[AgentMessage]
