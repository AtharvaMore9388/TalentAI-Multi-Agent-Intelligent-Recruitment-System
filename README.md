# TalentAI: Multi-Agent Intelligent Recruitment and Talent Matching System

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![CrewAI](https://img.shields.io/badge/Framework-CrewAI-purple.svg)](https://crewai.com)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js_14-black.svg)](https://nextjs.org)
[![Groq](https://img.shields.io/badge/LLM-Groq-orange.svg)](https://groq.com)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-yellow.svg)](https://chromadb.com)

## 🎯 Project Overview

TalentAI is a **multi-agent AI recruitment platform** that intelligently connects candidates and companies using five specialized AI agents, RAG-based semantic search, and an adaptive Orchestrator Agent that coordinates the entire pipeline — including **conflict resolution and dynamic replanning**.

### Key Features
- **5 Specialized Agents**: Each with a distinct role and LLM-powered reasoning
- **Real Agentic Behavior**: Agents disagree, challenge each other, and trigger replanning
- **RAG-Powered Matching**: ChromaDB vector store + sentence-transformers for semantic resume retrieval
- **Conflict Resolution**: EvaluationAgent can REJECT the Matching Agent's shortlist
- **Dynamic Replanning**: Orchestrator relaxes requirements or retries when candidates are insufficient
- **Real-Time Streaming**: SSE-based live agent message feed to the frontend

---

## 🤖 Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR AGENT                       │
│  (coordinates, delegates, monitors, replans on conflict)     │
└────────────────────────────┬────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌──────────────────┐
│  Job Analysis │   │Resume Analysis│   │  Matching Agent  │
│     Agent     │   │    Agent      │   │  (RAG + Score)   │
└───────────────┘   └───────────────┘   └──────────────────┘
                                                │
                                                ▼ shortlist
                                       ┌──────────────────┐
                                       │ Evaluation Agent │◄──── CONFLICT
                                       │ (independent)    │      REJECTION
                                       └──────────────────┘
                                                │
                                                ▼ approved
                                       ┌──────────────────┐
                                       │ Communication    │
                                       │    Agent         │
                                       └──────────────────┘
```

### Agent Roles

| Agent | Role | LLM Task |
|-------|------|----------|
| **OrchestratorAgent** | Coordinates pipeline, decides replanning | Strategic decision-making |
| **JobAnalysisAgent** | Extracts mandatory vs preferred requirements | Structured extraction |
| **ResumeAnalysisAgent** | Parses resumes into structured data | Entity extraction |
| **MatchingAgent** | Semantic search + ranking via RAG | Retrieval + scoring |
| **EvaluationAgent** | Independently verifies shortlist quality | Critical evaluation |
| **CommunicationAgent** | Generates personalized emails | Natural language generation |

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

### Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Backend Setup

```bash
cd backend
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

pip install -r requirements.txt
python main.py
# Backend runs at http://localhost:8000
```

### Frontend Setup

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
# Frontend runs at http://localhost:3000
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

## 👥 Team Members

| Name | GitHub Username | Primary Role |
|------|----------------|--------------|
| Atharva More | @atharvamore | Orchestrator + Evaluation Agent |

---

## 📄 Documentation

- [Design Document](docs/design_document.md)
- [Execution Trace](docs/execution_trace.md)
- [API Docs](http://localhost:8000/docs) (when running locally)
