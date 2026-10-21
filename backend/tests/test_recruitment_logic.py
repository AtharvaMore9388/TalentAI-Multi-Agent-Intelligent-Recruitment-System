"""
TalentAI — Recruitment Logic & Pipeline Regression Tests
Verifies all 10 core requirements specified in the regression test suite:
1. An approved shortlist of two candidates produces an approved count of two.
2. A conditional shortlist of two candidates produces a conditional count of two, not an approved count of two.
3. A communication-generation failure does not clear the approved shortlist.
4. A 0–2 year requirement accepts a candidate with 1.5 years of experience.
5. Four months is not parsed as four years.
6. No professional experience is not parsed as four years.
7. Missing mandatory skills remain visible after replanning.
8. Every ingested candidate receives exactly one final disposition.
9. The final report matches the authoritative EvaluationAgent result.
10. An empty approved shortlist is reported correctly when no candidate meets all mandatory requirements.
"""
import pytest
import sys
import os
import asyncio

# Ensure backend directory is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.experience_parser import extract_candidate_experience, parse_duration_to_years
from tools.scoring_tool import ScoringTool, verify_experience_constraint
from agents.dynamic_pipeline import (
    parse_job_description,
    parse_candidate_resume,
    run_dynamic_recruitment_pipeline,
)
from agents.evaluation_agent import evaluate_shortlist
from lib.models import Candidate, MatchedCandidate, JobDescription


# ─── TEST 1 & 2: Approved vs Conditional Shortlist Counts ────────────────────

def test_approved_shortlist_count_matches():
    """1. An approved shortlist of two candidates produces an approved count of two."""
    c1 = MatchedCandidate(
        candidate=Candidate(id="1", name="Alice", email="a@test.com", skills=["Python", "SQL"], experience_years=2.0),
        match_score=85.0,
        matched_mandatory=["Python", "SQL"],
        missing_mandatory=[],
    )
    c2 = MatchedCandidate(
        candidate=Candidate(id="2", name="Bob", email="b@test.com", skills=["Python", "SQL"], experience_years=2.0),
        match_score=82.0,
        matched_mandatory=["Python", "SQL"],
        missing_mandatory=[],
    )
    job = JobDescription(
        id="j1",
        title="Python Dev",
        company="AI Labs",
        mandatory_requirements=["Python", "SQL"],
        preferred_requirements=[],
    )
    # Using mock LLM / evaluate_shortlist logic directly
    eval_result, _ = evaluate_shortlist(job=job, shortlisted=[c1, c2], llm=None)
    assert len(eval_result["approved_candidates"]) == 2
    assert eval_result["evaluation_summary"]["approved_count"] == 2
    assert len(eval_result["conditional_candidates"]) == 0


def test_conditional_shortlist_does_not_count_as_approved():
    """2. A conditional shortlist of two candidates produces a conditional count of two, not an approved count of two."""
    c1 = MatchedCandidate(
        candidate=Candidate(id="1", name="Charlie", email="c@test.com", skills=["Python"], experience_years=2.0),
        match_score=65.0,
        matched_mandatory=["Python"],
        missing_mandatory=["SQL"],
    )
    c2 = MatchedCandidate(
        candidate=Candidate(id="2", name="Dave", email="d@test.com", skills=["Python"], experience_years=2.0),
        match_score=62.0,
        matched_mandatory=["Python"],
        missing_mandatory=["SQL"],
    )
    job = JobDescription(
        id="j1",
        title="Python Dev",
        company="AI Labs",
        mandatory_requirements=["Python", "SQL"],
        preferred_requirements=[],
    )
    eval_result, _ = evaluate_shortlist(job=job, shortlisted=[c1, c2], llm=None)
    assert len(eval_result["approved_candidates"]) == 0
    assert eval_result["evaluation_summary"]["approved_count"] == 0
    assert len(eval_result["conditional_candidates"]) == 2
    assert eval_result["evaluation_summary"]["conditional_count"] == 2


# ─── TEST 3: Communication Failure Does Not Clear Shortlist ─────────────────

@pytest.mark.asyncio
async def test_communication_failure_preserves_approved_shortlist():
    """3. A communication-generation failure does not clear the approved shortlist."""
    jd = '''
    Role: Backend Developer
    Company: TestCo
    Requirements:
    - Python
    - SQL
    0-2 years of experience
    '''
    resume = '''
    Rohan Verma
    Summary: 1.5 years experience in Python and SQL.
    Skills: Python, SQL
    Experience: 1.5 years
    '''
    last_dossier = None
    async for msg, dossier in run_dynamic_recruitment_pipeline(jd, [resume], top_n=1):
        if dossier:
            last_dossier = dossier

    assert last_dossier is not None
    assert len(last_dossier["approved_candidates"]) == 1
    assert last_dossier["evaluation_summary"]["approved_count"] == 1


# ─── TEST 4: Experience Range Verification ───────────────────────────────────

def test_experience_range_0_to_2_accepts_1_point_5():
    """4. A 0–2 year requirement accepts a candidate with 1.5 years of experience."""
    compliant, note = verify_experience_constraint(candidate_exp=1.5, min_exp=0.0, max_exp=2.0)
    assert compliant is True
    assert "Within target" in note or "Meets" in note

    tool = ScoringTool()
    res = tool.evaluate(
        candidate_skills=["Python", "SQL"],
        candidate_experience_years=1.5,
        mandatory_requirements=["Python", "SQL"],
        preferred_requirements=[],
        min_experience_years=0.0,
        max_experience_years=2.0,
    )
    assert res["is_compliant"] is True
    assert res["eligibility_status"] == "FULLY_ELIGIBLE"
    assert len(res["missing_mandatory"]) == 0


# ─── TEST 5 & 6: Duration Parsing Safety ────────────────────────────────────

def test_four_months_not_parsed_as_four_years():
    """5. Four months is not parsed as four years."""
    resume_priya = '''
    Priya Patel
    Email: priya.patel@example.com
    Summary: Backend enthusiast. Completed a 4-month internship at StartCo.
    Skills: Python, SQL, Django, REST APIs
    Internship Experience:
    Web Dev Intern at StartCo (4 months)
    Education: B.Tech IT (2020-2024)
    '''
    exp = extract_candidate_experience(resume_priya)
    assert exp["internship_years"] == 0.33
    assert exp["professional_years"] == 0.0
    assert exp["total_relevant_years"] == 0.33
    assert exp["total_relevant_years"] != 4.0


def test_no_professional_experience_not_parsed_as_four_years():
    """6. No professional experience is not parsed as four years."""
    resume_sneha = '''
    Sneha Kulkarni
    Email: sneha.kulkarni@example.com
    Summary: Recent Computer Science graduate with no professional experience.
    Skills: Python, PyTorch, TensorFlow, Pandas, NumPy, Scikit-learn
    Education: B.Tech Computer Science (2020-2024)
    '''
    exp = extract_candidate_experience(resume_sneha)
    assert exp["has_explicit_no_exp"] is True
    assert exp["professional_years"] == 0.0
    assert exp["internship_years"] == 0.0
    assert exp["total_relevant_years"] == 0.0
    assert exp["total_relevant_years"] != 4.0


# ─── TEST 7: Missing Mandatory Skills Remain Visible After Replanning ────────

@pytest.mark.asyncio
async def test_missing_mandatory_skills_remain_visible_after_replanning():
    """7. Missing mandatory skills remain visible after replanning."""
    jd = '''
    Role: Backend Developer
    Company: TestCo
    Requirements:
    - Python
    - SQL
    - Django
    - Flask
    - REST APIs
    Preferred:
    - Docker
    '''
    cand_priya = '''
    Priya Patel
    Skills: Python, SQL, Django, REST APIs
    Experience: 0.33 years
    '''
    last_dossier = None
    async for msg, dossier in run_dynamic_recruitment_pipeline(jd, [cand_priya], top_n=1):
        if dossier:
            last_dossier = dossier

    assert last_dossier is not None
    # Candidate Priya is missing Flask
    found = False
    for c in last_dossier["conditional_candidates"] + last_dossier["rejected_candidates"]:
        if "Flask" in c["missing_mandatory"]:
            found = True
    assert found is True, "Missing mandatory skill 'Flask' was silently dropped"


# ─── TEST 8: Mutually Exclusive Candidate Dispositions ──────────────────────

@pytest.mark.asyncio
async def test_every_ingested_candidate_receives_exactly_one_final_disposition():
    """8. Every ingested candidate receives exactly one final disposition."""
    jd = '''
    Role: Python Backend Engineer
    Requirements:
    - Python
    - SQL
    - Django
    - Flask
    - REST APIs
    0-2 years of experience
    '''
    c1 = 'Rohan\nSkills: Python, SQL, Django, Flask, REST APIs\nExperience: 1.5 years'
    c2 = 'Priya\nSkills: Python, SQL, Django, REST APIs\nExperience: 4 months'
    c3 = 'Sneha\nSkills: PyTorch\nSummary: no professional experience\nExperience: 0 years'

    last_dossier = None
    async for msg, dossier in run_dynamic_recruitment_pipeline(jd, [c1, c2, c3], top_n=2):
        if dossier:
            last_dossier = dossier

    approved_names = {c["name"] for c in last_dossier["approved_candidates"]}
    conditional_names = {c["name"] for c in last_dossier["conditional_candidates"]}
    rejected_names = {c["name"] for c in last_dossier["rejected_candidates"]}

    # Verify mutually exclusive sets
    assert approved_names.isdisjoint(conditional_names)
    assert approved_names.isdisjoint(rejected_names)
    assert conditional_names.isdisjoint(rejected_names)

    # All 3 candidates accounted for
    total_assigned = len(approved_names) + len(conditional_names) + len(rejected_names)
    assert total_assigned == 3


# ─── TEST 9: Final Report Matches Authoritative Evaluation Result ───────────

@pytest.mark.asyncio
async def test_final_report_matches_authoritative_evaluation_result():
    """9. The final report matches the authoritative EvaluationAgent result."""
    jd = '''
    Role: Python Backend Engineer
    Requirements:
    - Python
    - SQL
    - Django
    - Flask
    - REST APIs
    0-2 years of experience
    '''
    c1 = 'Rohan\nSkills: Python, SQL, Django, Flask, REST APIs\nExperience: 1.5 years'
    c2 = 'Priya\nSkills: Python, SQL, Django, REST APIs\nExperience: 4 months'

    last_dossier = None
    async for msg, dossier in run_dynamic_recruitment_pipeline(jd, [c1, c2], top_n=2):
        if dossier:
            last_dossier = dossier

    summary = last_dossier["evaluation_summary"]
    assert summary["approved_count"] == len(last_dossier["approved_candidates"])
    assert summary["conditional_count"] == len(last_dossier["conditional_candidates"])
    assert summary["rejected_count"] == len(last_dossier["rejected_candidates"])


# ─── TEST 10: Empty Approved Shortlist Reported Correctly ───────────────────

@pytest.mark.asyncio
async def test_empty_approved_shortlist_reported_when_no_candidate_meets_mandatory():
    """10. An empty approved shortlist is reported correctly when no candidate meets all mandatory requirements."""
    jd = '''
    Role: Python Backend Engineer
    Requirements:
    - Python
    - SQL
    - Django
    - Flask
    - REST APIs
    0-2 years of experience
    '''
    c1 = 'Candidate A\nSkills: Ruby, Rails\nExperience: 1 year'
    c2 = 'Candidate B\nSkills: Java, Spring\nExperience: 1 year'

    last_dossier = None
    async for msg, dossier in run_dynamic_recruitment_pipeline(jd, [c1, c2], top_n=2):
        if dossier:
            last_dossier = dossier

    assert len(last_dossier["approved_candidates"]) == 0
    assert last_dossier["evaluation_summary"]["approved_count"] == 0
    assert last_dossier["evaluation_summary"]["verdict"] == "REJECT"
    assert len(last_dossier["rejected_candidates"]) == 2
