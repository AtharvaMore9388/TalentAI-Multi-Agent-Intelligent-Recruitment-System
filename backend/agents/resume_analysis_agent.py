"""
TalentAI — Resume Analysis Agent
Parses raw resume text and extracts structured candidate information.
"""
from __future__ import annotations
import json
import uuid
from crewai import Agent, Task, Crew
from crewai_tools import BaseTool
from lib.models import Candidate, AgentMessage
from datetime import datetime, timezone


def get_resume_analysis_agent(llm) -> Agent:
    return Agent(
        role="Resume Analysis Specialist",
        goal=(
            "Parse raw resume text and extract structured information: "
            "name, email, phone, skills, years of experience, education, and a 2-sentence professional summary."
        ),
        backstory=(
            "You are an expert HR analyst with 10 years of experience parsing resumes "
            "across multiple industries. You are meticulous, structured, and always "
            "respond in valid JSON format as instructed."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


def analyze_resume(raw_resume: str, llm) -> tuple[Candidate, AgentMessage]:
    """Run the Resume Analysis Agent on a single raw resume."""
    agent = get_resume_analysis_agent(llm)

    task = Task(
        description=(
            f"Analyze the following resume and extract structured information.\n\n"
            f"RESUME:\n{raw_resume}\n\n"
            "Return a JSON object with EXACTLY these fields:\n"
            "- name (string)\n"
            "- email (string)\n"
            "- phone (string or null)\n"
            "- skills (list of strings, be specific)\n"
            "- experience_years (float)\n"
            "- education (string, highest degree + institution)\n"
            "- summary (string, 2-3 sentences professional summary)\n\n"
            "Return ONLY the JSON object, no markdown, no explanation."
        ),
        expected_output="A JSON object with name, email, phone, skills, experience_years, education, summary",
        agent=agent,
    )

    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    result = crew.kickoff()
    raw_output = str(result)

    # Parse JSON from output
    candidate_data = _parse_json_safely(raw_output)
    candidate = Candidate(
        id=str(uuid.uuid4()),
        raw_resume=raw_resume,
        **candidate_data,
    )

    msg = AgentMessage(
        agent="ResumeAnalysisAgent",
        role="action",
        content=f"Analyzed resume for {candidate.name} — extracted {len(candidate.skills)} skills, {candidate.experience_years} yrs exp",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    return candidate, msg


def _parse_json_safely(text: str) -> dict:
    """Extract and parse JSON from LLM output, with fallback."""
    import re
    # Try to find JSON block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            # Normalize fields
            return {
                "name": data.get("name", "Unknown"),
                "email": data.get("email", "unknown@example.com"),
                "phone": data.get("phone"),
                "skills": data.get("skills", []),
                "experience_years": float(data.get("experience_years", 0)),
                "education": data.get("education", ""),
                "summary": data.get("summary", ""),
            }
        except (json.JSONDecodeError, ValueError):
            pass

    # Fallback: return minimal candidate
    return {
        "name": "Candidate",
        "email": f"candidate_{uuid.uuid4().hex[:6]}@example.com",
        "phone": None,
        "skills": [],
        "experience_years": 0.0,
        "education": "",
        "summary": text[:200],
    }
