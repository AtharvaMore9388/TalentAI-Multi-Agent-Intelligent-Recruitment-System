"""
TalentAI — Experience & Duration Parser
Extracts professional experience, internship experience, and project work accurately.
Converts month durations to fractional years (4 months = 0.33, 6 months = 0.5, 18 months = 1.5).
Prevents extracting degree durations or non-experience numbers as experience.
"""
from __future__ import annotations
import re
from typing import Dict, Any, Optional

WORD_TO_NUM = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "twelve": 12, "eighteen": 18, "twenty-four": 24, "twenty four": 24,
    "thirty-six": 36, "thirty six": 36,
}


def parse_duration_to_years(text: str) -> float:
    """
    Parses a single duration string (e.g., '4 months', '6 mos', '18 months', '2.5 years')
    into decimal years with precision.
    """
    text_clean = text.lower().strip()

    # Check for word number, e.g. "four-month", "four months"
    for word, num in WORD_TO_NUM.items():
        if word in text_clean:
            text_clean = text_clean.replace(word, str(num))

    # Match month patterns: e.g. "4 months", "4-month", "6 mos", "18m"
    m_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|–)?\s*(?:months?|mos?)\b", text_clean)
    if m_match:
        months = float(m_match.group(1))
        return round(months / 12.0, 2)

    # Match year patterns: e.g. "1.5 years", "2 yrs", "3 year"
    y_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|–)?\s*(?:years?|yrs?)\b", text_clean)
    if y_match:
        return round(float(y_match.group(1)), 2)

    return 0.0


def extract_candidate_experience(raw_resume: str) -> Dict[str, Any]:
    """
    Analyzes resume text and extracts distinct experience categories:
    - professional_years: float (Full-time corporate/professional roles)
    - internship_years: float (Internships, traineeships)
    - total_relevant_years: float
    - experience_verified: bool
    - notes: list[str]
    """
    text = raw_resume
    text_lower = text.lower()

    # 1. Check for explicit "no professional experience" statements
    no_exp_patterns = [
        r"no\s+professional\s+experience",
        r"no\s+prior\s+work\s+experience",
        r"no\s+prior\s+experience",
        r"zero\s+(?:years|months|yrs)\s+(?:of\s+)?(?:professional\s+)?experience",
        r"0\s+(?:years|yrs)\s+(?:of\s+)?(?:professional\s+)?experience",
        r"\bfresher\b",
        r"fresh\s+graduate",
        r"freshly\s+graduated",
    ]
    has_explicit_no_exp = any(re.search(pat, text_lower) for pat in no_exp_patterns)

    # Separate resume into sections to avoid scanning Education for work experience
    lines = text.split("\n")
    current_section = "summary"
    section_lines: dict[str, list[str]] = {
        "summary": [],
        "experience": [],
        "internship": [],
        "projects": [],
        "education": [],
        "skills": [],
        "other": [],
    }

    for line in lines:
        line_clean = line.strip().lower()
        if not line_clean:
            continue

        # Header detection
        if any(h in line_clean for h in ["work experience", "professional experience", "employment history", "work history", "experience:"]):
            current_section = "experience"
            continue
        elif any(h in line_clean for h in ["internship", "internships", "trainee experience"]):
            current_section = "internship"
            continue
        elif any(h in line_clean for h in ["projects", "academic projects", "personal projects"]):
            current_section = "projects"
            continue
        elif any(h in line_clean for h in ["education", "academic background", "qualifications"]):
            current_section = "education"
            continue
        elif any(h in line_clean for h in ["skills", "technical skills", "core skills"]):
            current_section = "skills"
            continue

        section_lines.setdefault(current_section, []).append(line)

    exp_text = "\n".join(section_lines.get("experience", []))
    intern_text = "\n".join(section_lines.get("internship", []))
    summary_text = "\n".join(section_lines.get("summary", []))

    # Also detect inline mentions of internships in the general experience section
    internship_snippets = []
    professional_snippets = []

    for line in section_lines.get("experience", []):
        if any(w in line.lower() for w in ["intern", "internship", "trainee"]):
            internship_snippets.append(line)
        else:
            professional_snippets.append(line)

    internship_snippets.extend(section_lines.get("internship", []))

    # 2. Extract Internship Experience
    internship_years = 0.0
    for snippet in internship_snippets:
        dur = parse_duration_to_years(snippet)
        if dur > 0:
            internship_years += dur
        # Check date range like (2020-2021) or (Jan 2023 - Jun 2023)
        date_range = re.search(r"\((\d{4})\s*(?:-|–|to)\s*(\d{4})\)", snippet)
        if date_range and dur == 0:
            y1, y2 = int(date_range.group(1)), int(date_range.group(2))
            diff = max(0, y2 - y1)
            # Typically internships don't exceed 1 year
            internship_years += min(1.0, float(diff)) if diff > 0 else 0.5

    # Check for direct phrase in whole resume like "4-month internship" or "4 months internship"
    full_text_lower = text_lower
    for word, num in WORD_TO_NUM.items():
        full_text_lower = full_text_lower.replace(word, str(num))

    intern_dur_matches = re.findall(r"(\d+(?:\.\d+)?)\s*(?:-|–)?\s*(?:months?|mos?)\s+(?:of\s+)?(?:internship|intern)", full_text_lower)
    for m in intern_dur_matches:
        calc = round(float(m) / 12.0, 2)
        if calc > internship_years:
            internship_years = calc

    # 3. Extract Professional Experience
    professional_years = 0.0

    if has_explicit_no_exp:
        professional_years = 0.0
    else:
        # Check summary for overall years: e.g. "6 years of experience" or "Senior Full Stack with 5 years"
        # BUT verify it doesn't say "internship"
        summary_exp_match = re.search(r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+experience)?", summary_text, re.IGNORECASE)
        if summary_exp_match and "intern" not in summary_text.lower():
            professional_years = float(summary_exp_match.group(1))
        else:
            # Aggregate from professional role lines or date ranges
            for p_line in professional_snippets:
                # Check for explicit duration in role description
                dur = parse_duration_to_years(p_line)
                if dur > 0 and "intern" not in p_line.lower():
                    professional_years += dur
                else:
                    # Year ranges e.g., (2020–Present) or (2018–2021)
                    date_range = re.search(r"\((\d{4})\s*(?:-|–|to)\s*(\d{4}|present)\)", p_line, re.IGNORECASE)
                    if date_range:
                        y1 = int(date_range.group(1))
                        y2_str = date_range.group(2).lower()
                        y2 = 2024 if y2_str == "present" else int(y2_str)
                        if y2 >= y1:
                            professional_years += float(y2 - y1)

    # Clean up and normalize
    professional_years = round(professional_years, 2)
    internship_years = round(internship_years, 2)

    # Guardrails:
    # If Sneha Kulkarni or someone explicitly stated no professional experience:
    if has_explicit_no_exp:
        professional_years = 0.0

    # Total relevant experience for scoring (for entry-level roles 0-2 yrs, internship counts)
    total_relevant_years = round(professional_years + internship_years, 2)

    return {
        "professional_years": professional_years,
        "internship_years": internship_years,
        "total_relevant_years": total_relevant_years,
        "has_explicit_no_exp": has_explicit_no_exp,
        "experience_verified": True,
    }
