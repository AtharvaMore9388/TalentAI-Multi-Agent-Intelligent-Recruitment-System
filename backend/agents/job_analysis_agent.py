"""
TalentAI — Job Analysis Agent
Extracts mandatory and preferred requirements from raw job description text.
"""
from __future__ import annotations
import json
import re
import uuid
from crewai import Agent, Task, Crew
from lib.models import JobDescription, AgentMessage
from datetime import datetime, timezone


def get_job_analysis_agent(llm) -> Agent:
    return Agent(
        role="Job Requirements Analyst",
        goal=(
            "Read a job description and precisely separate mandatory requirements "
            "(non-negotiable skills/experience) from preferred requirements (nice-to-have). "
            "Identify the job title and company name."
        ),
        backstory=(
            "You are an expert talent acquisition specialist with deep experience in "
            "job architecture and competency frameworks. You understand the critical "
            "difference between must-have and nice-to-have qualifications and always "
            "classify them correctly."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


def analyze_job(raw_jd: str, llm) -> tuple[JobDescription, AgentMessage]:
    """Run the Job Analysis Agent on a raw job description."""
    agent = get_job_analysis_agent(llm)

    task = Task(
        description=(
            f"Analyze this job description and extract structured requirements.\n\n"
            f"JOB DESCRIPTION:\n{raw_jd}\n\n"
            "Return a JSON object with EXACTLY these fields:\n"
            "- title (string: job title)\n"
            "- company (string: company name, or 'Unknown' if not specified)\n"
            "- mandatory_requirements (list of strings: absolute must-haves, e.g. specific technologies, years of exp)\n"
            "- preferred_requirements (list of strings: nice-to-have skills or qualifications)\n"
            "- description (string: one paragraph summarizing the role)\n\n"
            "IMPORTANT: mandatory_requirements should be skills/technologies explicitly required. "
            "preferred_requirements are explicitly optional or bonus qualifications.\n"
            "Return ONLY the JSON object."
        ),
        expected_output="A JSON object with title, company, mandatory_requirements, preferred_requirements, description",
        agent=agent,
    )

    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    result = crew.kickoff()
    raw_output = str(result)

    jd_data = _parse_jd_json(raw_output, raw_jd=raw_jd)
    job = JobDescription(
        id=str(uuid.uuid4()),
        raw_jd=raw_jd,
        **jd_data,
    )

    msg = AgentMessage(
        agent="JobAnalysisAgent",
        role="action",
        content=(
            f"Analyzed JD for '{job.title}' at {job.company}. "
            f"Identified {len(job.mandatory_requirements)} mandatory and "
            f"{len(job.preferred_requirements)} preferred requirements."
        ),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    return job, msg


def _extract_exp_range(text: str) -> tuple[float, Optional[float], str]:
    """Extract experience range or minimum from text."""
    range_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)(?:\s+of)?(?:\s+experience)?", text, re.IGNORECASE)
    if range_match:
        min_e = float(range_match.group(1))
        max_e = float(range_match.group(2))
        return min_e, max_e, f"{range_match.group(1)}-{range_match.group(2)} years experience"
    plus_match = re.search(r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+experience)?", text, re.IGNORECASE)
    if plus_match:
        min_e = float(plus_match.group(1))
        return min_e, None, f"{plus_match.group(1)}+ years experience"
    return 0.0, None, "0+ years experience"


def _parse_jd_json(text: str, raw_jd: str = "") -> dict:
    source_text = text + "\n" + raw_jd
    min_exp, max_exp, exp_text = _extract_exp_range(source_text)

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            mand = data.get("mandatory_requirements", [])
            pref = data.get("preferred_requirements", [])
            # Filter out fabricated experience entries like "2+ years" if raw JD states otherwise
            cleaned_mand = []
            for m in mand:
                if re.search(r"\d+\+?\s*(?:years?|yrs?)", m, re.IGNORECASE):
                    continue
                cleaned_mand.append(m)

            cleaned_pref = []
            for p in pref:
                if re.search(r"\d+\+?\s*(?:years?|yrs?)", p, re.IGNORECASE):
                    continue
                cleaned_pref.append(p)

            return {
                "title": data.get("title", "Unknown Position"),
                "company": data.get("company", "Unknown Company"),
                "mandatory_requirements": cleaned_mand,
                "preferred_requirements": cleaned_pref,
                "min_experience_years": min_exp,
                "max_experience_years": max_exp,
                "experience_requirement_text": exp_text,
                "description": data.get("description", ""),
            }
        except (json.JSONDecodeError, ValueError):
            pass

    return {
        "title": "Unknown Position",
        "company": "Unknown Company",
        "mandatory_requirements": [],
        "preferred_requirements": [],
        "min_experience_years": min_exp,
        "max_experience_years": max_exp,
        "experience_requirement_text": exp_text,
        "description": text[:300],
    }
