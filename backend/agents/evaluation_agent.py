"""
TalentAI — Evaluation Agent
Independently verifies the Matching Agent's shortlist.
Can REJECT the shortlist and trigger replanning by the Orchestrator.
This is the key agent-to-agent conflict/challenge mechanism.
"""
from __future__ import annotations
import re
from crewai import Agent, Task, Crew
from lib.models import JobDescription, MatchedCandidate, AgentMessage
from datetime import datetime, timezone


REJECTION_THRESHOLD = 40.0   # score below this → candidate is rejected
MISSING_MANDATORY_LIMIT = 1   # more than N missing mandatory → shortlist challenged


def get_evaluation_agent(llm) -> Agent:
    return Agent(
        role="Independent Candidate Evaluator",
        goal=(
            "Critically and independently evaluate the shortlisted candidates against "
            "the job's mandatory requirements. Identify weak matches, challenge "
            "the shortlist if quality is insufficient, and provide detailed audit notes."
        ),
        backstory=(
            "You are a senior talent evaluator whose job is to quality-gate the recruitment "
            "process. You are independent of the matching team — your role is to catch "
            "mistakes and ensure only genuinely qualified candidates proceed. "
            "You are thorough, direct, and unafraid to reject an entire shortlist."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


def evaluate_shortlist(
    job: JobDescription,
    shortlisted: list[MatchedCandidate],
    llm,
) -> tuple[list[MatchedCandidate], bool, AgentMessage]:
    """
    Evaluates the shortlist. Returns:
    - approved candidates (may be subset of shortlisted)
    - evaluation_passed (bool) — False triggers Orchestrator replanning
    - agent message describing the evaluation decision
    """
    agent = get_evaluation_agent(llm)

    # Prepare evaluation input for the LLM
    candidates_summary = "\n".join([
        f"{i+1}. {mc.candidate.name} | Score={mc.match_score} | "
        f"Mandatory met={mc.matched_mandatory} | Missing mandatory={mc.missing_mandatory} | "
        f"Skills={mc.candidate.skills}"
        for i, mc in enumerate(shortlisted)
    ])

    task = Task(
        description=(
            f"ROLE: '{job.title}' at {job.company}\n"
            f"MANDATORY requirements: {job.mandatory_requirements}\n\n"
            f"SHORTLIST from MatchingAgent:\n{candidates_summary}\n\n"
            "Your task as Independent Evaluator:\n"
            "1. Review each candidate against mandatory requirements\n"
            "2. Identify any candidate missing critical mandatory skills\n"
            "3. Decide: APPROVE the shortlist OR REJECT it with specific reasons\n"
            "4. If approving, you may still flag concerns about specific candidates\n\n"
            "Respond with:\n"
            "VERDICT: APPROVE or REJECT\n"
            "REASON: (specific explanation, mention candidate names and missing skills)\n"
            "FLAGGED_CANDIDATES: (comma-separated names of weak candidates, or NONE)\n"
            "EVALUATION_NOTES: (per-candidate notes, 1 line each)"
        ),
        expected_output="VERDICT, REASON, FLAGGED_CANDIDATES, and EVALUATION_NOTES",
        agent=agent,
    )

    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    result = crew.kickoff()
    evaluation_text = str(result)

    # Parse evaluation verdict
    verdict = _extract_verdict(evaluation_text)
    reason = _extract_field(evaluation_text, "REASON")
    flagged_names = _extract_flagged(evaluation_text)

    # Annotate candidates with evaluation notes
    notes_section = _extract_field(evaluation_text, "EVALUATION_NOTES")
    approved_candidates = []
    for mc in shortlisted:
        # Add evaluation notes
        mc.evaluation_notes = _find_note_for(mc.candidate.name, notes_section)
        # Auto-reject if too many mandatory requirements missing
        if len(mc.missing_mandatory) > MISSING_MANDATORY_LIMIT or mc.match_score < REJECTION_THRESHOLD:
            if mc.candidate.name not in flagged_names:
                flagged_names.append(mc.candidate.name)
        if mc.candidate.name not in flagged_names:
            approved_candidates.append(mc)

    evaluation_passed = verdict == "APPROVE" and len(approved_candidates) >= 1

    if not evaluation_passed:
        role = "conflict"
        content = (
            f"⚠️ SHORTLIST REJECTED by EvaluationAgent. "
            f"Reason: {reason[:200]}. "
            f"Flagged: {flagged_names}. "
            f"Approved {len(approved_candidates)}/{len(shortlisted)} candidates. "
            f"Triggering Orchestrator replanning."
        )
    else:
        role = "result"
        content = (
            f"✅ SHORTLIST APPROVED by EvaluationAgent. "
            f"{len(approved_candidates)}/{len(shortlisted)} candidates approved. "
            + (f"Flagged concerns: {flagged_names}" if flagged_names else "No concerns raised.")
        )

    msg = AgentMessage(
        agent="EvaluationAgent",
        role=role,
        content=content,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    return approved_candidates, evaluation_passed, msg


# ─── Parsing Helpers ────────────────────────────────────────────────────────

def _extract_verdict(text: str) -> str:
    m = re.search(r"VERDICT:\s*(APPROVE|REJECT)", text, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    # Fallback: check for keywords
    if "reject" in text.lower():
        return "REJECT"
    return "APPROVE"


def _extract_field(text: str, field: str) -> str:
    m = re.search(rf"{field}:\s*(.*?)(?=\n[A-Z_]+:|$)", text, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""


def _extract_flagged(text: str) -> list[str]:
    m = re.search(r"FLAGGED_CANDIDATES:\s*(.*?)(?=\n[A-Z_]+:|$)", text, re.DOTALL | re.IGNORECASE)
    if m:
        val = m.group(1).strip()
        if val.upper() == "NONE" or not val:
            return []
        return [n.strip() for n in val.split(",") if n.strip()]
    return []


def _find_note_for(name: str, notes: str) -> str:
    for line in notes.split("\n"):
        if name.lower() in line.lower():
            return line.strip()
    return ""
