"""
Generate separate submission PDFs for AI CA3:
1. docs/Project_Synopsis.pdf (Problem, Solution, Target User, Scope Evolution)
2. docs/Design_Document.pdf (Architecture, Agent Roles, Orchestration Pattern, Tech Choices)
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, Preformatted
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, doc_title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.doc_title = doc_title
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8.5)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, f"TalentAI -- {self.doc_title}")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

        # Footer (all pages)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 34, page_str)
        self.drawString(54, 34, "Continuous Assessment 3 (AI CA3) -- Submission Deliverable")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 46, 558, 46)
        self.restoreState()


def get_common_styles():
    styles = getSampleStyleSheet()
    primary_color = colors.HexColor("#1E3A8A")  # Deep Navy
    secondary_color = colors.HexColor("#0F766E") # Teal
    dark_neutral = colors.HexColor("#0F172A")
    body_neutral = colors.HexColor("#334155")

    return {
        'primary': primary_color,
        'secondary': secondary_color,
        'title': ParagraphStyle(
            'DocTitle', parent=styles['Normal'],
            fontName='Helvetica-Bold', fontSize=22, leading=26,
            textColor=primary_color, spaceAfter=4
        ),
        'subtitle': ParagraphStyle(
            'DocSubtitle', parent=styles['Normal'],
            fontName='Helvetica', fontSize=11, leading=15,
            textColor=colors.HexColor("#475569"), spaceAfter=8
        ),
        'meta': ParagraphStyle(
            'DocMeta', parent=styles['Normal'],
            fontName='Helvetica-Bold', fontSize=8.5, leading=12,
            textColor=secondary_color
        ),
        'h1': ParagraphStyle(
            'H1', parent=styles['Normal'],
            fontName='Helvetica-Bold', fontSize=13.5, leading=17,
            textColor=primary_color, spaceBefore=12, spaceAfter=5,
            keepWithNext=True
        ),
        'h2': ParagraphStyle(
            'H2', parent=styles['Normal'],
            fontName='Helvetica-Bold', fontSize=10.5, leading=14,
            textColor=colors.HexColor("#1E293B"), spaceBefore=9, spaceAfter=3,
            keepWithNext=True
        ),
        'body': ParagraphStyle(
            'Body', parent=styles['Normal'],
            fontName='Helvetica', fontSize=9, leading=13.5,
            textColor=body_neutral, spaceAfter=6
        ),
        'bullet': ParagraphStyle(
            'BulletText', parent=styles['Normal'],
            fontName='Helvetica', fontSize=9, leading=13,
            textColor=body_neutral, leftIndent=12, firstLineIndent=-8, spaceAfter=3
        ),
        'th': ParagraphStyle(
            'TH', parent=styles['Normal'],
            fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white
        ),
        'td': ParagraphStyle(
            'TD', parent=styles['Normal'],
            fontName='Helvetica', fontSize=7.5, leading=10, textColor=dark_neutral
        ),
        'td_bold': ParagraphStyle(
            'TDBold', parent=styles['Normal'],
            fontName='Helvetica-Bold', fontSize=7.5, leading=10, textColor=primary_color
        ),
        'code': ParagraphStyle(
            'CodeStyle', parent=styles['Normal'],
            fontName='Courier', fontSize=6.8, leading=8.8,
            textColor=colors.HexColor("#1E293B"),
        )
    }


# =============================================================================
# 1. BUILD PROJECT SYNOPSIS PDF
# =============================================================================
def build_project_synopsis_pdf(out_path):
    st = get_common_styles()
    doc = SimpleDocTemplate(
        out_path, pagesize=letter,
        leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54
    )
    story = []

    # Title & Header
    story.append(Paragraph("TalentAI: Multi-Agent Intelligent Recruitment System", st['title']))
    story.append(Paragraph("Project Synopsis -- Problem, Solution, Target User &amp; Scope", st['subtitle']))
    story.append(Paragraph("<b>Course:</b> Continuous Assessment 3 (AI CA3) &nbsp;|&nbsp; <b>Deliverable:</b> Project Synopsis (PDF) &nbsp;|&nbsp; <b>Status:</b> Approved", st['meta']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=st['primary'], spaceBefore=5, spaceAfter=12))

    # Section 1: Problem Statement
    story.append(Paragraph("1. Problem Statement", st['h1']))
    story.append(Paragraph(
        "Modern corporate recruitment and candidate screening workflows are severely bottlenecked by large volumes of unstructured applicant data. Conventional Applicant Tracking Systems (ATS) rely primarily on rigid keyword matching, which produces two critical failure modes:",
        st['body']
    ))
    story.append(Paragraph("&bull; <b>High False Positives:</b> Unqualified candidates often engage in 'keyword stuffing' to artificially game ATS algorithms, inundating recruiters with applicants who lack demonstrable technical competency.", st['bullet']))
    story.append(Paragraph("&bull; <b>High False Negatives:</b> Exceptionally qualified candidates are discarded simply because they describe equivalent skills using alternate phrasing, modern synonyms, or specialized acronyms (e.g., 'k8s' vs. 'Kubernetes').", st['bullet']))
    story.append(Paragraph("&bull; <b>Cognitive Fatigue &amp; Inconsistent Evaluation:</b> Human recruiters manually reviewing hundreds of multi-page resumes face extreme fatigue, leading to subjective, non-standardized qualification bars and multi-week turnaround times.", st['bullet']))
    story.append(Spacer(1, 4))

    # Section 2: Proposed Solution
    story.append(Paragraph("2. Proposed Solution: The TalentAI Platform", st['h1']))
    story.append(Paragraph(
        "<b>TalentAI</b> is an autonomous multi-agent recruitment and candidate ranking platform that transforms technical hiring into a transparent, deterministic, and agentic workflow. Rather than delegating recruitment to a single prompt, TalentAI distributes operations across six specialized, collaborating agents:",
        st['body']
    ))
    story.append(Paragraph("&bull; <b>Orchestrator Agent:</b> Coordinates execution flow, maintains canonical pipeline state, detects inter-agent conflicts, and triggers adaptive replanning.", st['bullet']))
    story.append(Paragraph("&bull; <b>Job Analysis Agent:</b> Decomposes unstructured job descriptions into non-negotiable mandatory skills, preferred qualifications, and minimum experience thresholds.", st['bullet']))
    story.append(Paragraph("&bull; <b>Resume Analysis Agent:</b> Parses unstructured CVs in parallel, validates technical competencies, and indexes dense embeddings into ChromaDB vector space.", st['bullet']))
    story.append(Paragraph("&bull; <b>Matching &amp; Ranking Agent:</b> Executes semantic RAG retrieval and computes composite match scores (Mandatory 60%, Preferred 30%, Experience 10%).", st['bullet']))
    story.append(Paragraph("&bull; <b>Candidate Evaluation Agent (Dual-Stage Hybrid Critic):</b> Independently challenges shortlists by coupling deterministic rule checks (100% mandatory compliance) with qualitative LLM auditing.", st['bullet']))
    story.append(Paragraph("&bull; <b>Recruitment Communication Agent:</b> Crafts bespoke interview invitations highlighting specific achievements for approved candidates, and constructive rejection notices.", st['bullet']))
    story.append(Spacer(1, 4))

    # Section 3: Target Users
    story.append(Paragraph("3. Target User Persona", st['h1']))
    story.append(Paragraph(
        "TalentAI is engineered for <b>Corporate Talent Acquisition Teams, Technical Recruiters, Engineering Hiring Managers, and High-Growth SMEs</b>. These users manage technical job openings with high applicant-to-hire ratios and require rapid, bias-free, and verifiable first-round candidate shortlisting with explainable audit trails.",
        st['body']
    ))
    story.append(Spacer(1, 4))

    # Section 4: Project Scope & CA2 Scope Evolution
    story.append(Paragraph("4. Project Scope &amp; CA2 Evolution Notes", st['h1']))
    story.append(Paragraph(
        "<b>Consistency with Approved CA2 Description:</b> TalentAI fulfills the approved CA2 objective of automating candidate screening and ranking via specialized agents, semantic RAG retrieval, and structured scoring.",
        st['body']
    ))
    story.append(Paragraph(
        "<b>Explicit Scope Enhancements during CA3 Realization:</b><br/>"
        "In response to academic review comments and to demonstrate genuine multi-agent autonomy, the scope was deliberately upgraded in three key dimensions:",
        st['body']
    ))
    story.append(Paragraph("&bull; <b>Dual-Stage Hybrid Critic Architecture:</b> Upgraded the Evaluation Agent from a superficial LLM check to a dual-stage system: Stage 1 deterministically validates that 100% of non-negotiable mandatory criteria are satisfied in Python code; Stage 2 applies Groq LLaMA-3.3-70B for nuanced architectural and leadership review.", st['bullet']))
    story.append(Paragraph("&bull; <b>Dynamic Replanning &amp; Conflict Arbitration:</b> Integrated an autonomous negotiation loop. When the Evaluation Critic rejects a candidate, the Orchestrator executes strategic replanning -- selectively relaxing preferred requirements while strictly holding mandatory requirements 100% inviolable, with a bounded ceiling of 2 rounds.", st['bullet']))
    story.append(Paragraph("&bull; <b>Real-Time Telemetry Streaming:</b> Built a full-stack telemetry interface utilizing FastAPI Server-Sent Events (SSE) and Next.js 14, streaming chronological agent reasoning steps directly to an interactive recruiter dashboard.", st['bullet']))

    def canvas_maker(*args, **kwargs):
        return NumberedCanvas("Project Synopsis", *args, **kwargs)

    doc.build(story, canvasmaker=canvas_maker)
    print(f"Generated: {out_path}")


# =============================================================================
# 2. BUILD DESIGN DOCUMENT PDF
# =============================================================================
def build_design_document_pdf(out_path):
    st = get_common_styles()
    doc = SimpleDocTemplate(
        out_path, pagesize=letter,
        leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54
    )
    story = []

    # Title & Header
    story.append(Paragraph("TalentAI: Multi-Agent Intelligent Recruitment System", st['title']))
    story.append(Paragraph("Technical Design Document -- Architecture, Roles, Coordination &amp; Tech Choices", st['subtitle']))
    story.append(Paragraph("<b>Course:</b> Continuous Assessment 3 (AI CA3) &nbsp;|&nbsp; <b>Deliverable:</b> Design Document (PDF) &nbsp;|&nbsp; <b>Status:</b> Approved Architecture", st['meta']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=st['primary'], spaceBefore=5, spaceAfter=12))

    # 1. Architecture Diagram
    story.append(Paragraph("1. System Architecture &amp; Communication Topology", st['h1']))
    story.append(Paragraph(
        "TalentAI implements a <b>Centralized Orchestrator-Worker topology</b> with an independent quality evaluation gate. Inter-agent communication flows deterministically through the central Orchestrator, ensuring state consistency and bounded execution.",
        st['body']
    ))

    arch_diagram_text = (
        "+-----------------------------------------------------------------------------------------+\n"
        "|                                   ORCHESTRATOR AGENT                                    |\n"
        "|   * State Management (RecruitmentState)        * Inter-Agent Delegation & Telemetry     |\n"
        "|   * Conflict Detection & Arbitration           * Dynamic Replanning (Max 2 Rounds)      |\n"
        "+--------------------------------------------+--------------------------------------------+\n"
        "                     |                       |                       |\n"
        "       [1. Parse JD] |         [2. Parse CVs]|          [3. Rank]    |\n"
        "                     v                       v                       v\n"
        "+-------------------------+  +-------------------------+  +-------------------------------+\n"
        "|   JOB ANALYSIS AGENT    |  |  RESUME ANALYSIS AGENT  |  |   MATCHING & RANKING AGENT    |\n"
        "| - Extracts Mandatory &  |  | - Extracts Skills, Exp, |  | - ChromaDB Vector RAG Search  |\n"
        "|   Preferred Skills      |  |   Education & Contact   |  | - Deterministic Scoring Tool  |\n"
        "| - Returns JobDescription|  | - Ingests to ChromaDB   |  |   (Mandatory + Preferred)     |\n"
        "+-------------------------+  +-------------------------+  +---------------+---------------+\n"
        "                                                                          | Proposed Shortlist\n"
        "                                                                          v\n"
        "                                                          +-------------------------------+\n"
        "                                                          |   CANDIDATE EVALUATION AGENT  |\n"
        "                                                          |  (Independent Dual-Stage Critic)|\n"
        "                                                          |  Stage 1: Hard Rule Engine    |\n"
        "                                                          |  Stage 2: LLM Qualitative Bar |\n"
        "                                                          +---------------+---------------+\n"
        "                                                                          |\n"
        "                              +-------------------------------------------+-------------------+\n"
        "                              | REJECT (Conflict Signal)                                      | APPROVE\n"
        "                              v                                                               v\n"
        "        +-------------------------------------------+                     +-------------------+\n"
        "        |         ORCHESTRATOR REPLAN ENGINE        |                     |   COMMUNICATION   |\n"
        "        | - Relax preferred criteria only           |                     |       AGENT       |\n"
        "        | - Preserve 100% of mandatory requirements |                     | - Tailored Invites|\n"
        "        | - Re-invoke Matching Agent (Round <= 2)   |                     | - Constructive    |\n"
        "        +---------------------+---------------------+                     |   Rejection Notes |\n"
        "                              | Re-match Directive                        +-------------------+\n"
        "                              +---------------------------------------^"
    )
    story.append(Preformatted(arch_diagram_text, st['code']))
    story.append(Spacer(1, 10))

    # 2. Agent Roles and Responsibilities
    story.append(PageBreak())
    story.append(Paragraph("2. Agent Roles and Responsibilities", st['h1']))
    story.append(Paragraph(
        "Each agent executes a defined single-responsibility role with structured Pydantic inputs and outputs:",
        st['body']
    ))

    agent_data = [
        [
            Paragraph("Agent", st['th']),
            Paragraph("Role & Responsibilities", st['th']),
            Paragraph("Input / Output", st['th']),
            Paragraph("Tools & Tech", st['th'])
        ],
        [
            Paragraph("<b>1. Orchestrator Agent</b>", st['td_bold']),
            Paragraph("Central coordinator. Dispatches tasks across agents, maintains canonical state, detects Evaluation conflicts, and triggers dynamic replanning with bounded iterations (max 2).", st['td']),
            Paragraph("<b>In:</b> RecruitmentRequest<br/><b>Out:</b> RecruitmentState, SSE Stream", st['td']),
            Paragraph("CrewAI Agent, State Machine, Groq LLaMA-3.3-70B", st['td'])
        ],
        [
            Paragraph("<b>2. Job Analysis Agent</b>", st['td_bold']),
            Paragraph("Parses raw job postings into non-negotiable mandatory skills, preferred qualifications, experience bounds, role title, and company profile.", st['td']),
            Paragraph("<b>In:</b> Raw JD string<br/><b>Out:</b> JobDescription Model", st['td']),
            Paragraph("Groq LLaMA-3.3-70B (JSON entity extraction)", st['td'])
        ],
        [
            Paragraph("<b>3. Resume Analysis Agent</b>", st['td_bold']),
            Paragraph("Parses candidate resumes in parallel. Extracts verified technical skills, professional vs. internship experience, and indexes dense vectors into ChromaDB.", st['td']),
            Paragraph("<b>In:</b> Raw Resumes list<br/><b>Out:</b> Candidate Model list", st['td']),
            Paragraph("Groq LLaMA-3.1-8B-Instant, ChromaDB Ingestion", st['td'])
        ],
        [
            Paragraph("<b>4. Matching & Ranking Agent</b>", st['td_bold']),
            Paragraph("Executes semantic vector search across candidate embeddings and applies composite scoring formula (Mandatory 60%, Preferred 30%, Experience 10%). Supports relaxed rerun mode.", st['td']),
            Paragraph("<b>In:</b> JobDescription, Candidates<br/><b>Out:</b> MatchedCandidate list", st['td']),
            Paragraph("RAGRetrievalTool (ChromaDB), ScoringTool", st['td'])
        ],
        [
            Paragraph("<b>5. Candidate Evaluation Agent</b>", st['td_bold']),
            Paragraph("Independent quality gate. Implements a Dual-Stage Hybrid Critic: Stage 1 deterministically checks 100% mandatory compliance; Stage 2 performs qualitative audit. Emits APPROVE or REJECT.", st['td']),
            Paragraph("<b>In:</b> Shortlist, JobDescription<br/><b>Out:</b> Verdict, Audit Notes", st['td']),
            Paragraph("Independent LLM Call, Deterministic Rule Engine", st['td'])
        ],
        [
            Paragraph("<b>6. Communication Agent</b>", st['td_bold']),
            Paragraph("Generates personalized, professional interview invitations highlighting candidate achievements, and respectful, constructive feedback notices for non-selected applicants.", st['td']),
            Paragraph("<b>In:</b> Evaluated Shortlist<br/><b>Out:</b> Formatted Outreach Texts", st['td']),
            Paragraph("Groq LLaMA-3.3-70B (Generative NLG)", st['td'])
        ],
    ]

    t_agents = Table(agent_data, colWidths=[95, 175, 110, 124])
    t_agents.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), st['primary']),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_agents)
    story.append(Spacer(1, 10))

    # 3. Orchestration Pattern
    story.append(Paragraph("3. Orchestration Pattern &amp; Conflict Resolution Protocol", st['h1']))
    story.append(Paragraph(
        "<b>Pattern: Centralized Orchestrator-Worker with Adversarial Feedback Loop</b><br/>"
        "A centralized Orchestrator-Worker pattern was selected over peer-to-peer (P2P) for three foundational reasons: (1) <i>Single Source of Truth:</i> Centralized state ensures candidate records remain synchronized; (2) <i>Deadlock Elimination:</i> Unbounded negotiation cycles between agents are strictly bounded by <code>MAX_REPLAN_ROUNDS = 2</code>; (3) <i>Audit Compliance:</i> All decisions and conflict logs are serialized sequentially for recruiter review.",
        st['body']
    ))
    story.append(Paragraph("<b>Conflict Resolution Protocol:</b>", st['h2']))
    story.append(Paragraph("&bull; <b>Adversarial Quality Gate:</b> If a candidate (e.g. Arjun Mehta) achieves high vector similarity but lacks mandatory skills (missing TypeScript and having only 3 years experience against a 4+ year requirement), the Evaluation Agent issues an explicit <b>REJECT</b> conflict signal.", st['bullet']))
    story.append(Paragraph("&bull; <b>Orchestrator Strategic Decision:</b> The Orchestrator receives the rejection and executes <code>orchestrator_decide_replan()</code> to select from: <code>replan_relaxed</code>, <code>replan_strict</code>, <code>escalate</code>, or <code>accept_partial</code>.", st['bullet']))
    story.append(Paragraph("&bull; <b>Strict Mandatory Preservation Rule:</b> Under <code>replan_relaxed</code>, preferred criteria (AWS, GraphQL) are relaxed, but <b>mandatory criteria remain 100% non-negotiable</b>.", st['bullet']))
    story.append(Paragraph("&bull; <b>Bounded Execution:</b> Maximum 2 replan rounds prevent infinite looping.", st['bullet']))
    story.append(Spacer(1, 10))

    # 4. Technology Choices
    story.append(PageBreak())
    story.append(Paragraph("4. Technology Choices &amp; Architectural Justifications", st['h1']))
    story.append(Paragraph(
        "Each framework and library was selected to optimize latency, deterministic reliability, and local zero-cost execution:",
        st['body']
    ))

    tech_data = [
        [
            Paragraph("Component", st['th']),
            Paragraph("Technology Selected", st['th']),
            Paragraph("Version / Spec", st['th']),
            Paragraph("Engineering Justification", st['th'])
        ],
        [
            Paragraph("Agent Framework", st['td_bold']),
            Paragraph("CrewAI", st['td']),
            Paragraph("1.15.x", st['td']),
            Paragraph("Native Agent, Task, and Crew abstractions; clean tool bindings; supports structured Pydantic schemas and deterministic multi-agent workflows.", st['td'])
        ],
        [
            Paragraph("Primary LLM", st['td_bold']),
            Paragraph("Groq LLaMA-3.3-70B", st['td']),
            Paragraph("70B Versatile", st['td']),
            Paragraph("Sub-second inference (&lt;800ms) on Groq LPUs prevents timeouts during multi-turn orchestration. High reasoning quality for JD extraction and qualitative auditing.", st['td'])
        ],
        [
            Paragraph("Fast Parser LLM", st['td_bold']),
            Paragraph("Groq LLaMA-3.1-8B", st['td']),
            Paragraph("8B Instant", st['td']),
            Paragraph("High-throughput, cost-effective model for bulk resume entity extraction without sacrificing JSON structured accuracy.", st['td'])
        ],
        [
            Paragraph("Vector Database", st['td_bold']),
            Paragraph("ChromaDB", st['td']),
            Paragraph("0.5.x / 1.x", st['td']),
            Paragraph("In-process vector store with zero cloud latency, zero external API costs, local persistence, and native cosine similarity retrieval.", st['td'])
        ],
        [
            Paragraph("Embedding Model", st['td_bold']),
            Paragraph("sentence-transformers", st['td']),
            Paragraph("all-MiniLM-L6-v2 (384-d)", st['td']),
            Paragraph("Lightweight local embeddings capturing semantic equivalence between resume phrasing and job specifications.", st['td'])
        ],
        [
            Paragraph("Backend API", st['td_bold']),
            Paragraph("FastAPI", st['td']),
            Paragraph("0.115.x", st['td']),
            Paragraph("Asynchronous event loop, native Server-Sent Events (SSE) streaming for real-time agent telemetry, and native Pydantic schema validation.", st['td'])
        ],
        [
            Paragraph("Frontend UI", st['td_bold']),
            Paragraph("Next.js 14", st['td']),
            Paragraph("App Router / TS", st['td']),
            Paragraph("Modern reactive interface, real-time EventSource telemetry streaming, interactive candidate review studio, and side-by-side match breakdown.", st['td'])
        ]
    ]

    t_tech = Table(tech_data, colWidths=[90, 110, 80, 224])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), st['primary']),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_tech)

    def canvas_maker(*args, **kwargs):
        return NumberedCanvas("Design Document", *args, **kwargs)

    doc.build(story, canvasmaker=canvas_maker)
    print(f"Generated: {out_path}")


if __name__ == "__main__":
    base_docs = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))
    build_project_synopsis_pdf(os.path.join(base_docs, "Project_Synopsis.pdf"))
    build_design_document_pdf(os.path.join(base_docs, "Design_Document.pdf"))
