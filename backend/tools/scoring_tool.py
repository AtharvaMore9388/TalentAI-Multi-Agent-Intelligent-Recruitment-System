"""
TalentAI — Scoring & Eligibility Tool
Computes structured match score, skill breakdown, and independent mandatory eligibility
according to explicit configured business rules.
"""
from __future__ import annotations
import re
from typing import Optional, Dict, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# Comprehensive skill equivalence mapping
# Maps JD requirement keywords to candidate skills that satisfy them.
SKILL_ALIASES: dict[str, set[str]] = {
    # JavaScript Frameworks
    "node.js":    {"nodejs", "node.js", "node"},
    "nodejs":     {"nodejs", "node.js", "node"},
    "react":      {"react", "react.js", "reactjs"},
    "react.js":   {"react", "react.js", "reactjs"},
    "next.js":    {"next.js", "nextjs", "next"},
    "nextjs":     {"next.js", "nextjs", "next"},
    "vue":        {"vue", "vue.js", "vuejs"},
    "vue.js":     {"vue", "vue.js", "vuejs"},
    # Python
    "python programming": {"python", "python programming", "python3"},
    "python":             {"python", "python programming", "python3"},
    # Machine Learning - PyTorch/TensorFlow directly imply ML knowledge
    "machine learning": {
        "machine learning", "ml", "sklearn", "scikit-learn",
        "pytorch", "tensorflow", "keras", "xgboost",
        "random forest", "neural network", "deep learning",
    },
    "ml": {"machine learning", "ml", "sklearn", "pytorch", "tensorflow", "keras"},
    # Deep Learning - PyTorch and TensorFlow ARE deep learning frameworks
    "deep learning": {
        "deep learning", "dl", "deep learning fundamentals",
        "pytorch", "tensorflow", "keras", "neural network",
        "cnn", "rnn", "lstm", "transformer",
    },
    "deep learning fundamentals": {
        "deep learning", "dl", "deep learning fundamentals",
        "pytorch", "tensorflow", "keras", "neural network",
    },
    # ML Libraries
    "scikit-learn": {"scikit-learn", "sklearn", "scikit learn", "machine learning"},
    "sklearn":      {"scikit-learn", "sklearn", "scikit learn"},
    "tensorflow":   {"tensorflow", "tf", "keras", "deep learning"},
    "pytorch":      {"pytorch", "torch", "deep learning"},
    "pandas":       {"pandas", "data analysis", "dataframe"},
    "numpy":        {"numpy", "np", "numerical computing"},
    # REST APIs - FastAPI, Flask, Django all build REST APIs
    "rest apis": {
        "rest", "rest api", "rest apis", "restful",
        "fastapi", "fast api", "flask", "django", "express",
        "spring boot", "web api",
    },
    "rest api": {
        "rest", "rest api", "rest apis", "restful",
        "fastapi", "fast api", "flask", "django", "express",
    },
    "rest": {"rest", "rest api", "rest apis", "restful", "fastapi", "flask", "django"},
    # Flask and Django
    "flask":   {"flask", "bottle"},
    "django":  {"django", "drf"},
    "fastapi": {"fastapi", "fast api", "flask", "django", "rest api", "rest apis"},
    # Databases
    "sql": {"sql", "mysql", "postgresql", "postgres", "sqlite", "mariadb", "oracle", "database"},
    "database management": {
        "database management", "database", "sql", "mysql", "postgresql",
        "postgres", "mongodb", "sqlite", "nosql", "redis",
    },
    "database": {
        "database management", "database", "sql", "mysql",
        "postgresql", "postgres", "mongodb", "sqlite", "nosql",
    },
    "postgresql": {"postgresql", "postgres", "psql", "sql"},
    "postgres":   {"postgresql", "postgres", "psql", "sql"},
    "mongodb":    {"mongodb", "mongo", "nosql", "database"},
    # Version Control
    "git":    {"git", "github", "gitlab", "bitbucket", "version control", "vcs"},
    "github": {"github", "git", "gitlab", "bitbucket", "version control"},
    # Data Structures - any developer with Python/Java implicitly knows DSA
    "data structures": {
        "data structures", "dsa", "data structures and algorithms",
        "algorithms", "problem solving",
        "python", "java", "c++", "golang",
    },
    "data structures and algorithms": {
        "data structures", "dsa", "algorithms", "problem solving",
    },
    "algorithms": {
        "algorithms", "dsa", "data structures and algorithms",
        "data structures", "problem solving",
    },
    # Cloud & DevOps
    "aws":            {"aws", "amazon web services", "ec2", "s3", "lambda"},
    "azure":          {"azure", "microsoft azure"},
    "gcp":            {"gcp", "google cloud", "google cloud platform"},
    "cloud":          {"aws", "azure", "gcp", "cloud", "heroku", "vercel", "render"},
    "cloud platforms":{"aws", "azure", "gcp", "cloud", "heroku", "vercel"},
    "docker":         {"docker", "containerization", "containers"},
    "kubernetes":     {"kubernetes", "k8s"},
    "k8s":            {"kubernetes", "k8s"},
    "ci/cd":          {"ci/cd", "cicd", "github actions", "jenkins"},
    "cicd":           {"ci/cd", "cicd", "github actions", "jenkins"},
    # AI / NLP
    "natural language processing": {"natural language processing", "nlp"},
    "nlp":  {"natural language processing", "nlp"},
    "generative ai": {
        "generative ai", "gen ai", "llm", "large language model",
        "gpt", "openai", "langchain", "llama", "rag",
    },
    "large language models": {
        "llm", "large language model", "large language models",
        "gpt", "bert", "openai", "langchain", "generative ai",
    },
    "llm": {"llm", "large language model", "gpt", "bert", "langchain"},
}


def normalize_skill(skill: str) -> str:
    """Normalize skill string for exact comparison."""
    return re.sub(r"[^\w\+\#\.\/]", " ", skill.lower()).strip()


def skills_match(req_skill: str, cand_skills: set[str]) -> bool:
    """
    Check if candidate possesses a required skill using exact token match,
    canonical alias, or semantic equivalence.
    Handles compound requirements with 'or' and 'and'.
    """
    req_clean = req_skill.strip()
    if not req_clean:
        return True

    req_norm = normalize_skill(req_clean)
    cand_norms = {normalize_skill(s) for s in cand_skills}

    # 1. Soft skills & universal developer baseline
    soft_skills = {
        "problem solving", "problem solving and communication",
        "communication", "communication skills", "collaboration",
        "teamwork", "team player", "analytical thinking",
        "software development", "software engineering", "programming",
        "intelligent applications", "ai projects", "experience building ai projects"
    }
    if req_norm in soft_skills:
        return True

    # 2. If requirement contains ' or ': candidate satisfies ANY of the choices
    # e.g., "Flask or Django", "TensorFlow or PyTorch", "REST APIs and Flask or Django"
    if re.search(r"\bor\b", req_clean, re.IGNORECASE):
        or_options = [opt.strip() for opt in re.split(r"\bor\b", req_clean, flags=re.IGNORECASE) if opt.strip()]
        if any(skills_match(opt, cand_skills) for opt in or_options):
            return True

    # 3. If requirement contains ' and ': candidate satisfies if they have either core component
    # e.g., "Git and GitHub", "SQL and database management", "Data Structures and Algorithms",
    # "Machine Learning and Deep Learning fundamentals"
    if re.search(r"\band\b", req_clean, re.IGNORECASE):
        and_parts = [p.strip() for p in re.split(r"\band\b", req_clean, flags=re.IGNORECASE) if p.strip()]
        if any(skills_match(p, cand_skills) for p in and_parts):
            return True

    # 4. Direct normalized match
    if req_norm in cand_norms:
        return True

    # 5. Check canonical aliases
    aliases = SKILL_ALIASES.get(req_norm, {req_norm})
    if any(alias in cand_norms for alias in aliases):
        return True

    # 6. Whole phrase boundary check
    for cand_s in cand_norms:
        if re.search(r"\b" + re.escape(req_norm) + r"\b", cand_s):
            return True
        for alias in aliases:
            if re.search(r"\b" + re.escape(alias) + r"\b", cand_s):
                return True

    return False


def verify_experience_constraint(
    candidate_exp: float,
    min_exp: float = 0.0,
    max_exp: Optional[float] = None,
) -> tuple[bool, str]:
    """
    Verifies experience constraint correctly:
    - 0-2 years requirement: candidate with 0.0, 0.33, 0.5, 1.5, 2.0 passes.
    - 3+ years requirement: candidate with >= 3.0 passes.
    """
    if candidate_exp < min_exp:
        return False, f"Requires minimum {min_exp} yrs (candidate has {candidate_exp} yrs)"

    if max_exp is not None and candidate_exp > max_exp:
        # Overqualified or outside range, but if range is explicitly 0-2, verify compliance
        # Usually 0-2 years means entry-level up to 2 yrs.
        return True, f"Within target experience spectrum ({candidate_exp} yrs for {min_exp}-{max_exp} yrs)"

    return True, f"Meets experience criteria ({candidate_exp} yrs)"


class ScoringInput(BaseModel):
    candidate_skills: str = Field(..., description="Comma-separated list of candidate skills")
    candidate_experience_years: float = Field(..., description="Years of experience")
    mandatory_requirements: str = Field(..., description="Comma-separated mandatory requirements")
    preferred_requirements: str = Field(..., description="Comma-separated preferred requirements")
    min_experience_years: float = Field(default=0.0, description="Minimum experience required")
    max_experience_years: Optional[float] = Field(default=None, description="Maximum experience if range like 0-2")


class ScoringTool(BaseTool):
    name: str = "scoring_tool"
    description: str = (
        "Computes a match score and independent eligibility status for a candidate "
        "given their skills and experience vs mandatory and preferred requirements."
    )
    args_schema: type[BaseModel] = ScoringInput

    def _run(
        self,
        candidate_skills: str,
        candidate_experience_years: float,
        mandatory_requirements: str,
        preferred_requirements: str,
        min_experience_years: float = 0.0,
        max_experience_years: Optional[float] = None,
    ) -> str:
        res = self.evaluate(
            candidate_skills=[s.strip() for s in candidate_skills.split(",") if s.strip()],
            candidate_experience_years=candidate_experience_years,
            mandatory_requirements=[r.strip() for r in mandatory_requirements.split(",") if r.strip()],
            preferred_requirements=[r.strip() for r in preferred_requirements.split(",") if r.strip()],
            min_experience_years=min_experience_years,
            max_experience_years=max_experience_years,
        )
        return (
            f"SCORE: {res['match_score']}/100\n"
            f"ELIGIBILITY: {res['eligibility_status']}\n"
            f"Mandatory met: {len(res['matched_mandatory'])}/{len(res['matched_mandatory']) + len(res['missing_mandatory'])} -> {res['matched_mandatory']}\n"
            f"Missing mandatory: {res['missing_mandatory']}\n"
            f"Preferred met: {len(res['matched_preferred'])}/{len(res['matched_preferred']) + len(res['missing_preferred'])} -> {res['matched_preferred']}\n"
            f"Missing preferred: {res['missing_preferred']}\n"
            f"Experience score: {res['score_breakdown']['experience']}/15\n"
            f"PASS_MANDATORY: {'YES' if res['is_compliant'] else 'NO'}"
        )

    @staticmethod
    def evaluate(
        candidate_skills: list[str],
        candidate_experience_years: float,
        mandatory_requirements: list[str],
        preferred_requirements: list[str],
        min_experience_years: float = 0.0,
        max_experience_years: Optional[float] = None,
        mandatory_weight: float = 60.0,
        preferred_weight: float = 25.0,
        experience_weight: float = 15.0,
        mandatory_compliance_threshold: float = 0.75,
    ) -> Dict[str, Any]:
        """
        Deterministic evaluation with 75% mandatory compliance threshold.
        Candidates meeting >= 75% of mandatory requirements are considered COMPLIANT.
        This reflects real-world recruitment: core technical bar, not every bullet.
        """
        """
        Pure deterministic evaluation calculation.
        Keeps matching score separate from mandatory eligibility.
        """
        cand_skills_set = set(candidate_skills)

        # Skill filtering — ignore explicit experience requirement strings from skill list
        pure_mandatory = []
        parsed_min_exp = min_experience_years
        parsed_max_exp = max_experience_years

        for req in mandatory_requirements:
            exp_range = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)", req, re.IGNORECASE)
            exp_plus = re.search(r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)", req, re.IGNORECASE)
            if exp_range:
                parsed_min_exp = float(exp_range.group(1))
                parsed_max_exp = float(exp_range.group(2))
            elif exp_plus and any(w in req.lower() for w in ["exp", "year"]):
                parsed_min_exp = float(exp_plus.group(1))
            else:
                pure_mandatory.append(req)

        # Check matched mandatory skills
        matched_mandatory = [r for r in pure_mandatory if skills_match(r, cand_skills_set)]
        missing_mandatory = [r for r in pure_mandatory if not skills_match(r, cand_skills_set)]

        # Check matched preferred skills
        matched_preferred = [p for p in preferred_requirements if skills_match(p, cand_skills_set)]
        missing_preferred = [p for p in preferred_requirements if not skills_match(p, cand_skills_set)]

        # Verify experience constraint
        exp_compliant, exp_note = verify_experience_constraint(
            candidate_experience_years, parsed_min_exp, parsed_max_exp
        )
        if not exp_compliant:
            missing_mandatory.append(f"Experience: minimum {parsed_min_exp} yrs required (has {candidate_experience_years})")

        # ── Scores Calculation ────────────────────────────────────────────────
        # 1. Mandatory score
        if pure_mandatory:
            mand_score = (len(matched_mandatory) / len(pure_mandatory)) * mandatory_weight
        else:
            mand_score = mandatory_weight

        # 2. Preferred score
        if preferred_requirements:
            pref_score = (len(matched_preferred) / len(preferred_requirements)) * preferred_weight
        else:
            # If no preferred requirements are specified, do not penalize or invent
            pref_score = preferred_weight

        # 3. Experience score
        if parsed_max_exp is not None and parsed_max_exp > 0:
            # e.g., 0–2 years: candidate with 1.5 yrs is 100% in target sweet spot
            if parsed_min_exp <= candidate_experience_years <= parsed_max_exp:
                exp_score = experience_weight
            elif candidate_experience_years < parsed_min_exp:
                exp_score = max(0.0, (candidate_experience_years / parsed_min_exp) * experience_weight)
            else:
                exp_score = experience_weight  # experienced candidate
        elif parsed_min_exp > 0:
            exp_score = min(experience_weight, (candidate_experience_years / parsed_min_exp) * experience_weight)
        else:
            exp_score = experience_weight

        total_score = round(mand_score + pref_score + exp_score, 2)

        # ── Compliance: 75% mandatory threshold ───────────────────────────────
        # >= 75% mandatory met = COMPLIANT (shortlistable)
        # 100% mandatory met   = FULLY_ELIGIBLE
        # < 75%                = NON_COMPLIANT
        if pure_mandatory:
            mandatory_coverage = len(matched_mandatory) / len(pure_mandatory)
        else:
            mandatory_coverage = 1.0

        is_compliant = (mandatory_coverage >= mandatory_compliance_threshold) and exp_compliant

        if mandatory_coverage == 1.0 and exp_compliant:
            eligibility_status = "FULLY_ELIGIBLE"
        elif is_compliant:
            eligibility_status = "COMPLIANT"
        elif mandatory_coverage >= 0.5:
            eligibility_status = "CONDITIONALLY_ELIGIBLE"
        else:
            eligibility_status = "NON_COMPLIANT"

        return {
            "match_score": total_score,
            "is_compliant": is_compliant,
            "eligibility_status": eligibility_status,
            "matched_mandatory": matched_mandatory,
            "missing_mandatory": missing_mandatory,
            "matched_preferred": matched_preferred,
            "missing_preferred": missing_preferred,
            "mandatory_coverage": round(mandatory_coverage * 100, 1),
            "score_breakdown": {
                "mandatory": round(mand_score, 2),
                "preferred": round(pref_score, 2),
                "experience": round(exp_score, 2),
            },
            "experience_note": exp_note,
        }

