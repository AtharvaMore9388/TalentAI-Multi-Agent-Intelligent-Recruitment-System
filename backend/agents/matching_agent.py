"""
TalentAI — Matching & Ranking Agent
Uses RAG (ChromaDB semantic search) + scoring tool to rank candidates.
"""
from __future__ import annotations
import json
import re
from crewai import Agent, Task, Crew
from lib.models import JobDescription, Candidate, MatchedCandidate, AgentMessage
from lib.chroma_store import get_store
from tools.scoring_tool import ScoringTool
from tools.rag_tool import RAGRetrievalTool
from datetime import datetime, timezone


def get_matching_agent(llm) -> Agent:
    rag_tool = RAGRetrievalTool()
    scoring_tool = ScoringTool()
    return Agent(
        role="Candidate Matching & Ranking Specialist",
        goal=(
            "Use semantic search to retrieve the most relevant candidates for a job, "
            "then score each candidate against the mandatory and preferred requirements. "
            "Return a ranked shortlist with justification."
        ),
        backstory=(
            "You are a data-driven recruitment specialist who combines AI-powered semantic "
            "retrieval with structured scoring to surface the best-fit candidates. "
            "You use RAG to find candidates and scoring tools to rank them objectively."
        ),
        tools=[rag_tool, scoring_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


def match_candidates(
    job: JobDescription,
    candidates: list[Candidate],
    top_n: int,
    llm,
    relaxed: bool = False,
) -> tuple[list[MatchedCandidate], AgentMessage]:
    """
    Run the Matching Agent to retrieve and rank candidates.
    If relaxed=True, preferred requirements are treated more leniently.
    """
    # Build scoring for each candidate directly (deterministic)
    from tools.scoring_tool import ScoringTool
    scorer = ScoringTool()

    mandatory = job.mandatory_requirements
    preferred = job.preferred_requirements if not relaxed else []  # relax preferred when replanning

    scored: list[MatchedCandidate] = []
    for cand in candidates:
        result = scorer._run(
            candidate_skills=", ".join(cand.skills),
            candidate_experience_years=cand.experience_years,
            mandatory_requirements=", ".join(mandatory),
            preferred_requirements=", ".join(preferred),
            min_experience_years=job.min_experience_years,
            max_experience_years=job.max_experience_years,
        )
        parsed = _parse_score_result(result, cand, mandatory, preferred)
        scored.append(parsed)

    # Sort by match_score descending
    scored.sort(key=lambda x: x.match_score, reverse=True)
    shortlisted = scored[:top_n]

    # Now use the LLM Matching Agent to provide reasoning
    agent = get_matching_agent(llm)
    task = Task(
        description=(
            f"You have scored {len(candidates)} candidates for the role of '{job.title}' at {job.company}.\n"
            f"Mandatory requirements: {mandatory}\n"
            f"{'Preferred requirements (RELAXED - optional this round): ' if relaxed else 'Preferred requirements: '}{preferred}\n\n"
            f"Top {len(shortlisted)} candidates by score:\n"
            + "\n".join([
                f"- {mc.candidate.name}: score={mc.match_score}, mandatory_met={mc.matched_mandatory}, missing={mc.missing_mandatory}"
                for mc in shortlisted
            ])
            + "\n\nProvide a 2-3 sentence summary explaining your shortlisting rationale and any concerns."
        ),
        expected_output="2-3 sentence narrative on the shortlisting decision",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    result = crew.kickoff()
    rationale = str(result)

    status = "RELAXED" if relaxed else "NORMAL"
    msg = AgentMessage(
        agent="MatchingAgent",
        role="action" if not relaxed else "replan",
        content=(
            f"[{status}] Ranked {len(candidates)} candidates → shortlisted top {len(shortlisted)}. "
            f"Rationale: {rationale[:300]}"
        ),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    return shortlisted, msg


def _parse_score_result(
    result: str,
    cand: Candidate,
    mandatory: list[str],
    preferred: list[str],
) -> MatchedCandidate:
    """Parse scoring tool output into a MatchedCandidate."""
    import re
    score_match = re.search(r"SCORE:\s*([\d.]+)", result)
    score = float(score_match.group(1)) if score_match else 0.0

    def extract_list(label: str) -> list[str]:
        m = re.search(rf"{label}.*?->\s*\[(.*?)\]", result, re.DOTALL)
        if m:
            items = m.group(1).replace("'", "").split(",")
            return [i.strip() for i in items if i.strip()]
        return []

    def extract_missing(label: str) -> list[str]:
        m = re.search(rf"Missing {label}:\s*\[(.*?)\]", result, re.DOTALL)
        if m:
            items = m.group(1).replace("'", "").split(",")
            return [i.strip() for i in items if i.strip()]
        return []

    matched_mandatory = extract_list("Mandatory met")
    missing_mandatory = extract_missing("mandatory")
    matched_preferred = extract_list("Preferred met")
    missing_preferred = extract_missing("preferred")

    return MatchedCandidate(
        candidate=cand,
        match_score=score,
        matched_mandatory=matched_mandatory,
        matched_preferred=matched_preferred,
        missing_mandatory=missing_mandatory,
        missing_preferred=missing_preferred,
    )
