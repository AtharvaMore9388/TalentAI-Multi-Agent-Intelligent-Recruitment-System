# TalentAI — Design Document

## 1. System Overview

**TalentAI** is a multi-agent AI recruitment platform that autonomously processes job descriptions and resumes to intelligently match and rank candidates. The system demonstrates genuine multi-agent collaboration including conflict resolution, dynamic replanning, and adaptive decision-making.

**Target Users**: HR teams, recruiters, talent acquisition specialists, and small-to-medium businesses looking to automate first-stage candidate screening.

---

## 2. Architecture Diagram

```
                    ┌──────────────────────────────────────────────────────────┐
                    │                   ORCHESTRATOR AGENT                      │
                    │                                                            │
                    │  • Delegates to specialized agents                         │
                    │  • Monitors agent outputs                                  │
                    │  • Detects conflicts (EvaluationAgent rejection)           │
                    │  • Dynamically replans (relax requirements, retry)        │
                    │  • Decides when pipeline reaches satisfactory conclusion   │
                    └────────┬─────────────────────────────────────┬────────────┘
                             │ delegates                           │ reconciles
                    ┌────────▼──────────┐              ┌──────────▼──────────┐
                    │ Job Analysis Agent│              │  Resume Analysis    │
                    │                   │              │       Agent (×N)    │
                    │ • Reads raw JD    │              │                     │
                    │ • Extracts        │              │ • Parses raw text   │
                    │   mandatory reqs  │              │ • Extracts: name,   │
                    │ • Extracts        │              │   email, skills,    │
                    │   preferred reqs  │              │   experience, edu   │
                    │ • Returns JSON    │              │ • Indexes in Chroma │
                    └────────┬──────────┘              └──────────┬──────────┘
                             │                                    │
                             └──────────────┬─────────────────────┘
                                            │ job + candidates
                                   ┌────────▼────────────────┐
                                   │  Matching & Ranking      │
                                   │        Agent             │
                                   │                          │
                                   │ • RAG: ChromaDB semantic │
                                   │   search (cosine sim.)   │
                                   │ • Scores each candidate  │
                                   │   (mandatory 60% +       │
                                   │    preferred 30% +       │
                                   │    experience 10%)       │
                                   │ • Returns ranked list    │
                                   └────────┬────────────────┘
                                            │ shortlist
                                   ┌────────▼────────────────┐
                                   │   Evaluation Agent       │  ◄── INDEPENDENT
                                   │                          │      (separate LLM call)
                                   │ • Reviews each candidate │
                                   │ • Checks mandatory reqs  │
                                   │ • Can APPROVE or REJECT  │
                                   │ • Flags weak candidates  │
                                   │ • Adds audit notes       │
                                   └────────┬────────────────┘
                                            │
                         ┌──────────────────┴──────────────────┐
                         │ APPROVE                    REJECT    │
                         ▼                              ▼        │
                ┌────────────────┐          ┌──────────────────┐│
                │ Communication  │          │   Orchestrator   ││
                │    Agent       │          │   Replanning     ││
                │                │          │                  ││
                │ • Interview    │          │ • Relax prefs    ││
                │   invitations  │          │ • Retry matching ││
                │ • Rejection    │          │ • Escalate       ││
                │   notices      │          │ • Accept partial ││
                └────────────────┘          └──────────────────┘│
                         ▲                              │        │
                         └──────────────────────────────┘        │
                                      (max 2 rounds)              │
```

### Data Flow

```
INPUT: raw_job_description (string) + raw_resumes[] (string[])
    ↓
[JobAnalysisAgent] → JobDescription { title, company, mandatory[], preferred[] }
    ↓
[ResumeAnalysisAgent × N] → Candidate[] { name, email, skills[], experience, education }
    ↓ (stored in ChromaDB)
[MatchingAgent] → MatchedCandidate[] { score, matched_mandatory, missing_mandatory }
    ↓
[EvaluationAgent] → verdict: APPROVE | REJECT
    ↓ if REJECT
[Orchestrator] → action: replan_relaxed | replan_strict | escalate | accept_partial
    ↓
[CommunicationAgent] → List[email_text]
    ↓
OUTPUT: { shortlisted_candidates, communications, execution_trace }
```

---

## 3. Agent Roles & Responsibilities

### 3.1 Orchestrator Agent
- **Role**: Central coordinator and decision-maker
- **Responsibilities**:
  - Delegates tasks to specialized agents in the correct order
  - Reads each agent's output before deciding the next step
  - When EvaluationAgent rejects: calls `orchestrator_decide_replan()` which uses an LLM to decide between 4 strategies
  - Tracks replan round count (max 2 rounds to prevent infinite loops)
  - Maintains shared `RecruitmentState` object
- **Coordination Pattern**: **Orchestrator-Worker** (centralized control)
- **LLM Usage**: Strategic decision-making (replan decisions, pipeline summaries)

### 3.2 Job Analysis Agent
- **Role**: Job Description Parser
- **Responsibilities**:
  - Reads raw job description text
  - Extracts **mandatory requirements** (must-have skills/experience)
  - Extracts **preferred requirements** (nice-to-have)
  - Identifies job title and company name
- **Output**: `JobDescription` Pydantic model
- **LLM Usage**: Entity extraction, requirement classification

### 3.3 Resume Analysis Agent
- **Role**: Resume Parser
- **Responsibilities**:
  - Parses raw resume text for each candidate
  - Extracts: name, email, phone, skills[], experience_years, education, summary
  - Returns structured `Candidate` Pydantic model
  - Stores embedding in ChromaDB
- **Output**: `Candidate` Pydantic model
- **LLM Usage**: Structured information extraction (uses fast LLM: llama-3.1-8b-instant)

### 3.4 Matching & Ranking Agent
- **Role**: Semantic Candidate Retrieval & Scoring
- **Responsibilities**:
  - Performs semantic search via ChromaDB using `all-MiniLM-L6-v2` embeddings
  - Scores each candidate against mandatory (60%) and preferred (30%) requirements + experience (10%)
  - In relaxed mode (after Orchestrator replanning): drops preferred requirement scoring
  - Returns ranked shortlist with match breakdown
- **Tools**: `RAGRetrievalTool`, `ScoringTool`
- **LLM Usage**: Rationale generation for shortlisting decision

### 3.5 Evaluation Agent (Independent Verifier)
- **Role**: Quality Gate — Independent Reviewer
- **Responsibilities**:
  - Independently re-evaluates the shortlist provided by MatchingAgent
  - Checks mandatory requirement coverage for each candidate
  - Can issue APPROVE or REJECT verdict
  - Flags weak candidates
  - Triggers Orchestrator conflict resolution when rejecting
- **Key Design**: Operates independently from MatchingAgent — separate LLM call with no shared state
- **LLM Usage**: Critical evaluation, verdict generation

### 3.6 Communication Agent
- **Role**: Recruitment Communications Generator
- **Responsibilities**:
  - Generates personalized interview invitations for approved candidates
  - Generates respectful rejection notices for rejected candidates
  - Ensures professional tone without revealing internal scores
- **LLM Usage**: Natural language generation, personalization

---

## 4. Orchestration Pattern

**Pattern**: **Orchestrator-Worker** (centralized coordination)

The Orchestrator maintains full authority over the pipeline flow. Unlike a peer-to-peer pattern where agents communicate directly, all inter-agent communication goes through the Orchestrator. The EvaluationAgent can send a REJECT signal back to the Orchestrator, which then decides the next action.

**Conflict Resolution Mechanism**:
1. EvaluationAgent emits REJECT verdict
2. Orchestrator calls `orchestrator_decide_replan()` — an LLM-driven decision function
3. LLM considers: candidate count, missing requirements, replan rounds used, and requirement types
4. LLM selects one of 4 actions: `replan_relaxed | replan_strict | escalate | accept_partial`
5. Orchestrator executes the chosen action
6. Maximum 2 replan rounds to prevent infinite loops

---

## 5. Technology Choices

| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| Agent Framework | **CrewAI** | 1.15.x | Clean Agent/Task/Crew abstraction. Native tool support. Well-documented orchestrator-worker pattern. |
| LLM (Primary) | **Groq llama-3.3-70b-versatile** | - | Ultra-fast inference (<1s latency), high accuracy, generous free tier, no timeout issues |
| LLM (Fast) | **Groq llama-3.1-8b-instant** | - | For high-volume resume parsing, reduces cost while maintaining quality |
| Vector Store | **ChromaDB** | 1.x | Local persistence, cosine similarity, no API cost, easy integration with sentence-transformers |
| Embeddings | **sentence-transformers** | 6.x | `all-MiniLM-L6-v2` model: 384-dim embeddings, runs locally, excellent semantic quality |
| Backend | **FastAPI** | 0.115.x | Async SSE streaming (real-time agent messages), automatic OpenAPI docs, Pydantic integration |
| Frontend | **Next.js 14** | - | App Router, TypeScript, compatible with SSE streaming |

---

## 6. Input / Output Definitions

### 6.1 Input Schema

```json
{
  "job_description": "string (raw JD text, min 100 chars)",
  "resumes": ["string (raw resume text for each candidate)"],
  "top_n": "integer (default: 5, number of candidates to shortlist)"
}
```

**Sample Input** (POST `/api/recruit/stream`):
```json
{
  "job_description": "We are looking for a Senior Full Stack Engineer with 4+ years experience in React, Node.js, TypeScript. Must have: Docker, Kubernetes, PostgreSQL, AWS. Preferred: GraphQL, Redis, microservices.",
  "resumes": [
    "Priya Sharma | priya.sharma@email.com\nSKILLS: React, TypeScript, Node.js, Docker, Kubernetes, PostgreSQL, AWS, GraphQL\nEXPERIENCE: 6 years at Infosys...",
    "Arjun Mehta | arjun.mehta@email.com\nSKILLS: React, JavaScript, Node.js, MySQL\nEXPERIENCE: 3 years..."
  ],
  "top_n": 3
}
```

### 6.2 Output Schema

**Streaming Output** (SSE events, one per agent action):
```json
{
  "agent": "string (agent name)",
  "role": "action | decision | conflict | replan | result",
  "content": "string (message content)",
  "timestamp": "ISO 8601 datetime"
}
```

**Final State** (`/api/recruit` endpoint):
```json
{
  "state": {
    "job": { "id": "...", "title": "...", "company": "...", "mandatory_requirements": [...], "preferred_requirements": [...] },
    "candidates": [{ "id": "...", "name": "...", "email": "...", "skills": [...], "experience_years": 6.0, "education": "..." }],
    "shortlisted": [{
      "candidate": { ... },
      "match_score": 87.5,
      "matched_mandatory": ["react", "typescript", "docker"],
      "missing_mandatory": [],
      "matched_preferred": ["graphql"],
      "missing_preferred": ["redis"],
      "evaluation_notes": "Strong mandatory coverage; approved."
    }],
    "evaluation_passed": true,
    "replan_count": 1,
    "relaxed_requirements": true,
    "final_communications": ["📧 INTERVIEW INVITATION — Priya Sharma (priya.sharma@email.com)\n..."],
    "status": "completed"
  },
  "execution_trace": [{ "agent": "...", "role": "...", "content": "...", "timestamp": "..." }]
}
```

---

## 7. Agentic Behaviors Demonstrated

| Behavior | Implementation |
|----------|----------------|
| **Planning** | Orchestrator plans multi-step pipeline, adapts based on agent feedback |
| **Tool Use** | MatchingAgent uses `RAGRetrievalTool` and `ScoringTool` |
| **Memory** | `RecruitmentState` tracks full pipeline state; ChromaDB persists embeddings |
| **Adaptation** | Orchestrator relaxes requirements or escalates when candidates insufficient |
| **Agent-to-Agent Conflict** | EvaluationAgent challenges MatchingAgent's shortlist |
| **Conflict Resolution** | Orchestrator reconciles REJECT verdict via LLM-driven decision |
| **Dynamic Replanning** | Orchestrator reruns matching with modified strategy (up to 2 rounds) |
| **Independent Verification** | EvaluationAgent is intentionally kept separate from MatchingAgent |
