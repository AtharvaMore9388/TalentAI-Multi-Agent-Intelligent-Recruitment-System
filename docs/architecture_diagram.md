# TalentAI — Architecture Diagram & System Workflow

This document details the multi-agent architectural topology, message flow, and dynamic replanning sequence for **TalentAI**.

---

## 1. Multi-Agent Pipeline Topology

```mermaid
flowchart TD
    subgraph UI ["Frontend (Next.js 14)"]
        Client[Web Client / Recruiter Dashboard]
        SSE[SSE Live Stream Consumer]
    end

    subgraph API ["FastAPI Backend"]
        Endpoint["/api/recruit (Streaming Endpoint)"]
    end

    subgraph Orchestration ["Centralized Orchestrator"]
        Orch[Orchestrator Agent]
        State[(Recruitment State Store)]
    end

    subgraph Agents ["Specialized Domain Agents"]
        JAA[Job Analysis Agent]
        RAA[Resume Analysis Agent]
        MA[Matching & Ranking Agent]
        EA[Candidate Evaluation Agent]
        CA[Recruitment Communication Agent]
    end

    subgraph VectorDB ["RAG Knowledge Layer"]
        Chroma[(ChromaDB Vector Store)]
        Embed[all-MiniLM-L6-v2 Embeddings]
    end

    Client -->|Submit JD & Resumes| Endpoint
    Endpoint -->|Initialize State| Orch
    Orch <-->|Read / Write State| State
    Orch -->|Stream Agent Events| SSE
    SSE --> Client

    %% Workflow delegations
    Orch -->|1. Parse Requirements| JAA
    Orch -->|2. Extract Profiles| RAA
    RAA -->|Index Resumes| Chroma
    Embed -.->|Generate Vectors| Chroma

    Orch -->|3. Query & Rank| MA
    MA <-->|Semantic Search RAG| Chroma
    MA -->|Ranked Shortlist| Orch

    Orch -->|4. Independent Verification| EA
    
    %% Conflict & Replan Loop
    EA -- "Shortlist Approved (>= 2 verified)" --> Orch
    EA -- "Conflict: Shortlist Rejected" --> Orch
    Orch -.->|Dynamic Replan: Relax Requirements| MA

    %% Final Outreach
    Orch -->|5. Draft Communications| CA
    CA -->|Interview Invites & Rejections| Orch
    Orch -->|Final Results JSON + Stream| Endpoint
```

---

## 2. Dynamic Conflict Resolution & Replanning Sequence

```mermaid
sequenceDiagram
    autonumber
    actor Recruiter as User / Recruiter
    participant Orch as Orchestrator Agent
    participant JAA as Job Analysis Agent
    participant RAA as Resume Analysis Agent
    participant MA as Matching Agent
    participant Chroma as ChromaDB RAG
    participant EA as Evaluation Agent
    participant CA as Communication Agent

    Recruiter->>Orch: Submit Job Description & Candidate Resumes
    Orch->>JAA: Analyze JD (Mandatory vs. Preferred)
    JAA-->>Orch: JobDescription (mandatory=['Python', 'PyTorch'], preferred=['Kubernetes'])
    
    Orch->>RAA: Parse Candidates & Extract Skills
    RAA-->>Chroma: Index Candidate Resumes into Vector Store
    RAA-->>Orch: Structured Candidate Profiles

    Orch->>MA: Perform Semantic Match & Rank Candidates
    MA->>Chroma: Vector Similarity Search
    Chroma-->>MA: Top Candidate Matches
    MA-->>Orch: Ranked Candidates Shortlist [Candidate A, Candidate B]

    Orch->>EA: Independently Verify Shortlist Quality
    Note over EA: Evaluation Agent performs strict audit<br/>against mandatory requirements
    alt Evaluation Agent Rejects (Candidate lacks core requirement)
        EA-->>Orch: CONFLICT: Rejection (Candidate B lacks PyTorch!)
        Note over Orch: Dynamic Replanning Triggered: Relax preferred requirements<br/>and request re-match
        Orch->>MA: Replan Request: Lower preferred threshold, find substitutes
        MA->>Chroma: Re-query Vector DB with relaxed criteria
        Chroma-->>MA: New candidate pool
        MA-->>Orch: Revised Candidate Shortlist
        Orch->>EA: Re-evaluate Revised Shortlist
        EA-->>Orch: APPROVED: Revised Shortlist meets mandatory criteria
    else Evaluation Agent Approves
        EA-->>Orch: APPROVED: Shortlist satisfies criteria
    end

    Orch->>CA: Generate Outreach Messages
    CA-->>Orch: Drafted Personalized Emails (Invites + Rejections)
    Orch-->>Recruiter: Final Results (Shortlist, Audit Notes, Email Drafts)
```

---

## 3. Communication Pattern Summary

| Step | Sender | Receiver | Payload / Message Type | Purpose |
|------|--------|----------|------------------------|---------|
| 1 | Orchestrator | Job Analysis Agent | Raw Job Text | Extract required & preferred technical qualifications |
| 2 | Orchestrator | Resume Analysis Agent | Raw Resumes List | Structured extraction and vector indexing |
| 3 | Orchestrator | Matching Agent | `JobDescription` + candidate pool | Vector RAG retrieval and composite scoring |
| 4 | Orchestrator | Evaluation Agent | Shortlisted Candidates + `JobDescription` | Independent scrutiny and validation |
| 5 | Evaluation Agent | Orchestrator | `APPROVED` or `REJECTED` + conflict explanation | Quality gate / challenge to Matching Agent |
| 6 | Orchestrator (Replan) | Matching Agent | Revised search parameters | Dynamic replanning on conflict or low candidate count |
| 7 | Orchestrator | Communication Agent | Final evaluated shortlist | Automated tailored outreach email generation |
