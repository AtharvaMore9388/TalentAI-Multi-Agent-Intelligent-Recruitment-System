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
) -> tuple[dict, AgentMessage]:
    """
    Evaluates the shortlist and returns a structured evaluation dictionary conforming to:
    {
      "approved_candidates": [...],
      "conditional_candidates": [...],
      "rejected_candidates": [...],
      "rejection_reasons": [...],
      "evaluation_summary": {...}
    }
    """
    verdict = "APPROVE"
    reason = "Deterministic evaluation check."
    flagged_names = []
    notes_section = ""

    candidates_summary = "\n".join([
        f"{i+1}. {mc.candidate.name} | Score={mc.match_score} | "
        f"Mandatory met={mc.matched_mandatory} | Missing mandatory={mc.missing_mandatory} | "
        f"Skills={mc.candidate.skills} | Experience={mc.candidate.experience_years} yrs"
        for i, mc in enumerate(shortlisted)
    ])

    if llm is not None:
        try:
            agent = get_evaluation_agent(llm)
            task = Task(
                description=(
                    f"ROLE: '{job.title}' at {job.company}\n"
                    f"MANDATORY requirements: {job.mandatory_requirements}\n"
                    f"EXPERIENCE range/minimum: {job.experience_requirement_text or f'{job.min_experience_years}-{job.max_experience_years} years'}\n\n"
                    f"SHORTLIST from MatchingAgent:\n{candidates_summary}\n\n"
                    "Your task as Independent Evaluator:\n"
                    "1. Review each candidate against mandatory requirements and experience limits.\n"
                    "2. Business Rules:\n"
                    "   - A candidate is ONLY APPROVED if they meet 100% of mandatory requirements.\n"
                    "   - If they miss mandatory requirements, they are CONDITIONAL or REJECTED. Never approve non-compliant candidates.\n"
                    "3. Provide audit notes and reasons for every candidate.\n\n"
                    "Respond with:\n"
                    "VERDICT: APPROVE or REJECT\n"
                    "REASON: (specific explanation, mention candidate names and missing skills)\n"
                    "FLAGGED_CANDIDATES: (comma-separated names of non-compliant candidates, or NONE)\n"
                    "EVALUATION_NOTES: (per-candidate notes, 1 line each)"
                ),
                expected_output="VERDICT, REASON, FLAGGED_CANDIDATES, and EVALUATION_NOTES",
                agent=agent,
            )
            crew = Crew(agents=[agent], tasks=[task], verbose=False)
            result = crew.kickoff()
            evaluation_text = str(result)

            verdict = _extract_verdict(evaluation_text)
            reason = _extract_field(evaluation_text, "REASON")
            flagged_names = _extract_flagged(evaluation_text)
            notes_section = _extract_field(evaluation_text, "EVALUATION_NOTES")
        except Exception as e:
            reason = f"Evaluation executed deterministically ({e})."

    approved_candidates: list[MatchedCandidate] = []
    conditional_candidates: list[MatchedCandidate] = []
    rejected_candidates: list[MatchedCandidate] = []
    rejection_reasons: list[str] = []

    for mc in shortlisted:
        mc.evaluation_notes = _find_note_for(mc.candidate.name, notes_section)
        
        # Enforce business rules strictly:
        # Mandatory requirements must never be relaxed silently!
        if len(mc.missing_mandatory) == 0 and mc.match_score >= REJECTION_THRESHOLD:
            mc.eligibility_status = "FULLY_ELIGIBLE"
            mc.is_compliant = True
            approved_candidates.append(mc)
        elif len(mc.missing_mandatory) <= MISSING_MANDATORY_LIMIT and mc.match_score >= REJECTION_THRESHOLD:
            mc.eligibility_status = "CONDITIONALLY_ELIGIBLE"
            mc.is_compliant = False
            conditional_candidates.append(mc)
            rejection_reasons.append(f"{mc.candidate.name}: Conditional inclusion (Missing mandatory: {', '.join(mc.missing_mandatory)})")
        else:
            mc.eligibility_status = "NON_COMPLIANT"
            mc.is_compliant = False
            rejected_candidates.append(mc)
            rejection_reasons.append(f"{mc.candidate.name}: Rejected (Missing mandatory: {', '.join(mc.missing_mandatory) or 'Score below threshold'})")

    evaluation_passed = len(approved_candidates) >= 1 and (len(rejected_candidates) == 0)

    eval_summary = {
        "verdict": "APPROVE" if evaluation_passed else "REJECT",
        "passed": evaluation_passed,
        "total_shortlisted": len(shortlisted),
        "approved_count": len(approved_candidates),
        "conditional_count": len(conditional_candidates),
        "rejected_count": len(rejected_candidates),
        "reason": reason or ("All candidates meet mandatory requirements." if evaluation_passed else "Mandatory non-compliance found."),
    }

    structured_result = {
        "approved_candidates": approved_candidates,
        "conditional_candidates": conditional_candidates,
        "rejected_candidates": rejected_candidates,
        "rejection_reasons": rejection_reasons,
        "evaluation_summary": eval_summary,
    }

    if not evaluation_passed:
        role = "conflict"
        content = (
            f"⚠️ SHORTLIST CHALLENGED by EvaluationAgent. "
            f"Approved: {len(approved_candidates)}, Conditional: {len(conditional_candidates)}, Rejected: {len(rejected_candidates)}. "
            f"Reasons: {'; '.join(rejection_reasons) if rejection_reasons else reason[:200]}"
        )
    else:
        role = "result"
        content = (
            f"✅ SHORTLIST APPROVED by EvaluationAgent. "
            f"{len(approved_candidates)} candidate(s) fully verified against all mandatory requirements."
        )

    msg = AgentMessage(
        agent="EvaluationAgent",
        role=role,
        content=content,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    return structured_result, msg


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
