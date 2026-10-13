"""
TalentAI — Recruitment Communication Agent
Generates personalized interview invitations and rejection notices.
"""
from __future__ import annotations
from crewai import Agent, Task, Crew
from lib.models import JobDescription, MatchedCandidate, AgentMessage
from datetime import datetime, timezone


def get_communication_agent(llm) -> Agent:
    return Agent(
        role="Recruitment Communication Specialist",
        goal=(
            "Craft professional, personalized recruitment communications: "
            "interview invitations for shortlisted candidates and constructive "
            "rejection notices for those not selected."
        ),
        backstory=(
            "You are a senior recruitment communications expert known for writing "
            "warm, professional, and personalized messages. You believe every candidate "
            "deserves respectful communication regardless of outcome. "
            "Your messages are concise, specific, and always include next steps."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


def generate_communications(
    job: JobDescription,
    approved: list[MatchedCandidate],
    rejected: list[MatchedCandidate],
    llm,
) -> tuple[list[str], AgentMessage]:
    """
    Generate interview invitations for approved candidates
    and rejection notices for rejected candidates.
    """
    agent = get_communication_agent(llm)
    communications = []

    # Generate interview invitations
    for mc in approved:
        task = Task(
            description=(
                f"Write a professional interview invitation email.\n\n"
                f"Candidate: {mc.candidate.name}\n"
                f"Email: {mc.candidate.email}\n"
                f"Role: {job.title} at {job.company}\n"
                f"Why selected: Strong match on {mc.matched_mandatory} "
                f"with {mc.candidate.experience_years} years experience\n"
                f"Match Score: {mc.match_score}/100\n\n"
                "Write a warm, professional interview invitation. Include:\n"
                "- Personalized opening addressing the candidate by name\n"
                "- Mention specific skills that impressed us\n"
                "- Clear next steps (schedule a 30-min call)\n"
                "- Professional closing\n"
                "Keep it under 200 words."
            ),
            expected_output="A professional interview invitation email (under 200 words)",
            agent=agent,
        )
        crew = Crew(agents=[agent], tasks=[task], verbose=False)
        result = crew.kickoff()
        comm = f"📧 INTERVIEW INVITATION — {mc.candidate.name} ({mc.candidate.email})\n{str(result)}"
        communications.append(comm)

    # Generate rejection notices
    for mc in rejected:
        task = Task(
            description=(
                f"Write a respectful rejection notice email.\n\n"
                f"Candidate: {mc.candidate.name}\n"
                f"Email: {mc.candidate.email}\n"
                f"Role: {job.title} at {job.company}\n"
                f"Reason (internal, do not expose score): Profile did not fully match mandatory requirements\n\n"
                "Write a warm, professional rejection notice. Include:\n"
                "- Personalized opening\n"
                "- Thank them for their interest\n"
                "- Encourage future applications\n"
                "- Do NOT mention specific missing skills or scores\n"
                "Keep it under 120 words."
            ),
            expected_output="A professional, respectful rejection email (under 120 words)",
            agent=agent,
        )
        crew = Crew(agents=[agent], tasks=[task], verbose=False)
        result = crew.kickoff()
        comm = f"📧 REJECTION NOTICE — {mc.candidate.name} ({mc.candidate.email})\n{str(result)}"
        communications.append(comm)

    total_inv = len(approved)
    total_rej = len(rejected)
    msg = AgentMessage(
        agent="CommunicationAgent",
        role="result",
        content=(
            f"Generated {total_inv} interview invitation(s) and {total_rej} rejection notice(s) "
            f"for the '{job.title}' role at {job.company}."
        ),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    return communications, msg
