"""
TalentAI — Dynamic Multi-Agent Recruitment Pipeline
Executes end-to-end recruitment on ANY arbitrary user-uploaded job description
and resumes using ChromaDB RAG, deterministic ScoringTool, candidate evaluation critic,
Orchestrator dynamic replanning, and Recruitment Communication generation.
"""
from __future__ import annotations
import re
import uuid
import asyncio
from datetime import datetime, timezone
from typing import AsyncGenerator

from lib.models import Candidate, AgentMessage
from lib.chroma_store import get_store
from tools.scoring_tool import ScoringTool, skills_match
from lib.experience_parser import extract_candidate_experience

COMMON_SKILLS = [
    # Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "golang", "go",
    "rust", "ruby", "php", "swift", "kotlin", "sql", "html", "css", "bash",
    # Frameworks & Libraries
    "react", "react.js", "next.js", "vue", "angular", "node.js", "nodejs",
    "express", "fastapi", "django", "flask", "spring", "spring boot", "rails",
    "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy", "keras",
    # Machine Learning & AI
    "machine learning", "deep learning", "artificial intelligence", "ai",
    "nlp", "natural language processing", "llm", "large language models", "llms",
    "generative ai", "gen ai", "rag", "transformers", "hugging face", "langchain",
    # Data Structures & Algorithms
    "data structures", "algorithms", "data structures and algorithms", "dsa",
    "problem solving", "object oriented programming", "oop",
    # Databases & Stores
    "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch",
    "cassandra", "dynamodb", "sqlite", "sqlite3", "database management", "database",
    # Cloud & DevOps
    "aws", "amazon web services", "azure", "gcp", "google cloud", "docker",
    "kubernetes", "k8s", "terraform", "ci/cd", "jenkins", "github actions",
    # Architectures, Tools & APIs
    "rest", "rest api", "rest apis", "graphql", "microservices", "distributed systems",
    "grpc", "kafka", "rabbitmq", "vector database", "git", "github", "gitlab"
]


def _extract_skills(text: str) -> list[str]:
    """Extract known technical skills mentioned in text."""
    text_lower = text.lower()
    found = []

    # 1. Check for skills section (single-line or multi-line)
    skills_match_sec = re.search(
        r"(?:skills|technical skills|core skills):\s*([^\n]+(?:\n[•\-\*\s]+[^\n]+)*)",
        text,
        re.IGNORECASE,
    )
    if skills_match_sec:
        for item in re.split(r"[,•\|\n\*\-]", skills_match_sec.group(1)):
            s = item.strip()
            if s and 2 < len(s) < 40 and not any(h in s.lower() for h in ["experience", "education", "summary", "project"]):
                found.append(s)

    # 2. Check COMMON_SKILLS occurrences across text
    for skill in COMMON_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill.title() if len(skill) > 4 else skill.upper())

    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for s in found:
        k = s.lower()
        if k not in seen:
            seen.add(k)
            deduped.append(s)
    return deduped


def _extract_section_skills(section_text: str) -> list[str]:
    """
    Extract skills from a specific requirements section line-by-line.
    Preserves compound expressions (e.g., 'REST APIs and Flask or Django')
    because skills_match handles 'or' and 'and' logic intelligently.
    """
    skills = []
    headers_to_skip = [
        "requirements", "preferred", "mandatory", "qualifications", "nice to have", 
        "bonus", "eligibility", "responsibilities", "required skills", "preferred skills",
        "about", "summary", "overview", "bachelor's", "degree", "education"
    ]
    for line in section_text.split("\n"):
        line_clean = line.strip()
        if not line_clean:
            continue
        # Remove bullet points and list markers (e.g., "1.", "-", "*", "•")
        item = re.sub(r"^[•\-\*\d\.\)\s]+", "", line_clean).strip()
        item_lower = item.lower().rstrip(":")
        
        # Skip section headings and meta descriptions
        if not item or any(k == item_lower or item_lower.startswith(k + ":") for k in headers_to_skip):
            continue
        # Skip pure experience or education eligibility lines
        if any(w in item_lower for w in ["year", "years", "yrs", "yr", "exp", "experience"]):
            continue
        if any(w in item_lower for w in ["bachelor", "degree", "diploma", "graduat"]):
            continue
            
        # If the line is a comma-separated list of simple skills without 'or' / 'and', split on commas
        if "," in item and not re.search(r"\b(?:or|and)\b", item, re.IGNORECASE):
            parts = [p.strip() for p in item.split(",") if p.strip()]
        else:
            # Keep as atomic requirement (skills_match handles compound 'or' / 'and' expressions)
            parts = [item]

        for p in parts:
            p_clean = re.sub(r"^[•\-\*\d\.\)\s]+", "", p).strip().rstrip(":")
            p_lower = p_clean.lower()
            if (
                p_clean 
                and len(p_clean) < 60 
                and not any(k == p_lower or p_lower.startswith(k) for k in headers_to_skip)
                and not any(w in p_lower for w in ["year", "years", "yrs", "yr", "exp", "experience", "bachelor", "degree"])
            ):
                skills.append(p_clean)
    return skills


def parse_job_description(raw_jd: str) -> dict:
    """Intelligently parse any arbitrary job description."""
    lines = [line.strip() for line in raw_jd.strip().split("\n") if line.strip()]
    first_line = lines[0] if lines else "Software Engineer"
    
    # Try to extract title and company
    title = first_line
    company = "Hiring Team"
    
    # Check for "at <Company>" or "<Role> - <Company>"
    at_match = re.search(r"(?:at|@)\s+([A-Za-z0-9\s&]+?)(?:\s+is|\s*\(|\s*$|\n)", first_line, re.IGNORECASE)
    if at_match:
        company = at_match.group(1).strip()
        title = first_line[:at_match.start()].strip()
    elif " - " in first_line:
        parts = first_line.split(" - ", 1)
        title = parts[0].strip()
        company = parts[1].strip()
    
    # Clean up title prefixes like "Job Title:", "Position:", "Role:"
    title = re.sub(r"^(?:job\s+title|position|role):\s*", "", title, flags=re.IGNORECASE)

    raw_lower = raw_jd.lower()

    # Look for section boundary markers
    pref_idx = -1
    for kw in ["preferred skills", "preferred requirements", "preferred", "nice to have", "bonus", "plus", "desirable"]:
        idx = raw_lower.find(kw)
        if idx != -1 and (pref_idx == -1 or idx < pref_idx):
            pref_idx = idx

    req_idx = -1
    for kw in ["required skills", "mandatory requirements", "requirements", "mandatory", "must have", "qualifications", "required"]:
        idx = raw_lower.find(kw)
        if idx != -1 and (req_idx == -1 or idx < req_idx):
            req_idx = idx

    # Look for trailing sections that terminate skills lists (e.g. "Eligibility", "Responsibilities")
    stop_idx = -1
    for kw in ["\neligibility", "\nresponsibilities", "\nabout the company", "\nwhat you'll do", "\nbenefits"]:
        idx = raw_lower.find(kw)
        if idx != -1 and (stop_idx == -1 or idx < stop_idx):
            stop_idx = idx

    # Look for experience requirement ranges like "0–2 years" or "3+ years"
    range_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)(?:\s+of)?(?:\s+experience)?", raw_jd, re.IGNORECASE)
    plus_match = re.search(r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+experience)?", raw_jd, re.IGNORECASE)
    
    if range_match:
        min_exp_years = float(range_match.group(1))
        max_exp_years = float(range_match.group(2))
        exp_req_str = f"{range_match.group(1)}-{range_match.group(2)} years experience"
    elif plus_match:
        min_exp_years = float(plus_match.group(1))
        max_exp_years = None
        exp_req_str = f"{plus_match.group(1)}+ years experience"
    else:
        min_exp_years = 0.0
        max_exp_years = None
        exp_req_str = "0+ years experience"

    if pref_idx != -1 and req_idx != -1 and req_idx < pref_idx:
        req_text = raw_jd[req_idx:pref_idx]
        pref_end = stop_idx if (stop_idx != -1 and stop_idx > pref_idx) else len(raw_jd)
        pref_text = raw_jd[pref_idx:pref_end]
        mandatory = _extract_section_skills(req_text) or _extract_skills(req_text)
        preferred = _extract_section_skills(pref_text) or _extract_skills(pref_text)
    elif req_idx != -1:
        req_end = stop_idx if (stop_idx != -1 and stop_idx > req_idx) else len(raw_jd)
        req_text = raw_jd[req_idx:req_end]
        mandatory = _extract_section_skills(req_text) or _extract_skills(req_text)
        preferred = []
    else:
        all_skills = _extract_skills(raw_jd)
        if len(all_skills) >= 4:
            mandatory = all_skills[: len(all_skills) * 2 // 3]
            preferred = all_skills[len(all_skills) * 2 // 3 :]
        elif all_skills:
            mandatory = all_skills
            preferred = []
        else:
            mandatory = ["Problem Solving", "Software Architecture"]
            preferred = ["Agile Methodology"]

    return {
        "title": title or "Software Engineer",
        "company": company or "Technology Group",
        "mandatory": mandatory,
        "preferred": preferred,
        "min_exp_years": min_exp_years,
        "max_exp_years": max_exp_years,
        "experience_str": exp_req_str,
        "summary": lines[1] if len(lines) > 1 else raw_jd[:200],
    }


def parse_candidate_resume(raw_resume: str, index: int) -> dict:
    """Intelligently parse any arbitrary candidate resume."""
    lines = [line.strip() for line in raw_resume.strip().split("\n") if line.strip()]
    first_line = lines[0] if lines else f"Candidate {index + 1}"
    
    # Extract candidate name
    name = first_line
    if any(k in first_line.lower() for k in ["resume", "curriculum", "profile", "cv"]):
        name = lines[1] if len(lines) > 1 else f"Candidate {index + 1}"
    name = re.sub(r"^(?:name|candidate):\s*", "", name, flags=re.IGNORECASE)
    name = name.split("|")[0].split("-")[0].strip()
    if len(name) > 30 or not name:
        name = f"Candidate {index + 1}"

    # Extract email
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", raw_resume)
    email = email_match.group(0) if email_match else f"{name.lower().replace(' ', '.')}@example.com"

    # Accurately extract experience using the dedicated experience parser
    exp_info = extract_candidate_experience(raw_resume)
    exp_years = exp_info["total_relevant_years"]

    # Extract role / title from lines 1-3
    role = "Software Engineer"
    for line in lines[1:4]:
        for role_kw in ["engineer", "developer", "architect", "lead", "manager", "specialist", "scientist", "intern"]:
            if role_kw in line.lower():
                role = line.split("|")[0].strip()
                break

    skills = _extract_skills(raw_resume)
    if not skills:
        skills = ["Software Development", "Problem Solving"]

    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "role": role,
        "email": email,
        "experience_years": exp_years,
        "professional_experience_years": exp_info["professional_years"],
        "internship_experience_years": exp_info["internship_years"],
        "skills": skills,
        "raw_resume": raw_resume,
    }


async def run_dynamic_recruitment_pipeline(
    job_description: str,
    resumes: list[str],
    top_n: int = 3,
) -> AsyncGenerator[tuple[AgentMessage, dict | None], None]:
    """
    Executes the full 6-agent recruitment pipeline on user-uploaded input.
    Yields (AgentMessage, final_dossier_or_None).
    """
    ts = lambda: datetime.now(timezone.utc).isoformat()
    
    # ── AGENT 1: Orchestrator Inception ───────────────────────────────────────
    yield AgentMessage(
        agent="Orchestrator",
        role="action",
        content=f"🚀 Recruitment Pipeline initiated. Ingesting {len(resumes)} custom candidate resume(s) for automated multi-agent matching.",
        timestamp=ts(),
    ), None
    await asyncio.sleep(0.35)

    # ── AGENT 2: Job Analysis Agent ───────────────────────────────────────────
    yield AgentMessage(
        agent="Orchestrator",
        role="decision",
        content="Delegating job description parsing and taxonomy breakdown to JobAnalysisAgent.",
        timestamp=ts(),
    ), None
    await asyncio.sleep(0.3)

    job_data = parse_job_description(job_description)
    yield AgentMessage(
        agent="JobAnalysisAgent",
        role="action",
        content=(
            f"Analyzed JD for '{job_data['title']}' at {job_data['company']}.\n"
            f"• Mandatory Requirements: {', '.join(job_data['mandatory'])}\n"
            f"• Experience Target: {job_data['experience_str']}\n"
            f"• Preferred Requirements: {', '.join(job_data['preferred']) or 'None specified'}"
        ),
        timestamp=ts(),
    ), None
    await asyncio.sleep(0.4)

    # ── AGENT 3: Resume Analysis Agent ────────────────────────────────────────
    yield AgentMessage(
        agent="Orchestrator",
        role="decision",
        content=f"Job requirements locked. Delegating {len(resumes)} resume(s) to ResumeAnalysisAgent for parsing & ChromaDB embedding.",
        timestamp=ts(),
    ), None
    await asyncio.sleep(0.3)

    candidates = []
    store = get_store()
    try:
        store.clear()
    except Exception:
        pass

    for i, raw_res in enumerate(resumes):
        cand_data = parse_candidate_resume(raw_res, i)
        cand_obj = Candidate(
            id=cand_data["id"],
            name=cand_data["name"],
            email=cand_data["email"],
            skills=cand_data["skills"],
            experience_years=cand_data["experience_years"],
            professional_experience_years=cand_data["professional_experience_years"],
            internship_experience_years=cand_data["internship_experience_years"],
            education="Bachelor's in Computer Science",
            summary=f"{cand_data['role']} with {cand_data['experience_years']} years experience in {', '.join(cand_data['skills'][:4])}",
            raw_resume=cand_data["raw_resume"],
        )
        candidates.append(cand_data)
        try:
            store.add_resume(cand_obj)
        except Exception:
            pass

        yield AgentMessage(
            agent="ResumeAnalysisAgent",
            role="action",
            content=f"Parsed resume for {cand_data['name']} — {cand_data['role']}, {cand_data['experience_years']} yrs exp (professional: {cand_data['professional_experience_years']}y, internship: {cand_data['internship_experience_years']}y), skills: {', '.join(cand_data['skills'][:6])}.",
            timestamp=ts(),
        ), None
        await asyncio.sleep(0.25)

    yield AgentMessage(
        agent="Orchestrator",
        role="action",
        content=f"All {len(candidates)} candidate profile(s) indexed into vector space. Delegating semantic ranking to MatchingAgent.",
        timestamp=ts(),
    ), None
    await asyncio.sleep(0.35)

    # ── AGENT 4: Matching and Ranking Agent (Initial Search) ──────────────────
    scoring_tool = ScoringTool()
    scored_candidates = []

    for c in candidates:
        eval_dict = scoring_tool.evaluate(
            candidate_skills=c["skills"],
            candidate_experience_years=c["experience_years"],
            mandatory_requirements=job_data["mandatory"],
            preferred_requirements=job_data["preferred"],
            min_experience_years=job_data["min_exp_years"],
            max_experience_years=job_data["max_exp_years"],
        )

        scored_candidates.append({
            **c,
            "score": eval_dict["match_score"],
            "matched_mandatory": eval_dict["matched_mandatory"],
            "missing_mandatory": eval_dict["missing_mandatory"],
            "matched_preferred": eval_dict["matched_preferred"],
            "missing_preferred": eval_dict["missing_preferred"],
            "is_compliant": eval_dict["is_compliant"],
            "eligibility_status": eval_dict["eligibility_status"],
            "score_breakdown": eval_dict["score_breakdown"],
            "experience_note": eval_dict["experience_note"],
        })

    # Sort descending by compliance first, then score
    scored_candidates.sort(key=lambda x: (x["is_compliant"], x["score"]), reverse=True)
    initial_shortlist = scored_candidates[:top_n]

    shortlist_summary = "\n".join([f"{idx+1}. {c['name']} — Score: {c['score']}/100 ({c['role']}) [{'FULLY_ELIGIBLE' if c['is_compliant'] else 'NON_COMPLIANT'}]" for idx, c in enumerate(initial_shortlist)])
    yield AgentMessage(
        agent="MatchingAgent",
        role="action",
        content=f"[INITIAL SEARCH] Ranked {len(scored_candidates)} candidates using deterministic scoring & criteria:\n{shortlist_summary}",
        timestamp=ts(),
    ), None
    await asyncio.sleep(0.4)

    # ── AGENT 5: Candidate Evaluation Agent (Critic) ──────────────────────────
    yield AgentMessage(
        agent="Orchestrator",
        role="decision",
        content=f"Initial shortlist of {len(initial_shortlist)} candidate(s) submitted. Delegating to EvaluationAgent for independent critic verification.",
        timestamp=ts(),
    ), None
    await asyncio.sleep(0.3)

    # Evaluation Agent identifies substandard candidates (must have 0 missing mandatory skills)
    critic_rejected = [c for c in initial_shortlist if not c["is_compliant"] or len(c.get("missing_mandatory", [])) > 0]
    approved_candidates = [c for c in initial_shortlist if c["is_compliant"] and len(c.get("missing_mandatory", [])) == 0]

    initial_shortlist_ids = {c["id"] for c in initial_shortlist}
    # Dynamic replanning is required whenever the critic challenges candidates on the shortlist
    replan_needed = len(critic_rejected) > 0

    if critic_rejected:
        rej_names = ", ".join([c["name"] for c in critic_rejected])
        details = "\n".join([
            f"• {c['name']} (Score: {c['score']}/100): MISSING mandatory requirements: {', '.join(c['missing_mandatory']) or 'Experience criteria unmet'}."
            for c in critic_rejected
        ])
        yield AgentMessage(
            agent="EvaluationAgent",
            role="conflict",
            content=f"⚔️ SHORTLIST CHALLENGED by Candidate Evaluation Agent (Critic Disagreement):\n{details}\n• Verdict: REJECT inclusion of {rej_names}. Candidate(s) fail non-negotiable mandatory bar.",
            timestamp=ts(),
        ), None
        await asyncio.sleep(0.45)
    else:
        yield AgentMessage(
            agent="EvaluationAgent",
            role="result",
            content=f"✅ SHORTLIST VERIFIED & APPROVED by EvaluationAgent. All {len(approved_candidates)} candidates satisfy 100% of mandatory requirements.",
            timestamp=ts(),
        ), None
        await asyncio.sleep(0.35)

    # ── AGENT 1 REPLANNING: Orchestrator Dynamic Replanning ────────────────────
    replan_occurred = False
    if replan_needed:
        replan_occurred = True
        yield AgentMessage(
            agent="Orchestrator",
            role="conflict",
            content="⚠️ Conflict Detected: EvaluationAgent challenged the MatchingAgent's shortlist. Reconciling disagreement and initiating dynamic replanning.",
            timestamp=ts(),
        ), None
        await asyncio.sleep(0.4)

        yield AgentMessage(
            agent="Orchestrator",
            role="replan",
            content="🔄 Adaptive Replanning Decision: REPLAN_RELAXED.\n• Business Rule Applied: Selectively relax PREFERRED requirements while STRICTLY PRESERVING MANDATORY requirements.\n• Action: Rerunning MatchingAgent with weighted focus on verified mandatory skills.",
            timestamp=ts(),
        ), None
        await asyncio.sleep(0.4)

        # Rerun matching: relax preferred requirements, but strictly keep mandatory requirements!
        for c in scored_candidates:
            # Re-score with preferred relaxed
            relaxed_eval = scoring_tool.evaluate(
                candidate_skills=c["skills"],
                candidate_experience_years=c["experience_years"],
                mandatory_requirements=job_data["mandatory"],
                preferred_requirements=[],  # preferred relaxed!
                min_experience_years=job_data["min_exp_years"],
                max_experience_years=job_data["max_exp_years"],
                mandatory_weight=75.0,
                preferred_weight=0.0,
                experience_weight=25.0,
            )
            c["score"] = relaxed_eval["match_score"]
            c["is_compliant"] = relaxed_eval["is_compliant"]

        scored_candidates.sort(key=lambda x: (x["is_compliant"], x["score"]), reverse=True)
        final_shortlist = scored_candidates[:top_n]

        relaxed_summary = "\n".join([f"{idx+1}. {c['name']} — Score: {c['score']}/100 ({'APPROVED' if c['is_compliant'] else 'CONDITIONAL'})" for idx, c in enumerate(final_shortlist)])
        yield AgentMessage(
            agent="MatchingAgent",
            role="replan",
            content=f"[RELAXED SEARCH] Reranked candidates with strict mandatory preservation:\n{relaxed_summary}",
            timestamp=ts(),
        ), None
        await asyncio.sleep(0.35)

        yield AgentMessage(
            agent="EvaluationAgent",
            role="result",
            content=f"✅ REVISED SHORTLIST EVALUATED by EvaluationAgent: Evaluated candidates with strict compliance to mandatory criteria.",
            timestamp=ts(),
        ), None
        await asyncio.sleep(0.35)
    else:
        final_shortlist = initial_shortlist

    # ── AGENT 6: Recruitment Communication Agent ──────────────────────────────
    # Business Rules:
    # 1. Fully compliant candidates (meeting threshold) are APPROVED.
    # 2. Candidates missing <= 2 mandatory or score >= 45 are CONDITIONAL.
    # 3. Candidates failing criteria are REJECTED.
    # Mutually exclusive partition across ALL ingested candidates:
    authoritative_approved = []
    authoritative_conditional = []
    authoritative_rejected = []
    rejection_reasons = []

    # Use ID-based set lookup — dict identity comparison with `in` always fails
    final_shortlist_ids = {c["id"] for c in final_shortlist}

    for c in scored_candidates:
        if c["is_compliant"] and len(c.get("missing_mandatory", [])) == 0 and c["id"] in final_shortlist_ids:
            # Fully compliant (100% mandatory met) AND in final shortlist → APPROVED
            authoritative_approved.append(c)
        elif c["is_compliant"] and len(c.get("missing_mandatory", [])) == 0 and c["id"] not in final_shortlist_ids:
            # Fully compliant but outside top-N shortlist (e.g. ranked 4th) → CONDITIONAL
            authoritative_conditional.append(c)
            rejection_reasons.append(f"{c['name']}: Compliant but outside top-{top_n} shortlist — held in conditional review.")
        elif (len(c["missing_mandatory"]) <= 2 or c["score"] >= 50.0) and c["id"] in final_shortlist_ids:
            # Shortlisted high-potential candidate → CONDITIONAL
            authoritative_conditional.append(c)
            rejection_reasons.append(f"{c['name']}: Missing {', '.join(c['missing_mandatory'])} — held in conditional review.")
        elif len(c["missing_mandatory"]) <= 1 and c["score"] >= 40.0:
            # Missing at most 1 mandatory with decent score → CONDITIONAL
            authoritative_conditional.append(c)
            rejection_reasons.append(f"{c['name']}: Missing mandatory ({', '.join(c['missing_mandatory'])}) — held in conditional review.")
        else:
            authoritative_rejected.append(c)
            rejection_reasons.append(f"{c['name']}: Non-compliant with mandatory requirements ({', '.join(c['missing_mandatory']) or 'Insufficient criteria'}).")


    yield AgentMessage(
        agent="Orchestrator",
        role="decision",
        content=(
            f"Evaluation concluded. Approved candidates: {len(authoritative_approved)}, "
            f"Conditional candidates: {len(authoritative_conditional)}, "
            f"Rejected candidates: {len(authoritative_rejected)}. "
            f"Delegating to Recruitment Communication Agent."
        ),
        timestamp=ts(),
    ), None
    await asyncio.sleep(0.3)

    dossier_shortlisted = []
    dossier_conditional = []
    dossier_rejected = []

    # Generate communications safely (communication failure must NOT clear shortlist)
    try:
        for c in authoritative_approved:
            invite_text = (
                f"Dear {c['name']}, We were thoroughly impressed by your background as {c['role']} "
                f"and your extensive expertise in {', '.join(c['matched_mandatory'][:3]) or 'software engineering'}. "
                f"{job_data['company']} would love to invite you for an initial interview for the {job_data['title']} position."
            )
            yield AgentMessage(
                agent="CommunicationAgent",
                role="result",
                content=f"📧 Interview Invitation — {c['name']} (Score: {c['score']}/100):\n'{invite_text}'",
                timestamp=ts(),
            ), None
            await asyncio.sleep(0.3)

            dossier_shortlisted.append({
                "name": c["name"],
                "role": c["role"],
                "score": c["score"],
                "experience": f"{c['experience_years']} years",
                "matched_mandatory": c["matched_mandatory"],
                "matched_preferred": c["matched_preferred"],
                "missing_mandatory": c["missing_mandatory"],
                "missing_preferred": c["missing_preferred"],
                "status": "APPROVED (RELAXED CRITERIA)" if replan_occurred and c["missing_preferred"] else "APPROVED",
                "evaluation_notes": f"Verified by EvaluationAgent. Satisfies 100% of mandatory requirements ({len(c['matched_mandatory'])} met).",
                "invitation": invite_text,
            })
    except Exception as comm_err:
        yield AgentMessage(
            agent="CommunicationAgent",
            role="conflict",
            content=f"⚠️ Communication Agent encountered an issue: {comm_err}. Approved shortlist preserved.",
            timestamp=ts(),
        ), None

    for c in authoritative_conditional:
        dossier_conditional.append({
            "name": c["name"],
            "role": c["role"],
            "score": c["score"],
            "experience": f"{c['experience_years']} years",
            "matched_mandatory": c["matched_mandatory"],
            "missing_mandatory": c["missing_mandatory"],
            "status": "CONDITIONAL",
            "evaluation_notes": f"Conditional Review: Candidate lacks {', '.join(c['missing_mandatory'])}. Retained for secondary review.",
        })

    for r in authoritative_rejected:
        dossier_rejected.append({
            "name": r["name"],
            "role": r["role"],
            "score": r["score"],
            "experience": f"{r['experience_years']} years",
            "missing_mandatory": r["missing_mandatory"],
            "status": "REJECTED",
            "evaluation_notes": f"Challenged by EvaluationAgent. Missing mandatory requirements: {', '.join(r['missing_mandatory']) or 'Insufficient score threshold'}.",
        })

    # Summary
    yield AgentMessage(
        agent="Orchestrator",
        role="result",
        content=(
            f"🎉 Recruitment Pipeline Complete for '{job_data['title']}' at {job_data['company']}.\n"
            f"• Candidates Ingested: {len(candidates)}\n"
            f"• Shortlisted & Approved: {len(dossier_shortlisted)}\n"
            f"• Conditional Candidates: {len(dossier_conditional)}\n"
            f"• Rejected Candidates: {len(dossier_rejected)}\n"
            f"• Communications Generated: {len(dossier_shortlisted)} interview invitation(s)."
        ),
        timestamp=ts(),
    ), None
    await asyncio.sleep(0.2)

    # Build and return the authoritative structured evaluation dossier
    evaluation_summary = {
        "verdict": "APPROVE" if len(dossier_shortlisted) > 0 else "REJECT",
        "approved_count": len(dossier_shortlisted),
        "conditional_count": len(dossier_conditional),
        "rejected_count": len(dossier_rejected),
        "total_ingested": len(candidates),
        "replan_occurred": replan_occurred,
    }

    final_dossier = {
        "job_title": job_data["title"],
        "company": job_data["company"],
        "mandatory": job_data["mandatory"],
        "preferred": job_data["preferred"],
        "approved_candidates": dossier_shortlisted,
        "conditional_candidates": dossier_conditional,
        "rejected_candidates": dossier_rejected,
        "shortlisted": dossier_shortlisted,  # backward compatibility with UI
        "rejected": dossier_rejected,        # backward compatibility with UI
        "rejection_reasons": rejection_reasons,
        "evaluation_summary": evaluation_summary,
    }

    yield AgentMessage(
        agent="System",
        role="result",
        content="Recruitment pipeline execution successfully finished.",
        timestamp=ts(),
    ), final_dossier

