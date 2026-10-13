"""
TalentAI — Orchestrator Agent
The central coordinator that:
  1. Delegates tasks to specialized agents
  2. Monitors inter-agent outputs
  3. Detects conflicts (EvaluationAgent rejection)
  4. Dynamically replans (relaxes requirements, triggers new search rounds)
  5. Decides when the pipeline is complete

This is the core of the multi-agent agentic behavior.
"""
from __future__ import annotations
import os
import asyncio
from datetime import datetime, timezone
from typing import AsyncGenerator

from crewai import Agent, Task, Crew
from crewai.llm import LLM

from lib.models import (
    RecruitmentState, Candidate, JobDescription,
    MatchedCandidate, AgentMessage
)
from lib.chroma_store import get_store

from agents.resume_analysis_agent import analyze_resume
from agents.job_analysis_agent import analyze_job
from agents.matching_agent import match_candidates
from agents.evaluation_agent import evaluate_shortlist
from agents.communication_agent import generate_communications


MAX_REPLAN_ROUNDS = 2          # Max replanning iterations
MIN_APPROVED = 1               # Minimum approved candidates to consider success


def _log(state: RecruitmentState, agent: str, role: str, content: str) -> AgentMessage:
    """Append a structured message to state and return it."""
    msg = AgentMessage(
        agent=agent,
        role=role,
        content=content,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    state.messages.append(msg)
    return msg


def _make_llm() -> LLM:
    return LLM(
        model=f"groq/{os.getenv('LLM_MODEL', 'llama-3.3-70b-versatile')}",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.1,
    )


def _make_fast_llm() -> LLM:
    return LLM(
        model=f"groq/{os.getenv('LLM_MODEL_FAST', 'llama-3.1-8b-instant')}",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.1,
    )


# ─── Orchestrator Decision Agent ────────────────────────────────────────────

def _get_orchestrator_agent(llm) -> Agent:
    return Agent(
        role="Recruitment Orchestrator",
        goal=(
            "Coordinate the entire recruitment pipeline. Receive agent reports, "
            "make strategic decisions about replanning, requirement relaxation, "
            "and determine when the pipeline reaches a satisfactory conclusion."
        ),
        backstory=(
            "You are the head of talent acquisition operations, responsible for "
            "orchestrating a team of specialized AI agents. When the evaluation "
            "team rejects a shortlist, you decide whether to rerun the search with "
            "different criteria, relax requirements, or escalate to human review. "
            "You balance speed with quality and always explain your decisions."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


def orchestrator_decide_replan(
    state: RecruitmentState,
    evaluation_passed: bool,
    approved_count: int,
    llm,
) -> tuple[str, str]:
    """
    Orchestrator reasons about the current state and decides next action.
    Returns: (action, reasoning)
    action ∈ {"replan_relaxed", "replan_strict", "escalate", "accept_partial"}
    """
    agent = _get_orchestrator_agent(llm)
    task = Task(
        description=(
            f"RECRUITMENT PIPELINE STATUS REPORT:\n"
            f"- Role: {state.job.title} at {state.job.company}\n"
            f"- Candidates ingested: {len(state.candidates)}\n"
            f"- Shortlisted: {len(state.shortlisted)}\n"
            f"- EvaluationAgent verdict: {'PASS' if evaluation_passed else 'REJECT'}\n"
            f"- Approved candidates: {approved_count}\n"
            f"- Replan rounds so far: {state.replan_count}\n"
            f"- Mandatory requirements: {state.job.mandatory_requirements}\n"
            f"- Preferred requirements: {state.job.preferred_requirements}\n\n"
            f"Decide the next action. Choose ONE of:\n"
            f"1. replan_relaxed — run another matching pass with relaxed preferred requirements\n"
            f"2. replan_strict — run another matching pass with stricter emphasis on mandatory only\n"
            f"3. escalate — not enough suitable candidates, flag for human review\n"
            f"4. accept_partial — accept the {approved_count} approved candidates despite concerns\n\n"
            f"Respond with:\n"
            f"ACTION: <one of the 4 options above>\n"
            f"REASONING: <2-3 sentence explanation of your strategic decision>"
        ),
        expected_output="ACTION and REASONING",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    result = crew.kickoff()
    text = str(result)

    import re
    action_m = re.search(r"ACTION:\s*(\w+)", text, re.IGNORECASE)
    reason_m = re.search(r"REASONING:\s*(.*?)(?=$|\n\n)", text, re.DOTALL | re.IGNORECASE)
    action = action_m.group(1).lower() if action_m else "accept_partial"
    reason = reason_m.group(1).strip() if reason_m else text[:200]

    return action, reason


# ─── Main Pipeline ───────────────────────────────────────────────────────────

async def run_recruitment_pipeline(
    job_description: str,
    resumes: list[str],
    top_n: int = 5,
) -> AsyncGenerator[AgentMessage, None]:
    """
    Full agentic recruitment pipeline. Yields AgentMessage events as they occur
    for real-time streaming to the frontend.
    """
    state = RecruitmentState()
    state.status = "running"
    llm = _make_llm()
    fast_llm = _make_fast_llm()

    # ── STEP 1: Orchestrator starts the pipeline ─────────────────────────
    yield _log(state, "Orchestrator", "action",
               f"🚀 Pipeline started. Processing {len(resumes)} resume(s) for job analysis.")

    # ── STEP 2: Job Analysis ─────────────────────────────────────────────
    await asyncio.sleep(0)
    yield _log(state, "Orchestrator", "decision",
               "Delegating job description analysis to JobAnalysisAgent.")

    job, job_msg = analyze_job(job_description, llm)
    state.job = job
    state.messages.append(job_msg)
    yield job_msg

    yield _log(state, "Orchestrator", "decision",
               f"JobAnalysisAgent completed. Identified {len(job.mandatory_requirements)} mandatory "
               f"and {len(job.preferred_requirements)} preferred requirements. "
               f"Delegating resume analysis for {len(resumes)} resume(s).")

    # ── STEP 3: Resume Analysis (parallel using fast LLM) ───────────────
    await asyncio.sleep(0)
    store = get_store()
    store.clear()  # Fresh start for this session

    for i, raw_resume in enumerate(resumes):
        candidate, res_msg = analyze_resume(raw_resume, fast_llm)
        state.candidates.append(candidate)
        store.add_resume(candidate)
        state.messages.append(res_msg)
        yield res_msg
        await asyncio.sleep(0)

    yield _log(state, "Orchestrator", "action",
               f"All {len(state.candidates)} resumes analyzed and indexed in ChromaDB. "
               f"Delegating to MatchingAgent for semantic ranking.")

    # ── STEP 4: Matching + Evaluation loop (with replanning) ─────────────
    replan_round = 0
    relaxed = False

    while replan_round <= MAX_REPLAN_ROUNDS:
        await asyncio.sleep(0)

        # ── Matching ──────────────────────────────────────────────────
        shortlisted, match_msg = match_candidates(
            job=job,
            candidates=state.candidates,
            top_n=top_n,
            llm=llm,
            relaxed=relaxed,
        )
        state.shortlisted = shortlisted
        state.messages.append(match_msg)
        yield match_msg

        if not shortlisted:
            yield _log(state, "Orchestrator", "conflict",
                       "⚠️ MatchingAgent returned 0 candidates. Escalating for human review.")
            state.status = "completed"
            break

        yield _log(state, "Orchestrator", "decision",
                   f"MatchingAgent returned {len(shortlisted)} candidates. "
                   f"Delegating to EvaluationAgent for independent verification.")

        # ── Evaluation ────────────────────────────────────────────────
        await asyncio.sleep(0)
        approved, eval_passed, eval_msg = evaluate_shortlist(
            job=job, shortlisted=shortlisted, llm=llm
        )
        state.messages.append(eval_msg)
        yield eval_msg

        rejected = [mc for mc in shortlisted if mc not in approved]

        if eval_passed or replan_round >= MAX_REPLAN_ROUNDS:
            # Accept result
            state.evaluation_passed = eval_passed
            if not eval_passed:
                yield _log(state, "Orchestrator", "decision",
                           f"Max replan rounds ({MAX_REPLAN_ROUNDS}) reached. "
                           f"Accepting {len(approved)} available candidate(s) despite evaluation concerns.")
            else:
                yield _log(state, "Orchestrator", "decision",
                           f"✅ EvaluationAgent approved {len(approved)} candidate(s). "
                           f"Proceeding to communication generation.")
            break

        # ── Orchestrator Replanning ──────────────────────────────────
        state.replan_count += 1
        replan_round += 1

        yield _log(state, "Orchestrator", "conflict",
                   f"⚠️ EvaluationAgent REJECTED shortlist (round {replan_round}). "
                   f"Orchestrator initiating replanning analysis.")

        action, reasoning = orchestrator_decide_replan(
            state=state,
            evaluation_passed=False,
            approved_count=len(approved),
            llm=llm,
        )

        yield _log(state, "Orchestrator", "replan",
                   f"🔄 Replan decision: {action.upper()}. Reasoning: {reasoning}")

        if action == "escalate":
            yield _log(state, "Orchestrator", "decision",
                       "🚨 Escalating to human review — no suitable candidates found with current criteria.")
            approved = approved  # accept what we have
            rejected = [mc for mc in shortlisted if mc not in approved]
            break

        elif action == "accept_partial":
            yield _log(state, "Orchestrator", "decision",
                       f"Accepting {len(approved)} partially approved candidate(s).")
            break

        elif action in ("replan_relaxed", "replan_strict"):
            relaxed = (action == "replan_relaxed")
            state.relaxed_requirements = relaxed
            mode = "RELAXED preferred requirements" if relaxed else "STRICT mandatory-only focus"
            yield _log(state, "Orchestrator", "replan",
                       f"🔄 Rerunning MatchingAgent with {mode}.")
            continue

    # ── STEP 5: Communication Generation ─────────────────────────────────
    await asyncio.sleep(0)
    approved_final = [mc for mc in state.shortlisted if not mc.missing_mandatory or state.relaxed_requirements]
    rejected_final = [mc for mc in state.shortlisted if mc not in approved_final]

    yield _log(state, "Orchestrator", "decision",
               f"Delegating to CommunicationAgent: {len(approved_final)} invitation(s), "
               f"{len(rejected_final)} rejection(s).")

    comms, comm_msg = generate_communications(
        job=job,
        approved=approved_final,
        rejected=rejected_final,
        llm=llm,
    )
    state.final_communications = comms
    state.messages.append(comm_msg)
    yield comm_msg

    # ── STEP 6: Pipeline Complete ─────────────────────────────────────────
    state.status = "completed"
    yield _log(state, "Orchestrator", "result",
               f"🎉 Recruitment pipeline complete. "
               f"Processed {len(state.candidates)} candidates. "
               f"Shortlisted {len(state.shortlisted)}. "
               f"Approved: {len(approved_final)}. "
               f"Replan rounds: {state.replan_count}. "
               f"Requirement relaxation: {'YES' if state.relaxed_requirements else 'NO'}.")
