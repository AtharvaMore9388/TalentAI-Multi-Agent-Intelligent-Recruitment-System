"""
TalentAI — Scoring Tool
Computes a structured match score for a candidate vs job requirements.
"""
from __future__ import annotations
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class ScoringInput(BaseModel):
    candidate_skills: str = Field(..., description="Comma-separated list of candidate skills")
    candidate_experience_years: float = Field(..., description="Years of experience")
    mandatory_requirements: str = Field(..., description="Comma-separated mandatory requirements")
    preferred_requirements: str = Field(..., description="Comma-separated preferred requirements")


class ScoringTool(BaseTool):
    """
    Computes a deterministic skill-match score for a candidate against
    job mandatory and preferred requirements. Returns matched/missing
    skills and a composite score (0–100).
    """

    name: str = "scoring_tool"
    description: str = (
        "Computes a match score for a candidate given their skills/experience "
        "versus mandatory and preferred job requirements. Returns score breakdown."
    )
    args_schema: type[BaseModel] = ScoringInput

    def _run(
        self,
        candidate_skills: str,
        candidate_experience_years: float,
        mandatory_requirements: str,
        preferred_requirements: str,
    ) -> str:
        cand_skills = {s.strip().lower() for s in candidate_skills.split(",") if s.strip()}
        mandatory = [r.strip().lower() for r in mandatory_requirements.split(",") if r.strip()]
        preferred = [r.strip().lower() for r in preferred_requirements.split(",") if r.strip()]

        # Fuzzy matching — check if any requirement keyword appears in candidate skills
        def _skill_match(req: str, skills: set[str]) -> bool:
            req_words = set(req.split())
            for skill in skills:
                skill_words = set(skill.split())
                if req_words & skill_words:  # any overlap
                    return True
            return False

        matched_mandatory = [r for r in mandatory if _skill_match(r, cand_skills)]
        missing_mandatory = [r for r in mandatory if not _skill_match(r, cand_skills)]
        matched_preferred = [r for r in preferred if _skill_match(r, cand_skills)]
        missing_preferred = [r for r in preferred if not _skill_match(r, cand_skills)]

        # Score calculation
        mandatory_score = (len(matched_mandatory) / len(mandatory) * 60) if mandatory else 60
        preferred_score = (len(matched_preferred) / len(preferred) * 30) if preferred else 30
        exp_score = min(candidate_experience_years / 5.0 * 10, 10)
        total_score = round(mandatory_score + preferred_score + exp_score, 2)

        result = (
            f"SCORE: {total_score}/100\n"
            f"Mandatory met: {len(matched_mandatory)}/{len(mandatory)} -> {matched_mandatory}\n"
            f"Missing mandatory: {missing_mandatory}\n"
            f"Preferred met: {len(matched_preferred)}/{len(preferred)} -> {matched_preferred}\n"
            f"Missing preferred: {missing_preferred}\n"
            f"Experience score: {round(exp_score, 2)}/10\n"
            f"PASS_MANDATORY: {'YES' if not missing_mandatory else 'NO'}"
        )
        return result
