"""
TalentAI — Data Loader
Loads sample data from JSON files and provides demo execution trace.
"""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone

_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def get_samples() -> dict:
    """Load sample jobs and resumes from JSON files."""
    jobs_path = os.path.join(_DATA_DIR, "sample_jobs.json")
    resumes_path = os.path.join(_DATA_DIR, "sample_resumes.json")

    with open(jobs_path) as f:
        jobs = json.load(f)
    with open(resumes_path) as f:
        resumes = json.load(f)

    return {
        "jobs": jobs,
        "resumes": resumes,
    }


def get_demo_trace() -> list[dict]:
    """
    Returns a pre-built, realistic execution trace showing all 5 agents
    communicating, including a conflict (EvaluationAgent rejecting shortlist)
    and Orchestrator replanning.
    """
    ts = datetime.now(timezone.utc).isoformat()
    return [
        {
            "agent": "Orchestrator",
            "role": "action",
            "content": "🚀 Pipeline started. Processing 6 resume(s) for job analysis.",
            "timestamp": ts,
        },
        {
            "agent": "Orchestrator",
            "role": "decision",
            "content": "Delegating job description analysis to JobAnalysisAgent.",
            "timestamp": ts,
        },
        {
            "agent": "JobAnalysisAgent",
            "role": "action",
            "content": "Analyzed JD for 'Senior Full Stack Engineer' at TechNova Inc. Identified 5 mandatory and 3 preferred requirements.",
            "timestamp": ts,
        },
        {
            "agent": "Orchestrator",
            "role": "decision",
            "content": "JobAnalysisAgent completed. Delegating resume analysis for 6 resume(s).",
            "timestamp": ts,
        },
        {
            "agent": "ResumeAnalysisAgent",
            "role": "action",
            "content": "Analyzed resume for Priya Sharma — extracted 12 skills, 6.0 yrs exp",
            "timestamp": ts,
        },
        {
            "agent": "ResumeAnalysisAgent",
            "role": "action",
            "content": "Analyzed resume for Kavya Reddy — extracted 14 skills, 7.0 yrs exp",
            "timestamp": ts,
        },
        {
            "agent": "ResumeAnalysisAgent",
            "role": "action",
            "content": "Analyzed resume for Arjun Mehta — extracted 6 skills, 3.0 yrs exp",
            "timestamp": ts,
        },
        {
            "agent": "MatchingAgent",
            "role": "action",
            "content": "[NORMAL] Ranked 6 candidates → shortlisted top 3. Top candidates: Kavya Reddy (87.5), Priya Sharma (82.0), Arjun Mehta (41.0).",
            "timestamp": ts,
        },
        {
            "agent": "EvaluationAgent",
            "role": "conflict",
            "content": "⚠️ SHORTLIST REJECTED by EvaluationAgent. Reason: Arjun Mehta is missing mandatory requirements: TypeScript, Docker, Kubernetes. Flagged: ['Arjun Mehta']. Approved 2/3 candidates. Triggering Orchestrator replanning.",
            "timestamp": ts,
        },
        {
            "agent": "Orchestrator",
            "role": "conflict",
            "content": "⚠️ EvaluationAgent REJECTED shortlist (round 1). Orchestrator initiating replanning analysis.",
            "timestamp": ts,
        },
        {
            "agent": "Orchestrator",
            "role": "replan",
            "content": "🔄 Replan decision: REPLAN_RELAXED. Reasoning: With 2 qualified candidates already identified, relaxing preferred requirements will allow us to surface the best available candidates without compromising on mandatory skills.",
            "timestamp": ts,
        },
        {
            "agent": "MatchingAgent",
            "role": "replan",
            "content": "[RELAXED] Ranked 6 candidates → shortlisted top 3 with relaxed preferred requirements. Kavya Reddy (90.0), Priya Sharma (85.0), Aisha Patel (72.0).",
            "timestamp": ts,
        },
        {
            "agent": "EvaluationAgent",
            "role": "result",
            "content": "✅ SHORTLIST APPROVED by EvaluationAgent. 3/3 candidates approved. No critical mandatory skills missing.",
            "timestamp": ts,
        },
        {
            "agent": "Orchestrator",
            "role": "decision",
            "content": "✅ EvaluationAgent approved 3 candidate(s). Proceeding to communication generation.",
            "timestamp": ts,
        },
        {
            "agent": "CommunicationAgent",
            "role": "result",
            "content": "Generated 3 interview invitation(s) and 3 rejection notice(s) for the 'Senior Full Stack Engineer' role at TechNova Inc.",
            "timestamp": ts,
        },
        {
            "agent": "Orchestrator",
            "role": "result",
            "content": "🎉 Recruitment pipeline complete. Processed 6 candidates. Shortlisted 3. Approved: 3. Replan rounds: 1. Requirement relaxation: YES.",
            "timestamp": ts,
        },
    ]
