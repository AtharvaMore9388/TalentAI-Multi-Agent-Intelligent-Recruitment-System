"""
Generate the TalentAI Design Document PDF for AI CA3.
Uses ReportLab to build a professional, publication-quality PDF.
"""
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Preformatted
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
            self.drawString(54, 750, "TalentAI -- Multi-Agent Intelligent Recruitment System | Design Specification")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

        # Footer (all pages)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 34, page_str)
        self.drawString(54, 34, "Continuous Assessment 3 (AI CA3) -- Design Deliverable")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 46, 558, 46)
        self.restoreState()


def build_pdf(filename="TalentAI_Design_Document.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    primary_color = colors.HexColor("#1E3A8A")  # Deep Navy
    secondary_color = colors.HexColor("#0F766E") # Dark Teal
    dark_neutral = colors.HexColor("#0F172A")
    body_neutral = colors.HexColor("#334155")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=primary_color,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#475569"),
        spaceAfter=10
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=secondary_color
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=17,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=9,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=body_neutral,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )

    table_header = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    table_cell = ParagraphStyle(
        'TD',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=dark_neutral
    )

    table_cell_bold = ParagraphStyle(
        'TDBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=primary_color
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7,
        leading=9.2,
        textColor=colors.HexColor("#1E293B"),
    )

    story = []

    # ─────────────────────────────────────────────────────────────────────────────
    # COVER / HEADER & SECTION 1
    # ─────────────────────────────────────────────────────────────────────────────
    story.append(Paragraph("TalentAI: Multi-Agent Intelligent Recruitment System", title_style))
    story.append(Paragraph("System Architecture, Design Document &amp; Input/Output Specification", subtitle_style))
    
    meta_text = "<b>Course:</b> Continuous Assessment 3 (AI CA3) &nbsp;|&nbsp; <b>Deliverables:</b> Project Synopsis, Design Document, Input Definition, Output Definition &nbsp;|&nbsp; <b>Status:</b> Production Ready"
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=4, spaceAfter=12))

    # SECTION 1: PROJECT SYNOPSIS
    story.append(Paragraph("1. Project Synopsis", h1_style))
    story.append(Paragraph(
        "<b>The Problem:</b> Modern recruitment pipelines and traditional Applicant Tracking Systems (ATS) are fundamentally hindered by high volumes of unstructured candidate documentation. Standard keyword-based ATS filtering suffers from catastrophic error modes: high false-positive rates caused by unqualified candidates 'stuffing' resumes with buzzwords, and high false-negative rates where qualified applicants are discarded simply for using alternative phrasing or synonyms. Furthermore, human talent acquisition specialists experience severe cognitive fatigue when screening hundreds of multi-page resumes against rapidly evolving technical criteria, introducing subjective bias, delays, and inconsistent qualification bars.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Our Solution:</b> <b>TalentAI</b> is an autonomous multi-agent recruitment and candidate ranking platform that transforms technical hiring into a transparent, deterministic, and agentic workflow. Rather than relying on a single fallible prompt, TalentAI partitions the hiring pipeline across six specialized agents: Orchestrator, Job Analysis Agent, Resume Analysis Agent, Matching &amp; Ranking Agent, Candidate Evaluation Agent (Dual-Stage Hybrid Critic), and Recruitment Communication Agent. The system pairs Retrieval-Augmented Generation (RAG) using dense vector embeddings (sentence-transformers <i>all-MiniLM-L6-v2</i>) in ChromaDB with deterministic requirement verification. Most critically, TalentAI demonstrates authentic agentic behavior via inter-agent conflict resolution: when the independent Evaluation Critic identifies disqualifying skill deficiencies in a proposed shortlist, the Orchestrator initiates dynamic replanning -- selectively relaxing secondary preferred qualifications while strictly enforcing 100% of non-negotiable mandatory skills.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Target Users &amp; Scope Evolution (matching approved CA2 project description):</b> The platform is tailored for corporate talent acquisition teams, technical recruiters, engineering hiring managers, and small-to-medium enterprises requiring rigorous first-round technical screening.<br/>"
        "<i>Scope Evolution Note:</i> In the approved CA2 project proposal, the system was originally planned as a linear single-pass retrieval pipeline with heuristic scoring. During CA3 implementation, the architecture was intentionally expanded to resolve reviewer feedback regarding naive keyword matching: (1) we introduced an independent <b>Dual-Stage Hybrid Critic</b> in the Evaluation Agent combining deterministic python verification with LLM qualitative auditing; (2) we implemented <b>Dynamic Replanning and Conflict Reconciliation</b> in the central Orchestrator with bounded iterations to prevent infinite loops; and (3) we developed a real-time telemetry streaming interface via FastAPI Server-Sent Events (SSE) and Next.js 14 to provide transparent audit trails of multi-agent deliberation.",
        body_style
    ))
    
    # ─────────────────────────────────────────────────────────────────────────────
    # SECTION 2: DESIGN DOCUMENT
    # ─────────────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("2. Design Document", h1_style))
    
    # 2.1 Architecture Diagram
    story.append(Paragraph("2.1 System Architecture &amp; Agent Communication Topology", h2_style))
    story.append(Paragraph(
        "The architecture implements a centralized <b>Orchestrator-Worker</b> topology with an independent quality evaluation gate. Inter-agent communication flows deterministically through the central Orchestrator, ensuring state consistency and bounded execution.",
        body_style
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
    story.append(Preformatted(arch_diagram_text, code_style))
    story.append(Spacer(1, 8))

    # 2.2 Roles and Responsibilities
    story.append(Paragraph("2.2 Agent Roles and Responsibilities", h2_style))
    
    agent_data = [
        [
            Paragraph("Agent", table_header),
            Paragraph("Role & Responsibilities", table_header),
            Paragraph("Input / Output", table_header),
            Paragraph("Tools & Tech", table_header)
        ],
        [
            Paragraph("<b>1. Orchestrator Agent</b>", table_cell_bold),
            Paragraph("Central controller. Delegates pipeline stages, monitors inter-agent outputs, handles state transitions, reconciles Evaluation conflicts, and triggers dynamic replanning with bounded iterations (max 2).", table_cell),
            Paragraph("<b>In:</b> RecruitmentRequest<br/><b>Out:</b> RecruitmentState, SSE Stream", table_cell),
            Paragraph("CrewAI Agent, State Machine, Groq LLaMA-3.3-70B", table_cell)
        ],
        [
            Paragraph("<b>2. Job Analysis Agent</b>", table_cell_bold),
            Paragraph("Parses raw job descriptions to isolate non-negotiable mandatory skills, preferred qualifications, experience constraints, role title, and company profile into structured format.", table_cell),
            Paragraph("<b>In:</b> Raw JD string<br/><b>Out:</b> JobDescription Model", table_cell),
            Paragraph("Groq LLaMA-3.3-70B (JSON entity extraction)", table_cell)
        ],
        [
            Paragraph("<b>3. Resume Analysis Agent</b>", table_cell_bold),
            Paragraph("Parses candidate resumes in parallel. Extracts structured contact info, verified technical skills, professional vs. internship experience, and indexes document embeddings into vector space.", table_cell),
            Paragraph("<b>In:</b> Raw Resumes list<br/><b>Out:</b> Candidate Model list", table_cell),
            Paragraph("Groq LLaMA-3.1-8B-Instant, ChromaDB Ingestion", table_cell)
        ],
        [
            Paragraph("<b>4. Matching & Ranking Agent</b>", table_cell_bold),
            Paragraph("Executes semantic vector search across candidate embeddings and applies composite scoring formula (Mandatory 60%, Preferred 30%, Experience 10%). Supports relaxed-mode rerun upon replan.", table_cell),
            Paragraph("<b>In:</b> JobDescription, Candidates<br/><b>Out:</b> MatchedCandidate list", table_cell),
            Paragraph("RAGRetrievalTool (ChromaDB), ScoringTool", table_cell)
        ],
        [
            Paragraph("<b>5. Candidate Evaluation Agent</b>", table_cell_bold),
            Paragraph("Independent quality gate. Implements a Dual-Stage Hybrid Critic: Stage 1 deterministically checks 100% mandatory compliance; Stage 2 performs qualitative audit of engineering depth. Emits APPROVE or REJECT.", table_cell),
            Paragraph("<b>In:</b> Shortlist, JobDescription<br/><b>Out:</b> Verdict, Audit Notes", table_cell),
            Paragraph("Independent LLM Call, Deterministic Rule Engine", table_cell)
        ],
        [
            Paragraph("<b>6. Communication Agent</b>", table_cell_bold),
            Paragraph("Generates personalized, professional interview invitations highlighting specific achievements for approved candidates, and respectful, constructive feedback notices for non-selected applicants.", table_cell),
            Paragraph("<b>In:</b> Evaluated Shortlist<br/><b>Out:</b> Formatted Outreach Texts", table_cell),
            Paragraph("Groq LLaMA-3.3-70B (Generative NLG)", table_cell)
        ],
    ]

    t_agents = Table(agent_data, colWidths=[95, 175, 110, 124])
    t_agents.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
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
    
    # 2.3 Orchestration Pattern & 2.4 Tech Choices
    story.append(PageBreak())
    story.append(Paragraph("2.3 Orchestration Pattern: Centralized Orchestrator-Worker with Conflict Loop", h2_style))
    story.append(Paragraph(
        "TalentAI employs a <b>Centralized Orchestrator-Worker pattern</b> with an autonomous conflict resolution feedback loop. Direct peer-to-peer agent messaging was deliberately avoided to eliminate circular deliberation deadlocks and ensure that state updates remain atomic and deterministic.",
        body_style
    ))
    story.append(Paragraph("<b>Conflict Resolution Protocol:</b>", body_style))
    story.append(Paragraph("&bull; <b>Initial Proposed Shortlist:</b> The Matching Agent produces a top-N candidate shortlist based on semantic similarity and composite scoring.", bullet_style))
    story.append(Paragraph("&bull; <b>Adversarial Evaluation Gate:</b> The Candidate Evaluation Agent acts as an adversarial quality gate (critic). If a candidate possesses high semantic similarity but lacks mandatory skills (e.g., Arjun Mehta matching React/Node but lacking TypeScript and PostgreSQL), the Evaluation Agent issues an explicit <b>REJECT</b> conflict signal.", bullet_style))
    story.append(Paragraph("&bull; <b>Strategic Replanning Arbitration:</b> The Orchestrator receives the rejection and executes <code>orchestrator_decide_replan()</code>, selecting from four actions: <code>replan_relaxed</code>, <code>replan_strict</code>, <code>escalate</code>, or <code>accept_partial</code>.", bullet_style))
    story.append(Paragraph("&bull; <b>Strict Mandatory Preservation Rule:</b> Under this rule, the Orchestrator relaxes secondary preferred criteria (e.g. AWS, GraphQL) while holding mandatory requirements 100% inviolable, instructing the Matching Agent to search for qualified alternative candidates.", bullet_style))
    story.append(Paragraph("&bull; <b>Loop Boundedness:</b> Re-matching occurs with a hard ceiling of <b>MAX_REPLAN_ROUNDS = 2</b> to guarantee deterministic termination.", bullet_style))
    story.append(Spacer(1, 6))

    # 2.4 Technology & Framework Choices
    story.append(Paragraph("2.4 Technology Choices and Architectural Justifications", h2_style))
    
    tech_data = [
        [
            Paragraph("Component", table_header),
            Paragraph("Technology Selected", table_header),
            Paragraph("Version / Spec", table_header),
            Paragraph("Engineering Justification", table_header)
        ],
        [
            Paragraph("Agent Framework", table_cell_bold),
            Paragraph("CrewAI", table_cell),
            Paragraph("1.15.x", table_cell),
            Paragraph("Provides native Agent, Task, and Crew abstractions; clean tool binding; native support for structured output schemas and role-based execution.", table_cell)
        ],
        [
            Paragraph("Primary LLM", table_cell_bold),
            Paragraph("Groq LLaMA-3.3-70B", table_cell),
            Paragraph("70B Versatile", table_cell),
            Paragraph("Sub-second inference (&lt;800ms) on Groq LPUs avoids HTTP timeouts during multi-agent turns. Superior reasoning for JD extraction and qualitative auditing.", table_cell)
        ],
        [
            Paragraph("Fast Parser LLM", table_cell_bold),
            Paragraph("Groq LLaMA-3.1-8B", table_cell),
            Paragraph("8B Instant", table_cell),
            Paragraph("High-throughput, cost-effective extraction for bulk resume ingestion without sacrificing entity extraction accuracy.", table_cell)
        ],
        [
            Paragraph("Vector Database", table_cell_bold),
            Paragraph("ChromaDB", table_cell),
            Paragraph("0.5.x / 1.x", table_cell),
            Paragraph("Embedded local vector store with zero cloud latency, zero external API costs, local persistence, and native cosine similarity querying.", table_cell)
        ],
        [
            Paragraph("Embedding Model", table_cell_bold),
            Paragraph("sentence-transformers", table_cell),
            Paragraph("all-MiniLM-L6-v2 (384-d)", table_cell),
            Paragraph("Lightweight, runs locally on CPU/GPU, trained on 1B+ sentence pairs, captures semantic nuances between resume terminology and job specifications.", table_cell)
        ],
        [
            Paragraph("Backend API", table_cell_bold),
            Paragraph("FastAPI", table_cell),
            Paragraph("0.115.x", table_cell),
            Paragraph("Asynchronous event loop, native Server-Sent Events (SSE) streaming for real-time agent telemetry, and native Pydantic schema validation.", table_cell)
        ],
        [
            Paragraph("Frontend UI", table_cell_bold),
            Paragraph("Next.js 14", table_cell),
            Paragraph("App Router / TS", table_cell),
            Paragraph("Modern reactive interface, real-time SSE stream consumption, interactive candidate dossiers, and live multi-agent deliberation telemetry feed.", table_cell)
        ]
    ]

    t_tech = Table(tech_data, colWidths=[90, 110, 80, 224])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
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

    # ─────────────────────────────────────────────────────────────────────────────
    # SECTION 3: INPUT DEFINITION
    # ─────────────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("3. Input Definition", h1_style))
    story.append(Paragraph(
        "The TalentAI system accepts recruitment requests through the REST and SSE streaming endpoints (<code>POST /api/recruit</code> and <code>POST /api/recruit/stream</code>). The input format is strictly validated via Pydantic.",
        body_style
    ))
    
    story.append(Paragraph("3.1 Input Schema (RecruitmentRequest)", h2_style))
    input_schema_text = (
        "{\n"
        '  "$schema": "http://json-schema.org/draft-07/schema#",\n'
        '  "title": "RecruitmentRequest",\n'
        '  "type": "object",\n'
        '  "properties": {\n'
        '    "job_description": {\n'
        '      "type": "string",\n'
        '      "description": "Raw unformatted text of the job description (minimum 50 characters)."\n'
        '    },\n'
        '    "resumes": {\n'
        '      "type": "array",\n'
        '      "items": { "type": "string" },\n'
        '      "description": "List of raw unformatted candidate resume texts (minimum 1 resume)."\n'
        '    },\n'
        '    "top_n": {\n'
        '      "type": "integer",\n'
        '      "default": 5,\n'
        '      "minimum": 1,\n'
        '      "description": "Target number of top-matching candidates to shortlist."\n'
        '    }\n'
        '  },\n'
        '  "required": ["job_description", "resumes"]\n'
        "}"
    )
    story.append(Preformatted(input_schema_text, code_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("3.2 Real Sample Input (Production Scenario)", h2_style))
    sample_input_text = (
        "POST /api/recruit/stream HTTP/1.1\n"
        "Host: 127.0.0.1:8000\n"
        "Content-Type: application/json\n\n"
        "{\n"
        '  "job_description": "Senior Full Stack Engineer at TechNova Inc.\\nWe are seeking a Senior Full Stack Engineer with 4+ years experience. Must have: React, Node.js, TypeScript, PostgreSQL, and cloud infrastructure (AWS). Containerization with Docker and Kubernetes is required. Preferred: GraphQL, Redis, and microservices architecture.",\n'
        '  "resumes": [\n'
        '    "Kavya Reddy | kavya.reddy@email.com | 7 years exp\\nSKILLS: TypeScript, React, Node.js, PostgreSQL, Docker, Kubernetes (CKA), AWS Solutions Architect, GraphQL, Kafka.\\nEXPERIENCE: Lead Engineer at Razorpay (2020-Present), architected payment microservices.",\n'
        '    "Priya Sharma | priya.sharma@email.com | 6 years exp\\nSKILLS: React, Node.js, TypeScript, PostgreSQL, Docker, AWS (EC2, S3, RDS), Git, REST APIs.\\nEXPERIENCE: Senior Software Engineer at Infosys (2021-Present), built e-commerce platform for 500K users.",\n'
        '    "Arjun Mehta | arjun.mehta@email.com | 3 years exp\\nSKILLS: React, JavaScript, Node.js, Express, MySQL, basic PostgreSQL, Git, AWS basics.\\nEXPERIENCE: Junior Developer at StartupXYZ (2021-2023), frontend web components.",\n'
        '    "Aisha Patel | aisha.patel@email.com | 5 years exp\\nSKILLS: Python, FastAPI, PostgreSQL, AWS, Docker, Kubernetes, Microservices, REST APIs.\\nEXPERIENCE: Senior Backend Engineer at Google India (2022-Present), high-scale distributed systems."\n'
        '  ],\n'
        '  "top_n": 3\n'
        "}"
    )
    story.append(Preformatted(sample_input_text, code_style))

    # ─────────────────────────────────────────────────────────────────────────────
    # SECTION 4: OUTPUT DEFINITION
    # ─────────────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("4. Output Definition", h1_style))
    story.append(Paragraph(
        "TalentAI produces two complementary output formats: (1) a real-time event-driven <b>Server-Sent Events (SSE) telemetry stream</b> detailing each agent's decisions and conflict occurrences, and (2) a complete <b>RecruitmentResponse</b> containing the final recruitment state, candidate dossiers, eligibility audits, replan history, and generated communication drafts.",
        body_style
    ))

    story.append(Paragraph("4.1 Output Schema (RecruitmentResponse)", h2_style))
    output_schema_text = (
        "{\n"
        '  "title": "RecruitmentResponse",\n'
        '  "type": "object",\n'
        '  "properties": {\n'
        '    "state": {\n'
        '      "type": "object",\n'
        '      "properties": {\n'
        '        "job": { "$ref": "#/definitions/JobDescription" },\n'
        '        "candidates": { "type": "array", "items": { "$ref": "#/definitions/Candidate" } },\n'
        '        "shortlisted": { "type": "array", "items": { "$ref": "#/definitions/MatchedCandidate" } },\n'
        '        "evaluation_passed": { "type": "boolean" },\n'
        '        "replan_count": { "type": "integer" },\n'
        '        "relaxed_requirements": { "type": "boolean" },\n'
        '        "final_communications": { "type": "array", "items": { "type": "string" } },\n'
        '        "status": { "type": "string", "enum": ["pending", "running", "completed", "failed"] },\n'
        '        "final_status": { "type": "string", "enum": ["COMPLETED_SUCCESS", "COMPLETED_PARTIAL", "COMPLETED_NO_MATCH"] }\n'
        '      }\n'
        '    },\n'
        '    "execution_trace": {\n'
        '      "type": "array",\n'
        '      "items": {\n'
        '        "type": "object",\n'
        '        "properties": {\n'
        '          "agent": { "type": "string" },\n'
        '          "role": { "type": "string", "enum": ["action", "decision", "conflict", "replan", "result"] },\n'
        '          "content": { "type": "string" },\n'
        '          "timestamp": { "type": "string", "format": "date-time" }\n'
        '        }\n'
        '      }\n'
        '    }\n'
        '  }\n'
        "}"
    )
    story.append(Preformatted(output_schema_text, code_style))

    story.append(PageBreak())
    story.append(Paragraph("4.2 Real Sample Output (Resolved Multi-Agent Execution)", h2_style))
    sample_output_text = (
        "{\n"
        '  "state": {\n'
        '    "job": {\n'
        '      "id": "job-tech-01",\n'
        '      "title": "Senior Full Stack Engineer",\n'
        '      "company": "TechNova Inc.",\n'
        '      "mandatory_requirements": ["react", "node.js", "typescript", "postgresql", "docker", "kubernetes", "aws"],\n'
        '      "preferred_requirements": ["graphql", "redis", "microservices"],\n'
        '      "min_experience_years": 4.0\n'
        '    },\n'
        '    "shortlisted": [\n'
        '      {\n'
        '        "candidate": { "name": "Kavya Reddy", "email": "kavya.reddy@email.com", "experience_years": 7.0 },\n'
        '        "match_score": 90.0,\n'
        '        "matched_mandatory": ["react", "node.js", "typescript", "postgresql", "docker", "kubernetes", "aws"],\n'
        '        "missing_mandatory": [],\n'
        '        "matched_preferred": ["graphql", "microservices"],\n'
        '        "eligibility_status": "FULLY_ELIGIBLE",\n'
        '        "evaluation_notes": "Exceeds all criteria. CKA certified Kubernetes + AWS Architect. APPROVED by EvaluationAgent."\n'
        '      },\n'
        '      {\n'
        '        "candidate": { "name": "Priya Sharma", "email": "priya.sharma@email.com", "experience_years": 6.0 },\n'
        '        "match_score": 85.0,\n'
        '        "matched_mandatory": ["react", "node.js", "typescript", "postgresql", "docker", "aws"],\n'
        '        "missing_mandatory": [],\n'
        '        "matched_preferred": ["microservices"],\n'
        '        "eligibility_status": "FULLY_ELIGIBLE",\n'
        '        "evaluation_notes": "Solid enterprise full-stack engineer. Meets 100% of mandatory bar. APPROVED."\n'
        '      },\n'
        '      {\n'
        '        "candidate": { "name": "Aisha Patel", "email": "aisha.patel@email.com", "experience_years": 5.0 },\n'
        '        "match_score": 72.0,\n'
        '        "matched_mandatory": ["postgresql", "docker", "kubernetes", "aws"],\n'
        '        "missing_mandatory": [],\n'
        '        "matched_preferred": ["microservices"],\n'
        '        "eligibility_status": "CONDITIONALLY_ELIGIBLE",\n'
        '        "evaluation_notes": "Surfaced in Round 2 Replan after Orchestrator relaxed preferred criteria. Replaced rejected candidate Arjun Mehta."\n'
        '      }\n'
        '    ],\n'
        '    "evaluation_passed": true,\n'
        '    "replan_count": 1,\n'
        '    "relaxed_requirements": true,\n'
        '    "status": "completed",\n'
        '    "final_status": "COMPLETED_SUCCESS",\n'
        '    "final_communications": [\n'
        '      "Dear Kavya, We were thoroughly impressed by your 7 years of full-stack engineering and Kubernetes expertise at Razorpay. TechNova Inc. invites you to an initial architectural conversation for the Senior Full Stack Engineer role.",\n'
        '      "Dear Priya, Your 6 years of scalable React/Node.js enterprise development at Infosys stood out as an exceptional fit. We would like to schedule an introductory technical interview.",\n'
        '      "Dear Aisha, Your extensive distributed backend systems experience at Google India is an exciting match. We would love to discuss our Senior Platform Engineering opportunities."\n'
        '    ]\n'
        '  },\n'
        '  "execution_trace": [\n'
        '    { "agent": "Orchestrator", "role": "action", "content": "Pipeline initialized for 4 candidates.", "timestamp": "2026-10-21T18:40:00Z" },\n'
        '    { "agent": "JobAnalysisAgent", "role": "action", "content": "Extracted 7 mandatory and 3 preferred requirements.", "timestamp": "2026-10-21T18:40:02Z" },\n'
        '    { "agent": "MatchingAgent", "role": "action", "content": "Ranked candidates: Proposed Kavya (87.5), Priya (82.0), Arjun (41.0).", "timestamp": "2026-10-21T18:40:10Z" },\n'
        '    { "agent": "EvaluationAgent", "role": "conflict", "content": "CONFLICT: Shortlist REJECTED. Arjun Mehta critically lacks mandatory TypeScript, Docker, Kubernetes.", "timestamp": "2026-10-21T18:40:14Z" },\n'
        '    { "agent": "Orchestrator", "role": "replan", "content": "Dynamic Replan initiated: REPLAN_RELAXED. Relaxing secondary preferred skills while keeping mandatory requirements 100% strict.", "timestamp": "2026-10-21T18:40:18Z" },\n'
        '    { "agent": "MatchingAgent", "role": "replan", "content": "Re-ranking complete. Aisha Patel surfaced (72.0). Arjun Mehta removed.", "timestamp": "2026-10-21T18:40:22Z" },\n'
        '    { "agent": "EvaluationAgent", "role": "result", "content": "VERIFIED & APPROVED. Revised shortlist meets all mandatory qualifications.", "timestamp": "2026-10-21T18:40:26Z" },\n'
        '    { "agent": "CommunicationAgent", "role": "result", "content": "Bespoke interview invitation letters generated.", "timestamp": "2026-10-21T18:40:30Z" }\n'
        '  ]\n'
        "}"
    )
    story.append(Preformatted(sample_output_text, code_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated clean PDF at: {filename}")

if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(__file__), "..", "docs", "TalentAI_Design_Document.pdf")
    build_pdf(os.path.abspath(out_path))
