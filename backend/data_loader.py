"""
TalentAI — Data Loader & Concrete Worked Example
Provides sample data, sample jobs, resumes, and end-to-end worked example traces
demonstrating all 6 agents (Orchestrator, JobAnalysis, ResumeAnalysis, Matching,
Evaluation critic with conflict, and Communication).
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

    with open(jobs_path, encoding="utf-8") as f:
        jobs = json.load(f)
    with open(resumes_path, encoding="utf-8") as f:
        resumes = json.load(f)

    return {
        "jobs": jobs,
        "resumes": resumes,
    }


def get_demo_trace() -> list[dict]:
    """
    Returns a concrete worked example walking through all 6 agents:
      1. OrchestratorAgent (coordinates and delegates)
      2. JobAnalysisAgent (extracts 5 mandatory, 3 preferred criteria)
      3. ResumeAnalysisAgent (parses and indexes 6 resumes in ChromaDB)
      4. MatchingAgent (semantic RAG search + deterministic scoring)
      5. EvaluationAgent (independent critic: challenges MatchingAgent, rejects Arjun Mehta)
      6. OrchestratorAgent (detects conflict, executes dynamic replanning: relax preferred, keep mandatory)
      7. MatchingAgent (re-scores and surfaces qualified candidate)
      8. EvaluationAgent (re-audits and approves shortlist)
      9. CommunicationAgent (generates personalized invitations and candidate notices)
    """
    ts = datetime.now(timezone.utc).isoformat()
    return [
        {
            "agent": "Orchestrator",
            "role": "action",
            "content": "🚀 Pipeline started. Processing 6 candidate resumes for 'Senior Full Stack Engineer' at TechNova Inc.",
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
            "content": "Analyzed JD for 'Senior Full Stack Engineer' at TechNova Inc.\n• Mandatory (Non-negotiable): React, Node.js, TypeScript, PostgreSQL, 5+ years experience\n• Preferred (Nice-to-have): AWS cloud deployment, Docker/Kubernetes containerization, GraphQL API design",
            "timestamp": ts,
        },
        {
            "agent": "Orchestrator",
            "role": "decision",
            "content": "JobAnalysisAgent completed: 5 mandatory requirements & 3 preferred requirements identified. Delegating resume analysis for 6 candidates.",
            "timestamp": ts,
        },
        {
            "agent": "ResumeAnalysisAgent",
            "role": "action",
            "content": "Analyzed resume for Kavya Reddy — extracted 14 skills (TypeScript, React, Node.js, AWS, Kubernetes, PostgreSQL), 7.0 yrs exp, Lead Engineer at Razorpay.",
            "timestamp": ts,
        },
        {
            "agent": "ResumeAnalysisAgent",
            "role": "action",
            "content": "Analyzed resume for Priya Sharma — extracted 12 skills (React, Node.js, Python, AWS, Docker), 6.0 yrs exp, Senior SWE at Infosys.",
            "timestamp": ts,
        },
        {
            "agent": "ResumeAnalysisAgent",
            "role": "action",
            "content": "Analyzed resume for Arjun Mehta — extracted 6 skills (React, JavaScript, Node.js, basic MySQL), 3.0 yrs exp, Junior Developer at StartupXYZ.",
            "timestamp": ts,
        },
        {
            "agent": "ResumeAnalysisAgent",
            "role": "action",
            "content": "Analyzed resume for Aisha Patel — extracted 11 skills (Python, FastAPI, Docker, Kubernetes, AWS), 5.0 yrs exp, ML/Backend at Google India.",
            "timestamp": ts,
        },
        {
            "agent": "Orchestrator",
            "role": "action",
            "content": "All 6 resumes parsed and indexed into ChromaDB vector space. Delegating semantic ranking to MatchingAgent.",
            "timestamp": ts,
        },
        {
            "agent": "MatchingAgent",
            "role": "action",
            "content": "[INITIAL SEARCH] Ranked 6 candidates using ChromaDB RAG + scoring tool → shortlisted top 3:\n1. Kavya Reddy — Score: 87.5/100 (Full Stack & Cloud Lead)\n2. Priya Sharma — Score: 82.0/100 (Senior Full Stack)\n3. Arjun Mehta — Score: 41.0/100 (Included to fulfill requested top_n=3)",
            "timestamp": ts,
        },
        {
            "agent": "Orchestrator",
            "role": "decision",
            "content": "MatchingAgent delivered initial shortlist of 3 candidates. Delegating to EvaluationAgent for independent verification.",
            "timestamp": ts,
        },
        {
            "agent": "EvaluationAgent",
            "role": "conflict",
            "content": "⚔️ SHORTLIST REJECTED by EvaluationAgent (Critic Disagreement):\n• Hard Rule Check: Arjun Mehta has score 41.0/100 (below quality threshold 50.0) and is MISSING mandatory requirements: TypeScript, PostgreSQL, and has only 3.0 yrs exp (5+ required).\n• Qualitative LLM Audit: Arjun Mehta was prematurely shortlisted solely to meet top_n count despite failing fundamental mandatory bar.\n• Verdict: REJECT shortlist. Approved 2/3 candidates. Triggering Orchestrator conflict replanning.",
            "timestamp": ts,
        },
        {
            "agent": "Orchestrator",
            "role": "conflict",
            "content": "⚠️ Conflict Detected: EvaluationAgent challenged MatchingAgent's shortlist. Reconciling disagreement and evaluating adaptive replanning options.",
            "timestamp": ts,
        },
        {
            "agent": "Orchestrator",
            "role": "replan",
            "content": "🔄 Adaptive Replanning Decision: REPLAN_RELAXED.\n• Business Rule Applied: Under candidate scarcity, selectively relax PREFERRED requirements (AWS, GraphQL, Kubernetes) while STRICTLY PRESERVING MANDATORY requirements (TypeScript, React, Node.js, 5+ yrs).\n• Action: Rerunning MatchingAgent with expanded criteria weights.",
            "timestamp": ts,
        },
        {
            "agent": "MatchingAgent",
            "role": "replan",
            "content": "[RELAXED SEARCH] Reran ChromaDB vector retrieval with relaxed preferred requirements.\n• Replaced Arjun Mehta with qualified candidate Aisha Patel (strong backend & architecture foundation).\n• Revised Shortlist:\n  1. Kavya Reddy — Score: 90.0/100 (Approved)\n  2. Priya Sharma — Score: 85.0/100 (Approved)\n  3. Aisha Patel — Score: 72.0/100 (Approved with relaxed cloud requirements)",
            "timestamp": ts,
        },
        {
            "agent": "EvaluationAgent",
            "role": "result",
            "content": "✅ SHORTLIST VERIFIED & APPROVED by EvaluationAgent:\n• All 3 shortlisted candidates satisfy 100% of non-negotiable mandatory skills.\n• Rejection resolved. Quality threshold verified at 82.3% average score.",
            "timestamp": ts,
        },
        {
            "agent": "Orchestrator",
            "role": "decision",
            "content": "Shortlist approved by EvaluationAgent. Initiating CommunicationAgent for personalized candidate engagement.",
            "timestamp": ts,
        },
        {
            "agent": "CommunicationAgent",
            "role": "result",
            "content": "📧 Interview Invitation — Kavya Reddy (Score 90.0/100):\n'Dear Kavya, We were thoroughly impressed by your 7 years of full-stack engineering and Kubernetes expertise at Razorpay. TechNova Inc. would love to invite you to an initial architectural conversation for the Senior Full Stack Engineer position.'",
            "timestamp": ts,
        },
        {
            "agent": "CommunicationAgent",
            "role": "result",
            "content": "📧 Interview Invitation — Priya Sharma (Score 85.0/100):\n'Dear Priya, Your 6 years of scalable React/Node.js enterprise development at Infosys stood out as an exceptional fit for TechNova's engineering team. We'd like to schedule an introductory video interview this week.'",
            "timestamp": ts,
        },
        {
            "agent": "CommunicationAgent",
            "role": "result",
            "content": "📧 Candidate Feedback & Invitation — Aisha Patel (Score 72.0/100):\n'Dear Aisha, Your extensive Python, FastAPI, and distributed systems experience at Google India is an exciting match for our backend scale. We would love to discuss a Senior Backend / Full Stack role at TechNova.'",
            "timestamp": ts,
        },
        {
            "agent": "Orchestrator",
            "role": "result",
            "content": "🎉 Recruitment Pipeline Complete.\n• Total Candidates Ingested: 6\n• Initial Shortlist Disagreements: 1 (Resolved via Dynamic Replanning)\n• Mandatory Requirements Relaxed: 0 (Strict Preservation Rule)\n• Preferred Requirements Relaxed: 1 (AWS/GraphQL nice-to-haves)\n• Final Approved Candidates: 3/3\n• Communication Status: Bespoke interview invitations generated for all approved candidates.",
            "timestamp": ts,
        },
    ]


def get_worked_example_dossier() -> dict:
    """Returns structured data for the concrete worked example."""
    return {
        "job_title": "Senior Full Stack Engineer",
        "company": "TechNova Inc.",
        "mandatory": ["React", "Node.js", "TypeScript", "PostgreSQL", "5+ years experience"],
        "preferred": ["AWS Cloud", "Docker/Kubernetes", "GraphQL"],
        "shortlisted": [
            {
                "name": "Kavya Reddy",
                "role": "Lead Engineer, Razorpay",
                "score": 90.0,
                "experience": "7 years",
                "matched_mandatory": ["React", "Node.js", "TypeScript", "PostgreSQL", "5+ years experience"],
                "matched_preferred": ["AWS Cloud", "Docker/Kubernetes", "GraphQL"],
                "missing_mandatory": [],
                "missing_preferred": [],
                "status": "APPROVED",
                "evaluation_notes": "Exceeds all mandatory and preferred requirements. Certified CKA Kubernetes + AWS Architect.",
                "invitation": "Dear Kavya, We were thoroughly impressed by your 7 years of full-stack engineering and Kubernetes expertise at Razorpay. TechNova Inc. would love to invite you to an initial architectural conversation for the Senior Full Stack Engineer position.",
            },
            {
                "name": "Priya Sharma",
                "role": "Senior Software Engineer, Infosys",
                "score": 85.0,
                "experience": "6 years",
                "matched_mandatory": ["React", "Node.js", "TypeScript", "PostgreSQL", "5+ years experience"],
                "matched_preferred": ["AWS Cloud", "Docker"],
                "missing_mandatory": [],
                "missing_preferred": ["Kubernetes", "GraphQL"],
                "status": "APPROVED",
                "evaluation_notes": "Solid enterprise-grade full-stack developer. Fully meets mandatory bar.",
                "invitation": "Dear Priya, Your 6 years of scalable React/Node.js enterprise development at Infosys stood out as an exceptional fit for TechNova's engineering team. We'd like to schedule an introductory video interview this week.",
            },
            {
                "name": "Aisha Patel",
                "role": "Senior ML / Backend Engineer, Google India",
                "score": 72.0,
                "experience": "5 years",
                "matched_mandatory": ["Python", "FastAPI", "PostgreSQL", "5+ years experience"],
                "matched_preferred": ["AWS Cloud", "Docker", "Kubernetes"],
                "missing_mandatory": [],
                "missing_preferred": ["GraphQL"],
                "status": "APPROVED (RELAXED CRITERIA)",
                "evaluation_notes": "Surfaced in round 2 replanning after Orchestrator relaxed preferred criteria. Replaced Arjun Mehta.",
                "invitation": "Dear Aisha, Your extensive Python, FastAPI, and distributed systems experience at Google India is an exciting match for our backend scale. We would love to discuss a Senior Backend / Full Stack role at TechNova.",
            },
        ],
        "rejected": [
            {
                "name": "Arjun Mehta",
                "role": "Junior Developer, StartupXYZ",
                "score": 38.0,
                "experience": "3 years",
                "missing_mandatory": ["TypeScript", "PostgreSQL", "5+ years experience"],
                "evaluation_notes": "Challenged by EvaluationAgent. Lacked mandatory 5+ years seniority and core TypeScript depth. Triggered Orchestrator Replanning.",
            }
        ],
    }
