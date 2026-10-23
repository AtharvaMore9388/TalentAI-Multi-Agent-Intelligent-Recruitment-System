# TalentAI: Multi-Agent Intelligent Recruitment and Talent Matching System

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![CrewAI](https://img.shields.io/badge/Framework-CrewAI-purple.svg)](https://crewai.com)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js_14-black.svg)](https://nextjs.org)
[![Groq](https://img.shields.io/badge/LLM-Groq-orange.svg)](https://groq.com)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-yellow.svg)](https://chromadb.com)

## 🎯 Project Overview

**TalentAI** is a multi-agent AI recruitment platform that intelligently connects candidates and companies using specialized AI agents, Retrieval-Augmented Generation (RAG), semantic search, and a centralized orchestration mechanism.

The system consists of **6 collaborating AI agents**, including:
1. **Orchestrator Agent**: Coordinates agents, assigns tasks, manages outputs, resolves conflicts, and dynamically replans the recruitment workflow.
2. **Job Analysis Agent**: Extracts mandatory (non-negotiable) and preferred requirements from a job description.
3. **Resume Analysis Agent**: Parses unstructured candidate resumes into structured entities and indexes them into ChromaDB vector space.
4. **Matching and Ranking Agent**: Retrieves and ranks suitable candidates using semantic search and RAG-based scoring.
5. **Candidate Evaluation Agent**: Independently verifies the shortlisted candidates using a **Dual-Stage Hybrid Critic** and challenges the Matching Agent when mandatory skills or experience are missing.
6. **Recruitment Communication Agent**: Generates tailored interview invitations and actionable feedback.

### Key Capabilities
- **Genuine Critic Pattern**: Evaluation Agent independently reviews and rejects candidates who do not meet strict criteria.
- **Adaptive Replanning Rule**: Under scarcity, Orchestrator initiates dynamic replanning by selectively relaxing preferred requirements while strictly keeping mandatory requirements 100% unchanged.
- **RAG-Powered Retrieval**: Local ChromaDB vector database with `sentence-transformers/all-MiniLM-L6-v2` embeddings.
- **Real-Time Streaming**: Server-Sent Events (SSE) telemetry feed streaming agent reasoning to the frontend.

---

## 🤖 Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR AGENT                      │
│  (coordinates, delegates, monitors, replans on conflict)    │
└────────────────────────────┬────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌──────────────────┐
│ Job Analysis  │   │Resume Analysis│   │  Matching Agent  │
│     Agent     │   │     Agent     │   │  (RAG + Score)   │
└───────────────┘   └───────────────┘   └──────────────────┘
                                                │
                                                ▼ shortlist
                                       ┌──────────────────┐
                                       │ Evaluation Agent │◄──── CONFLICT
                                       │ (Hybrid Critic)  │      REJECTION
                                       └──────────────────┘
                                                │
                                                ▼ approved
                                       ┌──────────────────┐
                                       │  Communication   │
                                       │     Agent        │
                                       └──────────────────┘
```

### Agent Roles (All 6 Named Agents)

| Agent | Role | Execution Type |
|-------|------|----------------|
| **1. OrchestratorAgent** | Central coordinator, task delegator, conflict reconciler & dynamic replanner | Strategic Orchestration & Rule Engine |
| **2. JobAnalysisAgent** | Extracts mandatory vs preferred requirements from JD | Structured Extraction (LLM + JSON) |
| **3. ResumeAnalysisAgent** | Parses raw resumes, extracts skills & experience into ChromaDB | Entity Extraction & Vector Ingestion |
| **4. MatchingAgent** | Semantic search + deterministic ranking via RAG | ChromaDB Similarity + Scoring Tool |
| **5. Candidate Evaluation Agent** | Independent critic that challenges matching shortlist | **Dual-Stage Hybrid Critic** (Hard Rules + LLM) |
| **6. CommunicationAgent** | Crafts personalized outreach and interview invitations | Generative Communication (LLM) |

---

## 🎓 Response to Review Comments & Concrete Worked Example

### 1. Concrete Worked Example (End-to-End Across All 6 Agents)

A sample job posting (**"Senior Full Stack Engineer"** at TechNova Inc.) walked through all 6 agents:

1. **JobAnalysisAgent**: Extracts mandatory criteria (`React`, `Node.js`, `TypeScript`, `PostgreSQL`, `5+ years experience`) and preferred criteria (`AWS Cloud`, `Docker/Kubernetes`, `GraphQL`).
2. **ResumeAnalysisAgent**: Ingests 6 candidates into ChromaDB (Kavya Reddy, Priya Sharma, Arjun Mehta, Aisha Patel, Vikram Rao, Sneha Iyer).
3. **MatchingAgent**: Executes semantic RAG retrieval and proposes initial top 3 shortlist:
   - *Kavya Reddy* (Score: 87.5/100) — Strong lead
   - *Priya Sharma* (Score: 82.0/100) — Solid enterprise engineer
   - *Arjun Mehta* (Score: 41.0/100) — Prematurely included to fulfill requested `top_n=3` due to high keyword match.
4. **Candidate Evaluation Agent (Critic Disagreement)**: **CHALLENGES & REJECTS Arjun Mehta**:
   - *Hard Rule Check*: Arjun Mehta has score 41.0 (below 50.0 threshold) and is missing mandatory `TypeScript`, `PostgreSQL`, and has only 3.0 yrs experience (5+ required).
   - *LLM Qualitative Audit*: Superficial buzzword match without architectural depth. Shortlist rejected.
5. **OrchestratorAgent (Conflict Resolution & Dynamic Replanning)**:
   - Detects conflict from EvaluationAgent.
   - Applies the precise business rule: **Selectively relax PREFERRED requirements (AWS, GraphQL) while STRICTLY PRESERVING MANDATORY requirements (TypeScript, PostgreSQL, 5+ yrs)**.
   - Issues `REPLAN_RELAXED` directive to MatchingAgent.
6. **MatchingAgent (Rerun with Relaxed Preferred Criteria)**:
   - Retrieves *Aisha Patel* (Score: 72.0/100, strong distributed backend and database foundation).
   - Revised shortlist: Kavya Reddy (90.0), Priya Sharma (85.0), Aisha Patel (72.0).
7. **Candidate Evaluation Agent (Verification)**:
   - Verifies all 3 candidates satisfy 100% of mandatory requirements. **APPROVES shortlist**.
8. **CommunicationAgent (Outreach Generation)**:
   - Drafts bespoke interview invitation letters tailored to each candidate's specific background and achievements.

### 2. Evaluation Agent Challenge Mechanism: LLM vs Hard Rule Check

> **Reviewer Weakness Addressed**: *Is the Evaluation Agent's "challenge" an LLM judgment call or a hard rule-based check?*

It is explicitly a **Dual-Stage Hybrid Critic Architecture**:
- **Stage 1 (Hard Rule-Based Deterministic Check)**: Implemented in the Python scoring engine (`scoring_tool.py`). Deterministically validates that 100% of non-negotiable mandatory skills are present and composite score $\ge 50$. Any missing mandatory requirement triggers an automatic hard rejection flag.
- **Stage 2 (LLM Qualitative Judgment Call)**: Executed via Groq LLaMA-3.3-70B. Evaluates nuance that keyword tools miss: production architectural scale, engineering leadership, and verifies that claimed technologies align with demonstrable project outcomes in the raw resume text.

---

## 🏗️ Project Structure

```
AI_CA_3/
├── backend/
│   ├── agents/               # All 5 AI agents + orchestrator
│   │   ├── orchestrator.py   # Central coordinator with replanning
│   │   ├── resume_analysis_agent.py
│   │   ├── job_analysis_agent.py
│   │   ├── matching_agent.py
│   │   ├── evaluation_agent.py
│   │   └── communication_agent.py
│   ├── tools/                # CrewAI-compatible tools
│   │   ├── rag_tool.py       # ChromaDB semantic retrieval
│   │   └── scoring_tool.py   # Deterministic skill scoring
│   ├── lib/                  # Core library
│   │   ├── models.py         # Pydantic data models
│   │   └── chroma_store.py   # Vector store manager
│   ├── data/                 # Sample data
│   │   ├── sample_resumes.json
│   │   └── sample_jobs.json
│   ├── tests/                # Automated tests
│   │   └── test_agents.py
│   ├── main.py               # FastAPI backend
│   ├── data_loader.py        # Sample data + demo trace
│   └── requirements.txt
├── frontend/                 # Next.js 14 frontend
│   ├── app/                  # App Router pages
│   └── components/           # React components
├── docs/
│   ├── design_document.md    # Full system design
│   └── execution_trace.md    # Sample execution trace
└── README.md
```

---

## 🚀 Quick Start

### ⚡ 1-Click Launch (Windows)

Simply double-click **`run.bat`** (or run `.\run.ps1` in PowerShell).  
It will automatically:
1. Start the FastAPI backend on `http://127.0.0.1:8000`
2. Start the Next.js 14 frontend on `http://localhost:3001` (preventing any port 3000 collision)
3. Open your default browser directly to the dashboard.

---

### Manual Setup

#### Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API key (optional — if unconfigured, automatic concrete worked example simulation is streamed seamlessly)

#### Backend Setup

```bash
cd backend
cp .env.example .env
# Edit .env and set your GROQ_API_KEY (or use pre-built worked example)

pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
# Backend runs at http://127.0.0.1:8000
# Swagger documentation at http://127.0.0.1:8000/docs
```

#### Frontend Setup

```bash
cd frontend
npm install
npm run dev
# Frontend runs at http://localhost:3001
```

### Run Tests

```bash
cd backend
pytest tests/ -v
```

---

## 🔄 Agentic Pipeline Flow

```
Input: Job Description + Resumes
         │
         ▼
[1] JobAnalysisAgent → extracts mandatory + preferred requirements
         │
         ▼
[2] ResumeAnalysisAgent (×N) → parses each resume → indexes in ChromaDB
         │
         ▼
[3] MatchingAgent → semantic search via RAG → scores candidates
         │
         ▼
[4] EvaluationAgent → independent review
         │
    ┌────┴─────────────────────────┐
    │                              │
  APPROVE                       REJECT ──► Orchestrator replans
    │                              │         (relax requirements)
    ▼                              └──────►  [3] MatchingAgent (retry)
[5] CommunicationAgent
    → Interview invitations
    → Rejection notices
         │
         ▼
      Output: Ranked shortlist + Communications
```

---

## 🧪 Testing

```bash
cd backend
pytest tests/test_agents.py -v
```

Tests cover:
- Scoring tool (perfect match, missing mandatory, score range)
- Pydantic data models
- ChromaDB store (add, search, clear)
- Data loader (samples, demo trace with conflict/replan events)

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | System health + resume count |
| `GET` | `/api/samples` | Sample JDs and resumes |
| `POST` | `/api/recruit/stream` | SSE streaming pipeline |
| `POST` | `/api/recruit` | Non-streaming pipeline |
| `GET` | `/api/trace/demo` | Pre-built execution trace |
| `GET` | `/docs` | Interactive API docs (Swagger) |

---

## 🛠️ Technology Choices

| Component | Technology | Reason |
|-----------|-----------|--------|
| Agent Framework | **CrewAI** | Clean Agent/Task/Crew abstraction, native tool support |
| LLM Provider | **Groq** | Ultra-fast inference (llama-3.3-70b), free tier |
| Vector Store | **ChromaDB** | Local persistence, cosine similarity, no API cost |
| Embeddings | **sentence-transformers** | `all-MiniLM-L6-v2` — fast, accurate, local |
| Backend | **FastAPI** | Async SSE streaming, automatic OpenAPI docs |
| Frontend | **Next.js 14** | App Router, TypeScript, SSE-compatible |

---

---
## 📄 Documentation

- [Design Document](docs/design_document.md)
- [Execution Trace](docs/execution_trace.md)
- [API Docs](http://localhost:8000/docs) (when running locally)

