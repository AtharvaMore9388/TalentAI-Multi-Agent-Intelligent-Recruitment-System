import asyncio
import sys

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

from agents.dynamic_pipeline import run_dynamic_recruitment_pipeline


jd = """
Role: Python Backend Engineer
Company: AI Labs
Experience: 0-2 years of experience
Requirements / Mandatory:
- Python
- SQL
- Django
- Flask
- REST APIs
Preferred:
- PyTorch
- TensorFlow
- Scikit-learn
- Pandas
- NumPy
- Docker
"""

aarav = """
Aarav Gupta
Email: aarav.gupta@example.com
Summary: Software Developer Intern with 6 months of internship experience.
Skills: Python, SQL, Django, Flask, REST APIs, Git
Internship Experience:
Software Intern at ABC Tech (6 months)
- Developed REST APIs with Django and Flask
- Wrote SQL queries and Python scripts
Education: B.Tech CSE (2020-2024)
"""

priya = """
Priya Patel
Email: priya.patel@example.com
Summary: Backend enthusiast. Completed a 4-month internship at StartCo.
Skills: Python, SQL, Django, REST APIs
Internship Experience:
Web Dev Intern at StartCo (4 months)
- Built backend endpoints using Python and Django
- Managed SQL database
Education: B.Tech IT (2020-2024)
"""

rohan = """
Rohan Verma
Email: rohan.verma@example.com
Summary: Software Engineer with 1.5 years of experience in backend development.
Skills: Python, SQL, Django, Flask, REST APIs, Docker, Pandas
Experience:
Software Engineer at InnovateTech (1.5 years)
- Built scalable web APIs with Django, Flask, and REST APIs
- Automated database pipelines with SQL and Python
Education: B.E. Computer Engineering, 2022
"""

sneha = """
Sneha Kulkarni
Email: sneha.kulkarni@example.com
Summary: Recent Computer Science graduate with no professional experience. Passionate about machine learning and data analysis.
Skills: Python, PyTorch, TensorFlow, Pandas, NumPy, Scikit-learn
Projects:
- Deep Learning Image Classification using PyTorch and TensorFlow
Education: B.Tech Computer Science (2020-2024)
"""

async def main():
    last_dossier = None
    messages = []
    async for msg, dossier in run_dynamic_recruitment_pipeline(jd, [aarav, priya, rohan, sneha], top_n=2):
        messages.append(msg)
        if dossier:
            last_dossier = dossier

    print("=== PIPELINE TRACE MESSAGES ===")
    for m in messages:
        if m.role in ("decision", "conflict", "replan", "result"):
            print(f"[{m.agent} ({m.role})]: {m.content[:90]}...")

    print("\n=== FINAL CANDIDATE DISPOSITIONS ===")
    for c in last_dossier["approved_candidates"]:
        print(f"APPROVED: {c['name']} | Score: {c['score']}/100 | Exp: {c['experience']} | Notes: {c['evaluation_notes']}")
    for c in last_dossier["conditional_candidates"]:
        print(f"CONDITIONAL: {c['name']} | Score: {c['score']}/100 | Exp: {c['experience']} | Missing: {c['missing_mandatory']} | Notes: {c['evaluation_notes']}")
    for c in last_dossier["rejected_candidates"]:
        print(f"REJECTED: {c['name']} | Score: {c['score']}/100 | Exp: {c['experience']} | Missing: {c['missing_mandatory']} | Notes: {c['evaluation_notes']}")

    print("\n=== FINAL PIPELINE COUNTS ===")
    summary = last_dossier["evaluation_summary"]
    for k, v in summary.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    asyncio.run(main())
